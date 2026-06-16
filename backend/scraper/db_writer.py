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
from app import db_scheme as models

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
            highlights=product.highlights,
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
    El orden de chequeo importa: SPF antes que moisturizer, spot antes que lotion, etc.
    """
    name_lower = (product.name + " " + product.brand).lower()

    # 1. Excluir productos no faciales → "other" (no los recomendamos)
    NON_FACIAL = [
        "body wash", "body lotion", "body cream", "body milk", "body butter", "body spray",
        "body fluid", "body gel", "body oil", "body serum", "body scrub",
        "shampoo", "conditioner", "hair mask", "hair oil", "scalp", "dry shampoo",
        "deodorant", "antiperspirant",
        "hand cream", "hand lotion", "hand wash", "foot cream", "foot lotion",
        "baby wash", "baby shampoo", "baby lotion",
        "shower gel", "bath ", "bath&", "bubble bath",
        "toothpaste", "mouthwash",
        "lip balm", "lipstick", "lip gloss", "lip liner",
        "shaving", "aftershave", "after shave",
        "nail ", "cuticle",
        "intimate", "feminine wash",
    ]
    if any(w in name_lower for w in NON_FACIAL):
        return "other"

    # 2. Excluir maquillaje → "other"
    MAKEUP = [
        "bb cream", "cc cream", "foundation", "concealer", "primer",
        "powder", "loose powder", "setting powder",
        "blush", "bronzer", "contour", "highlighter",
        "mascara", "eyeshadow", "eyeliner", "eyebrow",
        "lip color", "lip stick",
        "tinted moisturizer", "tinted cream",
    ]
    if any(w in name_lower for w in MAKEUP):
        return "other"

    # 3. SPF — antes que moisturizer/cream/lotion para no clasificar suncreams como crema
    SPF = [
        "spf", "sunscreen", "sunblock", "suncream", "sun cream", "sun lotion",
        "uv defense", "uv clear", "uv shield", "uv protect",
        "sun protect", "ultra sheer", "solar",
        "anthelios", "sonnenschutz", "solaire",
        "mineral sunscreen", "chemical sunscreen",
    ]
    if any(w in name_lower for w in SPF):
        return "spf"

    # 4. Spot treatments — antes que lotion para no clasificar "drying lotion" como moisturizer
    SPOT = ["spot treatment", "blemish", "drying lotion", "acne patch", "pimple patch", "acne gel"]
    if any(w in name_lower for w in SPOT):
        return "spot"

    # 5. Retinoids
    RETINOID = ["retinol", "retinoid", "adapalene", "differin", "tretinoin",
                "granactive retinoid", "retinyl", "retin-"]
    if any(w in name_lower for w in RETINOID):
        return "retinoid"

    # 6. Exfoliants
    EXFOLIANT = ["exfoliant", "exfoliator", "exfoliating", "aha ", "bha ", "glycolic acid",
                 "lactic acid", "salicylic acid", "mandelic acid", "peeling solution",
                 "chemical peel", "physical scrub", " scrub"]
    if any(w in name_lower for w in EXFOLIANT):
        return "exfoliant"

    # 7. Cleansers
    CLEANSER = [
        "cleanser", "face wash", "facial wash", "foaming cleanser", "foam cleanser",
        "gel limpiador", "gel nettoyant", "limpiador",
        "cleansing balm", "cleansing oil", "cleansing milk", "cleansing water",
        "cleansing foam", "cleansing gel",
        "micellar water", "micellar", "agua micelar",
        "makeup remover", "make-up remover", "desmaquill",
        "mizellenwasser", "reinigungsgel", "reinigungsschaum",
    ]
    if any(w in name_lower for w in CLEANSER):
        return "cleanser"
    # "wash" y "foam" solo en contexto facial
    if any(w in name_lower for w in ["face wash", "facial foam", "cleansing foam"]):
        return "cleanser"

    # 8. Eye — antes de serum para que "brightening eye serum" → eye, no serum
    EYE = ["eye cream", "eye gel", "eye serum", "eye contour", "eye balm",
           "contorno de ojos", "contour des yeux", "under eye", "augencreme"]
    if any(w in name_lower for w in EYE):
        return "eye"

    # 9. Serums
    SERUM = ["serum", "sérum", "ampoule", "ampule", "booster serum",
             "concentrate serum", "essence serum"]
    if any(w in name_lower for w in SERUM):
        return "serum"

    # 10. Toners
    TONER = ["toner", "tónico", "lotion tonique", "skin toner", "clarifying toner",
             "balancing toner", "astringent"]
    if any(w in name_lower for w in TONER):
        return "toner"

    # 11. Masks
    MASK = ["face mask", "facial mask", "sheet mask", "clay mask", "sleeping mask",
            "mascarilla", "masque visage", "gesichtsmaske", " mask"]
    if any(w in name_lower for w in MASK):
        return "mask"

    # 12. Facial oils
    OIL = ["face oil", "facial oil", "dry oil", "beauty oil", "rosehip oil",
           "squalane", "rosehip seed oil", "marula oil", "jojoba oil", "argan oil"]
    if any(w in name_lower for w in OIL):
        return "oil"

    # 13. Moisturizers — último recurso para productos faciales
    MOISTURIZER = [
        "moisturizer", "moisturiser", "moisturizing cream", "moisturising cream",
        "day cream", "night cream", "face cream", "facial cream",
        "gel cream", "gel-cream", "water cream", "sleeping cream",
        "hydrating cream", "hydration cream",
        "creme", "crème", "feuchtigkeitscreme",
        "rich cream", "light cream",
    ]
    if any(w in name_lower for w in MOISTURIZER):
        return "moisturizer"
    # "cream" genérico y "lotion" como fallback facial (body ya fue excluido arriba)
    if any(w in name_lower for w in ["cream", "lotion", "emulsion", "fluid", "gel"]):
        return "moisturizer"

    return "other"
