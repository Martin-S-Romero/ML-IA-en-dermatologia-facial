from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db_scheme.base import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id                 = Column(Integer, primary_key=True, index=True)
    user_id            = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Archivos
    original_filename  = Column(String(255), nullable=True)   # se borra tras procesar (GDPR)
    censored_filename  = Column(String(255), nullable=True)
    face_censored      = Column(Boolean, default=False, nullable=False)

    # Contexto capturado desde el frontend
    lighting           = Column(String(50), nullable=True)    # natural / artificial / low / unknown
    device             = Column(String(255), nullable=True)

    # Estado: processing / completed / failed
    status             = Column(String(20), default="processing", nullable=False)
    error_message      = Column(String(500), nullable=True)

    # Columnas dedicadas para consultas rápidas (sin parsear JSONB)
    top1_label         = Column(String(50), nullable=True)    # ej. "acne-excoriated"
    top1_confidence    = Column(Float, nullable=True)          # ej. 0.351
    model_version      = Column(String(50), nullable=True)    # ej. "opcionA"

    # Resultado completo del modelo: all_scores{}, tta_passes, compute
    result                  = Column(JSONB, nullable=True)

    # Cache del último resultado del motor de recomendación
    cached_recommendations  = Column(JSONB, nullable=True)

    created_at         = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at       = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="analyses")
