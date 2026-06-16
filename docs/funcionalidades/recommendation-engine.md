# Motor de Recomendación de Productos — SkinAI

## Índice

1. [Contexto y motivación](#1-contexto-y-motivación)
2. [Arquitectura general](#2-arquitectura-general)
3. [Fuentes de datos](#3-fuentes-de-datos)
4. [Scraper de INCIDecoder](#4-scraper-de-incidecoder)
5. [Motor de scoring de ingredientes](#5-motor-de-scoring-de-ingredientes)
6. [Base científica](#6-base-científica)
7. [Consultas SQL de referencia](#7-consultas-sql-de-referencia)
8. [Ejemplos de resultados](#8-ejemplos-de-resultados)
9. [Endpoint REST](#9-endpoint-rest)
10. [Estado actual](#10-estado-actual-junio-2026)

---

## 1. Contexto y motivación

SkinAI detecta condiciones dérmicas faciales mediante visión por computadora (EfficientNet-B3). El ciclo
completo que promete la aplicación es:

> **foto → diagnóstico → rutina de productos personalizada**

Sin el tercer paso, el diagnóstico queda incompleto — el usuario sabe qué tiene pero no qué hacer.
El motor de recomendación cierra ese ciclo: toma el `top1_label` del análisis IA (p. ej. `rosacea-etr`)
y devuelve los mejores productos del catálogo para esa condición, rankeados por un score de ingredientes.

---

## 2. Arquitectura general

```
Análisis IA (PostgreSQL)
  └── top1_label: "rosacea-etr"
  └── result.severity_score: 0.54

            ↓

Recommendation Engine  (backend/app/core/recommendation_engine.py)
  ├── Carga productos por categoría  ← PostgreSQL (products + product_ingredients + ingredients)
  ├── Aplica scoring por ingrediente activo, posición en fórmula y rating INCIDecoder
  └── Retorna top-N por categoría

            ↓

GET /api/products/recommendations/{analysis_id}
```

---

## 3. Fuentes de datos

| Fuente | Productos | Datos de calidad | Ratings |
|--------|-----------|-----------------|---------|
| Open Beauty Facts (OBF) | 41,248 | No | NULL |
| **INCIDecoder** (scraper) | **4,411** | **Sí** | superstar / goodie / ok / icky |
| **Total en BD** | **45,659** | — | — |

**El problema de OBF:** el catálogo de 41,000 productos tiene los ingredientes en texto plano pero sin
evaluación de calidad. Todos los productos OBF reciben el mismo score base de 40 puntos porque ningún
ingrediente tiene rating. El scraper de INCIDecoder soluciona esto para las marcas clínicas más relevantes.

---

## 4. Scraper de INCIDecoder

### Qué extrae

Por cada producto, el scraper descarga la página de [incidecoder.com](https://incidecoder.com) y extrae:

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| `rating` | Evaluación editorial INCIDecoder | `superstar`, `goodie`, `ok`, `icky` |
| `irr_com` | Irritancy, Comedogenicity (escala 0–5 c/u) | `"0, 0"`, `"2, 3"` |
| `position` | Orden en la fórmula (1 = mayor concentración) | `2` |
| `highlights` | Hashtags del producto | `["#fragrance-free", "#non-comedogenic"]` |
| `function` | Función del ingrediente | `"moisturizer/humectant, soothing"` |

### Modos de ejecución

```bash
# Desde dentro del contenedor:
docker exec tesis20-backend-1 python /app/scraper/main.py test       # 5 productos, verificación rápida
docker exec tesis20-backend-1 python /app/scraper/main.py priority   # ~4,500 productos marcas clave (~6h)
docker exec tesis20-backend-1 python /app/scraper/main.py batch 500  # próximos 500 pendientes
docker exec tesis20-backend-1 python /app/scraper/main.py full       # todo el catálogo (~223h)
```

El modo `priority` filtra las 178,601 URLs del sitemap de INCIDecoder para quedarse solo con marcas
dermatológicamente relevantes. La lista completa está en `backend/scraper/main.py → PRIORITY_BRANDS`.

### Marcas incluidas (39)

| Categoría | Marcas |
|-----------|--------|
| Dermatología clínica | CeraVe, La Roche-Posay, Cetaphil, Eucerin, Aveeno, SkinCeuticals, EltaMD, ISDIN, Uriage, SVR, Avène, Bioderma, Vichy, Sesderma |
| Activos / evidencia científica | The Ordinary, Paula's Choice, Differin, The INKEY List |
| Farmacias / masivos | Neutrogena, Olay, NIVEA, Garnier, L'Oréal, Pond's, RoC |
| Premium / departamentales | Clinique, Kiehl's, Drunk Elephant, Mario Badescu |
| K-beauty | COSRX, Purito, Some By Mi, Skin1004, Beauty of Joseon |

Estas marcas fueron elegidas por: (a) disponibilidad real en farmacias de Panama y LATAM, (b) frecuencia
de recomendación en literatura dermatológica, (c) presencia documentada en INCIDecoder.

### Rate limiting

El scraper respeta a INCIDecoder con un delay aleatorio de 3–6 segundos entre requests y backoff de 60s
ante HTTP 429. Tiempo estimado para el modo `priority`: ~6-7 horas.

### Resultados — Batch 1

```
Guardados: 2,144
Skipped:   2,353  (ya existían en BD de OBF)
Errores:   3
Tiempo:    392.6 minutos
```

### Deduplicación automática

Antes de scrapear cada URL se consulta `source_url` en la BD. Si ya existe, se salta sin hacer request:

```python
def already_scraped(url: str) -> bool:
    return db.query(models.Product).filter(
        models.Product.source_url == url
    ).first() is not None
```

Esto hace que re-ejecutar el scraper sea seguro y acumulativo — cada batch agrega solo lo nuevo.

---

## 5. Motor de scoring de ingredientes

### Algoritmo completo

```
score = 40  (base neutral — todos los productos arrancan aquí)

① Para cada ingrediente en la fórmula que coincide con la condición detectada:
     score += 15 × position_weight × rating_weight

② Para cada highlight positivo del producto:
     score += 5

③ Para cada ingrediente con irr_com (irritancy o comedogenicity) ≥ 3:
     score -= 5

④ Si severity_score > 0.6 Y hay al menos 1 match de ingrediente:
     score × 1.15  (boost por severidad alta)

⑤ Si el producto contiene algún ingrediente de avoid_ingredients:
     score = -1  → producto descartado completamente
```

### Pesos de posición (`position_weight`)

Basado en la Directiva EU de Cosméticos 1223/2009: los ingredientes se listan en orden descendente de
concentración. Los primeros en la fórmula tienen mayor impacto en el efecto del producto.

```
position_weight = max(0.05,  1.0 − (posición − 1) × 0.05)

posición  1 → 1.00  (ingrediente base, e.g. Agua)
posición  2 → 0.95
posición  5 → 0.80
posición 10 → 0.55
posición 20 → 0.05 (mínimo)
```

### Pesos de rating INCIDecoder (`rating_weight`)

| Valor en BD | Descripción INCIDecoder | Peso |
|-------------|------------------------|------|
| `superstar` | Respaldado por evidencia sólida | **1.5** |
| `goodie` | Beneficioso, bien tolerado | **1.0** |
| `ok` | Seguro, sin beneficio especial | **0.7** |
| `icky` | Potencial irritante o problemático | **−0.5** |
| `caution` | Requiere precaución | **−0.5** |
| `""` / NULL | Sin rating (datos OBF) | **0.5** |

### Ingredientes objetivo y a evitar por condición

| Condición | Ingredientes objetivo | Ingredientes a evitar |
|-----------|----------------------|----------------------|
| `acne-comedonal` | Salicylic Acid, Niacinamide, Zinc PCA, Adapalene | Fragrance, Coconut Oil, Isopropyl Myristate |
| `acne-excoriated` | Centella Asiatica, Panthenol, Azelaic Acid | Fragrance, Alcohol Denat, Glycolic Acid |
| `acne-inflammatory` | Benzoyl Peroxide, Azelaic Acid, Niacinamide | Fragrance, Coconut Oil |
| `rosacea-etr` | Azelaic Acid, Niacinamide, Zinc Oxide, Titanium Dioxide | Alcohol Denat, Linalool, Fragrance, Glycolic Acid |
| `rosacea-inflammatory` | Azelaic Acid, Centella Asiatica | Alcohol Denat, Fragrance, Glycolic Acid |
| `seborrheic-dermatitis` | Zinc Pyrithione, Piroctone Olamine, Selenium Sulfide | Coconut Oil, Olive Oil, Fragrance |
| `perioral-dermatitis` | Zinc Oxide, Niacinamide | Hydrocortisone, Betamethasone, Fragrance |
| `healthy-skin` | Tocopherol, Glycerin, Zinc Oxide | — |

---

## 6. Base científica

### ¿Por qué scoring de ingredientes y no ranking por marca?

La evidencia dermatológica establece que la eficacia en el tratamiento de condiciones cutáneas está
determinada por los **ingredientes activos** y su **concentración** en la fórmula, no por la marca
ni el precio. Esto se sustenta en:

- **Zaenglein et al. (2022)** — *Guidelines of care for the management of acne vulgaris*. JAAD.
  Define Salicylic Acid, Niacinamide, Benzoyl Peroxide y Adapalene como activos de primera línea
  en acné. La recomendación es por ingrediente, no por producto específico.

- **Alexis et al. (2020)** — Recomendaciones para rosácea en piel Fitzpatrick alto (relevante para
  población latinoamericana). Azelaic Acid y Niacinamide aparecen como primera línea por su
  tolerabilidad en pieles oscuras.

- **Borda & Wikramanayake (2015)** — Revisión de tratamientos tópicos para dermatitis seborreica.
  Zinc Pyrithione y Piroctone Olamine como antifúngicos tópicos de elección.

### ¿Por qué INCIDecoder como fuente de ratings?

INCIDecoder es la base de datos de ingredientes cosméticos más consultada por dermatólogos y
formuladores en ejercicio. Sus ratings editoriales están revisados por químicos cosméticos y
reflejan evidencia científica, no popularidad ni patrocinio comercial. A diferencia de bases de
datos como EWG (que mezcla riesgo con toxicología ambiental), INCIDecoder evalúa el ingrediente
en el contexto de uso cosmético tópico.

### ¿Por qué penalizar `irr_com` ≥ 3?

La escala de irritancia/comedogenicidad (0–5) es estándar en formulación cosmética.

- **Comedogenicidad ≥ 3**: riesgo documentado de obstrucción folicular. Relevante para acné
  comedoniano donde el folículo obstruido es el mecanismo patológico central.
- **Irritancia ≥ 3**: potencial de daño a la barrera cutánea. Relevante para rosácea (barrera
  comprometida) y piel sensible.

### ¿Por qué el boost de severidad?

En pacientes con severidad alta (score del modelo > 0.6), la selección de productos con activos
específicos es más crítica. Un producto que contiene el ingrediente de primera línea en alta
concentración (position_weight alto) merece un mayor diferencial respecto a uno neutro.

---

## 7. Consultas SQL de referencia

### Estado general del catálogo

```sql
-- Productos por fuente
SELECT
  CASE WHEN source_url LIKE '%incidecoder%' THEN 'INCIDecoder'
       ELSE 'Open Beauty Facts'
  END AS fuente,
  COUNT(*) AS total
FROM products
GROUP BY fuente;
-- INCIDecoder: 4,411 | Open Beauty Facts: 41,248

-- Distribución por categoría
SELECT category, COUNT(*) AS total
FROM products
GROUP BY category
ORDER BY total DESC;

-- Distribución de ratings en ingredientes
SELECT rating, COUNT(*) AS total
FROM ingredients
WHERE rating IS NOT NULL AND rating != ''
GROUP BY rating
ORDER BY total DESC;
```

### Ingredientes clave por rating

```sql
-- Ingredientes superstar y goodie clínicamente relevantes
SELECT i.inci_name, i.rating, i.function
FROM ingredients i
WHERE i.rating IN ('superstar', 'goodie')
  AND i.inci_name IN (
    'Niacinamide', 'Glycerin', 'Zinc Oxide', 'Azelaic Acid',
    'Centella Asiatica', 'Panthenol', 'Salicylic Acid',
    'Tocopherol', 'Ceramide NP', 'Hyaluronic Acid'
  )
ORDER BY i.rating, i.inci_name;
```

Resultado:

```
inci_name           | rating    | function
--------------------+-----------+---------------------------------------------
Centella Asiatica   | goodie    | soothing, antioxidant, moisturizer/humectant
Ceramide NP         | goodie    | skin-identical ingredient
Hyaluronic Acid     | goodie    | moisturizer/humectant
Panthenol           | goodie    | soothing, moisturizer/humectant
Tocopherol          | goodie    | antioxidant
Zinc Oxide          | goodie    | sunscreen
Azelaic Acid        | superstar | anti-acne, soothing, buffering
Glycerin            | superstar | skin-identical, moisturizer/humectant
Niacinamide         | superstar | anti-acne, brightening, moisturizer
Salicylic Acid      | superstar | exfoliant, anti-acne, soothing
```

### Top marcas scrapeadas de INCIDecoder

```sql
SELECT brand, COUNT(*) AS productos
FROM products
WHERE source_url LIKE '%incidecoder%'
GROUP BY brand
ORDER BY productos DESC
LIMIT 10;
```

Resultado:

```
brand           | productos
----------------+----------
Neutrogena      | 769
La Roche-Posay  | 520
Avene           | 471
Vichy           | 321
Cetaphil        | 288
Bioderma        | 278
Paula's Choice  | 263
CeraVe          | 214
COSRX           | 206
The Ordinary    | 128
```

### Productos con más activos para rosacea-etr

```sql
-- Productos SPF con al menos 2 ingredientes objetivo para rosacea-etr
SELECT
  p.brand,
  p.name,
  COUNT(DISTINCT i.inci_name) AS activos_encontrados,
  STRING_AGG(DISTINCT i.inci_name, ', ') AS activos
FROM products p
JOIN product_ingredients pi ON pi.product_id = p.id
JOIN ingredients i ON i.id = pi.ingredient_id
WHERE p.category = 'spf'
  AND p.source_url LIKE '%incidecoder%'
  AND i.inci_name IN ('Zinc Oxide', 'Titanium Dioxide', 'Niacinamide', 'Azelaic Acid')
GROUP BY p.id, p.brand, p.name
HAVING COUNT(DISTINCT i.inci_name) >= 2
ORDER BY activos_encontrados DESC, p.brand
LIMIT 10;
```

---

## 8. Ejemplos de resultados

### Análisis: `healthy-skin` (severity 0.46)

Ingredientes objetivo: Tocopherol, Glycerin, Zinc Oxide

```
CLEANSER
  [67.4]  EltaMD - Oil-in-gel Cleanser
          matched: Glycerin, Tocopherol
  [66.6]  La Roche-Posay - Toleriane Hydrating Gentle Cleanser
          matched: Glycerin, Tocopherol

MOISTURIZER
  [74.1]  La Roche-Posay - Anthelios HA Mineral Daily Moisturizing Cream SPF
          matched: Zinc Oxide, Glycerin, Tocopherol
  [72.2]  COSRX - Centella Blemish Cream
          matched: Glycerin, Zinc Oxide

SPF
  [74.1]  SkinCeuticals - Physical UV Defense SPF 30
          matched: Zinc Oxide, Glycerin, Tocopherol
  [73.0]  Drunk Elephant - Umbra Tinte Physical Daily Defense SPF 30
          matched: Zinc Oxide, Glycerin, Tocopherol

SERUM
  [70.4]  Cetaphil - Vitamin C Serum
          matched: Glycerin, Tocopherol
  [69.6]  Biodermal - Serum Skin Booster Revitalizing Serum
          matched: Glycerin, Tocopherol
```

### Análisis: `rosacea-etr` (severity 0.54)

Ingredientes objetivo: Azelaic Acid, Niacinamide, Zinc Oxide, Titanium Dioxide
Excluidos automáticamente: productos con Alcohol Denat, Linalool, Fragrance, Glycolic Acid

```
CLEANSER
  [59.1]  CeraVe - Baby Wash & Shampoo
          matched: Niacinamide

MOISTURIZER
  [77.5]  Neutrogena - Stubborn Acne Spot Drying Lotion
          matched: Niacinamide, Zinc Oxide, Titanium Dioxide
  [76.8]  Purito - Wonder Releaf Centella BB Cream SPF30
          matched: Titanium Dioxide, Zinc Oxide, Niacinamide

SPF
  [73.0]  EltaMD - UV Clear Tinted Broad-spectrum SPF 46
          matched: Zinc Oxide, Niacinamide
  [71.9]  EltaMD - UV Clear Blemish-prone & Oil Balancing SPF 50
          matched: Zinc Oxide, Niacinamide

SERUM
  [73.8]  Purito SEOUL - Azelaic Acid 10 Kojic Tea Tree Serum
          matched: Niacinamide, Azelaic Acid
  [62.9]  Mario Badescu - Brightening Eye Serum
          matched: Niacinamide, Titanium Dioxide
```

> **Validación clínica:** EltaMD UV Clear es el mineral sunscreen de primera elección para rosácea
> según la American Academy of Dermatology (2023). El motor lo ubica en el top 2 de SPF para
> `rosacea-etr` sin haberlo programado explícitamente — emerge del scoring de ingredientes.

---

## 9. Endpoint REST

```
GET /api/products/recommendations/{analysis_id}
Authorization: Bearer <jwt_token>
```

### Parámetros

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `analysis_id` | path (int) | — | ID del análisis completado |
| `categories` | query (lista) | `cleanser,moisturizer,spf,serum` | Categorías a rankear |
| `top_n` | query (int) | `5` | Productos por categoría (máx. 20) |

### Respuesta exitosa (200)

```json
{
  "analysis_id": 38,
  "condition": "rosacea-etr",
  "severity_score": 0.54,
  "recommendations": {
    "spf": [
      {
        "product_id": 12345,
        "name": "UV Clear Tinted Broad-spectrum SPF 46",
        "brand": "EltaMD",
        "category": "spf",
        "score": 73.0,
        "matched_ingredients": ["Zinc Oxide", "Niacinamide"],
        "highlights": ["#fragrance-free", "#non-comedogenic"]
      }
    ],
    "cleanser": [ ... ],
    "moisturizer": [ ... ],
    "serum": [ ... ]
  }
}
```

### Códigos de error

| Código | Causa |
|--------|-------|
| 401 | Token ausente o inválido |
| 404 | `analysis_id` no existe o no pertenece al usuario autenticado |

---

## 10. Estado actual (Junio 2026)

| Métrica | Valor |
|---------|-------|
| Productos totales en BD | 45,659 |
| Productos con ratings INCIDecoder | 4,411 |
| Ingredientes únicos | 42,714 |
| Links producto-ingrediente | 400,203 |
| Marcas en BD (total) | 11,544 |
| Marcas en priority brands | 39 |
| Condiciones soportadas | 8 |
| Categorías de productos | 12 |

### Pendiente

- **Segundo batch en curso:** marcas ISDIN, Eucerin, Olay, NIVEA, Garnier, Clinique, Kiehl's,
  Pond's, RoC, Uriage, SVR, Some By Mi, Skin1004, Beauty of Joseon. Esperado: ~1,500–2,000
  productos adicionales con ratings completos.
- **Deduplicación:** algunos productos existen dos veces (uno de OBF y uno de INCIDecoder).
  Pendiente limpieza post-batch con `DISTINCT ON (brand, name)`.
- **Highlights:** los 2,144 productos del primer batch tienen `highlights` como string JSON doble-
  encoded. Los productos del segundo batch en adelante quedan correctos (fix aplicado en db_writer).
