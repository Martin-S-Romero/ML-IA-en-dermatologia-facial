import os
import json
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.celery_app import celery_app
from app import models
from app.core.face_censor import FaceCensor
from app.core.skin_analysis import run_mock_skin_analysis

# Worker needs its own DB connection to update analysis status
# Usamos el usuario 'postgres' superuser para saltar RLS desde el worker de backend
# o usamos el de entorno
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/tesis_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
    Tarea de Celery para procesar la imagen con IA y mock de análisis de piel.
    Se ejecuta en un contenedor aislado (Worker).

    Parámetros de censura:
        censor_mode: "blur" | "black" | "pixelate"
        blur_strength: intensidad del desenfoque (modo blur)
        pixel_size: tamaño del píxel (modo pixelate)
        expand: margen extra en píxeles alrededor de ojos y boca
    """
    db = SessionLocal()
    
    try:
        from sqlalchemy import text
        # 1. Configurar RLS manualmente para esta sesión
        db.execute(text(f"SET app.current_user_id = '{user_id}';"))
        
        analysis = db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()
        if not analysis:
            logger.error(f"Analysis {analysis_id} not found.")
            return "Analysis not found"

        logger.info(f"Starting censorship for analysis {analysis_id} with mode='{censor_mode}'")
        censor = FaceCensor(
            mode=censor_mode,
            blur_strength=blur_strength,
            expand=expand,
            pixel_size=pixel_size,
        )
        result = censor.process_image(input_path, output_path)

        if result is None:
            analysis.status = "failed"
            analysis.error_message = "No se detectó rostro o la resolución es insuficiente."
        else:
            censored_filename = os.path.basename(output_path)
            analysis.censored_filename = censored_filename
            
            # Simulamos análisis de piel en la IA
            analysis_result = run_mock_skin_analysis(output_path)
            analysis_result["censored_path"] = output_path
            analysis_result["mode"] = "blur"
            
            analysis.result = json.dumps(analysis_result)
            analysis.status = "completed"
            
            logger.info(f"Analysis {analysis_id} completed successfully.")

        db.commit()

    except Exception as e:
        logger.error(f"Task failed for analysis {analysis_id}: {e}", exc_info=True)
        try:
            from sqlalchemy import text
            db.execute(text(f"SET app.current_user_id = '{user_id}';"))
            analysis = db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()
            if analysis:
                analysis.status = "failed"
                analysis.error_message = str(e)
                db.commit()
        except Exception:
            pass
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
        
    finally:
        db.close()
        
        # Eliminar original GDPR compliance
        if os.path.exists(input_path):
            try:
                os.remove(input_path)
                logger.info(f"Deleted original image for GDPR compliance: {input_path}")
            except Exception as e:
                logger.error(f"Failed to delete original image {input_path}: {e}")

    return "Task completed"
