import os
import logging
from datetime import date, datetime, timezone

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.celery_app import celery_app
from app import db_scheme as models
from app.core.face_censor import FaceCensor
from app.core.ai_runner import run_inference
from app.core.skinai_config import EDAD_DEFAULT

DATABASE_URL = os.getenv("DATABASE_URL", "")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

UPLOAD_DIR    = os.getenv("UPLOAD_DIR",    "/app/uploads")
PROCESSED_DIR = os.getenv("PROCESSED_DIR", "/app/processed")

logger = logging.getLogger(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_perfil(db: Session, user_id: int) -> dict | None:
    """
    Construye el dict de perfil clínico a partir del SkinProfile del usuario.

    Los valores del frontend se almacenan en minúsculas ('masculino', 'grasa',
    'acné'). ajustar_por_perfil() espera la primera letra en mayúscula
    ('Masculino', 'Grasa', 'Acné'), por lo que se aplica .capitalize().
    """
    profile = (
        db.query(models.SkinProfile)
        .filter(models.SkinProfile.user_id == user_id)
        .first()
    )
    if not profile:
        return None

    edad = EDAD_DEFAULT
    if profile.birth_date:
        edad = (date.today() - profile.birth_date).days // 365

    return {
        'edad':          edad,
        'sexo':          (profile.gender    or '').capitalize(),
        'fototipo':      profile.fitzpatrick or 'Desconocido',
        'tipo_piel':     (profile.skin_type or '').capitalize(),
        'historial':     [c.capitalize() for c in (profile.skin_conditions or [])],
        'exposicion_ac': 'No',
    }


def _get_result_anterior(db: Session, user_id: int, current_analysis_id: int) -> dict | None:
    """Devuelve el campo result del último análisis completado del usuario."""
    prev = (
        db.query(models.Analysis)
        .filter(
            models.Analysis.user_id == user_id,
            models.Analysis.status  == "completed",
            models.Analysis.id      != current_analysis_id,
        )
        .order_by(models.Analysis.completed_at.desc())
        .first()
    )
    return prev.result if prev and prev.result else None


# ── Tarea Celery ──────────────────────────────────────────────────────────────

@celery_app.task(name="app.worker.tasks.process_image_task", bind=True, max_retries=3)
def process_image_task(
    self,
    analysis_id: int,
    input_path: str,
    output_path: str,
    user_id: int,
    censor_mode: str = "blur",
    blur_strength: int = 55,
    pixel_size: int = 10,
    expand: int = 10,
):
    """
    Tarea Celery: censura facial + análisis de piel con pipeline completo.
    Corre en el contenedor ai_worker, aislado del proceso principal de FastAPI.
    """
    db = SessionLocal()

    try:
        db.execute(
            text("SELECT set_config('app.current_user_id', :uid, false)"),
            {"uid": str(user_id)},
        )

        analysis = db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()
        if not analysis:
            logger.error(f"Analysis {analysis_id} not found in DB.")
            return

        # 1. Censura facial + extracción de métricas zonales
        logger.info(f"Starting censorship for analysis {analysis_id} (mode='{censor_mode}')")
        censor = FaceCensor(
            mode=censor_mode,
            blur_strength=blur_strength,
            expand=expand,
            pixel_size=pixel_size,
        )
        censor_result = censor.process_image(input_path, output_path)

        if censor_result is None:
            db.delete(analysis)
            db.commit()
            if os.path.exists(input_path):
                os.remove(input_path)
            logger.info(f"Analysis {analysis_id} deleted: no face detected.")
            return

        analisis_zonal = censor.ultimo_analisis_zonal
        analysis.censored_filename = os.path.basename(output_path)
        analysis.face_censored     = True

        # 2. Perfil clínico del usuario y análisis anterior para continuidad
        perfil          = _build_perfil(db, user_id)
        result_anterior = _get_result_anterior(db, user_id, analysis_id)

        # 3. Inferencia completa
        logger.info(f"Running full AI pipeline for analysis {analysis_id}")
        result = run_inference(
            output_path,
            analisis_zonal=analisis_zonal,
            perfil=perfil,
            result_anterior=result_anterior,
            n_aug=5,
        )

        analysis.top1_label      = result["condition"]
        analysis.top1_confidence = result["confidence"]
        analysis.model_version   = result.get("model_version")
        analysis.result          = result
        analysis.status          = "completed"
        analysis.completed_at    = datetime.now(timezone.utc)

        db.commit()
        logger.info(
            f"Analysis {analysis_id} completed: {result['condition']} "
            f"({result['confidence']*100:.1f}%) — severity {result['severity_score']:.3f}"
        )

        # 4. Borrar original tras commit exitoso (GDPR)
        if os.path.exists(input_path):
            os.remove(input_path)
            logger.info(f"Original image deleted (GDPR): {input_path}")

    except Exception as exc:
        logger.error(f"Task failed for analysis {analysis_id}: {exc}", exc_info=True)
        db.rollback()

        if self.request.retries >= self.max_retries:
            try:
                analysis = db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()
                if analysis:
                    analysis.status        = "failed"
                    analysis.error_message = str(exc)[:500]
                    db.commit()
            except Exception:
                pass

        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

    finally:
        db.close()
