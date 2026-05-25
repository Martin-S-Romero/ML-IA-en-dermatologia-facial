import io
import json
import os
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from PIL import Image

from app import models, schemas
from app.api import deps
from app.core.face_censor import FaceCensor
from app.core.logger import logger
from app.worker.tasks import process_image_task

router = APIRouter()

UPLOAD_DIR    = "/app/uploads"
PROCESSED_DIR = "/app/processed"
os.makedirs(UPLOAD_DIR,    exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

MAX_FILE_SIZE        = 10 * 1024 * 1024          # 10 MB
ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png"]


# ── HELPERS ───────────────────────────────────────────────────────────────

def _validate_image(contents: bytes, content_type: str) -> None:
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="El archivo supera el límite de 10 MB.",
        )
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato no permitido. Solo JPEG y PNG.",
        )
    try:
        Image.open(io.BytesIO(contents)).verify()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo no es una imagen válida o está corrupto.",
        )


# ── LA LÓGICA DE PROCESAMIENTO SE MOVIÓ A CELERY (app.worker.tasks) ──────────


# ── ENDPOINTS ─────────────────────────────────────────────────────────────

@router.post("/upload", response_model=schemas.AnalysisCreated, status_code=status.HTTP_202_ACCEPTED)
async def upload_image(
    file: UploadFile = File(..., description="Imagen JPG o PNG a analizar (máx 10 MB)"),
    censor_mode: str = Form("blur", description="Modo de censura facial: 'blur' (desenfoque), 'black' (recuadro negro) o 'pixelate' (pixelado)"),
    blur_strength: int = Form(55, description="Intensidad del desenfoque (solo aplica si censor_mode='blur'). Debe ser impar."),
    pixel_size: int = Form(10, description="Tamaño del píxel (solo aplica si censor_mode='pixelate')."),
    expand: int = Form(10, description="Píxeles extra de margen alrededor de ojos y boca en la censura."),
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """
    Recibe una imagen, la valida, crea un registro Analysis en estado 'processing'
    y lanza la censura facial como tarea de Celery en un Worker aislado.
    Devuelve el analysis_id para hacer polling de estado.

    **Modos de censura disponibles:**
    - `blur` (por defecto): Desenfoque gaussiano sobre ojos y boca.
    - `black`: Relleno negro sobre ojos y boca.
    - `pixelate`: Efecto de pixelado sobre ojos y boca.
    """
    if censor_mode not in ("blur", "black", "pixelate"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="censor_mode inválido. Usa: 'blur', 'black' o 'pixelate'.",
        )

    contents = await file.read()
    _validate_image(contents, file.content_type)

    ext              = (file.filename or "image").rsplit(".", 1)[-1].lower()
    original_name    = f"{uuid.uuid4()}.{ext}"
    censored_name    = f"{uuid.uuid4()}_censored.{ext}"
    input_path       = os.path.join(UPLOAD_DIR, original_name)
    output_path      = os.path.join(PROCESSED_DIR, censored_name)

    with open(input_path, "wb") as f:
        f.write(contents)

    analysis = models.Analysis(
        user_id           = current_user.id,
        original_filename = original_name,
        status            = "processing",
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # Lanzar la tarea de Celery al Worker de IA
    process_image_task.delay(  # type: ignore[attr-defined]
        analysis.id,
        input_path,
        output_path,
        current_user.id,
        censor_mode,
        blur_strength,
        pixel_size,
        expand,
    )

    logger.info(f"Analysis {analysis.id} sent to Celery Queue for user {current_user.id} (mode={censor_mode})")
    return {"analysis_id": analysis.id, "status": "processing"}


@router.get("/history", response_model=list[schemas.AnalysisSnapshot])
def get_history(
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Lista paginada de análisis del usuario, del más reciente al más antiguo."""
    return (
        db.query(models.Analysis)
        .filter(models.Analysis.user_id == current_user.id)
        .order_by(models.Analysis.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{analysis_id}/status", response_model=schemas.AnalysisStatusOut)
def get_status(
    analysis_id: int,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Estado del análisis: processing / completed / failed. Incluye mensaje de error si falló."""
    analysis = db.query(models.Analysis).filter(
        models.Analysis.id == analysis_id,
        models.Analysis.user_id == current_user.id,
    ).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado.")
    return {
        "analysis_id": analysis.id,
        "status": analysis.status,
        "error_message": analysis.error_message
    }


@router.get("/{analysis_id}", response_model=schemas.AnalysisOut)
def get_analysis(
    analysis_id: int,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Documento completo del análisis."""
    analysis = db.query(models.Analysis).filter(
        models.Analysis.id == analysis_id,
        models.Analysis.user_id == current_user.id,
    ).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado.")
    return analysis


@router.get("/{analysis_id}/image")
def get_analysis_image(
    analysis_id: int,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """
    Sirve la imagen censurada del análisis.
    Requiere autenticación obligatoria para garantizar que solo el propietario
    pueda acceder a sus imágenes.
    """
    analysis = db.query(models.Analysis).filter(
        models.Analysis.id == analysis_id,
        models.Analysis.user_id == current_user.id,
    ).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado.")

    # Preferir imagen censurada; caer en la original si no existe aún
    if analysis.censored_filename:
        path = os.path.join(PROCESSED_DIR, analysis.censored_filename)
        if os.path.exists(path):
            return FileResponse(path, media_type="image/jpeg")

    if analysis.original_filename:
        path = os.path.join(UPLOAD_DIR, analysis.original_filename)
        if os.path.exists(path):
            return FileResponse(path, media_type="image/jpeg")

    raise HTTPException(status_code=404, detail="Imagen no disponible aún.")
