import os
import uuid
import logging
from datetime import datetime, timezone

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.celery_app import celery_app
from app import db_scheme as models
from app.core.face_censor import FaceCensor
from app.core.skin_analysis import run_mock_skin_analysis

DATABASE_URL = os.getenv("DATABASE_URL", "")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

UPLOAD_DIR    = os.getenv("UPLOAD_DIR",    "/app/uploads")
PROCESSED_DIR = os.getenv("PROCESSED_DIR", "/app/processed")

logger = logging.getLogger(__name__)


@celery_app.task(name="app.worker.tasks.process_image_task", bind=True, max_retries=3)
def process_image_task(self, analysis_id: int, input_path: str, output_path: str, user_id: int):
    """
    Tarea de Celery: censura facial + análisis de piel.
    Corre en el contenedor ai_worker, aislado del proceso principal de FastAPI.
    """
    db = SessionLocal()
    original_deleted = False

    try:
        db.execute(
            text("SELECT set_config('app.current_user_id', :uid, false)"),
            {"uid": str(user_id)},
        )

        analysis = db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()
        if not analysis:
            logger.error(f"Analysis {analysis_id} not found in DB.")
            return

        # 1. Censura facial con MediaPipe
        logger.info(f"Starting face censorship for analysis {analysis_id}")
        censor = FaceCensor(mode="blur", blur_strength=55, expand=10)
        result = censor.process_image(input_path, output_path)

        if result is None:
            analysis.status = "failed"
            analysis.error_message = "No se detectó rostro o la resolución es insuficiente."
            db.commit()
            return

        analysis.censored_filename = os.path.basename(output_path)

        # 2. Análisis de piel (mock hasta integrar el modelo DL real)
        analysis_result = run_mock_skin_analysis(output_path)
        analysis_result["mode"] = "blur"

        # Con JSONB, se asigna el dict directamente — sin json.dumps
        analysis.result       = analysis_result
        analysis.status       = "completed"
        analysis.completed_at = datetime.now(timezone.utc)

        db.commit()
        logger.info(f"Analysis {analysis_id} completed successfully.")

        # 3. Borrar original SOLO después del commit exitoso (GDPR)
        # No va en finally para que los reintentos de Celery encuentren el archivo
        if os.path.exists(input_path):
            os.remove(input_path)
            original_deleted = True
            logger.info(f"Original image deleted for GDPR compliance: {input_path}")

    except Exception as exc:
        logger.error(f"Task failed for analysis {analysis_id}: {exc}", exc_info=True)
        db.rollback()

        # Marcar como fallido solo en el último reintento
        if self.request.retries >= self.max_retries:
            try:
                analysis = db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()
                if analysis:
                    analysis.status = "failed"
                    analysis.error_message = str(exc)[:500]
                    db.commit()
            except Exception:
                pass

        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

    finally:
        db.close()
