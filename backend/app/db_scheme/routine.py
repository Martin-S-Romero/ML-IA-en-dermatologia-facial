from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.db_scheme.base import Base


class Routine(Base):
    __tablename__ = "routines"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id", ondelete="SET NULL"), nullable=True)
    is_active   = Column(Boolean, default=True, nullable=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at  = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user  = relationship("User",    back_populates="routines")
    steps = relationship(
        "RoutineStep",
        back_populates="routine",
        cascade="all, delete-orphan",
        order_by="RoutineStep.step_order",
    )


class RoutineStep(Base):
    __tablename__ = "routine_steps"

    id               = Column(Integer, primary_key=True, index=True)
    routine_id       = Column(Integer, ForeignKey("routines.id", ondelete="CASCADE"), nullable=False)
    step_order       = Column(Integer, nullable=False)
    time_of_day      = Column(String(10), nullable=False)     # am / pm / both
    product_name     = Column(String(255), nullable=False)    # nombre generado por IA (siempre presente)
    product_category = Column(String(50), nullable=True)      # cleanser, moisturizer, spf, serum, etc.
    reason           = Column(String(500), nullable=True)
    product_id       = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    ai_suggested     = Column(Boolean, default=True, nullable=False)   # ¿generado por la IA?
    user_replaced    = Column(Boolean, default=False, nullable=False)  # ¿el usuario lo cambió?
    replaced_with    = Column(String(255), nullable=True)              # por qué lo reemplazó
    is_active        = Column(Boolean, default=True, nullable=False)

    routine = relationship("Routine", back_populates="steps")


class SkinCheck(Base):
    __tablename__ = "skin_checks"

    id               = Column(Integer, primary_key=True, index=True)
    user_id          = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    routine_id       = Column(Integer, ForeignKey("routines.id", ondelete="CASCADE"), nullable=False)
    followed_routine = Column(Boolean, nullable=False)
    notes            = Column(String(500), nullable=True)
    created_at       = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
