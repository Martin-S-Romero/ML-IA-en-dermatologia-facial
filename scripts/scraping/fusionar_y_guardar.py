#!/usr/bin/env python3
"""
fusionar_y_guardar.py

1. Lee ambos inci_results.jsonl
2. Fusiona registros del mismo barcode (union de campos, ninguno se pierde)
3. Guarda en SQLite: inciapi.db

Schema:
  products          — un registro por barcode
  ingredientes      — uno por (barcode, inci_name)
  skin_compatibility — uno por (barcode, skin_type)
  efficacy          — uno por (barcode, effect)
"""

import json
import sqlite3
from pathlib import Path

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
BASE_DIR   = Path(__file__).parent
FILE_A     = BASE_DIR / "pantalla inicio"   / "inci_results.jsonl"
FILE_B     = BASE_DIR / "entorno de prueba" / "inci_results.jsonl"
DB_FILE    = BASE_DIR / "inciapi.db"

# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------

def load_jsonl(path: Path, label: str):
    records = {}
    if not path.exists():
        print(f"[WARN] No existe: {path}")
        return records
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                bc  = obj.get("barcode", "").strip()
                if bc:
                    records[bc] = {"source": label, "obj": obj}
            except Exception:
                pass
    print(f"  [{label}] {len(records):,} barcodes cargados.")
    return records


# ---------------------------------------------------------------------------
# Merge profundo
# ---------------------------------------------------------------------------

def deep_merge(base: dict, override: dict) -> dict:
    """
    Fusiona dos dicts. Para cada clave:
    - Si solo uno tiene el valor → lo usa
    - Si ambos tienen dict      → merge recursivo
    - Si ambos tienen lista     → usa la mas larga (mas datos)
    - Si ambos tienen escalar   → prefiere el que no es None
    """
    result = dict(base)
    for k, v_over in override.items():
        v_base = result.get(k)
        if v_base is None:
            result[k] = v_over
        elif v_over is None:
            pass  # mantener base
        elif isinstance(v_base, dict) and isinstance(v_over, dict):
            result[k] = deep_merge(v_base, v_over)
        elif isinstance(v_base, list) and isinstance(v_over, list):
            result[k] = v_base if len(v_base) >= len(v_over) else v_over
        else:
            # escalar: preferir el que no sea None/vacio
            result[k] = v_over if v_over not in (None, "", []) else v_base
    return result


def fusionar(recs_a: dict, recs_b: dict) -> list:
    """Devuelve lista de dicts fusionados con campo 'source'."""
    todos_bc = set(recs_a) | set(recs_b)
    merged   = []

    for bc in todos_bc:
        in_a = bc in recs_a
        in_b = bc in recs_b

        if in_a and in_b:
            source = "ambos"
            obj_a  = recs_a[bc]["obj"]
            obj_b  = recs_b[bc]["obj"]
            data   = deep_merge(obj_a.get("data") or {}, obj_b.get("data") or {})
            ep_demo = obj_a.get("endpoint")
            ep_auth = obj_b.get("endpoint")
        elif in_a:
            source  = "demo"
            obj_a   = recs_a[bc]["obj"]
            data    = obj_a.get("data") or {}
            ep_demo = obj_a.get("endpoint")
            ep_auth = None
        else:
            source  = "auth"
            obj_b   = recs_b[bc]["obj"]
            data    = obj_b.get("data") or {}
            ep_demo = None
            ep_auth = obj_b.get("endpoint")

        merged.append({
            "barcode"      : bc,
            "source"       : source,
            "endpoint_demo": ep_demo,
            "endpoint_auth": ep_auth,
            "data"         : data,
        })

    print(f"  Total barcodes fusionados: {len(merged):,}")
    only_a = sum(1 for m in merged if m["source"] == "demo")
    only_b = sum(1 for m in merged if m["source"] == "auth")
    both   = sum(1 for m in merged if m["source"] == "ambos")
    print(f"    Solo demo  : {only_a:,}")
    print(f"    Solo auth  : {only_b:,}")
    print(f"    En ambos   : {both:,}")
    return merged


# ---------------------------------------------------------------------------
# Base de datos
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    barcode               TEXT PRIMARY KEY,
    name                  TEXT,
    brand                 TEXT,
    category              TEXT,   -- JSON array como texto
    vertical              TEXT,
    overall_safety_score  REAL,
    safety_level          TEXT,
    pregnancy_safe        INTEGER, -- 1=true, 0=false, NULL=sin dato
    inci_raw              TEXT,
    source                TEXT,   -- 'demo' | 'auth' | 'ambos'
    endpoint_demo         TEXT,
    endpoint_auth         TEXT,
    raw_data              TEXT    -- JSON completo fusionado
);

CREATE TABLE IF NOT EXISTS ingredientes (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode              TEXT REFERENCES products(barcode),
    inci_name            TEXT,
    safety_score         REAL,
    safety_level         TEXT,
    is_allergen          INTEGER,
    comedogenicity_rating INTEGER,
    pregnancy_safe       INTEGER
);

CREATE TABLE IF NOT EXISTS skin_compatibility (
    barcode    TEXT REFERENCES products(barcode),
    skin_type  TEXT,
    compatible INTEGER,
    PRIMARY KEY (barcode, skin_type)
);

CREATE TABLE IF NOT EXISTS efficacy (
    barcode  TEXT REFERENCES products(barcode),
    effect   TEXT,
    strength TEXT,
    PRIMARY KEY (barcode, effect)
);

-- Indices utiles para consultas
CREATE INDEX IF NOT EXISTS idx_products_brand         ON products(brand);
CREATE INDEX IF NOT EXISTS idx_products_safety_score  ON products(overall_safety_score);
CREATE INDEX IF NOT EXISTS idx_products_safety_level  ON products(safety_level);
CREATE INDEX IF NOT EXISTS idx_productos_pregnancy    ON products(pregnancy_safe);
CREATE INDEX IF NOT EXISTS idx_ingredientes_barcode   ON ingredientes(barcode);
CREATE INDEX IF NOT EXISTS idx_ingredientes_inci_name ON ingredientes(inci_name);
CREATE INDEX IF NOT EXISTS idx_skin_barcode           ON skin_compatibility(barcode);
CREATE INDEX IF NOT EXISTS idx_efficacy_barcode       ON efficacy(barcode);
CREATE INDEX IF NOT EXISTS idx_efficacy_effect        ON efficacy(effect);
"""


def bool_to_int(val):
    if val is True:  return 1
    if val is False: return 0
    return None


def to_text(val):
    """Convierte cualquier valor a texto apto para SQLite, o None."""
    if val is None:
        return None
    if isinstance(val, str):
        return val
    if isinstance(val, (dict, list)):
        return json.dumps(val, ensure_ascii=False)
    return str(val)


def insertar(conn: sqlite3.Connection, merged: list):
    cur = conn.cursor()

    prod_rows  = []
    ingr_rows  = []
    skin_rows  = []
    efic_rows  = []

    for m in merged:
        bc       = m["barcode"]
        data     = m["data"]
        product  = data.get("product") or {}
        details  = data.get("details") or {}
        analysis = details.get("analysis") or {}

        # --- products ---
        cats = product.get("category") or product.get("categories")
        prod_rows.append((
            bc,
            to_text(product.get("name")),
            to_text(product.get("brand")),
            json.dumps(cats, ensure_ascii=False) if cats else None,
            to_text(product.get("vertical")),
            analysis.get("overallSafetyScore"),
            to_text(analysis.get("safetyLevel")),
            bool_to_int(analysis.get("pregnancySafe")),
            to_text(details.get("inci")),
            m["source"],
            to_text(m["endpoint_demo"]),
            to_text(m["endpoint_auth"]),
            json.dumps(data, ensure_ascii=False),
        ))

        # --- ingredientes ---
        parsed = analysis.get("parsedIngredients") or []
        for ing in parsed:
            if not isinstance(ing, dict):
                continue
            ingr_rows.append((
                bc,
                to_text(ing.get("inciName")),
                ing.get("safetyScore"),
                to_text(ing.get("safetyLevel")),
                bool_to_int(ing.get("isAllergen")),
                ing.get("comedogenicityRating"),
                bool_to_int(ing.get("pregnancySafe")),
            ))

        # --- skin_compatibility ---
        compat = analysis.get("skinTypeCompatibility") or {}
        if isinstance(compat, dict):
            for skin_type, val in compat.items():
                skin_rows.append((bc, skin_type, bool_to_int(val)))

        # --- efficacy ---
        efficacy = analysis.get("efficacySummary") or {}
        if isinstance(efficacy, dict):
            for effect, strength in efficacy.items():
                efic_rows.append((bc, to_text(effect), to_text(strength)))

    # Insertar en bloque
    cur.executemany("""
        INSERT OR REPLACE INTO products
        (barcode, name, brand, category, vertical,
         overall_safety_score, safety_level, pregnancy_safe, inci_raw,
         source, endpoint_demo, endpoint_auth, raw_data)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, prod_rows)

    cur.executemany("""
        INSERT INTO ingredientes
        (barcode, inci_name, safety_score, safety_level,
         is_allergen, comedogenicity_rating, pregnancy_safe)
        VALUES (?,?,?,?,?,?,?)
    """, ingr_rows)

    cur.executemany("""
        INSERT OR REPLACE INTO skin_compatibility (barcode, skin_type, compatible)
        VALUES (?,?,?)
    """, skin_rows)

    cur.executemany("""
        INSERT OR REPLACE INTO efficacy (barcode, effect, strength)
        VALUES (?,?,?)
    """, efic_rows)

    conn.commit()

    print(f"\n  Filas insertadas:")
    print(f"    products          : {len(prod_rows):,}")
    print(f"    ingredientes      : {len(ingr_rows):,}")
    print(f"    skin_compatibility: {len(skin_rows):,}")
    print(f"    efficacy          : {len(efic_rows):,}")


# ---------------------------------------------------------------------------
# Resumen post-insercion
# ---------------------------------------------------------------------------

def resumen(conn: sqlite3.Connection):
    cur = conn.cursor()
    print("\n  Verificacion en DB:")

    cur.execute("SELECT COUNT(*) FROM products")
    print(f"    products total         : {cur.fetchone()[0]:,}")

    cur.execute("SELECT COUNT(*) FROM products WHERE name IS NOT NULL")
    print(f"    con nombre             : {cur.fetchone()[0]:,}")

    cur.execute("SELECT COUNT(*) FROM products WHERE overall_safety_score IS NOT NULL")
    print(f"    con safety score       : {cur.fetchone()[0]:,}")

    cur.execute("SELECT ROUND(AVG(overall_safety_score),2) FROM products WHERE overall_safety_score IS NOT NULL")
    print(f"    score promedio         : {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM ingredientes")
    print(f"    ingredientes total     : {cur.fetchone()[0]:,}")

    cur.execute("SELECT COUNT(DISTINCT inci_name) FROM ingredientes WHERE inci_name IS NOT NULL")
    print(f"    ingredientes unicos    : {cur.fetchone()[0]:,}")

    cur.execute("SELECT COUNT(*) FROM skin_compatibility")
    print(f"    skin_compatibility rows: {cur.fetchone()[0]:,}")

    cur.execute("SELECT COUNT(*) FROM efficacy")
    print(f"    efficacy rows          : {cur.fetchone()[0]:,}")

    cur.execute("SELECT source, COUNT(*) FROM products GROUP BY source")
    print(f"    por fuente:")
    for row in cur.fetchall():
        print(f"      {row[0]:<10}: {row[1]:,}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  FUSIONAR Y GUARDAR EN SQLITE")
    print("=" * 60)

    print("\n[->] Cargando archivos...")
    recs_a = load_jsonl(FILE_A, "demo")
    recs_b = load_jsonl(FILE_B, "auth")

    print("\n[->] Fusionando registros...")
    merged = fusionar(recs_a, recs_b)

    print(f"\n[->] Creando base de datos: {DB_FILE.name}")
    if DB_FILE.exists():
        DB_FILE.unlink()
        print("  (archivo anterior eliminado)")

    conn = sqlite3.connect(DB_FILE)
    conn.executescript(SCHEMA)

    print("\n[->] Insertando datos...")
    insertar(conn, merged)

    resumen(conn)
    conn.close()

    print(f"\n{'='*60}")
    print(f"  DB guardada en: {DB_FILE}")
    print(f"{'='*60}")
    print("""
  Consultas de ejemplo:
    -- Top 10 marcas con mas productos
    SELECT brand, COUNT(*) n FROM products WHERE brand IS NOT NULL GROUP BY brand ORDER BY n DESC LIMIT 10;

    -- Productos seguros para piel sensible
    SELECT p.name, p.brand, p.overall_safety_score
    FROM products p JOIN skin_compatibility sc ON p.barcode = sc.barcode
    WHERE sc.skin_type = 'sensitive' AND sc.compatible = 1
    ORDER BY p.overall_safety_score DESC LIMIT 20;

    -- Ingrediente mas comun
    SELECT inci_name, COUNT(*) n FROM ingredientes WHERE inci_name IS NOT NULL GROUP BY inci_name ORDER BY n DESC LIMIT 20;

    -- Productos aptos para embarazo con score alto
    SELECT name, brand, overall_safety_score FROM products
    WHERE pregnancy_safe = 1 AND overall_safety_score >= 8
    ORDER BY overall_safety_score DESC;
""")


if __name__ == "__main__":
    main()
