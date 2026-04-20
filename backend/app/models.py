from __future__ import annotations
from typing import Optional
from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id:              int                = Column(Integer, primary_key=True, index=True)
    email:           str                = Column(String, unique=True, index=True, nullable=False)
    hashed_password: str                = Column(String, nullable=False)
    full_name:       Optional[str]      = Column(String, nullable=True)
    gdpr_accepted:   bool               = Column(Boolean, default=False)
    is_active:       bool               = Column(Boolean, default=True)
    created_at:      Optional[datetime] = Column(DateTime(timezone=True), server_default=func.now())


class SkinProfile(Base):
    __tablename__ = "skin_profiles"

    id:              int            = Column(Integer, primary_key=True, index=True)
    user_id:         int            = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    age:             Optional[int]  = Column(Integer, nullable=True)
    gender:          Optional[str]  = Column(String, nullable=True)        # masculino / femenino
    fitzpatrick:     Optional[str]  = Column(String, nullable=True)        # I – VI
    skin_type:       Optional[str]  = Column(String, nullable=True)        # seca / grasa / mixta / normal / sensible
    skin_conditions: Optional[str]  = Column(Text, nullable=True)          # JSON array string
    allergies:       Optional[str]  = Column(Text, nullable=True)          # JSON array string
    country:         Optional[str]  = Column(String, nullable=True)
    city:            Optional[str]  = Column(String, nullable=True)
    updated_at:      Optional[datetime] = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref="skin_profile", uselist=False)


class Analysis(Base):
    __tablename__ = "analyses"

    id                 = Column(Integer, primary_key=True, index=True)
    user_id            = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_filename  = Column(String, nullable=False)
    censored_filename  = Column(String, nullable=True)
    status             = Column(String, default="processing")  # processing / completed / failed
    result             = Column(Text, nullable=True)            # JSON con metadata del resultado
    error_message      = Column(String, nullable=True)
    created_at         = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="analyses")


class Routine(Base):
    __tablename__ = "routines"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=True)
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    steps = relationship(
        "RoutineStep", backref="routine",
        cascade="all, delete-orphan",
        order_by="RoutineStep.step_order"
    )
    user = relationship("User", backref="routines")


class RoutineStep(Base):
    __tablename__ = "routine_steps"

    id               = Column(Integer, primary_key=True, index=True)
    routine_id       = Column(Integer, ForeignKey("routines.id"), nullable=False)
    step_order       = Column(Integer, nullable=False)
    time_of_day      = Column(String, nullable=False)   # am / pm / both
    product_name     = Column(String, nullable=False)
    product_category = Column(String, nullable=True)    # cleanser, moisturizer, spf, serum, etc.
    reason           = Column(String, nullable=True)
    is_active        = Column(Boolean, default=True)


class SkinCheck(Base):
    __tablename__ = "skin_checks"

    id               = Column(Integer, primary_key=True, index=True)
    user_id          = Column(Integer, ForeignKey("users.id"), nullable=False)
    routine_id       = Column(Integer, ForeignKey("routines.id"), nullable=False)
    followed_routine = Column(Boolean, nullable=False)
    notes            = Column(String, nullable=True)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())


# ── Catálogo de productos scrapeados de INCIDecoder ───────────────────────────

from sqlalchemy import UniqueConstraint
from datetime import datetime as _datetime


class Product(Base):
    __tablename__ = "products"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(255), nullable=False)
    brand       = Column(String(100), index=True)
    category    = Column(String(50), index=True)   # cleanser, moisturizer, spf, serum…
    description = Column(Text)
    highlights  = Column(Text)         # JSON list: ["#alcohol-free", "#fragrance-free"]
    source_url  = Column(String(512), unique=True, nullable=False)
    created_at  = Column(DateTime, default=_datetime.utcnow)

    product_ingredients = relationship(
        "ProductIngredient",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Product {self.brand} - {self.name}>"


class Ingredient(Base):
    __tablename__ = "ingredients"

    id          = Column(Integer, primary_key=True, index=True)
    inci_name   = Column(String(255), unique=True, nullable=False, index=True)
    function    = Column(String(255))   # "solvent", "emollient, moisturizer", etc.
    rating      = Column(String(50))    # "Superstar", "Good stuff", "OK", "Caution"
    description = Column(Text)
    created_at  = Column(DateTime, default=_datetime.utcnow)

    product_ingredients = relationship(
        "ProductIngredient",
        back_populates="ingredient",
    )

    def __repr__(self):
        return f"<Ingredient {self.inci_name}>"


class ProductIngredient(Base):
    """
    Tabla intermedia Producto ↔ Ingrediente.
    Guarda el orden (posición) del ingrediente en la fórmula.
    """
    __tablename__ = "product_ingredients"
    __table_args__ = (
        UniqueConstraint("product_id", "ingredient_id", name="uq_product_ingredient"),
    )

    id            = Column(Integer, primary_key=True)
    product_id    = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    position      = Column(Integer, nullable=False)   # 1 = primero en la lista
    irr_com       = Column(String(20))                # irritancy/comedogenicity: "0, 0"

    product    = relationship("Product",    back_populates="product_ingredients")
    ingredient = relationship("Ingredient", back_populates="product_ingredients")
