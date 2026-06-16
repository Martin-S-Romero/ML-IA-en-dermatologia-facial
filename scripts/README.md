# scripts/

Scripts de soporte del proyecto SkinAI: pruebas, migraciones, mantenimiento de datos,
configuración del entorno y scraping de catálogo.

---

## Estructura

```
scripts/
├── tests/              Pruebas de integración contra la API HTTP
│   └── attacks/        Pruebas de seguridad ofensiva
├── migrations/         Scripts de migración one-time
├── maintenance/        Mantenimiento de datos en BD (deduplicación, correcciones)
├── setup/              Configuración inicial del entorno
├── utils/              Herramientas de diagnóstico y verificación
└── scraping/           Scrapers del catálogo de ingredientes (INCIDecoder / OBF)
```

> **Prerequisito general** — la mayoría de los tests y utils asumen que el backend
> está corriendo en `http://localhost:8000`. Para levantarlo:
> ```bash
> docker-compose up
> ```

---

## tests/

Pruebas de integración que golpean la API HTTP directamente vía `requests`.
Cada archivo es independiente y crea sus propios usuarios efímeros de prueba.

Para correr todos:
```bash
# Linux / macOS
bash run_all_tests.sh

# Windows
run_all_tests.bat
```

Para correr uno solo:
```bash
python scripts/tests/test_auth_flow.py
```

### Archivos

| Archivo | Qué prueba | Endpoints cubiertos |
|---|---|---|
| `test_auth_flow.py` | Registro (con y sin GDPR), login fallido, login exitoso y generación de token JWT | `POST /auth/register`, `POST /auth/login` |
| `test_rate_limit.py` | Rate limiting en forgot-password: bloquea tras 3 peticiones/min con HTTP 429 | `POST /auth/forgot-password` |
| `test_users.py` | CRUD de perfil de usuario: datos personales, tipo de piel, condiciones, alergias | `GET/PUT /users/me`, `GET/PUT /users/profile` |
| `test_routines.py` | Ciclo completo de rutina: creación, lectura, actualización de paso, skin check | `POST/GET /routines/`, `PATCH /routines/active/steps`, `POST /routines/check` |
| `test_products.py` | Búsqueda de productos, recomendaciones por perfil y detalle de producto | `GET /products/search`, `GET /products/recommended`, `GET /products/{id}` |
| `test_recommendations_phase2.py` | Motor de recomendación (Fase 2): 4 escenarios clínicos + contrato del endpoint | `GET /products/recommendations/{analysis_id}` |
| `test_analysis_endpoints.py` | Historial de análisis, documento completo, estado e imagen censurada | `GET /analysis/history`, `GET /analysis/{id}`, `GET /analysis/{id}/status`, `GET /analysis/{id}/image` |
| `test_censorship_modes.py` | Modos de censura facial: blur, pixelate y black sobre imagen de prueba | Directo sobre `FaceCensor` (unit test local) |
| `test_skin_mock.py` | Pipeline completo: registro → subida de imagen → polling Celery → resultado IA | `POST /analysis/upload`, `GET /analysis/{id}/status`, `GET /analysis/{id}` |
| `test_processing.py` | Subida de imagen con los tres modos de censura; guarda imágenes procesadas en disco | `POST /analysis/upload` |

#### test_recommendations_phase2.py — uso avanzado

Para correr los escenarios clínicos con una cuenta que ya tiene análisis completados:
```bash
TEST_USER_EMAIL=usuario@example.com python scripts/tests/test_recommendations_phase2.py
```
Sin esa variable, los escenarios 1–4 se omiten (el usuario nuevo no tiene historial).

---

### tests/attacks/

Pruebas de seguridad ofensiva. Simulan ataques reales para verificar que las defensas
del backend están activas.

| Archivo | Qué ataca / verifica |
|---|---|
| `test_cors_isolation.py` | Política CORS: permite al frontend legítimo y bloquea orígenes no autorizados |
| `test_security_headers.py` | Presencia de 6 headers HTTP de seguridad: `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Strict-Transport-Security`, `Content-Security-Policy`, `Referrer-Policy` |
| `test_rls_isolation.py` | Row-Level Security: el Usuario B no puede acceder a análisis ni imágenes del Usuario A |

---

## migrations/

Scripts que se corren **una sola vez** para transformar o importar datos.
Después de ejecutarse quedan como registro histórico de qué se hizo y cuándo.

| Archivo | Cuándo usarlo | Descripción |
|---|---|---|
| `migrate_sqlite_to_postgres.py` | Migración inicial | Mueve productos, ingredientes y `product_ingredients` de la BD SQLite de desarrollo (`scraping/inciapi.db`) a PostgreSQL (`tesis_db`). Maneja compatibilidad de piel y scores de seguridad como JSONB. |
| `migrate_product_categories.sql` | Post-importación | Re-categoriza productos por coincidencia de palabras clave en nombre/descripción. Mapea a 12 categorías (cleanser, moisturizer, spf, serum, exfoliant, retinoid, toner, eye, mask, oil, spot, other) en orden de especificidad. |
| `analyses_202606121038.sql` | Backfill de análisis | INSERT de 7 registros reales de análisis con condiciones clasificadas (acne-excoriated, rosacea-inflammatory, healthy-skin) y análisis detallado por zonas faciales. |

### Cómo correr las migraciones SQL

```bash
# Desde el host, conectando a PostgreSQL del contenedor
docker-compose exec db psql -U postgres -d tesis_db -f /ruta/al/archivo.sql

# O copiando el archivo primero al contenedor
docker cp scripts/migrations/migrate_product_categories.sql <container_id>:/tmp/
docker-compose exec db psql -U postgres -d tesis_db -f /tmp/migrate_product_categories.sql
```

### Cómo correr la migración Python

```bash
# Requiere psycopg2 y acceso a ambas BDs
pip install psycopg2-binary
python scripts/migrations/migrate_sqlite_to_postgres.py
```

---

## maintenance/

Scripts PowerShell que corren código Python **dentro del contenedor backend** para
operar directamente sobre la BD de producción/local.

Todos siguen el mismo patrón de ejecución:
```powershell
# Desde la raíz del proyecto
.\scripts\maintenance\<script>.ps1
```

| Archivo | Qué hace | Cuándo usarlo |
|---|---|---|
| `deduplicate_products.ps1` | Elimina productos duplicados. Prioriza la fuente INCIDecoder sobre Open Beauty Facts; cuando ambos duplicados son de la misma fuente, conserva el de mayor ID. | Después de una importación masiva de productos |
| `fix_highlights.ps1` | Corrige el campo `highlights` con JSON doblemente codificado (string en vez de array). Detecta y convierte los valores `text` a `jsonb` correcto. | Si el scraper guardó highlights como string JSON en lugar de array |
| `recategorize_products.ps1` | Re-categoriza todos los productos usando una función `_infer_category` mejorada que reconoce 40+ tipos de producto y filtra maquillaje, productos corporales y artículos no-faciales a la categoría `other`. | Cuando se agrega lógica de categorización mejorada al scraper |

---

## setup/

Scripts para dejar el entorno listo desde cero. Se corren en orden la primera vez
que se levanta el proyecto o en un entorno nuevo.

### Orden de ejecución recomendado

```
1. docker-compose up           # levantar la BD
2. setup_rls.sql               # crear rol y políticas RLS en PostgreSQL
3. setup_rls.py                # (alternativa Python a setup_rls.sql)
4. seed_db.py                  # crear usuarios de prueba via API
```

| Archivo | Qué hace |
|---|---|
| `setup_rls.sql` | Configura Row-Level Security en PostgreSQL. Crea el rol `app_user`, le asigna permisos, y establece políticas RLS en 6 tablas (`users`, `skin_profiles`, `analyses`, `routines`, `routine_steps`, `skin_checks`) usando `app.current_user_id` como contexto de sesión. |
| `setup_rls.py` | Equivalente Python de `setup_rls.sql`. Conecta directamente a la BD con psycopg2 y ejecuta el mismo DDL. Útil si se prefiere correr desde Python en lugar de psql. |
| `seed_db.py` | Crea dos usuarios de prueba (Ana García y Carlos López) con perfiles completos: edad, género, escala de Fitzpatrick, tipo de piel, condiciones y alergias. Valida conectividad con la API antes de empezar. |

```bash
# Correr seed_db desde el host (requiere backend levantado)
python scripts/setup/seed_db.py

# Correr setup_rls.sql desde el host
docker-compose exec db psql -U postgres -d tesis_db < scripts/setup/setup_rls.sql
```

---

## utils/

Herramientas de diagnóstico y verificación puntuales. No forman parte del flujo
normal de pruebas.

| Archivo | Qué hace | Cuándo usarlo |
|---|---|---|
| `check_mp.py` | Verifica la instalación de MediaPipe: intenta importar `mediapipe`, `mediapipe.python`, `mediapipe.solutions` y `face_mesh`, e imprime la versión y ruta del módulo. | Al configurar un entorno nuevo si hay errores con la detección facial |
| `verify_upload.py` | Hace login con credenciales de prueba, sube una imagen JPEG y verifica que la respuesta contiene el nombre de archivo. Prueba rápida del endpoint de subida sin esperar el procesamiento IA. | Para verificar que el volumen de uploads y los permisos del contenedor están bien |
| `test_recommendations.ps1` | Corre el motor de recomendación directamente dentro del contenedor con dos condiciones clínicas (`rosacea-etr` y `acne-comedonal`) y muestra los scores de los productos top. | Para inspeccionar resultados del engine contra la BD real sin levantar los tests completos |

```bash
# check_mp (dentro del contenedor)
docker-compose exec backend python /app/scripts/utils/check_mp.py   # si se mueve al contenedor

# verify_upload (desde el host)
python scripts/utils/verify_upload.py

# test_recommendations (PowerShell, desde la raíz del proyecto)
.\scripts\utils\test_recommendations.ps1
```

---

## scraping/

Scrapers del catálogo de ingredientes. Extraen datos de **INCIDecoder** (vía la API
privada de inciapi.com) y de **Open Beauty Facts** (CSV público) para poblar la BD
de productos.

> Estos scripts se corrieron durante la fase de construcción del catálogo.
> No son parte del flujo de desarrollo normal.

### Arquitectura del proceso de scraping

```
Open Beauty Facts CSV  ──┐
                          ├── fusionar_y_guardar.py ──► inci_results.jsonl ──► migrate_sqlite_to_postgres.py
INCIDecoder (inciapi) ───┘
    │
    ├── pantalla inicio/       Scraping de la demo pública (sin auth, async, 15 peticiones paralelas)
    ├── entorno de prueba/     Scraping del dashboard autenticado (Playwright DOM)
    └── network sniffer/       Captura de red para descubrir endpoints privados
```

### Subcarpetas

#### `pantalla inicio/`

Scraping del endpoint público `/api/web/demo/products/{barcode}` de inciapi.com.
No requiere autenticación. Usa `aiohttp` con 15 peticiones concurrentes.

| Archivo | Rol |
|---|---|
| `inciapi_scraper.py` | Scraper principal: itera barcodes del CSV de Open Beauty Facts, consulta el endpoint demo, guarda resultados en `inci_results_pantalla_inicio.jsonl` |
| `inci_monitor.py` | Monitor en tiempo real: muestra barra de progreso con conteo de éxitos, 404s y errores mientras el scraper corre en paralelo |

```bash
# Correr en terminales separadas
python scripts/scraping/pantalla\ inicio/inciapi_scraper.py &
python scripts/scraping/pantalla\ inicio/inci_monitor.py
```

#### `entorno de prueba/`

Scraping del dashboard autenticado de inciapi.com. Usa **Playwright** para hacer
login, navegar al playground y capturar datos calculados por JavaScript
(safety scores, compatibilidad de piel).

| Archivo | Rol |
|---|---|
| `inciapi_scraper_sandbox.py` | Scraper vía Playwright: hace login, envía barcodes por el formulario y captura respuestas de red |
| `inciapi_dom_scraper.py` | Variante DOM: extrae los datos renderados en pantalla en lugar de interceptar la red |
| `inci_monitor_sandbox.py` | Monitor en tiempo real equivalente al de `pantalla inicio/` |

```bash
# Requiere Playwright instalado
pip install playwright && playwright install chromium
python scripts/scraping/entorno\ de\ prueba/inciapi_scraper_sandbox.py
```

#### `network sniffer/`

Scripts de exploración usados durante la fase de ingeniería inversa de la API
de inciapi.com.

| Archivo | Rol |
|---|---|
| `sniffer.py` | Playwright con interceptación de red: captura peticiones y respuestas HTTP para identificar endpoints privados y formato de datos |
| `sniffer_page.html` | Dump de la página del playground capturada durante la exploración |
| `sniffer_resultado.json` | Ejemplo de respuesta capturada con `overallSafetyScore` y `skinTypeCompatibility` |

#### Archivos en raíz de `scraping/`

| Archivo | Rol |
|---|---|
| `fusionar_y_guardar.py` | Fusiona los `.jsonl` de `pantalla inicio/` y `entorno de prueba/` en uno solo. Usa `deep_merge` para consolidar duplicados por barcode, priorizando INCIDecoder sobre OBF y valores más completos sobre nulos. |
| `analisis.py` | Análisis de los resultados del scraping: genera 3 reportes Markdown con métricas de éxito/error, estructura de datos y estadísticas de seguridad comparando ambas fuentes. |

```bash
# Fusionar resultados de ambas fuentes
python scripts/scraping/fusionar_y_guardar.py

# Generar reportes de análisis
python scripts/scraping/analisis.py
```
