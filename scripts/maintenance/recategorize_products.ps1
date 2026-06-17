# recategorize_products.ps1
# Re-categoriza todos los productos de la BD usando la lógica mejorada de _infer_category.

$script = @'
import sys
sys.path.insert(0, "/app")
from app.core.database import SessionLocal
from sqlalchemy import text

# ── Misma lógica que db_writer._infer_category (actualizada) ──────────────────
def infer_category(name: str, brand: str) -> str:
    n = (name + " " + brand).lower()

    NON_FACIAL = [
        "body wash", "body lotion", "body cream", "body milk", "body butter", "body spray",
        "body fluid", "body gel", "body oil", "body serum", "body scrub",
        "shampoo", "conditioner", "hair mask", "hair oil", "scalp", "dry shampoo",
        "deodorant", "antiperspirant",
        "hand cream", "hand lotion", "hand wash", "foot cream", "foot lotion",
        "baby wash", "baby shampoo", "baby lotion",
        "shower gel", "bath ", "bubble bath",
        "toothpaste", "mouthwash",
        "lip balm", "lipstick", "lip gloss", "lip liner",
        "shaving", "aftershave", "after shave",
        "nail ", "cuticle",
        "intimate", "feminine wash",
    ]
    if any(w in n for w in NON_FACIAL):
        return "other"

    MAKEUP = [
        "bb cream", "cc cream", "foundation", "concealer", "primer",
        "powder", "loose powder", "setting powder",
        "blush", "bronzer", "contour", "highlighter",
        "mascara", "eyeshadow", "eyeliner", "eyebrow",
        "lip color", "lip stick",
        "tinted moisturizer", "tinted cream",
    ]
    if any(w in n for w in MAKEUP):
        return "other"

    SPF = [
        "spf", "sunscreen", "sunblock", "suncream", "sun cream", "sun lotion",
        "uv defense", "uv clear", "uv shield", "uv protect",
        "sun protect", "ultra sheer", "solar",
        "anthelios", "sonnenschutz", "solaire",
    ]
    if any(w in n for w in SPF):
        return "spf"

    SPOT = ["spot treatment", "blemish", "drying lotion", "acne patch", "pimple patch", "acne gel"]
    if any(w in n for w in SPOT):
        return "spot"

    RETINOID = ["retinol", "retinoid", "adapalene", "differin", "tretinoin",
                "granactive retinoid", "retinyl", "retin-"]
    if any(w in n for w in RETINOID):
        return "retinoid"

    EXFOLIANT = ["exfoliant", "exfoliator", "exfoliating", "aha ", "bha ", "glycolic acid",
                 "lactic acid", "salicylic acid", "mandelic acid", "peeling solution",
                 "chemical peel", " scrub"]
    if any(w in n for w in EXFOLIANT):
        return "exfoliant"

    CLEANSER = [
        "cleanser", "face wash", "facial wash", "foaming cleanser", "foam cleanser",
        "gel limpiador", "gel nettoyant", "limpiador",
        "cleansing balm", "cleansing oil", "cleansing milk", "cleansing water",
        "cleansing foam", "cleansing gel",
        "micellar water", "micellar", "agua micelar",
        "makeup remover", "make-up remover", "desmaquill",
        "mizellenwasser", "reinigungsgel", "reinigungsschaum",
    ]
    if any(w in n for w in CLEANSER):
        return "cleanser"

    EYE = ["eye cream", "eye gel", "eye serum", "eye contour", "eye balm",
           "contorno de ojos", "under eye", "augencreme"]
    if any(w in n for w in EYE):
        return "eye"

    SERUM = ["serum", "sérum", "ampoule", "ampule"]
    if any(w in n for w in SERUM):
        return "serum"

    TONER = ["toner", "tónico", "lotion tonique", "skin toner", "clarifying toner",
             "balancing toner", "astringent"]
    if any(w in n for w in TONER):
        return "toner"

    MASK = ["face mask", "facial mask", "sheet mask", "clay mask", "sleeping mask",
            "mascarilla", "masque visage", "gesichtsmaske", " mask"]
    if any(w in n for w in MASK):
        return "mask"

    OIL = ["face oil", "facial oil", "dry oil", "beauty oil", "rosehip oil",
           "squalane", "rosehip seed oil", "marula oil", "jojoba oil", "argan oil"]
    if any(w in n for w in OIL):
        return "oil"

    MOISTURIZER = [
        "moisturizer", "moisturiser", "moisturizing cream", "moisturising cream",
        "day cream", "night cream", "face cream", "facial cream",
        "gel cream", "gel-cream", "water cream", "sleeping cream",
        "hydrating cream", "hydration cream",
        "creme", "crème", "feuchtigkeitscreme",
    ]
    if any(w in n for w in MOISTURIZER):
        return "moisturizer"
    if any(w in n for w in ["cream", "lotion", "emulsion", "fluid", "gel"]):
        return "moisturizer"

    return "other"


db = SessionLocal()
try:
    rows = db.execute(text("SELECT id, name, brand, category FROM products")).fetchall()
    print(f"Total productos: {len(rows):,}")

    updates = {}  # new_category -> [ids]
    changed = 0
    for pid, name, brand, old_cat in rows:
        new_cat = infer_category(name or "", brand or "")
        if new_cat != old_cat:
            updates.setdefault(new_cat, []).append(pid)
            changed += 1

    print(f"Productos a re-categorizar: {changed:,}")
    print()

    for new_cat, ids in sorted(updates.items()):
        print(f"  -> {new_cat:<15} {len(ids):>5} productos")
        db.execute(text(
            "UPDATE products SET category = :cat WHERE id = ANY(:ids)"
        ), {"cat": new_cat, "ids": ids})

    db.commit()
    print()
    print("Re-categorización completada.")

    # Resumen final
    cats = db.execute(text("""
        SELECT category, COUNT(*) as n
        FROM products
        GROUP BY category
        ORDER BY n DESC
    """)).fetchall()
    print()
    print("Distribución final por categoría:")
    for row in cats:
        print(f"  {row[0]:<20} {row[1]:>6,}")

finally:
    db.close()
'@

$script | docker exec -i tesis20-backend-1 python3 -
