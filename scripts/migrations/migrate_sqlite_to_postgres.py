"""
Migra datos de inciapi.db (SQLite) a PostgreSQL (tesis_db).

Tablas origen  -> Tablas destino
  products     -> products
  ingredientes -> ingredients + product_ingredients
  skin_compatibility -> products.suitable_for (jsonb)
"""

import sqlite3
import json
import sys
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

SQLITE_PATH = Path(__file__).parent / "scraping" / "inciapi.db"
PG_DSN = "postgresql://postgres:password@localhost:5432/tesis_db"
BATCH_SIZE = 500


def parse_category(raw):
    if not raw:
        return None
    try:
        cats = json.loads(raw)
        if cats:
            return cats[0][:50]
    except Exception:
        pass
    return str(raw)[:50]


def build_suitable_for(compat_rows):
    """Convierte filas skin_compatibility en dict {skin_type: bool}."""
    return {row[0]: bool(row[1]) for row in compat_rows}


def build_highlights(row):
    return {
        "overall_safety_score": row["overall_safety_score"],
        "safety_level": row["safety_level"],
        "pregnancy_safe": bool(row["pregnancy_safe"]) if row["pregnancy_safe"] is not None else None,
    }


def run():
    print(f"Abriendo SQLite: {SQLITE_PATH}")
    sq = sqlite3.connect(SQLITE_PATH)
    sq.row_factory = sqlite3.Row

    print(f"Conectando a PostgreSQL...")
    pg = psycopg2.connect(PG_DSN)
    cur = pg.cursor()

    # ── 1. Cargar skin_compatibility en memoria (105k filas, ~20 MB) ──────────
    print("Cargando skin_compatibility...")
    compat: dict[str, list] = {}
    for row in sq.execute("SELECT barcode, skin_type, compatible FROM skin_compatibility"):
        compat.setdefault(row[0], []).append((row[1], row[2]))

    # ── 2. Insertar products ──────────────────────────────────────────────────
    print("Insertando products...")
    sq_products = sq.execute(
        "SELECT barcode, name, brand, category, overall_safety_score, "
        "safety_level, pregnancy_safe, endpoint_demo FROM products"
    )

    product_id_map: dict[str, int] = {}  # barcode -> pg id
    inserted_p = skipped_p = 0
    batch = []

    def flush_products():
        nonlocal inserted_p, skipped_p
        if not batch:
            return
        result = execute_values(
            cur,
            """
            INSERT INTO products (name, brand, category, source_url, highlights, suitable_for)
            VALUES %s
            ON CONFLICT (source_url) DO NOTHING
            RETURNING id, source_url
            """,
            batch,
            fetch=True,
        )
        for pid, url in result:
            bc = url.split("/")[-1]
            product_id_map[bc] = pid
            inserted_p += 1
        skipped_p += len(batch) - len(result)
        batch.clear()

    for row in sq_products:
        bc = row["barcode"]
        name = (row["name"] or "").strip()
        if not name:
            skipped_p += 1
            continue

        source_url = row["endpoint_demo"] or f"https://inciapi.com/api/web/demo/products/{bc}"

        batch.append((
            name[:255],
            (row["brand"] or "")[:100] or None,
            parse_category(row["category"]),
            source_url[:512],
            json.dumps(build_highlights(row)),
            json.dumps(build_suitable_for(compat.get(bc, []))),
        ))

        if len(batch) >= BATCH_SIZE:
            flush_products()

    flush_products()
    pg.commit()
    print(f"  Products insertados: {inserted_p}  omitidos/duplicados: {skipped_p}")

    # Cargar los productos ya existentes que ON CONFLICT omitió
    print("  Cargando IDs de productos ya existentes...")
    cur.execute("SELECT id, source_url FROM products")
    for pid, url in cur.fetchall():
        bc = url.split("/")[-1]
        if bc not in product_id_map:
            product_id_map[bc] = pid

    # ── 3. Insertar ingredients (únicos por inci_name) ────────────────────────
    print("Insertando ingredients...")
    sq_ingr = sq.execute(
        "SELECT DISTINCT inci_name, safety_level FROM ingredientes WHERE inci_name IS NOT NULL"
    )

    ingredient_id_map: dict[str, int] = {}
    inserted_i = 0
    batch_i = []

    def flush_ingredients():
        nonlocal inserted_i
        if not batch_i:
            return
        result = execute_values(
            cur,
            """
            INSERT INTO ingredients (inci_name, rating)
            VALUES %s
            ON CONFLICT (inci_name) DO NOTHING
            RETURNING id, inci_name
            """,
            batch_i,
            fetch=True,
        )
        for iid, name in result:
            ingredient_id_map[name.upper()] = iid
            inserted_i += 1
        batch_i.clear()

    for row in sq_ingr:
        name = (row[0] or "").strip()
        if not name:
            continue
        batch_i.append((name[:255], (row[1] or "")[:50] or None))
        if len(batch_i) >= BATCH_SIZE:
            flush_ingredients()

    flush_ingredients()
    pg.commit()
    print(f"  Ingredients insertados: {inserted_i}")

    # Cargar IDs de los ya existentes
    cur.execute("SELECT id, inci_name FROM ingredients")
    for iid, name in cur.fetchall():
        ingredient_id_map[name.upper()] = iid

    # ── 4. Insertar product_ingredients ──────────────────────────────────────
    print("Insertando product_ingredients...")
    sq_pi = sq.execute(
        "SELECT barcode, inci_name, safety_score, is_allergen, "
        "comedogenicity_rating, ROW_NUMBER() OVER (PARTITION BY barcode ORDER BY id) AS pos "
        "FROM ingredientes ORDER BY barcode, id"
    )

    inserted_pi = skipped_pi = 0
    batch_pi = []

    def flush_pi():
        nonlocal inserted_pi, skipped_pi
        if not batch_pi:
            return
        execute_values(
            cur,
            """
            INSERT INTO product_ingredients (product_id, ingredient_id, position, irr_com)
            VALUES %s
            ON CONFLICT (product_id, ingredient_id) DO NOTHING
            """,
            batch_pi,
        )
        inserted_pi += len(batch_pi)
        batch_pi.clear()

    for row in sq_pi:
        bc = row[0]
        inci = (row[1] or "").strip().upper()
        prod_id = product_id_map.get(bc)
        ingr_id = ingredient_id_map.get(inci)

        if not prod_id or not ingr_id:
            skipped_pi += 1
            continue

        irr_com = str(row[4]) if row[4] is not None else None
        batch_pi.append((prod_id, ingr_id, int(row[5]), irr_com))

        if len(batch_pi) >= BATCH_SIZE:
            flush_pi()

    flush_pi()
    pg.commit()
    print(f"  Product_ingredients insertados: {inserted_pi}  omitidos: {skipped_pi}")

    # ── 5. Resumen final ──────────────────────────────────────────────────────
    cur.execute("SELECT COUNT(*) FROM products")
    print(f"\nTotal en PostgreSQL:")
    print(f"  products:            {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM ingredients")
    print(f"  ingredients:         {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM product_ingredients")
    print(f"  product_ingredients: {cur.fetchone()[0]}")

    cur.close()
    pg.close()
    sq.close()
    print("\nMigracion completada.")


if __name__ == "__main__":
    run()
