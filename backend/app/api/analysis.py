import io
import json
import os
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from PIL import Image

from app import models, schemas
from app.api import deps
from app.core.face_censor import FaceCensor
from app.core.logger import logger

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


def _run_censorship(analysis_id: int, input_path: str, output_path: str, db_url: str) -> None:
    """Tarea en background: aplica censura facial y actualiza el registro en BD."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine  = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    db      = Session()

    try:
        analysis = db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()
        if not analysis:
            return

        censor = FaceCensor(mode="blur", blur_strength=55, expand=10)
        result = censor.process_image(input_path, output_path)

        if result is None:
            analysis.status        = "failed"
            analysis.error_message = "No se detectó rostro o la resolución es insuficiente (mínimo ~720p)."
        else:
            censored_filename         = os.path.basename(output_path)
            analysis.status           = "completed"
            analysis.censored_filename = censored_filename
            analysis.result           = json.dumps({
                "censored_path": output_path,
                "mode": "blur",
            })
            logger.info(f"Analysis {analysis_id} completed — {censored_filename}")

        db.commit()

    except Exception as e:
        logger.error(f"Background censorship failed for analysis {analysis_id}: {e}", exc_info=True)
        try:
            analysis = db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()
            if analysis:
                analysis.status        = "failed"
                analysis.error_message = str(e)
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


# ── ENDPOINTS ─────────────────────────────────────────────────────────────

@router.post("/upload", response_model=schemas.AnalysisCreated, status_code=status.HTTP_202_ACCEPTED)
async def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """
    Recibe una imagen, la valida, crea un registro Analysis en estado 'processing'
    y lanza la censura facial como tarea en background.
    Devuelve el analysis_id para hacer polling de estado.
    """
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

    from app.core.database import DATABASE_URL
    background_tasks.add_task(
        _run_censorship,
        analysis.id,
        input_path,
        output_path,
        DATABASE_URL,
    )

    logger.info(f"Analysis {analysis.id} queued for user {current_user.id}")
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
    """Estado del análisis: processing / completed / failed."""
    analysis = db.query(models.Analysis).filter(
        models.Analysis.id == analysis_id,
        models.Analysis.user_id == current_user.id,
    ).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado.")
    return {"analysis_id": analysis.id, "status": analysis.status}


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
    db: Session = Depends(deps.get_db),
):
    """
    Sirve la imagen censurada del análisis.
    Sin autenticación — los nombres de archivo son UUIDs opacos.
    """
    analysis = db.query(models.Analysis).filter(
        models.Analysis.id == analysis_id,
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
