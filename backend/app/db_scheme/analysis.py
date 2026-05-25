from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db_scheme.base import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id                 = Column(Integer, primary_key=True, index=True)
    user_id            = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    original_filename  = Column(String(255), nullable=False)
    censored_filename  = Column(String(255), nullable=True)

    # processing / completed / failed
    status             = Column(String(20), default="processing", nullable=False)
    error_message      = Column(String(500), nullable=True)

    # Resultado del análisis: dict libre por ahora.
    # Cuando el modelo DL esté integrado, se agrega una migración con campos tipados.
    result             = Column(JSONB, nullable=True)

    created_at         = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at       = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="analyses")
