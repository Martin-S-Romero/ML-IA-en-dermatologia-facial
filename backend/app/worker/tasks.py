import os
import logging
from datetime import datetime, timezone

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.celery_app import celery_app
from app import db_scheme as models
from app.core.face_censor_v2 import FaceCensor
from app.core.ai_runner import run_inference

DATABASE_URL = os.getenv("DATABASE_URL", "")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

UPLOAD_DIR    = os.getenv("UPLOAD_DIR",    "/app/uploads")
PROCESSED_DIR = os.getenv("PROCESSED_DIR", "/app/processed")

logger = logging.getLogger(__name__)


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
<<<<<<< HEAD
    Tarea de Celery: censura facial + análisis de piel con modelo real.
=======
>>>>>>> c81be0d2805a5c3c85a3b2d26d6b57df4695a085
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

        logger.info(f"Starting censorship for analysis {analysis_id} with mode='{censor_mode}'")
        censor = FaceCensor(
            mode=censor_mode,
            blur_strength=blur_strength,
            expand=expand,
            pixel_size=pixel_size,
        )
        result = censor.process_image(input_path, output_path)

        if result is None:
            # Borrar el registro completo — no aparece en historial
            db.delete(analysis)
            db.commit()
            if os.path.exists(input_path):
                os.remove(input_path)
            logger.info(f"Analysis {analysis_id} deleted: no face detected.")
            return

        analysis.censored_filename = os.path.basename(output_path)
        analysis.face_censored     = True

        # 2. Análisis de piel con modelo EfficientNet-B3 + TTA
        logger.info(f"Running AI inference for analysis {analysis_id}")
        inference = run_inference(output_path, n_aug=5)

        analysis.top1_label      = inference["top1_label"]
        analysis.top1_confidence = inference["top1_confidence"]
        analysis.model_version   = inference["model_version"]
        analysis.result          = inference          # JSONB — dict directo
        analysis.status          = "completed"
        analysis.completed_at    = datetime.now(timezone.utc)

        db.commit()
        logger.info(
            f"Analysis {analysis_id} completed: {inference['top1_label']} "
            f"({inference['top1_confidence']*100:.1f}%)"
        )

        # 3. Borrar original SOLO después del commit exitoso (GDPR)
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
