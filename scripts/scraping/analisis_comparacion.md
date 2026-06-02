# Comparación: pantalla inicio vs entorno de prueba

## Volumen y cobertura

| Métrica | pantalla inicio | entorno de prueba |
|---|---|---|
| Total registros | 64,237 | 64,237 |
| Barcodes únicos | 64,237 | 64,237 |
| Con producto | 41,247 (64.2%) | 41,248 (64.2%) |
| No encontrado (404) | 22,990 (35.8%) | 22,989 (35.8%) |
| Errores | 0 (0.0%) | 0 (0.0%) |

## Overlap de barcodes

| | Cantidad |
|---|---|
| En ambos archivos | 64,237 |
| Solo en pantalla inicio | 0 |
| Solo en entorno de prueba | 0 |
| Con producto en **ambos** | 41,247 |
| Con producto solo en pantalla inicio | 0 |
| Con producto solo en entorno de prueba | 1 |

## Comparación de datos de seguridad

| Métrica | pantalla inicio | entorno de prueba |
|---|---|---|
| Registros con score | 17,576 | 17,577 |
| Score promedio | 5.04 | 5.04 |
| Score mínimo | 0 | 0 |
| Score máximo | 10 | 10 |

## Endpoints

| Script | Endpoint base |
|---|---|
| pantalla inicio | `https://inciapi.com/api/web/demo/products/{barcode}` |
| entorno de prueba | `https://inciapi.com/api/web/products/{barcode}` |

## Observaciones

- **Cobertura combinada**: 41,248 barcodes únicos con datos de producto entre ambas fuentes.
- **41,247 barcodes** tienen respuesta en ambos endpoints — útil para comparar si la data del endpoint autenticado es más rica.
- Diferencia en score promedio entre endpoints: **0.00 puntos**.
- Endpoint `/demo/` es público (sin login) → apto para scraping masivo.
- Endpoint autenticado devuelve datos con mayor nivel de detalle (requiere sesión activa en browser).