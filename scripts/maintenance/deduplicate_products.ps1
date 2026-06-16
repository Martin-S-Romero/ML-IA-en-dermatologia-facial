# deduplicate_products.ps1
# Elimina productos duplicados (mismo nombre + marca, fuentes distintas OBF vs INCIDecoder).
# Estrategia: conservar la version de INCIDecoder (mas datos: position, irr_com, highlights).
# Si ambas son INCIDecoder, conservar la mas reciente (id mayor).

$script = @'
import sys
sys.path.insert(0, "/app")
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    # 1. Ver cuántos duplicados hay antes de limpiar
    dupes = db.execute(text("""
        SELECT LOWER(TRIM(name)), LOWER(TRIM(brand)), COUNT(*) as n
        FROM products
        GROUP BY LOWER(TRIM(name)), LOWER(TRIM(brand))
        HAVING COUNT(*) > 1
        ORDER BY n DESC
        LIMIT 20
    """)).fetchall()

    print(f"Grupos con duplicados (top 20):")
    for row in dupes:
        print(f"  {row[2]}x  {row[1]} - {row[0]}")

    total_dupes = db.execute(text("""
        SELECT COUNT(*) FROM (
            SELECT LOWER(TRIM(name)), LOWER(TRIM(brand))
            FROM products
            GROUP BY LOWER(TRIM(name)), LOWER(TRIM(brand))
            HAVING COUNT(*) > 1
        ) t
    """)).scalar()
    print(f"\nTotal grupos duplicados: {total_dupes}")

    # 2. Identificar IDs a eliminar:
    # Por cada grupo duplicado, conservar el de INCIDecoder (si existe); si hay varios, el de id mayor.
    # Eliminar los restantes (junto con sus product_ingredients).
    ids_to_delete = db.execute(text("""
        WITH ranked AS (
            SELECT id,
                   name,
                   brand,
                   source_url,
                   CASE WHEN source_url LIKE '%incidecoder%' THEN 1 ELSE 2 END AS source_priority,
                   ROW_NUMBER() OVER (
                       PARTITION BY LOWER(TRIM(name)), LOWER(TRIM(brand))
                       ORDER BY
                           CASE WHEN source_url LIKE '%incidecoder%' THEN 1 ELSE 2 END ASC,
                           id DESC
                   ) AS rn
            FROM products
        )
        SELECT id FROM ranked WHERE rn > 1
    """)).fetchall()

    ids = [r[0] for r in ids_to_delete]
    print(f"\nProductos a eliminar: {len(ids)}")

    if not ids:
        print("No hay duplicados que limpiar.")
    else:
        # Primero eliminar product_ingredients (FK)
        db.execute(text(
            "DELETE FROM product_ingredients WHERE product_id = ANY(:ids)"
        ), {"ids": ids})
        # Luego eliminar productos
        db.execute(text(
            "DELETE FROM products WHERE id = ANY(:ids)"
        ), {"ids": ids})
        db.commit()
        print(f"Eliminados {len(ids)} productos duplicados.")

    # 3. Estado final
    total = db.execute(text("SELECT COUNT(*) FROM products")).scalar()
    print(f"\nProductos en BD tras limpieza: {total:,}")

finally:
    db.close()
'@

$script | docker exec -i tesis20-backend-1 python3 -
