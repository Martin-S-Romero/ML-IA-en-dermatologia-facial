# Plan de Implementación — Motor de Recomendación

> Hoja de ruta para implementar la Opción C seguida de la Opción D.
> Ver diseño técnico completo en [recommendation-engine.md](./recommendation-engine.md).

---

## Visión general

```
Fase 1 — Opción C        Fase 2 — Iteración C       Fase 3 — Opción D       Fase 4 — Iteración D
─────────────────────    ───────────────────────    ─────────────────────    ────────────────────
Scoring de               Análisis de datos          C + templates de         Análisis de feedback
ingredientes puro   →   y ajuste de pesos      →   rutina completa     →   y ajuste de templates
(2 días)                 (1-2 semanas uso real)     (1 día sobre C)          (1-2 semanas uso real)
```

---

## Fase 1 — Implementación Opción C (Scoring de ingredientes)

### Prerequisito: Auditoría de catálogo

Antes de escribir una línea del engine, ejecutar estas queries y resolver discrepancias:

```sql
-- 1. Verificar valores reales de category
SELECT category, COUNT(*) as productos
FROM products
GROUP BY category
ORDER BY 2 DESC;

-- 2. Verificar cobertura de ingredientes
SELECT
    COUNT(DISTINCT p.id) as productos_con_ingredientes,
    (SELECT COUNT(*) FROM products) as total_productos
FROM products p
JOIN product_ingredients pi ON pi.product_id = p.id;

-- 3. Verificar ratings disponibles
SELECT rating, COUNT(*) FROM ingredients GROUP BY rating;

-- 4. Verificar formato real de irr_com
SELECT DISTINCT irr_com FROM product_ingredients LIMIT 20;

-- 5. Verificar si suitable_for tiene datos
SELECT COUNT(*) FROM products WHERE suitable_for IS NOT NULL AND suitable_for != '[]';
```

Resultados esperados a validar:
- `products.category` usa los strings exactos que se usan en los templates (`'cleanser'`, `'spf'`, `'serum'`, `'moisturizer'`, `'spot'`)
- Al menos 70% de los productos tienen datos de ingredientes
- `irr_com` tiene formato consistente `"N, N"` o `"N"`
- Documentar si `suitable_for` está poblado o no

### Archivos a crear / modificar

| Archivo | Acción | Descripción |
|---|---|---|
| `backend/app/core/recommendation_engine.py` | Crear | Lógica de scoring C |
| `backend/app/api/products.py` | Modificar | Endpoint `/recommendations` usando el engine |
| `backend/app/schemas.py` | Modificar | Schema `RecommendationOut` |

### Estructura del engine (C)

```python
# backend/app/core/recommendation_engine.py

from sqlalchemy.orm import Session
from app.db_scheme.product import Product, Ingredient, ProductIngredient
from app.db_scheme.analysis import Analysis
from app.core.skinai_analizar_v3 import INGREDIENTES_OBJETIVO, INGREDIENTES_EVITAR

RATING_WEIGHTS = {
    'Superstar': 1.5,
    'Good stuff': 1.0,
    'OK':         0.7,
    'Caution':   -0.5,
}

def normalize(name: str) -> str:
    return name.lower().strip()

def parse_irr_com(val: str | None) -> list[int]:
    if not val:
        return []
    return [int(x.strip()) for x in val.split(',') if x.strip().isdigit()]

def score_product(
    product: Product,
    target_ingredients: set[str],   # normalized lowercase
    avoid_ingredients: set[str],    # normalized lowercase
    bonus_highlights: list[str],
    severity_score: float,
) -> float:
    product_incis = {
        normalize(pi.ingredient.inci_name): pi
        for pi in product.product_ingredients
    }

    # Paso 1: hard exclude
    if any(avoid in product_incis for avoid in avoid_ingredients):
        return -1.0

    score = 40.0

    # Paso 2: target ingredient matching
    for inci_norm, pi in product_incis.items():
        if inci_norm in target_ingredients:
            pos_weight  = max(0.05, 1.0 - (pi.position - 1) * 0.05)
            rat_weight  = RATING_WEIGHTS.get(pi.ingredient.rating, 0.0)
            score      += 15 * pos_weight * rat_weight

    # Paso 3: highlights bonus
    highlights = product.highlights or []
    for h in bonus_highlights:
        if h in highlights:
            score += 5

    # Paso 4: irr_com penalty
    for pi in product.product_ingredients:
        for v in parse_irr_com(pi.irr_com):
            if v >= 3:
                score -= 5

    # Paso 5: severity boost
    if severity_score > 0.6 and score > 40.0:
        score *= 1.15

    return score


def get_recommendations(
    db: Session,
    analysis_id: int,
    categories: list[str],
    top_n: int = 5,
) -> dict[str, list[dict]]:
    analysis = db.query(Analysis).filter_by(id=analysis_id).first()
    condition = analysis.top1_label
    severity  = analysis.result.get('severity_score', 0.0)

    target = {normalize(i) for i in INGREDIENTES_OBJETIVO.get(condition, [])}
    avoid  = {normalize(i) for i in INGREDIENTES_EVITAR.get(condition, [])}

    # bonus_highlights por condición — mover a recommendation_config.py en Fase 3
    bonus_map = {
        'acne-comedonal':        ['#non-comedogenic', '#oil-free', '#fragrance-free'],
        'acne-inflammatory':     ['#fragrance-free', '#non-comedogenic'],
        'acne-excoriated':       ['#fragrance-free', '#sensitive', '#soothing'],
        'rosacea-etr':           ['#fragrance-free', '#no-alcohol', '#mineral-spf'],
        'rosacea-inflammatory':  ['#fragrance-free', '#no-alcohol'],
        'perioral-dermatitis':   ['#fragrance-free', '#sensitive'],
        'seborrheic-dermatitis': ['#fragrance-free', '#no-oil'],
        'healthy-skin':          ['#fragrance-free'],
    }
    bonus = bonus_map.get(condition, [])

    results = {}
    for category in categories:
        products = (
            db.query(Product)
            .filter(Product.category == category)
            .all()
        )
        scored = []
        for p in products:
            s = score_product(p, target, avoid, bonus, severity)
            if s >= 0:
                scored.append((s, p))

        scored.sort(key=lambda x: x[0], reverse=True)
        results[category] = [
            {
                'product_id':   p.id,
                'name':         p.name,
                'brand':        p.brand,
                'score':        round(s, 2),
                'highlights':   p.highlights,
            }
            for s, p in scored[:top_n]
        ]

    return results
```

### Nuevo endpoint

```python
# backend/app/api/products.py — agregar endpoint

@router.get("/recommendations/{analysis_id}")
def get_recommendations_for_analysis(
    analysis_id: int,
    categories: list[str] = Query(default=['cleanser', 'moisturizer', 'spf', 'serum']),
    top_n: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Retorna los mejores productos por categoría para la condición detectada
    en el análisis especificado. Usa scoring de ingredientes (Opción C).
    """
    analysis = db.query(Analysis).filter_by(
        id=analysis_id, user_id=current_user.id
    ).first()
    if not analysis:
        raise HTTPException(404, "Análisis no encontrado")
    if analysis.status != 'completed':
        raise HTTPException(400, "Análisis aún no completado")

    return get_recommendations(db, analysis_id, categories, top_n)
```

### Criterios de aceptación (C)

- [ ] El endpoint retorna resultados para todas las categorías solicitadas
- [ ] Productos con `avoid_ingredients` no aparecen en ningún resultado
- [ ] El score más alto en una categoría tiene al menos un `target_ingredient` matcheado
- [ ] Productos sin ingredientes en BD reciben score = 40 (baseline)
- [ ] El `irr_com` se parsea correctamente para el penalty
- [ ] La normalización INCI funciona: `'Niacinamide'` == `'niacinamide'` == `'NIACINAMIDE'`

---

## Fase 2 — Pruebas y recolección de datos (Opción C)

### Qué probar manualmente

Con el engine C activo, probar los siguientes escenarios contra la BD real:

**Escenario 1 — Condición con múltiples coincidencias de ingredientes**
- Usar `analysis_id` de un análisis con `top1_label = 'acne-comedonal'`
- Verificar que los productos rankeados #1 tienen `salicylic acid` o `niacinamide` en posición alta
- Verificar que ningún producto con `fragrance` o `coconut oil` aparece

**Escenario 2 — Condición sin matches en catálogo**
- Usar `top1_label = 'seborrheic-dermatitis'`
- `zinc pyrithione` y `piroctone olamine` son activos especializados; probablemente pocos o ningún producto los tiene
- Resultado esperado: todos los productos puntúan ~40 (baseline); no es un bug, es información sobre el catálogo

**Escenario 3 — Severity boost**
- Comparar recomendaciones para el mismo `top1_label` con `severity_score = 0.3` vs `0.7`
- El top-5 debe ser el mismo; los scores de los productos con matches deben ser 15% más altos en el caso severo

**Escenario 4 — Producto con rating Caution en target**
- Verificar que benzoyl peroxide (Caution en INCIDecoder) genera score menor que niacinamide (Good stuff) cuando ambos están en posición 1

### Métricas a medir

```
┌─────────────────────────────────────────────────────────────┐
│  Métricas de cobertura del catálogo (ejecutar en BD)        │
├─────────────────────────────────────────────────────────────┤
│  % productos con ≥1 target_ingredient para acne-comedonal   │
│  % productos con ≥1 target_ingredient para rosacea-etr      │
│  % slots vacíos (ningún producto apto) por condición        │
│  # categorías con < 3 productos elegibles por condición     │
└─────────────────────────────────────────────────────────────┘
```

### Ajustes esperados en esta fase

Los ajustes más probables después de ver datos reales:

1. **Ampliar `INGREDIENTES_OBJETIVO`** — si hay slots en baseline (score 40) para varias condiciones, agregar 5-8 ingredientes secundarios por condición expande el rango de scores
2. **Ajustar pesos** — si el severity boost ×1.15 genera scores que se sienten exagerados, cambiar a ×1.10; si `irr_com >= 3` penaliza demasiado, cambiar threshold a `>= 4`
3. **Normalizar `products.category`** — si la auditoría revela strings inconsistentes, actualizar los datos o agregar mapeo en el engine
4. **Seed de bonus_highlights** — si `product.highlights` está mayormente vacío, quitar o bajar el peso de ese bonus hasta que el scraper genere datos

---

## Fase 3 — Implementación Opción D (C + templates de rutina)

### Prerequisito

- Fase 1 y Fase 2 completadas
- Se conocen los valores reales de `products.category` en la BD
- Se validó que el scoring C produce resultados sensatos para al menos 3 condiciones
- Se definió `CONDITION_PROFILES` completo en `recommendation_config.py`

### Archivos a crear / modificar

| Archivo | Acción | Descripción |
|---|---|---|
| `backend/app/core/recommendation_config.py` | Crear | `ConditionProfile` + `CONDITION_PROFILES` |
| `backend/app/core/recommendation_engine.py` | Extender | Agregar `build_routine()` sobre el scoring C |
| `backend/app/api/routines.py` | Modificar | `POST /routines/` consume `analysis_id` |
| `backend/app/schemas.py` | Modificar | `RoutineCreateFromAnalysis` schema |

### Cambio en el endpoint de rutinas

```python
# backend/app/api/routines.py — modificar POST /routines/

@router.post("/", response_model=RoutineOut)
def create_routine_from_analysis(
    payload: RoutineCreateFromAnalysis,   # { analysis_id: int }
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Crea una rutina AM/PM completa basada en el análisis IA.
    Usa scoring C + templates por condición (Opción D).
    """
    analysis = db.query(Analysis).filter_by(
        id=payload.analysis_id, user_id=current_user.id
    ).first()
    if not analysis or analysis.status != 'completed':
        raise HTTPException(400, "Análisis no válido")

    routine_steps = build_routine(db, analysis)

    routine = Routine(
        user_id     = current_user.id,
        analysis_id = analysis.id,        # ← llenar el FK
        is_active   = True,
    )
    db.add(routine)
    db.flush()

    for step in routine_steps:
        step.routine_id = routine.id
        db.add(step)

    db.commit()
    db.refresh(routine)
    return routine
```

### Criterios de aceptación (D)

- [ ] `POST /routines/` con `analysis_id` crea Routine con `analysis_id` populado (no NULL)
- [ ] Los steps AM y PM están en el orden correcto del template de la condición
- [ ] Ningún step tiene `product_id` de un producto contraindicado
- [ ] Para rosacea-etr: no hay steps de categoría `exfoliant` ni `retinoid`
- [ ] Steps con slot vacío tienen `product_id = NULL` y `product_name` con mensaje claro
- [ ] El campo `reason` está lleno en cada step con texto específico
- [ ] El campo `ai_suggested = True` en todos los steps generados

---

## Fase 4 — Pruebas y recolección de datos (Opción D)

### Qué medir con D activo

**Señal de feedback implícita** (ya está en el schema):

```sql
-- ¿Cuántos productos AI-sugeridos reemplazó el usuario?
SELECT
    COUNT(*) FILTER (WHERE user_replaced = TRUE)  as reemplazados,
    COUNT(*) FILTER (WHERE user_replaced = FALSE) as mantenidos,
    COUNT(*)                                       as total
FROM routine_steps
WHERE ai_suggested = TRUE;

-- ¿Qué categorías se reemplazan más?
SELECT
    product_category,
    COUNT(*) FILTER (WHERE user_replaced = TRUE) as reemplazos,
    COUNT(*) as total,
    ROUND(100.0 * COUNT(*) FILTER (WHERE user_replaced = TRUE) / COUNT(*), 1) as pct
FROM routine_steps
WHERE ai_suggested = TRUE
GROUP BY product_category
ORDER BY 3 DESC;

-- Correlación seguimiento de rutina → mejora en siguiente análisis
SELECT
    sc.followed_routine,
    a2.result->>'severity_score' as severidad_siguiente,
    COUNT(*) as casos
FROM skin_checks sc
JOIN routines r ON r.id = sc.routine_id
JOIN analyses a1 ON a1.id = r.analysis_id
JOIN analyses a2 ON a2.user_id = r.user_id AND a2.created_at > a1.created_at
GROUP BY sc.followed_routine, a2.result->>'severity_score'
ORDER BY 1, 2;
```

### Ajustes esperados en esta fase

1. **Templates que generan muchos reemplazos en una categoría** → esa categoría necesita más productos en el catálogo o los criterios de scoring son demasiado restrictivos
2. **`followed_routine = FALSE` consistente para una condición** → el template puede ser demasiado exigente o los productos no están disponibles en el mercado local
3. **Steps con `product_id = NULL` frecuentes** → el catálogo tiene gaps para esas condiciones; priorizar scraping de esas categorías
4. **`reason` field con texto genérico** → mejorar la función `generar_reason()` para ser más específica en los matches encontrados

---

## Resumen de timelines

| Fase | Duración estimada | Output |
|---|---|---|
| Prerequisito: auditoría de catálogo | 1-2 horas | Queries de auditoría + fixes de category |
| Fase 1: Implementación C | 2 días | Endpoint `/recommendations/{analysis_id}` funcional |
| Fase 2: Pruebas + iteración C | 1-2 semanas uso | Pesos ajustados, listas ampliadas, cobertura validada |
| Fase 3: Implementación D | 1 día sobre C | `POST /routines/` genera rutina AM/PM desde `analysis_id` |
| Fase 4: Pruebas + iteración D | 1-2 semanas uso | Templates refinados, señales de feedback recolectadas |

> **Nota**: las duraciones de "uso real" son tiempo de exposición al sistema con usuarios reales, no tiempo de desarrollo. El desarrollo en sí es 1-2 horas de ajuste por iteración basado en los datos recolectados.

---

## Deuda técnica a tener en mente

Estos ítems no bloquean el MVP pero deben resolverse en iteraciones posteriores:

- **Sinónimos INCI** — `'Salicylic Acid'`, `'BHA'`, `'2-Hydroxybenzoic acid'` son el mismo compuesto. Sin un mapa de aliases, los matches son incompletos. Solución: tabla `ingredient_aliases` o normalización por CAS number.
- **`suitable_for` vacío** — el scraper de INCIDecoder no extrae ese campo. Los +10 del paso 5 de C nunca se aplican. Resolver en el scraper o eliminar ese bonus hasta que haya datos.
- **Multi-condición** — si `top2_label` tiene confianza > 0.3, la rutina debería integrar restricciones de ambas condiciones. D solo usa `top1_label`. Solución: merge de `avoid_ingredients` y `avoid_categories` de ambos perfiles.
- **`INGREDIENTES_OBJETIVO` corto** — 2-4 ingredientes por condición limita el rango de scores. Ampliar a 8-12 ingredientes por condición (primarios + secundarios + sinérgicos) es el lever de mayor impacto en calidad de C.
- **Interacciones entre productos** — retinol en PM serum + AHA en PM moisturizer es una combinación contraindicada. D no lo detecta; requeriría validación post-construcción de rutina.
