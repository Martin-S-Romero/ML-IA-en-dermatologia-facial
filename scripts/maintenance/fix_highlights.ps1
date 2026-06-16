# fix_highlights.ps1
# Corrige el doble-encoding de highlights en productos del batch 1.
# El problema: db_writer.py usaba json.dumps() antes de insertar en columna JSONB,
# por lo que el valor quedó como string JSON en vez de array nativo JSONB.
# Ejemplo malo:  highlights = '"[\"#fragrance-free\", \"#sensitive\"]"'
# Ejemplo bueno: highlights = '["#fragrance-free", "#sensitive"]'

$script = @'
import sys, json
sys.path.insert(0, "/app")
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    # Detectar productos con highlights que son strings JSON (doble-encoded)
    rows = db.execute(text("""
        SELECT id, highlights
        FROM products
        WHERE highlights IS NOT NULL
          AND jsonb_typeof(highlights) = 'string'
    """)).fetchall()

    print(f"Productos con highlights doble-encoded: {len(rows)}")

    fixed = 0
    errors = 0
    for row in rows:
        pid = row[0]
        raw = row[1]  # es un string JSON dentro de JSONB, ej: '"[\"#fragrance-free\"]"'
        try:
            # SQLAlchemy ya deserializó el JSONB string a Python string.
            # raw = '["#fragrance-free"]' o '[]'
            # Un solo json.loads() da el array directamente.
            arr = json.loads(raw)
            if not isinstance(arr, list):
                raise ValueError(f"No es lista: {arr}")
            db.execute(text(
                "UPDATE products SET highlights = CAST(:h AS jsonb) WHERE id = :id"
            ), {"h": json.dumps(arr), "id": pid})
            fixed += 1
        except Exception as e:
            print(f"  [!] Error en producto {pid}: {e} | raw={raw!r}")
            errors += 1

    db.commit()
    print(f"Corregidos: {fixed} | Errores: {errors}")

    # Verificar que no queden
    remaining = db.execute(text("""
        SELECT COUNT(*) FROM products
        WHERE highlights IS NOT NULL
          AND jsonb_typeof(highlights) = 'string'
    """)).scalar()
    print(f"Pendientes tras fix: {remaining}")

finally:
    db.close()
'@

$script | docker exec -i tesis20-backend-1 python3 -
