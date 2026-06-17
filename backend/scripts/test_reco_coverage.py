"""
test_reco_coverage.py — Métricas de cobertura del catálogo (Fase 2)
====================================================================
Ejecuta análisis de cobertura de ingredientes y scoring directamente
contra la BD del contenedor backend.

Cómo ejecutar (desde el host):
    docker-compose exec backend python /app/scripts/test_reco_coverage.py

Secciones:
  1  Resumen del catálogo (productos, ingredientes, cobertura)
  2  Cobertura de target_ingredients por condición
  3  Slots vacíos: condición × categoría con < 3 productos elegibles
  4  Validación del campo irr_com (formato y distribución de valores)
  5  Cobertura de highlights (bonus del paso 3 del engine)
  6  Simulación de scoring con análisis reales de la BD
"""

import sys
sys.path.insert(0, "/app")

from collections import defaultdict
from sqlalchemy.orm import joinedload
from sqlalchemy import func, distinct

from app.core.database import SessionLocal
from app import db_scheme as models
from app.core.recommendation_engine import (
    FALLBACK_TARGET,
    FALLBACK_AVOID,
    BONUS_HIGHLIGHTS,
    _normalize,
    _score_product,
    get_recommendations,
)

SEP  = "─" * 65
OK   = "OK  "
WARN = "WARN"
INFO = "··· "


def run_coverage():
    db = SessionLocal()
    try:
        _catalog_overview(db)
        _ingredient_coverage(db)
        _slots_by_condition(db)
        _irr_com_validation(db)
        _highlights_coverage(db)
        _scoring_simulation(db)
    finally:
        db.close()
        print(f"\n{'='*65}")
        print("  Cobertura completada.")
        print(f"{'='*65}\n")


# ── Sección 1: Resumen del catálogo ───────────────────────────────────────────

def _catalog_overview(db):
    print(f"\n{'='*65}")
    print("  1. RESUMEN DEL CATÁLOGO")
    print(f"{'='*65}")

    total_products    = db.query(models.Product).count()
    total_ingredients = db.query(models.Ingredient).count()
    total_pi          = db.query(models.ProductIngredient).count()
    products_with_ing = db.query(
        func.count(distinct(models.ProductIngredient.product_id))
    ).scalar() or 0

    print(f"  Productos totales:               {total_products}")
    print(f"  Ingredientes únicos:             {total_ingredients}")
    print(f"  Entradas product_ingredients:    {total_pi}")
    if total_products:
        pct = products_with_ing / total_products * 100
        flag = OK if pct >= 70 else WARN
        print(f"  [{flag}] Productos con ingredientes: {products_with_ing} ({pct:.1f}%)")
    else:
        print("  Sin productos en la BD.")
        return

    print(f"\n  Productos por categoría:")
    cats = (
        db.query(models.Product.category, func.count(models.Product.id))
        .group_by(models.Product.category)
        .order_by(func.count(models.Product.id).desc())
        .all()
    )
    for cat, cnt in cats:
        print(f"    {(cat or 'NULL'):<22} {cnt:>5} productos")


# ── Sección 2: Cobertura de target_ingredients por condición ──────────────────

def _ingredient_coverage(db):
    print(f"\n{'='*65}")
    print("  2. COBERTURA DE TARGET_INGREDIENTS POR CONDICIÓN")
    print(f"{'='*65}")
    print(f"  {'Condición':<28} {'Flag':<6} {'% con match':<14} Matches/Total")
    print(f"  {SEP}")

    all_products = _load_products_with_ingredients(db)
    total = len(all_products)

    for condition, targets in FALLBACK_TARGET.items():
        target_set = {_normalize(t) for t in targets}
        matched    = sum(
            1 for p in all_products
            if any(
                _normalize(pi.ingredient.inci_name) in target_set
                for pi in p.product_ingredients
                if pi.ingredient
            )
        )
        pct  = matched / total * 100 if total else 0
        flag = OK if pct >= 15 else WARN
        print(f"  [{flag}] {condition:<28} {pct:>6.1f}%        {matched}/{total}")

    # Desglose acne-comedonal por categoría (la condición más frecuente)
    print(f"\n  Desglose acne-comedonal por categoría:")
    target_set = {_normalize(t) for t in FALLBACK_TARGET["acne-comedonal"]}
    for cat in ["cleanser", "moisturizer", "spf", "serum"]:
        prods = [p for p in all_products if p.category == cat]
        if not prods:
            print(f"    {WARN} {cat:<15} — sin productos en catálogo")
            continue
        matched_cat = sum(
            1 for p in prods
            if any(
                _normalize(pi.ingredient.inci_name) in target_set
                for pi in p.product_ingredients
                if pi.ingredient
            )
        )
        pct  = matched_cat / len(prods) * 100
        flag = OK if pct >= 10 else WARN
        print(f"    [{flag}] {cat:<15} {pct:>5.1f}% ({matched_cat}/{len(prods)})")


# ── Sección 3: Slots vacíos condición × categoría ─────────────────────────────

def _slots_by_condition(db):
    print(f"\n{'='*65}")
    print("  3. SLOTS VACÍOS POR CONDICIÓN (elegibles para top_n=5)")
    print(f"{'='*65}")

    categories   = ["cleanser", "moisturizer", "spf", "serum"]
    all_products = _load_products_with_ingredients(db)

    header = f"  {'Condición':<28}" + "".join(f"{c:<14}" for c in categories)
    print(header)
    print(f"  {SEP}")

    gaps_found = []

    for condition in FALLBACK_TARGET:
        target_set = {_normalize(t) for t in FALLBACK_TARGET.get(condition, [])}
        avoid_set  = {_normalize(a) for a in FALLBACK_AVOID.get(condition, [])}
        bonus      = BONUS_HIGHLIGHTS.get(condition, [])

        row = f"  {condition:<28}"
        for cat in categories:
            prods    = [p for p in all_products if p.category == cat]
            eligible = sum(
                1 for p in prods
                if _score_product(p, target_set, avoid_set, bonus, 0.5)[0] >= 0
            )
            if eligible == 0:
                marker = f"✗{eligible:<2}"
                gaps_found.append(f"{condition}/{cat}")
            elif eligible < 3:
                marker = f"!{eligible:<2}"
            else:
                marker = f"✓{eligible:<2}"
            row += f"{marker:<14}"
        print(row)

    print(f"\n  Leyenda: ✓ ≥3 productos  ! 1-2 productos  ✗ sin productos elegibles")

    if gaps_found:
        print(f"\n  [{WARN}] Slots vacíos detectados ({len(gaps_found)}):")
        for g in gaps_found:
            print(f"    → {g}")
    else:
        print(f"\n  [{OK}] Sin slots vacíos — todas las combinaciones tienen ≥1 producto.")


# ── Sección 4: Validación de irr_com ──────────────────────────────────────────

def _irr_com_validation(db):
    print(f"\n{'='*65}")
    print("  4. VALIDACIÓN DEL CAMPO irr_com")
    print(f"{'='*65}")

    all_pi    = db.query(models.ProductIngredient).all()
    with_irr  = [pi for pi in all_pi if pi.irr_com]
    null_irr  = len(all_pi) - len(with_irr)

    malformed    = []
    values_dist  = defaultdict(int)

    for pi in with_irr:
        parts = [x.strip() for x in pi.irr_com.split(",")]
        valid = True
        for part in parts:
            if part.isdigit():
                values_dist[int(part)] += 1
            else:
                malformed.append(pi.irr_com)
                valid = False
                break

    total = len(all_pi)
    pct_with = len(with_irr) / total * 100 if total else 0

    flag_null = OK if null_irr / total < 0.5 else WARN
    flag_mal  = OK if not malformed else WARN

    print(f"  Total product_ingredients:  {total}")
    print(f"  [{flag_null}] Con irr_com:           {len(with_irr)} ({pct_with:.1f}%)")
    print(f"  [{flag_null}] Sin irr_com (NULL):    {null_irr} ({100-pct_with:.1f}%)")
    print(f"  [{flag_mal }] Malformados:           {len(malformed)}")
    if malformed[:5]:
        print(f"    Ejemplos: {malformed[:5]}")

    if values_dist:
        print(f"\n  Distribución de valores irr_com:")
        for v in sorted(values_dist):
            bar  = "█" * min(v * 3, 20)
            warn = " ← penaliza en engine (umbral ≥3)" if v >= 3 else ""
            print(f"    valor={v}: {values_dist[v]:>6} ocurrencias  {bar}{warn}")


# ── Sección 5: Cobertura de highlights ────────────────────────────────────────

def _highlights_coverage(db):
    print(f"\n{'='*65}")
    print("  5. COBERTURA DE HIGHLIGHTS (bonus paso 3 del engine)")
    print(f"{'='*65}")

    products  = db.query(models.Product).all()
    with_list = [p for p in products if isinstance(p.highlights, list) and p.highlights]
    total     = len(products)

    pct  = len(with_list) / total * 100 if total else 0
    flag = OK if pct >= 20 else WARN
    print(f"  [{flag}] Productos con highlights (lista): {len(with_list)}/{total} ({pct:.1f}%)")

    if not with_list:
        print(f"  [{WARN}] highlights vacío — el bonus de +5 puntos nunca aplica.")
        print(f"         Solución: revisar el scraper para que extraiga los hashtags.")
        return

    tag_counts = defaultdict(int)
    for p in with_list:
        for h in p.highlights:
            tag_counts[h] += 1

    all_bonus_tags = sorted({tag for tags in BONUS_HIGHLIGHTS.values() for tag in tags})
    covered  = 0
    print(f"\n  Cobertura de bonus_highlights en catálogo:")
    for tag in all_bonus_tags:
        cnt  = tag_counts.get(tag, 0)
        flag = OK if cnt > 0 else WARN
        if cnt > 0:
            covered += 1
        print(f"    [{flag}] {tag:<28} {cnt:>4} productos")

    print(f"\n  [{OK if covered else WARN}] {covered}/{len(all_bonus_tags)} tags con al menos 1 producto.")


# ── Sección 6: Simulación de scoring con análisis reales ──────────────────────

def _scoring_simulation(db):
    print(f"\n{'='*65}")
    print("  6. SIMULACIÓN DE SCORING (últimos 5 análisis completados)")
    print(f"{'='*65}")

    analyses = (
        db.query(models.Analysis)
        .filter(models.Analysis.status == "completed")
        .order_by(models.Analysis.created_at.desc())
        .limit(5)
        .all()
    )

    if not analyses:
        print(f"  Sin análisis completados en BD.")
        return

    categories = ["cleanser", "moisturizer", "spf", "serum"]

    for a in analyses:
        result = get_recommendations(
            db=db,
            analysis_id=a.id,
            user_id=a.user_id,
            categories=categories,
            top_n=3,
        )
        if not result:
            continue

        cond     = result["condition"]
        severity = result["severity_score"]
        reco     = result["recommendations"]

        print(f"\n  Analysis {a.id} | {cond:<28} | severity={severity:.2f}")
        print(f"  {SEP}")

        for cat in categories:
            prods = reco.get(cat, [])
            if not prods:
                print(f"    {WARN} {cat:<12} — sin productos elegibles")
            else:
                top     = prods[0]
                matches = top.get("matched_ingredients", [])
                name    = f"{top.get('brand','') or ''} {top['name']}"[:42]
                match_s = f" → {matches}" if matches else " → (sin match, baseline)"
                print(f"    {cat:<12} [{top['score']:>6.1f}] {name}{match_s}")


# ── Helpers ────────────────────────────────────────────────────────────────────

def _load_products_with_ingredients(db):
    return (
        db.query(models.Product)
        .options(
            joinedload(models.Product.product_ingredients)
            .joinedload(models.ProductIngredient.ingredient)
        )
        .all()
    )


if __name__ == "__main__":
    run_coverage()
