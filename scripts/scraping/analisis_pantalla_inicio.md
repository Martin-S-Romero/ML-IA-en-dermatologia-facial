# Análisis: pantalla inicio  (demo endpoint)

**Archivo:** `C:\Users\Sheen\Downloads\Tesis 2.0\scripts\scraping\pantalla inicio\inci_results.jsonl`

## Resumen general

| Métrica | Valor |
|---|---|
| Total registros | 64,237 |
| Barcodes únicos | 64,237 |
| Duplicados | 0 |
| **Con producto (éxito)** | **41,247 (64.2%)** |
| No encontrado (404) | 22,990 (35.8%) |
| Errores de scraper | 0 (0.0%) |
| Otros | 0 (0.0%) |

## Endpoints detectados

| Endpoint | Requests |
|---|---|
| `https://inciapi.com/api/web/demo/products/{barcode}` | 64,237 |

## Estructura de respuestas exitosas

*(Muestra: 500 registros)*

### Campos `product`

| Campo | Presencia |
|---|---|
| `product.name` | 500 (100.0%) |
| `product.brand` | 500 (100.0%) |
| `product.barcode` | 500 (100.0%) |
| `product.imageUrls` | 500 (100.0%) |
| `product.category` | 500 (100.0%) |
| `product.vertical` | 500 (100.0%) |

### Campos `details.analysis`

| Campo | Presencia |
|---|---|
| `analysis.barcode` | 234 (46.8%) |
| `analysis.rawInci` | 234 (46.8%) |
| `analysis.parsedIngredients` | 234 (46.8%) |
| `analysis.overallSafetyScore` | 234 (46.8%) |
| `analysis.safetyLevel` | 234 (46.8%) |
| `analysis.allergenFlags` | 234 (46.8%) |
| `analysis.skinTypeCompatibility` | 234 (46.8%) |
| `analysis.pregnancySafe` | 234 (46.8%) |
| `analysis.pregnancyUnsafeIngredients` | 234 (46.8%) |
| `analysis.cleanBeautyScore` | 234 (46.8%) |
| `analysis.comedogenicityScore` | 234 (46.8%) |
| `analysis.analyzedAt` | 234 (46.8%) |
| `analysis.pfasIngredients` | 34 (6.8%) |
| `analysis.flags` | 34 (6.8%) |
| `analysis.coverage` | 26 (5.2%) |
| `analysis.efficacySummary` | 25 (5.0%) |
| `analysis.compatibilityConflicts` | 25 (5.0%) |
| `analysis.skinTypeRecommendations` | 25 (5.0%) |
| `analysis.evidenceCoverage` | 23 (4.6%) |

## Estadísticas de seguridad

### overallSafetyScore

| Métrica | Valor |
|---|---|
| Registros con score | 17,576 |
| Mínimo | 0 |
| Máximo | 10 |
| Promedio | 5.04 |

**Distribución por rango:**

| Rango | Productos |
|---|---|
| 0-1 | 77 |
| 1-2 | 116 |
| 10-11 | 7 |
| 2-3 | 417 |
| 3-4 | 1,737 |
| 4-5 | 4,169 |
| 5-6 | 8,033 |
| 6-7 | 2,148 |
| 7-8 | 683 |
| 8-9 | 131 |
| 9-10 | 58 |

### pregnancySafe

| Valor | Cantidad |
|---|---|
| True | 14,790 (84.1%) |
| False | 2,786 (15.9%) |

### Compatibilidad por tipo de piel

| Tipo de piel | Productos compatibles |
|---|---|
| oily | 17,576 |
| dry | 17,576 |
| sensitive | 17,576 |
| combination | 17,576 |
| normal | 17,576 |
| acneProne | 17,576 |

### Efectos de eficacia detectados

| Efecto | Productos |
|---|---|
| topEffects | 1,864 |
| evidencedIngredientCount | 1,864 |
| evidenceScore | 1,864 |