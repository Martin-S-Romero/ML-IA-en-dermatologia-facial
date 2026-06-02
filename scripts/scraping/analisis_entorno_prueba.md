# Análisis: entorno de prueba (auth endpoint)

**Archivo:** `C:\Users\Sheen\Downloads\Tesis 2.0\scripts\scraping\entorno de prueba\inci_results.jsonl`

## Resumen general

| Métrica | Valor |
|---|---|
| Total registros | 64,237 |
| Barcodes únicos | 64,237 |
| Duplicados | 0 |
| **Con producto (éxito)** | **41,248 (64.2%)** |
| No encontrado (404) | 22,989 (35.8%) |
| Errores de scraper | 0 (0.0%) |
| Otros | 0 (0.0%) |

## Endpoints detectados

| Endpoint | Requests |
|---|---|
| `https://inciapi.com/api/web/products/{barcode}` | 64,237 |

## Estructura de respuestas exitosas

*(Muestra: 500 registros)*

### Campos `product`

| Campo | Presencia |
|---|---|
| `product.barcode` | 500 (100.0%) |
| `product.name` | 500 (100.0%) |
| `product.brand` | 500 (100.0%) |
| `product.manufacturer` | 500 (100.0%) |
| `product.category` | 500 (100.0%) |
| `product.country` | 500 (100.0%) |
| `product.imageUrls` | 500 (100.0%) |
| `product.weight` | 500 (100.0%) |
| `product.volume` | 500 (100.0%) |
| `product.packaging` | 500 (100.0%) |
| `product.dataSources` | 500 (100.0%) |
| `product.qualityScore` | 500 (100.0%) |
| `product.vertical` | 500 (100.0%) |
| `product.createdAt` | 500 (100.0%) |
| `product.updatedAt` | 500 (100.0%) |

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
| Registros con score | 17,577 |
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
| 3-4 | 1,736 |
| 4-5 | 4,170 |
| 5-6 | 8,033 |
| 6-7 | 2,149 |
| 7-8 | 683 |
| 8-9 | 131 |
| 9-10 | 58 |

### pregnancySafe

| Valor | Cantidad |
|---|---|
| True | 14,791 (84.1%) |
| False | 2,786 (15.9%) |

### Compatibilidad por tipo de piel

| Tipo de piel | Productos compatibles |
|---|---|
| oily | 17,577 |
| dry | 17,577 |
| sensitive | 17,577 |
| combination | 17,577 |
| normal | 17,577 |
| acneProne | 17,577 |

### Efectos de eficacia detectados

| Efecto | Productos |
|---|---|
| topEffects | 1,865 |
| evidencedIngredientCount | 1,865 |
| evidenceScore | 1,865 |