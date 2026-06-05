from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db_scheme.base import Base


class Product(Base):
    __tablename__ = "products"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(255), nullable=False)
    brand       = Column(String(100), index=True)
    category    = Column(String(50), index=True)    # cleanser, moisturizer, spf, serum…
    description = Column(Text)
    highlights      = Column(JSONB)                  # ["#alcohol-free", "#fragrance-free"]
    suitable_for    = Column(JSONB, nullable=True)   # ["seca", "sensible", "acne"]
    source_url      = Column(String(512), unique=True, nullable=False)
    last_scraped_at = Column(DateTime(timezone=True), nullable=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product_ingredients = relationship(
        "ProductIngredient",
        back_populates="product",
        cascade="all, delete-orphan",
    )


class Ingredient(Base):
    __tablename__ = "ingredients"

    id          = Column(Integer, primary_key=True, index=True)
    inci_name   = Column(String(255), unique=True, nullable=False, index=True)
    function    = Column(String(255))     # "solvent", "emollient, moisturizer", etc.
    rating      = Column(String(50))      # "Superstar", "Good stuff", "OK", "Caution"
    description = Column(Text)
    created_at  = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product_ingredients = relationship(
        "ProductIngredient",
        back_populates="ingredient",
    )


class ProductIngredient(Base):
    """Tabla intermedia Producto ↔ Ingrediente. Guarda el orden del ingrediente en la fórmula."""
    __tablename__ = "product_ingredients"
    __table_args__ = (
        UniqueConstraint("product_id", "ingredient_id", name="uq_product_ingredient"),
    )

    id            = Column(Integer, primary_key=True)
    product_id    = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    position      = Column(Integer, nullable=False)   # 1 = primero en la lista
    irr_com       = Column(String(20))                # irritancy/comedogenicity

    product    = relationship("Product",    back_populates="product_ingredients")
    ingredient = relationship("Ingredient", back_populates="product_ingredients")
