"""
recommendation_engine.py — SkinAI
===================================
Motor de scoring de ingredientes (Opción C).

Puntúa productos contra la condición detectada en un análisis IA.
Lee target_ingredients y avoid_ingredients del JSONB de analyses.result.
Si el JSONB no los tiene (análisis generados con versiones anteriores del
engine que no guardaban esos campos), cae back a las listas hardcodeadas
de FALLBACK_TARGET / FALLBACK_AVOID — idénticas a INGREDIENTES_OBJETIVO /
INGREDIENTES_EVITAR de skinai_analizar_v3, pero definidas aquí para no
importar ese módulo (que carga PyTorch a nivel de módulo).

Algoritmo por producto:
  1. Hard exclude si contiene avoid_ingredient  → score = -1, descarta
  2. Base: 40 puntos
  3. +15 × position_weight × rating_weight por cada target_ingredient
  4. +5 por cada bonus_highlight coincidente en product.highlights
  5. -5 por cada ingrediente con irr_com >= 3
  6. ×1.15 si severity_score > 0.6 Y tiene al menos un match

Ref position_weight: EU Cosmetics Directive 1223/2009.
Ref rating: INCIDecoder editorial (Superstar / Good stuff / OK / Caution).
"""

from sqlalchemy.orm import Session, joinedload
from app import db_scheme as models


# ── Pesos de rating (case-insensitive, normalizado en _score_product) ─────────
# INCIDecoder guarda: superstar / goodie / ok / icky / caution
# OBF/EWG guarda:     safe / low_risk / moderate / high_risk / hazardous

RATING_WEIGHTS: dict[str, float] = {
    # INCIDecoder
    'superstar':  1.5,
    'goodie':     1.0,
    'good stuff': 1.0,   # variante legacy
    'ok':         0.7,
    'icky':      -0.5,
    'caution':   -0.5,
    # OBF / EWG
    'safe':       1.0,
    'low_risk':   0.7,
    'moderate':   0.3,
    'high_risk':  0.0,
    'hazardous': -0.5,
    '':           0.5,   # sin rating — neutro
}

# ── Fallback: listas clínicas por condición ────────────────────────────────────
# Usadas cuando analyses.result no contiene target_ingredients / avoid_ingredients
# (análisis generados con versiones previas del engine).
# Fuente: Zaenglein 2022 (acné), Alexis 2020 (rosácea), Borda 2015 (derm. seb.)
# Mantener en sync con INGREDIENTES_OBJETIVO / INGREDIENTES_EVITAR
# en skinai_analizar_v3.py.

FALLBACK_TARGET: dict[str, list[str]] = {
    'acne-comedonal':        ['Salicylic Acid', 'Niacinamide', 'Zinc PCA', 'Adapalene'],
    'acne-excoriated':       ['Centella Asiatica', 'Panthenol', 'Azelaic Acid'],
    'acne-inflammatory':     ['Benzoyl Peroxide', 'Azelaic Acid', 'Niacinamide'],
    'perioral-dermatitis':   ['Zinc Oxide', 'Niacinamide'],
    'rosacea-etr':           ['Azelaic Acid', 'Niacinamide', 'Zinc Oxide', 'Titanium Dioxide'],
    'rosacea-inflammatory':  ['Azelaic Acid', 'Centella Asiatica'],
    'seborrheic-dermatitis': ['Zinc Pyrithione', 'Piroctone Olamine', 'Selenium Sulfide'],
    'healthy-skin':          ['Tocopherol', 'Glycerin', 'Zinc Oxide'],
}

FALLBACK_AVOID: dict[str, list[str]] = {
    'acne-comedonal':        ['fragrance', 'coconut oil', 'isopropyl myristate'],
    'acne-excoriated':       ['fragrance', 'alcohol denat', 'glycolic acid'],
    'acne-inflammatory':     ['fragrance', 'coconut oil'],
    'perioral-dermatitis':   ['hydrocortisone', 'betamethasone', 'fragrance'],
    'rosacea-etr':           ['alcohol denat', 'linalool', 'fragrance', 'glycolic acid'],
    'rosacea-inflammatory':  ['alcohol denat', 'fragrance', 'glycolic acid'],
    'seborrheic-dermatitis': ['coconut oil', 'olive oil', 'fragrance'],
    'healthy-skin':          [],
}

# ── Highlights de bonus por condición ─────────────────────────────────────────
# Mapeo condition_label → hashtags de product.highlights que suman puntos.
# Se usan los hashtags tal como los guarda el scraper de INCIDecoder.

BONUS_HIGHLIGHTS: dict[str, list[str]] = {
    'acne-comedonal':        ['#non-comedogenic', '#oil-free', '#fragrance-free'],
    'acne-excoriated':       ['#fragrance-free', '#sensitive', '#soothing'],
    'acne-inflammatory':     ['#fragrance-free', '#non-comedogenic', '#sensitive'],
    'perioral-dermatitis':   ['#fragrance-free', '#sensitive'],
    'rosacea-etr':           ['#fragrance-free', '#no-alcohol', '#sensitive', '#mineral-spf'],
    'rosacea-inflammatory':  ['#fragrance-free', '#no-alcohol', '#sensitive'],
    'seborrheic-dermatitis': ['#fragrance-free', '#no-oil'],
    'healthy-skin':          ['#fragrance-free'],
}


# ── Helpers internos ───────────────────────────────────────────────────────────

def _normalize(name: str) -> str:
    return name.lower().strip()


def _parse_irr_com(val: str | None) -> list[int]:
    """Parsea 'irritancy, comedogenicity' de string '2, 3' a [2, 3]."""
    if not val:
        return []
    return [int(x.strip()) for x in val.split(',') if x.strip().isdigit()]


def _score_product(
    product: models.Product,
    target: set[str],
    avoid: set[str],
    bonus: list[str],
    severity: float,
) -> tuple[float, list[str]]:
    """
    Retorna (score, lista_de_inci_matcheados).
    Score -1.0 significa hard exclude — el producto no debe aparecer.
    product.product_ingredients debe estar cargado con joinedload.
    """
    pis = product.product_ingredients
    incis: dict[str, models.ProductIngredient] = {
        _normalize(pi.ingredient.inci_name): pi
        for pi in pis
        if pi.ingredient is not None
    }

    # Paso 1: hard exclude
    if any(av in incis for av in avoid):
        return -1.0, []

    score = 40.0
    matched: list[str] = []

    # Paso 2: target ingredient matching
    for inci_norm, pi in incis.items():
        if inci_norm in target:
            pos_weight = max(0.05, 1.0 - ((pi.position or 10) - 1) * 0.05)
            rat_key    = (pi.ingredient.rating or '').lower().strip()
            rat_weight = RATING_WEIGHTS.get(rat_key, 0.5)
            score += 15.0 * pos_weight * rat_weight
            matched.append(pi.ingredient.inci_name)

    # Paso 3: highlights bonus (ignorar si no es lista — OBF guarda dicts)
    highlights: list = product.highlights if isinstance(product.highlights, list) else []
    for h in bonus:
        if h in highlights:
            score += 5.0

    # Paso 4: irr_com penalty
    for pi in pis:
        for v in _parse_irr_com(pi.irr_com):
            if v >= 3:
                score -= 5.0

    # Paso 5: severity boost
    if severity > 0.6 and score > 40.0:
        score *= 1.15

    return round(score, 2), matched


# ── API pública ────────────────────────────────────────────────────────────────

def get_recommendations(
    db: Session,
    analysis_id: int,
    user_id: int,
    categories: list[str],
    top_n: int = 5,
) -> dict | None:
    """
    Retorna los top_n productos rankeados por score para cada categoría.
    Devuelve None si el análisis no existe o no pertenece al usuario.

    El resultado tiene esta forma:
    {
        'analysis_id': int,
        'condition': str,
        'severity_score': float,
        'recommendations': {
            'cleanser': [{'product_id', 'name', 'brand', 'score', 'matched_ingredients', ...}, ...],
            'moisturizer': [...],
            ...
        }
    }
    """
    analysis = db.query(models.Analysis).filter_by(
        id=analysis_id, user_id=user_id
    ).first()
    if not analysis:
        return None

    # top1_label es columna dedicada (indexed) — más fiable que parsear el JSONB.
    # El campo 'condition' en JSONB v3 y 'top1_label' en v1 son equivalentes;
    # usamos la columna dedicada que existe desde la primera versión del schema.
    condition = analysis.top1_label or 'healthy-skin'
    result    = analysis.result or {}

    # severity_score: presente en análisis v3 (model_version efficientnet_b3_v3).
    # En análisis v1 el JSONB no lo tiene → cae a 0.0 (sin severity boost).
    severity  = float(result.get('severity_score', 0.0))

    # target_ingredients / avoid_ingredients: solo presentes en análisis generados
    # con el engine que incluye construir_resultado_completo() actualizado.
    # Los análisis existentes en BD usan JSONB sin esos campos → fallback a listas
    # hardcodeadas idénticas a las de skinai_analizar_v3.
    target_raw: list[str] = result.get('target_ingredients') or FALLBACK_TARGET.get(condition, [])
    avoid_raw:  list[str] = result.get('avoid_ingredients')  or FALLBACK_AVOID.get(condition, [])

    target: set[str] = {_normalize(i) for i in target_raw}
    avoid:  set[str] = {_normalize(i) for i in avoid_raw}
    bonus:  list[str] = BONUS_HIGHLIGHTS.get(condition, [])

    recommendations: dict[str, list[dict]] = {}

    for category in categories:
        products = (
            db.query(models.Product)
            .filter(models.Product.category == category)
            .options(
                joinedload(models.Product.product_ingredients)
                .joinedload(models.ProductIngredient.ingredient)
            )
            .all()
        )

        scored: list[dict] = []
        for p in products:
            score, matched = _score_product(p, target, avoid, bonus, severity)
            if score < 0:
                continue
            scored.append({
                'product_id':          p.id,
                'name':                p.name,
                'brand':               p.brand,
                'category':            p.category,
                'score':               score,
                'matched_ingredients': matched,
                'highlights':          p.highlights if isinstance(p.highlights, list) else [],
            })

        scored.sort(key=lambda x: x['score'], reverse=True)
        recommendations[category] = scored[:top_n]

    return {
        'analysis_id':     analysis_id,
        'condition':       condition,
        'severity_score':  severity,
        'recommendations': recommendations,
    }
