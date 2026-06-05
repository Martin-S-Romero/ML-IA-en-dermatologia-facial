from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from app.db_scheme.base import Base


class Consent(Base):
    __tablename__ = "consents"

    id               = Column(Integer, primary_key=True, index=True)
    user_id          = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    gdpr_accepted    = Column(Boolean, nullable=False)
    data_processing  = Column(Boolean, nullable=False)
    image_storage    = Column(Boolean, nullable=False)
    ai_analysis      = Column(Boolean, nullable=False)
    ip_address       = Column(String(45), nullable=True)   # IPv4 o IPv6
    accepted_at      = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
