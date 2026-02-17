from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

class ProcessedImage(Base):
    __tablename__ = "processed_images"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_filename = Column(String, nullable=False)
    processed_filename = Column(String, nullable=False)
    mode = Column(String, nullable=False)  # blur, black, pixelate
    parameters = Column(String, nullable=True)  # JSON string
    status = Column(String, default="completed")  # completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="processed_images")