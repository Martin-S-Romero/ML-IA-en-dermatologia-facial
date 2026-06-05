from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db_scheme.base import Base


class User(Base):
    __tablename__ = "users"

    id               = Column(Integer, primary_key=True, index=True)
    email            = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password  = Column(String(255), nullable=False)
    full_name        = Column(String(255), nullable=True)
    gdpr_accepted    = Column(Boolean, default=False, nullable=False)
    is_active        = Column(Boolean, default=True, nullable=False)
    created_at       = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at       = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    skin_profile = relationship("SkinProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    analyses     = relationship("Analysis",    back_populates="user", cascade="all, delete-orphan")
    routines     = relationship("Routine",     back_populates="user", cascade="all, delete-orphan")
    consents     = relationship("Consent",     backref="user",        cascade="all, delete-orphan")


class SkinProfile(Base):
    __tablename__ = "skin_profiles"

    id               = Column(Integer, primary_key=True, index=True)
    user_id          = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    birth_date       = Column(Date, nullable=True)               # reemplaza age
    gender           = Column(String(20), nullable=True)
    fitzpatrick      = Column(String(5), nullable=True)           # I – VI
    skin_type        = Column(String(20), nullable=True)          # seca / grasa / mixta / normal / sensible
    skin_conditions  = Column(JSONB, nullable=True, default=list)
    allergies        = Column(JSONB, nullable=True, default=list)
    country          = Column(String(100), nullable=True)
    city             = Column(String(100), nullable=True)
    updated_at       = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="skin_profile")
