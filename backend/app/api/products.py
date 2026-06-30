from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app import db_scheme as models, schemas
from app.api import deps
from app.core.recommendation_engine import get_recommendations
import json

# Ingredientes genéricos de relleno que no aportan información en el catálogo
_FILLER_INGS: set[str] = {'water', 'aqua', 'eau'}

router = APIRouter()

"""
products.py
Endpoints de productos consultando la base de datos.
Los datos provienen del scraper de INCIDecoder (backend/scraper/).
"""

# ── ENDPOINTS ─────────────────────────────────────────────────────────────────

@router.get("/recommendations/{analysis_id}", response_model=schemas.RecommendationsOut)
def get_product_recommendations(
    analysis_id: int,
    categories: List[str] = Query(
        default=['cleanser', 'moisturizer', 'spf', 'serum'],
        description="Categorías a rankear. Valores válidos: cleanser | moisturizer | spf | serum | exfoliant | retinoid | spot | toner | eye | mask | oil | other",
    ),
    top_n: int = Query(default=5, ge=1, le=20, description="Productos a retornar por categoría"),
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """
    Retorna los mejores productos por categoría para la condición detectada
    en el análisis indicado. Usa scoring de ingredientes (Opción C).

    - Productos con ingredientes contraindicados para la condición son excluidos.
    - El score refleja: posición en fórmula, rating INCIDecoder, highlights compatibles,
      comedogenicidad/irritancia, y un boost por severidad alta.
    - El score solo es comparable dentro de la misma categoría.
    """
    # Cache hit: mismas categorías y top_n que la llamada anterior
    analysis = db.query(models.Analysis).filter_by(
        id=analysis_id, user_id=current_user.id
    ).first()
    if analysis is None:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")

    cache = analysis.cached_recommendations or {}
    cache_key = f"{sorted(categories)}|{top_n}"
    if cache.get("key") == cache_key and cache.get("data"):
        return cache["data"]

    # Cache miss: calcular y guardar
    result = get_recommendations(
        db=db,
        analysis_id=analysis_id,
        user_id=current_user.id,
        categories=categories,
        top_n=top_n,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")

    analysis.cached_recommendations = {"key": cache_key, "data": result}
    db.commit()

    return result


@router.get("/search", response_model=list[schemas.ProductOut])
def search_products(
    q:        Optional[str] = Query(None, description="Nombre o fragmento del producto / marca"),
    category: Optional[str] = Query(None, description="cleanser | moisturizer | spf | serum | exfoliant | retinoid | spot | toner | eye | mask | oil | other"),
    skip:     int           = Query(0,    ge=0),
    limit:    int           = Query(20,   ge=1, le=100),
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Busca productos en la BD por nombre/marca y/o categoría."""
    query = db.query(models.Product)

    if q:
        q_like = f"%{q}%"
        query = query.filter(
            models.Product.name.ilike(q_like) |
            models.Product.brand.ilike(q_like)
        )

    if category:
        query = query.filter(models.Product.category == category.lower())

    return query.order_by(models.Product.name).offset(skip).limit(limit).all()


@router.get("/recommended", response_model=list[schemas.ProductOut])
def get_recommended(
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Devuelve productos recomendados según el perfil de piel del usuario."""
    profile = db.query(models.SkinProfile).filter(
        models.SkinProfile.user_id == current_user.id
    ).first()

    base_categories = ["cleanser", "moisturizer", "spf"]

    if not profile:
        return _get_top_per_category(db, base_categories)

    # Con JSONB, skin_conditions ya llega como lista — sin json.loads
    conditions: list = profile.skin_conditions or []

    extra_categories = []
    if any(c in conditions for c in ["acne", "acné"]):
        extra_categories += ["serum", "exfoliant"]
    if any(c in conditions for c in ["rosácea", "rosacea", "manchas", "hiperpigmentación"]):
        extra_categories.append("serum")

    all_categories = list(dict.fromkeys(base_categories + extra_categories))
    return _get_top_per_category(db, all_categories, skin_type=profile.skin_type or "")



@router.get("/catalog", response_model=schemas.ProductCatalogResponse)
def get_product_catalog(
    q:           Optional[str] = Query(None, description="Buscar por nombre, marca o ingrediente"),
    category:    Optional[str] = Query(None, description="Filtro por categoría"),
    sort_by:     str           = Query("name_asc", description="name_asc | name_desc | category_asc | category_desc | brand_asc | brand_desc"),
    analysis_id: Optional[int] = Query(None, description="Filtrar por productos recomendados en este análisis"),
    page:        int           = Query(1, ge=1),
    page_size:   int           = Query(12, ge=1, le=50),
    current_user: models.User  = Depends(deps.get_current_user),
    db:          Session       = Depends(deps.get_db),
):
    """Catálogo paginado de productos con búsqueda, filtros por categoría y por análisis."""
    from sqlalchemy import or_

    # 1. Si se filtra por análisis, obtener los product_ids recomendados en ese análisis
    analysis_product_ids: Optional[set] = None
    if analysis_id is not None:
        analysis = db.query(models.Analysis).filter_by(
            id=analysis_id, user_id=current_user.id
        ).first()
        if analysis and analysis.cached_recommendations:
            reco_data = analysis.cached_recommendations.get('data', {})
            ids: set[int] = set()
            for cond in reco_data.get('conditions', []):
                for cat_products in cond.get('recommendations', {}).values():
                    for p in cat_products:
                        if p.get('product_id'):
                            ids.add(int(p['product_id']))
            analysis_product_ids = ids

    # 2. Base query — excluir: categoría "other", sin marca, sin ingredientes
    from sqlalchemy import exists
    base_q = db.query(models.Product).filter(
        models.Product.category != 'other',
        models.Product.brand.isnot(None),
        models.Product.brand != '',
        exists().where(models.ProductIngredient.product_id == models.Product.id),
    )

    if analysis_product_ids is not None:
        base_q = base_q.filter(models.Product.id.in_(analysis_product_ids))

    if category:
        base_q = base_q.filter(models.Product.category == category.lower())

    if q:
        q_like = f"%{q}%"
        ing_ids = (
            db.query(models.ProductIngredient.product_id)
            .join(models.Ingredient)
            .filter(models.Ingredient.inci_name.ilike(q_like))
            .subquery()
        )
        base_q = base_q.filter(
            or_(
                models.Product.name.ilike(q_like),
                models.Product.brand.ilike(q_like),
                models.Product.id.in_(ing_ids),
            )
        )

    # 3. Ordenación y paginación
    _SORT = {
        'name_asc':      [models.Product.name.asc()],
        'name_desc':     [models.Product.name.desc()],
        'category_asc':  [models.Product.category.asc(),  models.Product.name.asc()],
        'category_desc': [models.Product.category.desc(), models.Product.name.asc()],
        'brand_asc':     [models.Product.brand.asc(),     models.Product.name.asc()],
        'brand_desc':    [models.Product.brand.desc(),    models.Product.name.asc()],
    }
    order_cols = _SORT.get(sort_by, [models.Product.name.asc()])

    total = base_q.count()
    prods = (
        base_q
        .order_by(*order_cols)
        .options(joinedload(models.Product.product_ingredients).joinedload(models.ProductIngredient.ingredient))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # 4. Construir items — ingredientes clave = primeros por posición (mayor concentración)
    items = [
        schemas.CatalogProductOut(
            id=p.id,
            name=p.name,
            brand=p.brand,
            category=p.category,
            key_ingredients=[
                pi.ingredient.inci_name
                for pi in sorted(p.product_ingredients, key=lambda x: x.position)
                if pi.ingredient.inci_name.lower().strip() not in _FILLER_INGS
            ][:3],
        )
        for p in prods
    ]

    return schemas.ProductCatalogResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{product_id}", response_model=schemas.ProductDetailOut)
def get_product(
    product_id: int,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Retorna un producto con su lista completa de ingredientes."""
    product = (
        db.query(models.Product)
        .options(
            joinedload(models.Product.product_ingredients)
            .joinedload(models.ProductIngredient.ingredient)
        )
        .filter(models.Product.id == product_id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


# ── Helper interno ─────────────────────────────────────────────────────────────

def _get_top_per_category(
    db: Session,
    categories: list[str],
    skin_type: str = "",
    per_category: int = 2,
) -> list[models.Product]:
    """Retorna los N mejores productos de cada categoría."""
    results = []
    for cat in categories:
        query = db.query(models.Product).filter(models.Product.category == cat)
        if skin_type == "seca" and cat == "cleanser":
            query = query.filter(models.Product.name.ilike("%hydrat%"))
        elif skin_type in ("grasa", "mixta") and cat == "cleanser":
            query = query.filter(models.Product.name.ilike("%foam%"))
        results += query.limit(per_category).all()
    return results
