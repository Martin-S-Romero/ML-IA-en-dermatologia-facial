# SkinAI — Technical Project Audit

> Facial Skin Condition Analysis Platform · AI-Powered · Privacy-First · Academic MVP

---

## 1. Project Overview

SkinAI es una plataforma web académica (tesis) que aplica inteligencia artificial para clasificar condiciones cutáneas faciales a partir de una fotografía, y generar recomendaciones de rutina de cuidado personalizadas. Se construyó como MVP funcional para demostrar la viabilidad técnica de un sistema de apoyo diagnóstico no clínico, con énfasis en privacidad del usuario (GDPR) y ética médica — posicionando el sistema como herramienta informativa, no como sustituto de un dermatólogo.

| Field | Detail |
|---|---|
| **Name** | SkinAI |
| **Type** | Full-Stack Web Application (Thesis / Academic MVP) |
| **Domain** | Dermatology · AI-assisted diagnosis aid |
| **Purpose** | Automated facial skin condition classification + personalized skincare recommendations |
| **Users** | Patients, skincare users seeking non-clinical first assessment |
| **Compliance** | GDPR-aligned (explicit consent, right to deletion, data minimization) |
| **Deployment** | Docker Compose (local/cloud-agnostic) |

---

## 2. Architecture Summary

El sistema sigue una arquitectura de microservicios ligera con 5 contenedores Docker independientes. Esta separación existe por una razón técnica concreta: el procesamiento de IA es computacionalmente pesado y bloqueante, por lo que se aisló en un worker dedicado (Celery) que consume tareas de una cola Redis, evitando que el servidor API quede bloqueado mientras analiza imágenes. El frontend se sirve de manera independiente para permitir despliegue desacoplado y facilitar el desarrollo paralelo. PostgreSQL centraliza todos los datos persistentes, mientras Redis actúa únicamente como bus de mensajes efímero.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Docker Network: tesis-network                  │
│                                                                             │
│  ┌──────────────┐   HTTP/REST    ┌───────────────┐   Enqueue   ┌─────────┐ │
│  │   Frontend   │ ─────────────► │    Backend    │ ──────────► │  Redis  │ │
│  │   (Vite 3)   │ ◄───────────── │  (FastAPI)    │ ◄────────── │  Queue  │ │
│  │  Port: 3000  │   JSON / JWT   │  Port: 8000   │  Result     └────┬────┘ │
│  └──────────────┘                └───────┬───────┘             ┌────▼────┐ │
│                                          │ SQL                 │AI Worker│ │
│                                   ┌──────▼──────┐             │(Celery) │ │
│                                   │ PostgreSQL  │             └────┬────┘ │
│                                   │     DB      │                  │      │
│                                   │  Port: 5432 │ ◄────────────────┘      │
│                                   └─────────────┘                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

**5 containerized services:** `frontend` · `backend` · `ai_worker` · `db` · `redis`

El flujo de una petición pasa por los contenedores en este orden:

**① `frontend`** → **② `backend`** → **③ `redis`** → **④ `ai_worker`** → **⑤ `db`**

| # | Contenedor | Imagen base | Qué hace | Por qué existe separado |
|---|---|---|---|---|
| 1 | **frontend** | Node 18 + Vite | Es la interfaz del usuario. Sirve la SPA (HTML/JS/CSS) en el puerto 3000. El usuario interactúa aquí: se registra, sube su foto, ve resultados. Todas las acciones se traducen en peticiones HTTP hacia el backend. | Desacoplado del backend para que pueda servirse desde un CDN/Nginx en producción sin tocar el servidor API. En desarrollo corre con hot-reload para velocidad. |
| 2 | **backend** | python:3.10-slim | Es el portero del sistema. Corre FastAPI en el puerto 8000. Recibe cada petición del frontend: valida el token JWT, comprueba permisos, valida los datos de entrada (Pydantic), y decide qué hacer — responder directamente (consulta de historial) o encolar una tarea pesada (análisis de imagen). Corre `alembic upgrade head` al arrancar para mantener el schema de BD actualizado. | Es el único punto de entrada externo. No ejecuta IA — su trabajo es ser rápido y delegar. Separarlo del worker permite que responda en milisegundos mientras el análisis tarda segundos en otro proceso. |
| 3 | **redis** | redis:7-alpine | Es el buzón de tareas entre el backend y el worker. Cuando el backend recibe una imagen para analizar, deposita la tarea (con su ID y parámetros) en una cola Redis. El worker la recoge cuando está disponible. También guarda el resultado temporal de la tarea para que el backend pueda consultarlo. | Sin Redis, el backend tendría que esperar bloqueado a que el análisis termine, o abrir una conexión directa con el worker. Redis desacopla totalmente el productor (backend) del consumidor (worker). Es efímero — no guarda datos críticos, solo mensajes en tránsito. |
| 4 | **ai_worker** | python:3.10-slim | Es el cerebro del sistema. Proceso Celery que escucha la cola Redis continuamente. Al recibir una tarea: carga el modelo EfficientNet-B3 en memoria (una sola vez, como singleton), ejecuta la detección facial con MediaPipe, censura los ojos, extrae métricas por zona, corre la inferencia con TTA ×5, aplica los ajustes clínicos, y guarda el resultado completo en la base de datos. | El análisis IA es bloqueante y tarda varios segundos. Correr esto en el mismo proceso que la API congela el servidor para todos los usuarios. Al ser un contenedor separado puede escalarse añadiendo más réplicas (`concurrency=2` por worker) sin tocar la API. |
| 5 | **db** | postgres:15-alpine | Es la memoria permanente del sistema. PostgreSQL almacena todo lo que debe sobrevivir a un reinicio: usuarios, perfiles de piel, resultados de análisis (JSONB), rutinas, productos, consentimientos GDPR. Tanto el backend como el ai_worker leen y escriben aquí. Tiene health-check cada 5 segundos para que los otros servicios no arranquen hasta que esté lista. | Separar la BD en su propio contenedor garantiza que los datos persisten en el volumen `postgres_data` independientemente del ciclo de vida de la app. Permite hacer backups, actualizar la versión de Postgres o conectar herramientas externas sin tocar el código. |

---

## 3. Technology Stack

Las tecnologías fueron seleccionadas priorizando madurez del ecosistema, soporte para deep learning en CPU, y velocidad de desarrollo académico. FastAPI se eligió sobre Flask/Django por su validación automática con Pydantic y su soporte nativo para operaciones asíncronas. PyTorch con timm provee acceso directo a EfficientNet-B3 preentrenado. Tailwind CSS y Vanilla JS eliminan la complejidad de un framework frontend (React/Vue), lo cual es adecuado para una SPA académica de alcance definido. Docker Compose permite reproducibilidad total del entorno en cualquier máquina.

| Layer | Technology | Version |
|---|---|---|
| **Frontend** | Vanilla JavaScript + Vite + Tailwind CSS | ES2022 / v5 / v3 |
| **Charts** | Chart.js | v4 |
| **Backend API** | FastAPI + Uvicorn | Python 3.10 |
| **ORM** | SQLAlchemy + Alembic | v2 / v1.12 |
| **Database** | PostgreSQL | v15 |
| **Auth** | JWT (HS256) + Argon2 password hashing | — |
| **Task Queue** | Celery + Redis | v7 |
| **Deep Learning** | PyTorch + timm (EfficientNet-B3) | CPU build |
| **Computer Vision** | OpenCV + MediaPipe FaceMesh | v4.8 / v0.10 |
| **Image I/O** | Pillow + pillow-heif | HEIC support |
| **Rate Limiting** | SlowAPI | — |
| **Containerization** | Docker Compose | v3.8 |

---

## 4. Backend Structure

El backend aplica separación de capas estricta: la capa `api/` solo enruta y valida, `core/` contiene toda la lógica de negocio e IA, `db_scheme/` define el modelo de datos, y `worker/` gestiona tareas asíncronas. Esta separación facilita el mantenimiento, las pruebas unitarias por capa, y permite escalar el worker de IA de forma independiente al servidor API. El directorio `models/` guarda los pesos del modelo ML fuera del código fuente, y `scraper/` es un componente offline para poblar el catálogo de productos.

```
backend/
├── app/
│   ├── api/            # REST endpoints (auth, users, analysis, routines, products)
│   ├── core/           # Business logic, AI pipeline, security, Celery
│   ├── db_scheme/      # SQLAlchemy ORM models (11 tables)
│   ├── worker/         # Celery async tasks
│   ├── main.py         # FastAPI app, middleware, routers
│   └── schemas.py      # Pydantic request/response models
├── models/             # ML model weights + label map
├── scraper/            # Product data scraper (INCIDecoder)
└── alembic/            # DB migration scripts
```

### API Surface (~30 endpoints)

| Router | Prefix | Key Endpoints |
|---|---|---|
| Auth | `/api/auth` | register, login, forgot-password, reset-password |
| Users | `/api/users` | profile CRUD, change-password, delete account |
| Analysis | `/api/analysis` | upload image, poll status, full result, image serve, history |
| Routines | `/api/routines` | active routine, create routine |
| Products | `/api/products` | search, recommended, detail |

---

## 5. Frontend Structure

El frontend es una SPA (Single Page Application) construida sin framework, donde el router.js gestiona la navegación cliente-lado inyectando vistas HTML en el div `#app`. Esta decisión evita la sobrecarga de un bundler complejo y mantiene el código accesible para un equipo académico. Cada página tiene su script de inicialización independiente (`initDashboard`, `initCapture`, etc.), lo que reduce acoplamiento. El estado de sesión vive en `localStorage` (token JWT + bandera de perfil completo), y las rutas protegidas redirigen automáticamente si el usuario no está autenticado o no ha completado su perfil de piel.

```
frontend/src/
├── pages/          # 10 HTML views (SPA — injected into #app div)
│   ├── landing, auth, profile, capture
│   ├── analyzing, dashboard, account
│   └── routine-check, routine-change, reset-password
└── scripts/        # 10 JavaScript modules
    ├── router.js   # SPA navigation + auth guards
    ├── main.js     # Bootstrap, global functions
    ├── auth.js, profile.js, capture.js
    ├── analyzing.js, dashboard.js, account.js
    ├── charts.js   # Chart.js visualizations
    └── ui.js       # Shared UI helpers
```

**Architecture:** Single Page Application (SPA) — no framework  
**Routing:** Client-side, auth-guarded, profile-required guards  
**State:** `localStorage` (JWT token, user object, profile completeness flag)

---

## 6. Database Schema (11 Tables)

El modelo de datos está diseñado alrededor del usuario como entidad central, con cascadas de eliminación que garantizan que borrar una cuenta elimina todos sus datos (análisis, rutinas, perfil, consentimientos). La tabla `analyses` almacena el resultado completo del modelo IA como JSONB, lo que permite evolucionar el esquema de salida del modelo sin migraciones de columnas. El catálogo de productos (`products`, `ingredients`, `product_ingredients`) fue diseñado para datos scrapeados de INCIDecoder y permite recomendaciones basadas en ingredientes INCI. La tabla `consents` existe exclusivamente para cumplimiento GDPR, registrando cada acción de consentimiento con IP y timestamp.

```
users ──────────────────────────────────────┐
 ├── skin_profiles (1:1)                    │
 ├── analyses (1:N)                         │
 ├── routines (1:N)                         │
 │    └── routine_steps (1:N)               │
 ├── skin_checks (1:N)                      │
 └── consents (1:N)  ← GDPR audit trail    │
                                            │
products ──────────────────────────────────┤
 └── product_ingredients (N:M)             │
      └── ingredients                       │
                                            │
reset_tokens (1:N → users) ────────────────┘
```

| Table | Purpose |
|---|---|
| `users` | Accounts, credentials, GDPR flags |
| `skin_profiles` | Fitzpatrick, skin type, conditions, allergies, location |
| `analyses` | AI result (JSONB), image filenames, status, confidence |
| `routines` / `routine_steps` | AI-generated skincare routines |
| `skin_checks` | Daily routine adherence log |
| `products` / `ingredients` | Scraped product catalog with INCI ingredients |
| `consents` | Granular GDPR consent events with IP + timestamp |
| `reset_tokens` | Time-limited password reset tokens |

**Key DB features:** JSONB columns for flexible result storage · Row-Level Security context · Cascade deletes on user removal · Indexed FKs

---

## 7. AI / ML Pipeline

El pipeline de IA combina inferencia de deep learning con un sistema de ajustes clínicos por reglas, porque el modelo de red neuronal sólo produce probabilidades brutas basadas en píxeles — no conoce el historial del paciente ni puede interpretar la distribución espacial de síntomas en zonas faciales. Los ajustes clínicos en capas (zonal → perfil → historial) transforman esas probabilidades brutas en una clasificación clínicamente coherente. EfficientNet-B3 fue elegido por su equilibrio entre precisión y tamaño de modelo (apto para CPU). Test-Time Augmentation (TTA) con 5 pases reduce la varianza de predicción ante cambios de iluminación o ángulo de la foto, aumentando robustez sin reentrenar el modelo.

### Model

| Property | Value |
|---|---|
| **Architecture** | EfficientNet-B3 (timm) |
| **Input** | 300×300 RGB, ImageNet normalization |
| **Head** | BatchNorm → Dropout(0.3) → Dense(256) → ReLU → Dropout(0.2) → Dense(8) |
| **Output** | 8-class skin condition probability vector |
| **Runtime** | PyTorch CPU (GPU-ready) |

### 8 Condition Classes

```
0: acne-comedonal          4: perioral-dermatitis
1: acne-excoriated         5: rosacea-etr (erythematotelangiectasic)
2: acne-inflammatory       6: rosacea-inflammatory
3: healthy-skin            7: seborrheic-dermatitis
```

### Inference Steps

```
Image Input
    │
    ▼
[1] Preprocess → Resize 300×300 · Normalize (ImageNet μ/σ)
    │
    ▼
[2] TTA (Test-Time Augmentation) × 5 passes
    │   Flip · Rotation ±10° · Random crop (0.93–1.0) · Brightness jitter ±10%
    │   → Average 6 softmax vectors
    │
    ▼
[3] Base Probabilities (8 classes)
    │
    ▼
[4] Zonal Adjustments (MediaPipe FaceMesh → 13 facial regions)
    │   Erythema · Comedones · Scales per zone
    │   Boost/penalize conditions by zonal evidence
    │
    ▼
[5] Clinical Profile Adjustments
    │   Fitzpatrick · Skin type · Age · Sex · History · AC exposure
    │
    ▼
[6] Continuity Adjustment (previous diagnosis weight)
    │
    ▼
[7] Final Classification → Top-N (≥ 10% confidence threshold)
    │
    ▼
Result: condition · confidence · severity · zones · delta vs. previous
```

### 13 Facial Zones (MediaPipe FaceMesh 468 landmarks)

| Zone Group | Regions |
|---|---|
| **Display (5)** | Forehead · Left cheek · Right cheek · Nose · Chin |
| **Diagnostic (8)** | Eyebrows (L/R) · Jaw (L/R) · Nasal laterals · Perioral · T-zone composite |

### Zonal Metrics per Region

| Metric | Method | Weight in Severity |
|---|---|---|
| **Erythema** | R/(G+ε) ratio | 50% |
| **Comedones** | Adaptive threshold dark-pixel ratio | 30% |
| **Scales** | Laplacian variance / 300 | 20% |

### Clinical Boost / Penalty Matrix (selection)

| Condition | Trigger | Multiplier |
|---|---|---|
| Rosacea-ETR | Bilateral symmetric cheek erythema | ×1.4 |
| Acné comedonal | High comedones in T-zone | ×1.3 |
| Perioral dermatitis | Concentrated chin erythema | ×1.5 |
| Seborrheic dermatitis | T-zone + eyebrow scales | ×1.3+ |
| Healthy skin | All zones < 0.06 erythema | ×1.5 |
| Rosacea (any) | Scales present → penalize | ×(1 − 0.3×scales) |

---

## 8. Image Processing Pipeline

Este módulo tiene dos responsabilidades distintas: proteger la identidad del usuario (censura de ojos) y extraer métricas clínicas por zona facial. El censado de ojos se realiza antes de almacenar la imagen, cumpliendo con el principio de minimización de datos GDPR. Crítico: se hace una copia del frame sin censurar antes de aplicar el censado, porque las métricas de eritema, comedones y escamas deben extraerse de la imagen original — de lo contrario las zonas de los ojos distorsionarían los valores. La imagen original se elimina tras el procesamiento; sólo la versión censurada se guarda. Si no se detecta ningún rostro, el análisis se aborta y no se persiste nada.

**Module:** `face_censor_v3.py · FaceCensor`

```
Upload (JPEG/PNG/WebP/BMP/TIFF/HEIC · max 10 MB)
    │
    ▼
Validate → Min resolution 430×360 px
    │
    ▼
MediaPipe FaceMesh → Detect face (max 1, confidence ≥ 0.5)
    │
    ├── No face → Reject · Delete file · Abort analysis
    │
    ▼
Clone frame (uncensored copy for metric extraction)
    │
    ▼
Censor eyes:
    ├── blur     → Gaussian kernel (σ=30)
    ├── black    → Fill ROI with [0,0,0]
    └── pixelate → Downsample → Upsample (nearest neighbor)
    │
    ▼
Extract 13-zone metrics from uncensored clone
    │
    ▼
Save censored image (JPEG q=92)
    │
    ▼
Delete original (GDPR data minimization)
```

---

## 9. Async Processing Flow

El análisis de una imagen tarda varios segundos (detección facial + inferencia TTA + ajustes), tiempo en el que un servidor API sincrónico quedaría bloqueado e incapaz de atender otras peticiones. La solución es el patrón productor-consumidor: el endpoint `/upload` encola la tarea en Redis y responde inmediatamente con un `analysis_id`; el AI Worker la procesa de forma independiente; el frontend hace polling cada 2 segundos contra `/status` hasta recibir `completed`. Este diseño permite escalar el número de workers de IA sin tocar el servidor API, y soporta múltiples usuarios simultáneos sin degradación de respuesta.

```
User (Browser)          Backend (FastAPI)           Redis           AI Worker (Celery)         PostgreSQL
     │                        │                       │                    │                       │
     │── POST /upload ────────►│                       │                    │                       │
     │                        │── INSERT analysis ────────────────────────────────────────────────►│
     │                        │   status="processing"                      │                       │
     │◄── {analysis_id} ──────│                       │                    │                       │
     │                        │── enqueue task ───────►│                   │                       │
     │                        │                       │── dispatch ────────►│                      │
     │── GET /status (poll) ──►│                       │                    │── FaceCensor         │
     │◄── {processing} ───────│                       │                    │── ai_runner           │
     │                        │                       │                    │── adjust + result     │
     │── GET /status (poll) ──►│                       │                    │                       │
     │                        │                       │                    │── UPDATE analysis ────►│
     │                        │                       │                    │   status="completed"  │
     │◄── {completed} ────────│◄──────────────────────────────────────────────────────────────────│
     │                        │                       │                    │                       │
     │── GET /{id} ───────────►│── SELECT analysis ────────────────────────────────────────────────►│
     │◄── Full Result ─────────│◄──────────────────────────────────────────────────────────────────│
```

**Polling interval:** 2 seconds · **Max retries on failure:** 3 (exponential backoff)

---

## 10. Security Implementation

La seguridad se implementó en múltiples capas porque ninguna medida individual es suficiente para un sistema que maneja imágenes faciales y datos médicos sensibles. Argon2 se usa en lugar de bcrypt porque es el ganador del Password Hashing Competition y es más resistente a ataques de hardware especializado. Row-Level Security en PostgreSQL garantiza que, incluso si hay un bug en la lógica de la API, una consulta SQL nunca devolverá datos de otro usuario. Los headers HTTP defensivos (HSTS, CSP, X-Frame-Options) protegen contra ataques de cliente como clickjacking y XSS. La eliminación de la imagen original tras el análisis no es opcional — es la implementación técnica del principio GDPR de minimización de datos.

| Layer | Mechanism |
|---|---|
| **Passwords** | Argon2 hashing (passlib) |
| **Auth tokens** | JWT HS256 · 60-min expiry · localStorage |
| **API protection** | OAuth2PasswordBearer on all protected routes |
| **Rate limiting** | 20 req/min on auth endpoints (SlowAPI) |
| **Input validation** | File type whitelist · 10 MB cap · Min resolution · Pydantic schemas |
| **Data isolation** | PostgreSQL Row-Level Security context per user session |
| **HTTP headers** | HSTS · X-Frame-Options: DENY · CSP · XSS-Protection · nosniff |
| **GDPR** | Granular consent · Right to deletion · Original image deleted post-processing |
| **Cascade delete** | `DELETE /api/users/me` removes: analyses · routines · profile · consents |

---

## 11. End-to-End Data Flow

Esta sección describe el recorrido completo de un análisis desde que el usuario toma la foto hasta que ve el resultado en el dashboard. Cada paso existe por una razón funcional o de cumplimiento: la detección facial temprana (paso 3) evita almacenar y procesar imágenes sin rostro; la extracción de métricas zonales (paso 4) alimenta los ajustes clínicos que le dan contexto espacial al modelo; la recuperación del perfil y análisis anterior (paso 5) permite personalización y coherencia longitudinal. El resultado se almacena como JSONB completo (paso 9) para que el dashboard pueda mostrar cualquier nivel de detalle sin hacer nuevas inferencias.

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                      COMPLETE FACIAL ANALYSIS FLOW                             │
│                                                                                │
│  [1] USER INPUT                                                                │
│      User uploads photo (gallery or camera) via capture.html                  │
│                                                                                │
│  [2] UPLOAD & QUEUE                                                            │
│      POST /api/analysis/upload → Backend stores file → Celery task enqueued   │
│      Frontend receives analysis_id · Navigates to analyzing.html              │
│                                                                                │
│  [3] FACE DETECTION & CENSORING (AI Worker)                                   │
│      MediaPipe FaceMesh detects face · Eyes censored (blur/black/pixelate)    │
│      No face → abort · Original file deleted                                  │
│                                                                                │
│  [4] ZONE METRIC EXTRACTION                                                    │
│      13 facial regions → Erythema · Comedones · Scales per zone               │
│                                                                                │
│  [5] PROFILE RETRIEVAL                                                         │
│      Fetch user skin profile (Fitzpatrick, conditions, age, skin type)        │
│      Fetch previous analysis (for continuity adjustment)                      │
│                                                                                │
│  [6] ML INFERENCE (EfficientNet-B3)                                            │
│      Preprocess → Base prediction → TTA ×5 → Average probabilities           │
│                                                                                │
│  [7] CLINICAL ADJUSTMENTS                                                      │
│      Zonal evidence boosts/penalties · Profile adjustments · History weight   │
│      → Final ranked condition list                                             │
│                                                                                │
│  [8] RESULT ASSEMBLY                                                           │
│      Top-N conditions (≥10% confidence) · Severity score · Delta vs. prior   │
│      Affected zones · Diagnostic notes · Model version / TTA metadata        │
│                                                                                │
│  [9] STORAGE                                                                   │
│      analyses.result (JSONB) · status="completed" · top1_label + confidence  │
│                                                                                │
│  [10] RESULT DELIVERY                                                          │
│       Frontend polls → Navigates to dashboard.html                            │
│       Displays: condition · confidence · severity · zone map · history chart  │
│                                                                                │
│  [11] ROUTINE GENERATION                                                       │
│       AI-suggested skincare routine steps stored in routines + routine_steps  │
│       Matched to product catalog (ingredients, suitability)                   │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 12. Complete Process Flow Diagram

Diagrama visual del proceso completo de análisis facial, desde la captura de imagen hasta la generación de resultados y rutina. Se lee de arriba hacia abajo: primero validación e integridad de la imagen, luego privacidad (censura), extracción de señales clínicas visuales, inferencia del modelo ML, tres capas de ajuste contextual, y finalmente almacenamiento y presentación. El bloque de "Clinical Adjustments" es el diferenciador clave del sistema respecto a un clasificador de imágenes estándar: incorpora conocimiento dermatológico que el modelo solo no puede aprender.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    SKINAI — FACIAL ANALYSIS PROCESS                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ┌──────────┐     ┌──────────────┐     ┌────────────────┐                  ║
║  │  CAPTURE │     │   VALIDATE   │     │  FACE DETECT   │                  ║
║  │          │────►│ Type · Size  │────►│  MediaPipe     │                  ║
║  │ Gallery  │     │ Max 10 MB    │     │  FaceMesh      │                  ║
║  │ Camera   │     │ Min 430×360  │     │  468 landmarks │                  ║
║  └──────────┘     └──────────────┘     └───────┬────────┘                  ║
║                                                │                            ║
║                                     ┌──────────▼──────────┐                ║
║                                     │  No face detected?  │                ║
║                                     │  → Reject & abort   │                ║
║                                     └──────────┬──────────┘                ║
║                                                │ Face found                 ║
║                                     ┌──────────▼──────────┐                ║
║  ┌────────────────────────┐         │  EYE CENSORING      │                ║
║  │  ZONE METRIC EXTRACT   │◄────────│  blur / black /     │                ║
║  │                        │         │  pixelate           │                ║
║  │  13 facial regions     │         └─────────────────────┘                ║
║  │  · Erythema (R/G)      │                                                ║
║  │  · Comedones (thresh)  │                                                ║
║  │  · Scales (Laplacian)  │                                                ║
║  └──────────┬─────────────┘                                                ║
║             │                                                               ║
║  ┌──────────▼─────────────────────────────────────────────────┐            ║
║  │               ML INFERENCE (EfficientNet-B3)               │            ║
║  │                                                            │            ║
║  │  Input 300×300 → Backbone → Custom Head (256-D) → 8 probs │            ║
║  │                                                            │            ║
║  │  TTA ×5: flip · rotate ±10° · crop · brightness jitter    │            ║
║  │          ↓ Average 6 predictions                          │            ║
║  └──────────┬─────────────────────────────────────────────────┘            ║
║             │                                                               ║
║  ┌──────────▼─────────────────────────────────────────────────┐            ║
║  │             CLINICAL ADJUSTMENTS (3 layers)                │            ║
║  │                                                            │            ║
║  │  [A] Zonal Evidence  → boost/penalize per region finding   │            ║
║  │  [B] User Profile    → Fitzpatrick · age · skin type · sex │            ║
║  │  [C] History Weight  → continuity from previous analysis   │            ║
║  └──────────┬─────────────────────────────────────────────────┘            ║
║             │                                                               ║
║  ┌──────────▼─────────────────────────────────────────────────┐            ║
║  │                    RESULT ASSEMBLY                         │            ║
║  │                                                            │            ║
║  │  · Top-N conditions (≥ 10% confidence)                    │            ║
║  │  · Severity score (0–1) · Worst zone                      │            ║
║  │  · Delta vs. previous (trend: improving/stable/worsening) │            ║
║  │  · Zone map (5 display + 8 diagnostic)                    │            ║
║  └──────────┬─────────────────────────────────────────────────┘            ║
║             │                                                               ║
║    ┌────────▼─────────┐    ┌────────────────────┐    ┌──────────────────┐  ║
║    │  STORE IN DB     │    │  ROUTINE GENERATOR  │    │  DASHBOARD VIEW  │  ║
║    │  analyses.result │───►│  routine_steps      │───►│  Charts · Zones  │  ║
║    │  (JSONB)         │    │  Product matching   │    │  History · PDF   │  ║
║    └──────────────────┘    └────────────────────┘    └──────────────────┘  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## 13. Frontend User Journey

El flujo de usuario está diseñado con guardas progresivas: no es posible llegar al dashboard sin estar autenticado, y no es posible hacer un análisis sin haber completado el perfil de piel. Esto no es una restricción arbitraria — el perfil (Fitzpatrick, tipo de piel, condiciones previas) es entrada obligatoria para los ajustes clínicos del modelo IA. Si el usuario intenta saltarse el perfil, el router lo redirige automáticamente. La pantalla de "Analyzing" existe porque el análisis tarda 5–15 segundos; mostrar una animación por pasos reduce la percepción de espera y comunica que algo real está ocurriendo en el servidor.

```
Landing ──► Register/Login ──► Skin Profile Setup
                                       │
                                       ▼
                               Image Capture / Upload
                                       │
                                       ▼
                            Analyzing (progress animation)
                            ← polls /status every 2 sec →
                                       │
                                       ▼
                    ┌──────────────────────────────────────┐
                    │           Dashboard                   │
                    │  ┌──────────┬──────────┬──────────┐  │
                    │  │Dashboard │ History  │  Charts  │  │
                    │  │ (latest) │ (all)    │ (trends) │  │
                    │  └──────────┴──────────┴──────────┘  │
                    │           + Routine tab               │
                    └──────────────────────────────────────┘
                                       │
                              Account Settings
                         (change password / delete account)
```

---

## 14. External Services & Tools

El sistema minimiza dependencias de servicios externos para mantener control total sobre los datos del usuario y reducir costos operativos. PostgreSQL y Redis se ejecutan en contenedores propios — no se usan servicios en la nube como RDS o ElastiCache. MediaPipe corre en-proceso (no es una API externa), lo que garantiza que las imágenes nunca salen del servidor. Gmail SMTP es opcional porque el reset de contraseña por email no es crítico para el flujo principal. INCIDecoder sólo se usa durante el setup inicial del catálogo de productos mediante el scraper offline.

| Service | Purpose | Required? |
|---|---|---|
| **PostgreSQL 15** | Primary relational database | Yes |
| **Redis 7** | Celery message broker + result backend | Yes |
| **MediaPipe FaceMesh** | 468-landmark face detection in-process | Yes |
| **Gmail SMTP** | Password reset email delivery | Optional |
| **INCIDecoder** | Product/ingredient data source (scraper) | Setup only |
| **Docker Hub** | Base images (python:3.10-slim, postgres:15, redis:7) | Dev/Deploy |

---

## 15. Key Dependencies Summary

Cada librería cumple un rol específico y no existe redundancia entre ellas. En el backend, la combinación `torch + timm` provee el modelo preentrenado y su infraestructura de inferencia; `mediapipe` hace la detección de puntos faciales (468 landmarks) con alta precisión en CPU; `opencv` procesa los píxeles para censura y métricas; `celery + redis` desacoplan el procesamiento pesado del servidor API. En el frontend, la decisión de no usar React o Vue es deliberada: la aplicación tiene flujos lineales simples que no requieren gestión de estado reactivo, y Vanilla JS con Vite es suficiente y más rápido de construir para un MVP.

### Backend (Python)
```
fastapi · uvicorn            # Web framework + ASGI server
sqlalchemy · alembic         # ORM + database migrations
psycopg2-binary              # PostgreSQL driver
passlib[argon2]              # Password hashing
python-jose[cryptography]    # JWT tokens
python-multipart             # File upload handling
slowapi                      # Rate limiting
celery · redis               # Async task queue
torch · torchvision · timm   # Deep learning (EfficientNet-B3)
opencv-python-headless       # Image processing
mediapipe                    # Face landmark detection
Pillow · pillow-heif         # Image I/O (incl. HEIC)
numpy                        # Numerical operations
httpx · beautifulsoup4 · lxml# Product web scraper
email-validator              # Input validation
```

### Frontend (JavaScript)
```
vite          # Build tool + dev server
tailwindcss   # Utility-first CSS framework
postcss       # CSS processing
chart.js      # Data visualization (lazy-loaded)
```

---

## 16. System Metrics at a Glance

Resumen cuantitativo del sistema para dimensionar su alcance técnico de forma rápida. Estos números son relevantes para evaluar complejidad: 30 endpoints de API indican un sistema completo pero no sobredimensionado; 13 zonas faciales analizadas muestran la granularidad clínica del análisis; 6 pases de inferencia (TTA) indican un compromiso consciente entre precisión y costo computacional; las 4 categorías de consentimiento GDPR reflejan una implementación seria de privacidad diferenciada por tipo de uso de datos.

| Metric | Value |
|---|---|
| Backend Python modules | ~22 |
| Frontend JS modules | ~10 |
| HTML pages (SPA views) | ~10 |
| REST API endpoints | ~30 |
| Database tables | 11 |
| ML condition classes | 8 |
| Facial zones analyzed | 13 |
| TTA augmentation passes | 5 (+1 base = 6) |
| Container services | 5 |
| Celery worker concurrency | 2 |
| JWT expiry | 60 minutes |
| Auth rate limit | 20 req/min |
| Max image upload | 10 MB |
| Min image resolution | 430 × 360 px |
| Censoring modes | 3 (blur / black / pixelate) |
| GDPR consent types | 4 (gdpr, data processing, image storage, AI analysis) |

---

## 17. Module Responsibilities Summary

Cada módulo tiene una responsabilidad única y no solapada (principio de responsabilidad única). La separación entre `ai_runner.py` (inferencia pura) y `skinai_analizar_v3.py` (ajustes clínicos + ensamblado de resultado) es deliberada: permite reemplazar el modelo ML sin tocar la lógica clínica, y viceversa. `skinai_config.py` centraliza todos los umbrales y multiplicadores para que los ajustes clínicos sean auditables y modificables sin tocar código de lógica. El módulo `face_censor_v3.py` combina censura y extracción de métricas porque ambas operaciones requieren los mismos landmarks faciales de MediaPipe — ejecutarlos una sola vez es más eficiente.

| Module | File(s) | Responsibility |
|---|---|---|
| **API Layer** | `api/analysis.py` `api/users.py` `api/auth.py` | Request routing, validation, auth enforcement |
| **ML Inference** | `core/ai_runner.py` | Model loading (singleton), TTA, probability averaging |
| **Clinical Logic** | `core/skinai_analizar_v3.py` | Profile/zone/history adjustments, result assembly |
| **Face Processing** | `core/face_censor_v3.py` | Face detection, eye censoring, zone metric extraction |
| **Config** | `core/skinai_config.py` | All thresholds, boost factors, model hyperparameters |
| **Task Queue** | `worker/tasks.py` | Async image-processing orchestration |
| **ORM Models** | `db_scheme/*.py` | Database table definitions + relationships |
| **Schemas** | `schemas.py` | Pydantic request/response validation |
| **SPA Router** | `scripts/router.js` | Client-side navigation, auth/profile guards |
| **Dashboard** | `scripts/dashboard.js` | Result display, history, routine rendering |
| **Visualizations** | `scripts/charts.js` | Trend charts (Chart.js) |
| **Analysis UI** | `scripts/analyzing.js` | Progress animation, status polling |

---

## 18. GDPR & Ethics Compliance

El cumplimiento GDPR no es una capa añadida al final — está embebido en la arquitectura del sistema. Las imágenes faciales son datos biométricos de categoría especial bajo GDPR, lo que exige consentimiento explícito diferenciado por tipo de tratamiento (almacenamiento vs. análisis vs. procesamiento). La eliminación automática de la imagen original tras el análisis es la implementación técnica del principio de minimización de datos: el sistema sólo retiene lo necesario (imagen censurada + resultado JSON). El endpoint de eliminación de cuenta que hace cascada sobre todos los datos es la implementación del derecho al olvido. Posicionar el sistema como herramienta informativa (no diagnóstico médico) es una decisión ética y legal que delimita la responsabilidad del sistema.

- **Consent:** 4 granular checkboxes at registration (data processing · image storage · AI analysis · general GDPR)
- **Data minimization:** Original images deleted immediately after AI processing
- **Right to deletion:** Single endpoint cascades deletion of all user data
- **Audit trail:** `consents` table records IP + timestamp per consent event
- **Disclaimer:** System positioned as informational aid, not medical diagnosis
- **Transparency:** T&C modal with legal disclaimers visible throughout app

---

*Audit generated: 2026-06-09 · Branch: Phase7-8 · Model: EfficientNet-B3 v3 · SkinAI MVP*
