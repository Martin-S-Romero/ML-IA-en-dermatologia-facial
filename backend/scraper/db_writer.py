"""
db_writer.py
Inserta o actualiza productos e ingredientes en la base de datos.
Usa los modelos SQLAlchemy de la app existente.
"""

import os
import sys
import json

# Permite importar 'app' desde backend/ cuando se corre desde backend/scraper/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import SessionLocal
from app import models

from product_scraper import ScrapedProduct


# ── Helpers ────────────────────────────────────────────────────────────────────

def already_scraped(url: str) -> bool:
    """Retorna True si el producto ya existe en la BD (para evitar duplicados)."""
    db: Session = SessionLocal()
    try:
        return db.query(models.Product).filter(
            models.Product.source_url == url
        ).first() is not None
    finally:
        db.close()


def _get_or_create_ingredient(
    db: Session,
    inci_name: str,
    function: str,
    rating: str,
) -> models.Ingredient:
    """Busca el ingrediente por nombre INCI; si no existe, lo crea."""
    ingr = db.query(models.Ingredient).filter(
        models.Ingredient.inci_name == inci_name
    ).first()

    if not ingr:
        ingr = models.Ingredient(
            inci_name=inci_name,
            function=function,
            rating=rating,
        )
        db.add(ingr)
        db.flush()  # obtener el id sin hacer commit todavía

    return ingr


# ── Guardado principal ─────────────────────────────────────────────────────────

def save_product(product: ScrapedProduct) -> bool:
    """
    Inserta un ScrapedProduct en la BD.
    Retorna True si se guardó, False si ya existía o hubo error.
    """
    db: Session = SessionLocal()
    try:
        existing = db.query(models.Product).filter(
            models.Product.source_url == product.source_url
        ).first()

        if existing:
            return False

        category = _infer_category(product)

        db_product = models.Product(
            name=product.name,
            brand=product.brand,
            description=product.description,
            category=category,
            source_url=product.source_url,
            highlights=json.dumps(product.highlights),
        )
        db.add(db_product)
        db.flush()

        for ing in product.ingredients:
            db_ingredient = _get_or_create_ingredient(
                db,
                inci_name=ing.inci_name,
                function=ing.function,
                rating=ing.rating,
            )

            link = models.ProductIngredient(
                product_id=db_product.id,
                ingredient_id=db_ingredient.id,
                position=ing.position,
                irr_com=ing.irr_com,
            )
            db.add(link)

        db.commit()
        return True

    except IntegrityError as e:
        db.rollback()
        print(f"  [!] IntegrityError guardando {product.source_url}: {e}")
        return False
    except Exception as e:
        db.rollback()
        print(f"  [x] Error guardando {product.source_url}: {e}")
        return False
    finally:
        db.close()


def _infer_category(product: ScrapedProduct) -> str:
    """
    Infiere la categoría del producto basándose en el nombre y marca.
    """
    name_lower = (product.name + " " + product.brand).lower()

    if any(w in name_lower for w in ["cleanser", "wash", "foam", "gel limpiador", "cleansing"]):
        return "cleanser"
    if any(w in name_lower for w in ["moisturizer", "cream", "lotion", "hydrat", "moisturising"]):
        return "moisturizer"
    if any(w in name_lower for w in ["spf", "sunscreen", "sunblock", "solar", "anthelios", "ultra sheer"]):
        return "spf"
    if any(w in name_lower for w in ["serum", "sérum"]):
        return "serum"
    if any(w in name_lower for w in ["exfoliant", "aha", "bha", "acid", "peel"]):
        return "exfoliant"
    if any(w in name_lower for w in ["retinol", "retinoid", "adapalene", "differin", "tretinoin"]):
        return "retinoid"
    if any(w in name_lower for w in ["toner", "essence"]):
        return "toner"
    if any(w in name_lower for w in ["eye", "ojo", "contorno"]):
        return "eye"
    if any(w in name_lower for w in ["mask", "mascarilla"]):
        return "mask"
    if any(w in name_lower for w in ["oil", "aceite"]):
        return "oil"
    if any(w in name_lower for w in ["spot", "blemish", "drying lotion"]):
        return "spot"

    return "other"
