# Documentación Técnica del Sistema — SkinAI
## Plataforma Web de Análisis Cutáneo Asistido por Inteligencia Artificial

> **Contexto:** Proyecto de tesis — Ingeniería de Software  
> **Rama de referencia:** `Phase7-8` (estado más avanzado del sistema)  
> **Fecha de documentación:** Abril 2026

---

## 1. Descripción General del Sistema

### 1.1 Propósito del Sistema

SkinAI es una plataforma web que permite a los usuarios subir fotografías de su rostro para obtener un **análisis visual de posibles afecciones cutáneas** — principalmente acné y rosácea — y recibir **recomendaciones de ingredientes cosméticos** adaptadas a su perfil de piel. El sistema está orientado al cuidado personal informado, no al diagnóstico médico.

El proyecto surge de la necesidad de democratizar el acceso a orientación dermatológica básica, utilizando técnicas de visión por computador e inteligencia artificial para procesar imágenes faciales de forma automatizada, segura y respetuosa con la privacidad del usuario.

### 1.2 Problema que Resuelve

El acceso a consultas dermatológicas es limitado por costo, disponibilidad geográfica y tiempo de espera. Muchos usuarios desconocen el tipo de piel que tienen, qué productos son adecuados para su condición, o si ciertas afecciones visibles en su rostro requieren atención especializada. SkinAI actúa como una herramienta de primer contacto: analiza la imagen, identifica patrones visuales y traduce esa información en recomendaciones de rutina de cuidado, usando lenguaje accesible y no clínico.

### 1.3 Flujo General de Funcionamiento

El flujo completo del sistema, de inicio a fin, es el siguiente:

```
1. El usuario accede a la plataforma y se registra (nombre, email, contraseña, consentimiento GDPR)
2. Completa su perfil de piel (edad, tipo de piel, fototipo Fitzpatrick, condiciones, alergias)
3. Sube una fotografía de su rostro desde la pantalla de captura
4. El backend valida la imagen (formato, tamaño, integridad)
5. Se lanza un proceso en segundo plano que:
   a. Detecta el rostro con MediaPipe FaceMesh
   b. Aplica censura sobre ojos y boca (privacidad)
   c. Guarda la imagen censurada (nunca la original)
   d. Actualiza el estado del análisis en la base de datos
6. El frontend hace polling del estado hasta que el análisis finaliza
7. El usuario visualiza los resultados en el dashboard:
   - Imagen censurada con zonas marcadas
   - Diagnóstico (tipo, severidad, confianza del modelo)
   - Rutina de productos personalizada AM/PM
   - Historial de análisis anteriores con gráficas comparativas
8. El usuario puede exportar el reporte en PDF
```

---

## 2. Arquitectura del Sistema

### 2.1 Tipo de Arquitectura

El sistema adopta una **arquitectura modular basada en contenedores**, organizada como cliente-servidor con separación lógica de responsabilidades. Aunque no es una arquitectura de microservicios pura, cada componente se ejecuta en su propio contenedor Docker y puede evolucionar hacia microservicios independientes. Esta decisión responde al principio de **simplicidad progresiva**: construir un MVP funcional y escalarlo gradualmente.

### 2.2 Diagrama Lógico de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENTE                              │
│   Navegador web — HTML + Vite + Tailwind CSS                │
│   Puerto 3000                                               │
│   SPA con router propio, JWT en localStorage                │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST (JSON)
                           │ Authorization: Bearer <JWT>
┌──────────────────────────▼──────────────────────────────────┐
│                    API GATEWAY / BACKEND                    │
│   FastAPI (Python) — Puerto 8000                            │
│   /api/auth/   /api/users/   /api/analysis/                 │
│   /api/routines/   /api/products/                           │
│   Rate Limiting · CORS · JWT · Logs · BackgroundTasks       │
└──────┬─────────────────────────┬───────────────────────────┘
       │                         │
       ▼                         ▼
┌─────────────┐       ┌──────────────────────────┐
│  PostgreSQL │       │  Sistema de Archivos      │
│  Puerto 5432│       │  /app/uploads  (originales│
│  Base de    │       │  /app/processed (censuradas│
│  datos SQL  │       │  /app/logs     (logs JSON) │
└─────────────┘       └──────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│          Módulo de IA / Visión por Computador │
│  OpenCV + MediaPipe FaceMesh                  │
│  Censura facial (blur, black, pixelate)       │
│  [Futuro] Modelos ONNX para análisis cutáneo  │
└──────────────────────────────────────────────┘
```

Todos los componentes se orquestan dentro de una **red Docker interna** (`tesis-network`), lo que garantiza aislamiento y comunicación segura entre servicios.

### 2.3 Comunicación entre Servicios

- **Frontend → Backend:** HTTP/REST a través del puerto 8000. El frontend envía peticiones con el token JWT en la cabecera `Authorization: Bearer <token>`. Todas las respuestas son JSON.
- **Backend → Base de datos:** SQLAlchemy ORM sobre TCP/IP interno de Docker. La cadena de conexión se inyecta como variable de entorno `DATABASE_URL`.
- **Backend → Sistema de archivos:** El módulo de procesamiento escribe directamente en volúmenes Docker montados (`/app/uploads`, `/app/processed`).
- **CORS:** El backend habilita explícitamente `http://localhost:3000` como origen permitido para el desarrollo local.

### 2.4 Contenedores Docker

El sistema define tres servicios en `docker-compose.yml`:

| Servicio | Imagen base | Puerto | Rol |
|----------|-------------|--------|-----|
| `backend` | `python:3.10-slim` | 8000 | API FastAPI + módulo IA |
| `db` | `postgres:15-alpine` | 5432 | Base de datos relacional |
| `frontend` | `node:18-alpine` | 3000 | Servidor Vite (desarrollo) |

El servicio `backend` depende del servicio `db` mediante un healthcheck (`pg_isready`) antes de iniciar, evitando errores de conexión en el arranque.

---

## 3. Frontend

### 3.1 Tecnologías Utilizadas

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| HTML5 | — | Estructura de páginas |
| Vite | 5.2 | Servidor de desarrollo y bundler |
| Tailwind CSS | 3.4 | Framework de estilos utility-first |
| PostCSS + Autoprefixer | — | Procesamiento de CSS |
| Chart.js | 4.4 | Gráficas del dashboard (CDN) |
| Google Fonts | — | Tipografías: Fraunces + DM Sans |
| JavaScript ES2022+ | — | Lógica de aplicación (módulos nativos) |

**Decisión de diseño:** Se optó por HTML/Vite/Tailwind en lugar de frameworks como React o Vue para mantener el proyecto comprensible, evitar dependencias innecesarias y conservar control total sobre el comportamiento de la aplicación. Vite aporta módulos ES nativos y recarga en caliente sin la complejidad de un framework de componentes.

### 3.2 Estructura del Proyecto Frontend

```
frontend/
├── index.html                  ← Shell HTML de la SPA
├── package.json                ← Dependencias y scripts npm
├── vite.config.js              ← Configuración del servidor Vite
├── tailwind.config.js          ← Design tokens del sistema
├── postcss.config.js           ← Pipeline de CSS
└── src/
    ├── main.js                 ← Bootstrap: carga componentes globales, registra funciones
    ├── styles/
    │   └── style.css           ← Tailwind base + componentes CSS personalizados
    ├── pages/                  ← Vistas inyectadas dinámicamente
    │   ├── landing.html        ← Página de inicio con hero y features
    │   ├── auth.html           ← Registro, login y recuperar contraseña
    │   ├── profile.html        ← Formulario de perfil de piel (6 secciones)
    │   ├── capture.html        ← Subida de foto con guías de captura
    │   ├── routine-check.html  ← ¿Seguiste tu rutina? (antes del análisis)
    │   ├── routine-change.html ← Actualización de productos de la rutina
    │   ├── analyzing.html      ← Pantalla de espera con 7 pasos animados
    │   ├── dashboard.html      ← Panel principal con tabs y sidebar
    │   └── account.html        ← Perfil y ajustes de cuenta del usuario
    ├── components/             ← Fragmentos HTML reutilizables globales
    │   ├── navbar.html         ← Barra de navegación superior
    │   ├── sidebar.html        ← Sidebar del dashboard (desktop)
    │   ├── drawer.html         ← Menú lateral deslizante (mobile)
    │   └── modals.html         ← Modales: términos y condiciones, exportar PDF
    └── scripts/
        ├── router.js           ← Navegación SPA, auth guards, helpers de sesión
        ├── auth.js             ← Registro, login, recuperar contraseña → API real
        ├── ui.js               ← Drawer, modales, estados de captura
        ├── dashboard.js        ← Tabs, historial de análisis, rutina, acordeones
        ├── profile.js          ← Formulario de perfil → API real
        ├── account.js          ← Cuenta y edición de campos → API real
        └── charts.js           ← 5 gráficas Chart.js (carga lazy)
```

### 3.3 Arquitectura de la SPA (Single Page Application)

El frontend funciona como una SPA sin framework: una sola página HTML (`index.html`) que contiene un contenedor vacío (`<main id="app">`). El sistema de navegación propio carga fragmentos HTML desde `/src/pages/` mediante `fetch()` y los inyecta en ese contenedor, sin recarga del navegador.

**Flujo de navegación:**
```
main.js (bootstrap)
  → Carga componentes globales (navbar, modals, drawer) en paralelo
  → Registra todas las funciones globales (window.go, window.logout, etc.)
  → Registra delegación de eventos para atributos [data-go]
  → Navega a la página inicial (landing)

router.js (navigate)
  → Verifica si el usuario tiene sesión activa (token en localStorage)
  → Si la página requiere sesión y no hay token → redirige a auth
  → Si hay sesión y va a landing/auth → redirige a dashboard
  → Carga el HTML de la página con fetch()
  → Lo inyecta en #app
  → Ejecuta la función de inicialización específica de esa página
```

**Auth guards:** Las páginas están clasificadas en `PROTECTED` (requieren token) y `PUBLIC_ONLY` (solo sin token). El router evalúa estas restricciones antes de cada navegación.

### 3.4 Sistema de Design Tokens

Tailwind CSS se configura con una paleta de colores semántica diseñada para una aplicación de ámbito médico-estético:

| Token | Color | Uso |
|-------|-------|-----|
| `forest` | `#233D30` | Color primario (botones, headers, sidebar) |
| `bark` | `#B89A72` | Acento dorado (logo, highlights) |
| `cream` | `#FAF8F3` | Fondo de tarjetas y formularios |
| `bg` | `#F0EDE6` | Fondo general de la aplicación |
| `rose` | `#C47060` | Estados de alerta, acné severo |
| `slate` | `#5A6474` | Texto secundario |
| `ok` | `#2E7D5A` | Estados positivos, mejoría |
| `warn` | `#D4942A` | Advertencias, severidad moderada |
| `ink` | `#181C24` | Texto principal |

Las tipografías son **Fraunces** (display/títulos, con variante itálica para énfasis) y **DM Sans** (cuerpo de texto), cargadas desde Google Fonts.

### 3.5 Manejo de Sesión

La autenticación en el frontend se gestiona mediante `localStorage`:

- `skinai_token`: JWT emitido por el backend, incluido en el header `Authorization: Bearer` de cada petición protegida.
- `skinai_user`: Objeto JSON con datos básicos del usuario (`id`, `email`, `full_name`) para poblar la interfaz sin necesidad de una petición adicional en cada navegación.

El perfil de piel extendido (edad, fototipo, tipo de piel, alergias) se obtiene mediante una llamada explícita a `GET /api/users/profile` al cargar la página de cuenta, garantizando datos frescos desde la base de datos.

### 3.6 Diseño Responsive

La interfaz está diseñada para funcionar en dispositivos móviles y escritorio. Se utilizan los breakpoints de Tailwind (`lg:`) para adaptar el layout:

- **Mobile:** Navegación mediante drawer deslizante (hamburger menu), columnas simples.
- **Desktop:** Sidebar fijo a la izquierda del dashboard, layouts de dos columnas, headers más amplios.

El dashboard tiene un header doble: uno para mobile (con hamburger) y otro para desktop (con sidebar colapsable), ambos controlados por JavaScript.

### 3.7 Comunicación con el Backend

Todos los scripts que acceden a la API siguen el mismo patrón:

```javascript
const token = localStorage.getItem('skinai_token')
const res   = await fetch('http://localhost:8000/api/<endpoint>', {
  method:  'POST',
  headers: {
    'Content-Type':  'application/json',
    'Authorization': `Bearer ${token}`,
  },
  body: JSON.stringify(payload),
})
const data = await res.json()
if (!res.ok) throw new Error(data.detail || 'Error genérico')
```

Los errores se muestran en cajas de error inline (sin alertas del navegador), y los estados de carga se reflejan deshabilitando botones y cambiando su texto a "Procesando...".

---

## 4. Backend

### 4.1 Framework Utilizado

El backend está construido con **FastAPI** (Python), un framework moderno de alto rendimiento basado en tipado estático y generación automática de documentación OpenAPI. FastAPI usa `async/await` de forma nativa y es compatible con ASGI, lo que lo hace adecuado para operaciones de I/O concurrentes.

Dependencias principales del backend:

| Librería | Propósito |
|----------|-----------|
| `fastapi` | Framework web |
| `uvicorn` | Servidor ASGI |
| `sqlalchemy` | ORM para PostgreSQL |
| `psycopg2-binary` | Driver PostgreSQL |
| `passlib[argon2]` | Hash de contraseñas con Argon2 |
| `python-jose[cryptography]` | Generación y validación de JWT |
| `python-multipart` | Recepción de archivos (`UploadFile`) |
| `slowapi` | Rate limiting |
| `Pillow` | Validación de imágenes (verify) |
| `opencv-python-headless` | Procesamiento de imágenes |
| `mediapipe` | Detección facial con FaceMesh |
| `email-validator` | Validación de formato de correo electrónico |
| `pydantic` | Validación y serialización de datos |

### 4.2 Estructura del Código

```
backend/
├── Dockerfile
└── app/
    ├── main.py              ← Punto de entrada: configuración de la app, middlewares, routers
    ├── models.py            ← Modelos SQLAlchemy (tablas de la base de datos)
    ├── schemas.py           ← Schemas Pydantic (validación y serialización)
    ├── api/
    │   ├── auth.py          ← Endpoints de autenticación
    │   ├── users.py         ← Endpoints de usuario y perfil de piel
    │   ├── analysis.py      ← Endpoints de análisis (upload, status, historial)
    │   ├── routines.py      ← Endpoints de rutinas cosméticas
    │   ├── products.py      ← Endpoints de catálogo de productos
    │   ├── deps.py          ← Dependencias compartidas (get_db, get_current_user)
    │   ├── upload.py        ← [Legacy] Endpoint de subida simple
    │   └── process.py       ← [Legacy] Endpoint de procesamiento directo
    └── core/
        ├── database.py      ← Configuración de SQLAlchemy y conexión a PostgreSQL
        ├── security.py      ← Funciones JWT, hashing de contraseñas
        ├── logger.py        ← Logger centralizado con formato JSON
        └── ratelimit.py     ← Configuración de SlowAPI (60 req/min por IP)
```

**Separación de responsabilidades:** La capa `api/` contiene únicamente la lógica de enrutamiento y validación de entrada/salida. La lógica de negocio (procesamiento de imagen, cálculo de recomendaciones) vive en `core/` y se invoca desde los routers. Los modelos de datos están en `models.py` y los contratos de la API en `schemas.py`.

### 4.3 Endpoints Disponibles

Todos los endpoints están agrupados bajo el prefijo `/api/` y organizados por dominio funcional.

#### Autenticación — `/api/auth/`

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `POST` | `/register` | Crea cuenta, valida GDPR, devuelve JWT + datos del usuario | No |
| `POST` | `/login` | Valida credenciales, devuelve JWT + datos del usuario | No |
| `POST` | `/logout` | Registra cierre de sesión (el cliente elimina el token) | Sí |
| `POST` | `/forgot-password` | Solicita recuperación de contraseña por email | No |

#### Usuarios — `/api/users/`

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/me` | Devuelve datos básicos del usuario autenticado | Sí |
| `PUT` | `/me` | Actualiza nombre y/o campos del perfil de piel | Sí |
| `DELETE` | `/me` | Elimina cuenta y todos sus datos (irreversible) | Sí |
| `POST` | `/profile` | Guarda o reemplaza el perfil de piel completo | Sí |
| `GET` | `/profile` | Devuelve el perfil de piel del usuario | Sí |

#### Análisis — `/api/analysis/`

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `POST` | `/upload` | Recibe imagen, la valida, inicia análisis en background, devuelve `analysis_id` | Sí |
| `GET` | `/{id}/status` | Estado del análisis: `processing` / `completed` / `failed` | Sí |
| `GET` | `/{id}` | Documento completo del análisis con resultado | Sí |
| `GET` | `/history` | Lista paginada de análisis del usuario (`skip`, `limit`) | Sí |

#### Rutinas — `/api/routines/`

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/active` | Devuelve la rutina activa del usuario con todos sus pasos | Sí |
| `POST` | `/` | Crea nueva rutina (desactiva la anterior) | Sí |
| `PATCH` | `/active/steps` | Actualiza productos en pasos específicos de la rutina activa | Sí |
| `POST` | `/check` | Registra si el usuario siguió su rutina antes del análisis | Sí |

#### Productos — `/api/products/`

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/search` | Busca productos por nombre/marca/categoría en la base de datos | Sí |
| `GET` | `/recommended` | Devuelve productos recomendados según perfil de piel del usuario | Sí |
| `GET` | `/{product_id}` | Detalle de un producto con lista completa de ingredientes | Sí |

### 4.4 Lógica de Negocio Principal

**Validación de imágenes:** Antes de procesar cualquier imagen, el backend verifica tres condiciones: (1) el tamaño no supera 10 MB, (2) el tipo MIME es `image/jpeg` o `image/png`, y (3) la biblioteca Pillow puede abrir y verificar el archivo como imagen real. Esto previene ataques de tipo "polyglot file" o archivos corruptos.

**Flujo de análisis asíncrono:** El endpoint `POST /api/analysis/upload` guarda la imagen, crea un registro `Analysis` con estado `"processing"` y devuelve inmediatamente el `analysis_id`. El procesamiento real (censura facial con FaceCensor) se ejecuta en una tarea de background de FastAPI. Cuando termina, actualiza el registro a `"completed"` o `"failed"`. El frontend hace polling de `GET /api/analysis/{id}/status` para detectar el cambio.

**Recomendaciones de productos:** La lógica de recomendación en `GET /api/products/recommended` consulta el perfil de piel del usuario, extrae su tipo de piel y condiciones declaradas, y filtra el catálogo de productos. Los productos base (limpiador, hidratante, SPF) se recomiendan siempre; los activos (BHA, niacinamida, ácido azelaico) se añaden según las condiciones presentes (acné, rosácea, manchas).

### 4.5 Autenticación y Autorización

**JWT (JSON Web Token):** El sistema usa tokens firmados con el algoritmo HS256 y una clave secreta configurable. Los tokens expiran en 30 minutos. Cada token contiene el email del usuario como `sub` (subject).

**Dependencia `get_current_user`:** FastAPI inyecta automáticamente esta función en los endpoints protegidos. Decodifica el token JWT del header `Authorization`, extrae el email, consulta la base de datos y devuelve el objeto `User`. Si el token es inválido o expirado, responde con HTTP 401.

**Hash de contraseñas:** Se utiliza el algoritmo **Argon2** (ganador del Password Hashing Competition 2015), considerado el estado del arte en almacenamiento seguro de contraseñas. Es resistente a ataques de fuerza bruta por GPU.

**Rate Limiting:** SlowAPI limita por defecto a 60 solicitudes por minuto por IP. Los endpoints de registro y login tienen un límite adicional de 5 solicitudes por minuto para mitigar ataques de fuerza bruta.

### 4.6 Middleware y Logging

**Middleware HTTP:** Cada solicitud es interceptada por un middleware que registra: ruta, método HTTP, código de respuesta y tiempo de procesamiento. Estos registros se emiten en formato JSON al archivo de log y a stdout.

**Logger JSON:** El logger centralizado (`logger.py`) emite registros estructurados en JSON con campos estandarizados: `timestamp`, `level`, `message`, `module`, `funcName`. Esto facilita la ingesta en sistemas de observabilidad como Elasticsearch o CloudWatch en producción.

---

## 5. Módulo de Inteligencia Artificial / Visión por Computador

### 5.1 Librerías Utilizadas

| Librería | Versión | Propósito |
|----------|---------|-----------|
| OpenCV (`opencv-python-headless`) | 4.8.1 | Lectura, escritura y manipulación de imágenes |
| MediaPipe | 0.10.8 | Detección de landmarks faciales (FaceMesh) |
| NumPy | 1.24.3 | Operaciones sobre arrays de píxeles |

### 5.2 Módulo FaceCensor

El módulo de visión por computador está implementado en `backend/app/core/face_censor.py` como la clase `FaceCensor`. Su propósito es **detectar el rostro en una imagen y censurar zonas sensibles (ojos y boca) antes de cualquier almacenamiento**, garantizando la privacidad del usuario.

**Parámetros de configuración:**

| Parámetro | Tipo | Por defecto | Descripción |
|-----------|------|-------------|-------------|
| `mode` | str | `"blur"` | Tipo de censura: `blur`, `black`, `pixelate` |
| `blur_strength` | int | 55 | Intensidad del desenfoque gaussiano (debe ser impar) |
| `expand` | int | 10 | Píxeles de expansión alrededor de cada región |
| `pixel_size` | int | 10 | Tamaño del píxel en modo pixelado |
| `cut` | bool | False | Si `True`, recorta la imagen al bounding box del rostro |

### 5.3 Modelos de IA Utilizados

**MediaPipe FaceMesh** es un modelo de estimación de landmarks faciales desarrollado por Google. Detecta 468 puntos de referencia (landmarks) en el rostro en tiempo real. En este sistema se configura para:

- `max_num_faces=1`: Procesar solo el primer rostro detectado.
- `refine_landmarks=True`: Activar landmarks de alta precisión para iris y labios.
- `min_detection_confidence=0.5`: Umbral mínimo para la detección inicial.
- `min_tracking_confidence=0.5`: Umbral mínimo para el seguimiento.

Los landmarks utilizados para la censura son:

| Región | Índices de landmarks |
|--------|---------------------|
| Ojo izquierdo | 33, 133 |
| Ojo derecho | 362, 263 |
| Boca | 78, 308, 14, 13 |

### 5.4 Flujo de Procesamiento de Imagen

```
ENTRADA: Imagen original (JPEG/PNG, min. ~720p de píxeles totales)
    │
    ▼
1. Lectura con OpenCV (cv2.imread) → Array NumPy BGR
    │
    ▼
2. Validación de resolución
   - Mínimo: 1280×720 píxeles totales (~921,600 px)
   - Permite imágenes portrait (ej: 798×1200 = 957,600 px)
   - Si falla → status "failed", mensaje de error
    │
    ▼
3. Conversión BGR → RGB para MediaPipe
    │
    ▼
4. FaceMesh.process(frame_rgb)
   - Detecta 468 landmarks en el rostro
   - Si no detecta rostro → devuelve frame sin modificar
    │
    ▼
5. Para cada región (ojo izquierdo, ojo derecho, boca):
   a. Calcular bounding box a partir de los landmarks
   b. Expandir el área según parámetro `expand`
   c. Extraer Region of Interest (ROI)
   d. Aplicar censura según modo:
      - blur:      GaussianBlur(roi, (k,k), 30)
      - black:     roi[:] = (0,0,0)
      - pixelate:  resize a pixel_size → resize de vuelta
   e. Reinyectar ROI censurada en la imagen
    │
    ▼
6. [Opcional] Si cut=True: recortar imagen al bounding box del rostro completo
    │
    ▼
7. Guardar imagen procesada con cv2.imwrite
    │
    ▼
SALIDA: Imagen censurada en /app/processed/<uuid>_censored.<ext>
```

**Principio de privacidad por diseño:** La imagen original se guarda temporalmente en `/app/uploads/` pero **nunca se persiste de forma permanente ni se muestra al usuario**. Solo la imagen censurada llega a la base de datos y al frontend.

### 5.5 Módulo de Análisis Cutáneo (Estado Futuro)

El sistema está preparado para incorporar modelos ONNX para el análisis real de afecciones cutáneas (acné, rosácea, tipo de piel). El pipeline de análisis ya existe: el endpoint `POST /api/analysis/upload` ejecuta el procesamiento en background y actualiza el campo `result` del registro `Analysis` con un JSON de resultados. Actualmente, ese campo contiene únicamente la ruta de la imagen censurada; el análisis probabilístico de condiciones dérmicas es el siguiente hito de desarrollo.

---

## 6. Bases de Datos

### 6.1 Motor Utilizado

**PostgreSQL 15** es el único motor de base de datos activo en el sistema. Aunque la arquitectura de referencia contemplaba MongoDB para resultados de análisis no estructurados, se optó por mantener todo en PostgreSQL para el MVP, simplificando la infraestructura y la consistencia de datos. Redis (caché) y MongoDB (resultados) son componentes planificados para fases posteriores.

### 6.2 Esquema Relacional

El esquema está compuesto por **9 tablas** con las siguientes relaciones:

```
users (1) ─────────────── (1) skin_profiles
  │
  ├── (1) ─── (N) analyses
  │                 │
  │                 └── referenciada por routines
  │
  ├── (1) ─── (N) routines
  │                 │
  │                 ├── (1) ─── (N) routine_steps
  │                 │
  │                 └── (1) ─── (N) skin_checks
  │
  └── (1) ─── (N) skin_checks

products (1) ─── (N) product_ingredients (N) ─── (1) ingredients
```

### 6.3 Descripción de Tablas

**`users`** — Datos de acceso y consentimiento

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer PK | Identificador único del usuario |
| `email` | String UNIQUE | Correo electrónico (usado como identificador de login) |
| `hashed_password` | String | Contraseña hasheada con Argon2 |
| `full_name` | String | Nombre completo del usuario |
| `gdpr_accepted` | Boolean | Registro de aceptación de términos y tratamiento de datos |
| `is_active` | Boolean | Estado de la cuenta (permite desactivar sin eliminar) |
| `created_at` | DateTime | Fecha y hora de registro |

**`skin_profiles`** — Perfil dermatológico del usuario

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer PK | — |
| `user_id` | Integer FK UNIQUE | Referencia a `users` (relación 1:1) |
| `age` | Integer | Edad del usuario |
| `gender` | String | Sexo biológico declarado |
| `fitzpatrick` | String | Fototipo Fitzpatrick (I a VI) |
| `skin_type` | String | Tipo de piel: seca, grasa, mixta, normal, sensible |
| `skin_conditions` | Text | JSON array de condiciones declaradas (acné, rosácea, manchas...) |
| `allergies` | Text | JSON array de ingredientes a evitar |
| `country` / `city` | String | Localización del usuario |
| `updated_at` | DateTime | Última actualización del perfil |

**`analyses`** — Registros de análisis cutáneo

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer PK | Identificador del análisis |
| `user_id` | Integer FK | Usuario propietario |
| `original_filename` | String | Nombre del archivo original (para referencia interna) |
| `censored_filename` | String | Nombre del archivo censurado guardado |
| `status` | String | Estado: `processing` / `completed` / `failed` |
| `result` | Text | JSON con resultados del análisis (modelo IA) |
| `error_message` | String | Mensaje de error si el análisis falló |
| `created_at` | DateTime | Fecha del análisis |

**`routines`** — Rutinas de cuidado personalizadas

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer PK | — |
| `user_id` | Integer FK | Usuario propietario |
| `analysis_id` | Integer FK | Análisis que generó la rutina (nullable) |
| `is_active` | Boolean | Solo una rutina puede estar activa por usuario |
| `created_at` | DateTime | Fecha de creación |

**`routine_steps`** — Pasos individuales de una rutina

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer PK | — |
| `routine_id` | Integer FK | Rutina a la que pertenece |
| `step_order` | Integer | Posición del paso en la secuencia |
| `time_of_day` | String | Momento de aplicación: `am`, `pm`, `both` |
| `product_name` | String | Nombre del producto recomendado |
| `product_category` | String | Categoría: cleanser, moisturizer, spf, serum, etc. |
| `reason` | String | Justificación de la recomendación |
| `is_active` | Boolean | Permite desactivar pasos sin eliminarlos |

**`skin_checks`** — Registro de adherencia a la rutina

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer PK | — |
| `user_id` | Integer FK | Usuario |
| `routine_id` | Integer FK | Rutina evaluada |
| `followed_routine` | Boolean | Si el usuario siguió la rutina antes del análisis |
| `notes` | String | Notas adicionales del usuario |
| `created_at` | DateTime | Fecha del registro |

**`products`** — Catálogo de productos cosméticos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer PK | — |
| `name` | String | Nombre del producto |
| `brand` | String | Marca |
| `category` | String | cleanser, moisturizer, spf, serum, exfoliant, retinoid, spot, etc. |
| `description` | Text | Descripción del producto |
| `highlights` | Text | JSON array de etiquetas (#alcohol-free, #fragrance-free) |
| `source_url` | String UNIQUE | URL de origen del scraper (INCIDecoder) |
| `created_at` | DateTime | — |

**`ingredients`** — Ingredientes cosméticos (INCI)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer PK | — |
| `inci_name` | String UNIQUE | Nombre INCI del ingrediente |
| `function` | String | Función cosmética (emollient, solvent, moisturizer, etc.) |
| `rating` | String | Valoración de seguridad (Superstar, Good stuff, OK, Caution) |
| `description` | Text | Descripción del ingrediente |

**`product_ingredients`** — Relación producto ↔ ingrediente

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `product_id` | Integer FK | — |
| `ingredient_id` | Integer FK | — |
| `position` | Integer | Posición del ingrediente en la fórmula (1 = primero) |
| `irr_com` | String | Irritancia y comedogenicidad: "0, 0" |

---

## 7. Procesamiento Asíncrono

### 7.1 Mecanismo Utilizado

El sistema utiliza **`BackgroundTasks`** de FastAPI para ejecutar operaciones de larga duración sin bloquear la respuesta HTTP. Cuando el usuario sube una imagen, el endpoint devuelve inmediatamente un `analysis_id` con estado `"processing"`, mientras la tarea de censura facial se ejecuta en segundo plano.

### 7.2 Implementación

```python
@router.post("/upload")
async def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    ...
):
    # 1. Validar y guardar imagen
    # 2. Crear registro Analysis con status="processing"
    # 3. Lanzar tarea en background
    background_tasks.add_task(
        _run_censorship,
        analysis.id,
        input_path,
        output_path,
        DATABASE_URL,
    )
    # 4. Responder inmediatamente con el analysis_id
    return {"analysis_id": analysis.id, "status": "processing"}
```

La función `_run_censorship` crea su propia sesión de base de datos (ya que BackgroundTasks se ejecuta fuera del ciclo de vida de la petición HTTP), ejecuta `FaceCensor.process_image()` y actualiza el registro con el resultado o el error.

### 7.3 Polling desde el Frontend

El frontend consulta periódicamente `GET /api/analysis/{id}/status` hasta que el estado cambia de `"processing"` a `"completed"` o `"failed"`. La pantalla `analyzing.html` muestra 7 pasos animados durante este período para mantener al usuario informado.

### 7.4 Limitaciones y Evolución

`BackgroundTasks` de FastAPI ejecuta las tareas en el mismo proceso del servidor. Para cargas de trabajo intensivas o procesamiento con múltiples instancias, se recomienda migrar a **Celery + Redis** como cola de mensajes, lo que permite escalar workers de forma independiente.

---

## 8. Infraestructura

### 8.1 Docker y docker-compose

El sistema está completamente contenedorizado. Cada servicio tiene su propio `Dockerfile` y se orquestan mediante `docker-compose.yml`.

**Dockerfile del backend:**
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY ./app /app/app
# Dependencias del sistema para OpenCV y MediaPipe
RUN apt-get update && apt-get install -y \
    libsm6 libxext6 libxrender-dev libgomp1 libgl1 libglib2.0-0
# Dependencias Python
RUN pip install fastapi uvicorn sqlalchemy psycopg2-binary \
    passlib[argon2] python-jose[cryptography] python-multipart \
    email-validator slowapi Pillow requests \
    opencv-python-headless==4.8.1.78 \
    mediapipe==0.10.8 numpy==1.24.3
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Las dependencias del sistema (`libsm6`, `libgl1`, etc.) son necesarias para que OpenCV funcione en un entorno sin interfaz gráfica.

**Dockerfile del frontend:**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--host"]
```

**Volúmenes Docker:**

| Volumen | Propósito |
|---------|-----------|
| `postgres_data` | Persistencia de la base de datos PostgreSQL |
| `uploaded_data` | Imágenes subidas por los usuarios (`/app/uploads`) |
| `./logs/backend.log` | Archivo de log persistente fuera del contenedor |

### 8.2 Variables de Entorno

| Variable | Servicio | Valor por defecto | Descripción |
|----------|----------|-------------------|-------------|
| `DATABASE_URL` | backend | `sqlite:///./test.db` | Cadena de conexión a PostgreSQL |
| `POSTGRES_USER` | db | `postgres` | Usuario de PostgreSQL |
| `POSTGRES_PASSWORD` | db | `password` | Contraseña de PostgreSQL |
| `POSTGRES_DB` | db | `tesis_db` | Nombre de la base de datos |

> **Nota de seguridad:** Las credenciales hardcodeadas en `docker-compose.yml` y la `SECRET_KEY` en `security.py` son adecuadas para desarrollo local, pero deben reemplazarse por variables de entorno inyectadas desde un gestor de secretos (AWS Secrets Manager, `.env` file, etc.) antes del despliegue en producción.

### 8.3 Preparación para Despliegue

El sistema está diseñado para migrar a entornos cloud:

- **AWS EC2:** El `docker-compose.yml` puede ejecutarse directamente en una instancia EC2.
- **AWS S3:** El almacenamiento de imágenes actualmente usa el sistema de archivos local; la migración a S3 requiere reemplazar las operaciones de `open(path, "wb")` por el SDK boto3.
- **Nginx:** Se puede agregar un servicio Nginx como proxy inverso que gestione HTTPS y distribuya tráfico entre el frontend (puerto 3000) y el backend (puerto 8000) desde un único punto de entrada público.
- **Docker Swarm:** La arquitectura actual es compatible con escalamiento horizontal mediante Docker Swarm, distribuyendo réplicas del servicio `backend` entre nodos.

---

## 9. Modelos de Datos y Entidades

### 9.1 Modelos SQLAlchemy (ORM)

Los modelos son clases Python que mapean directamente a tablas en PostgreSQL, heredando de `Base = declarative_base()`.

**Relaciones entre modelos:**

```
User
 ├── SkinProfile     (1:1, backref="skin_profile")
 ├── Analysis        (1:N, backref="analyses")
 ├── Routine         (1:N, backref="routines")
 └── SkinCheck       (1:N, via user_id)

Routine
 ├── RoutineStep     (1:N, cascade="all, delete-orphan", ordered by step_order)
 └── SkinCheck       (1:N, via routine_id)

Analysis
 └── Routine         (referenciada, no cascade)

Product
 └── ProductIngredient  (1:N, cascade="all, delete-orphan")

Ingredient
 └── ProductIngredient  (1:N)
```

### 9.2 Schemas Pydantic (DTOs)

Los schemas Pydantic sirven como Data Transfer Objects: definen la estructura exacta de los datos que entran y salen de la API, independientemente de los modelos de base de datos.

**Schemas de autenticación:**

- `UserCreate`: `full_name`, `email`, `password`, `gdpr_accepted` → para registro
- `UserLogin`: `email`, `password` → para login
- `UserOut`: `id`, `email`, `full_name`, `is_active`, `created_at` → respuesta pública del usuario
- `TokenResponse`: `access_token`, `token_type`, `user: UserOut` → respuesta de auth

**Schemas de perfil:**

- `SkinProfileCreate`: todos los campos editables del perfil de piel
- `SkinProfileOut`: extiende `SkinProfileCreate` con `id`, `user_id`, `updated_at` + validator JSON que convierte los campos `skin_conditions` y `allergies` de string a `List[str]` automáticamente

**Schemas de análisis:**

- `AnalysisCreated`: `analysis_id`, `status` → respuesta inmediata del upload
- `AnalysisStatusOut`: `analysis_id`, `status` → para polling
- `AnalysisOut`: documento completo del análisis
- `AnalysisSnapshot`: versión resumida para el historial

**Schemas de rutinas:**

- `RoutineOut`: incluye la lista completa de `steps: List[RoutineStepOut]`
- `RoutineStepsUpdate`: lista de `{ step_id, product_name }` para actualización parcial
- `SkinCheckCreate`: `followed_routine` (bool) + `notes` opcionales

**Schemas de productos:**

- `ProductOut`: `id`, `name`, `brand`, `category`, `description`
- `ProductDetailOut`: extiende `ProductOut` con `highlights`, `source_url` y `product_ingredients: List[ProductIngredientOut]`
- `IngredientOut`: `id`, `inci_name`, `function`, `rating`

---

## 10. Flujo Completo del Sistema

```
USUARIO                     FRONTEND                    BACKEND                     BD / FS
   │                            │                           │                          │
   │── Accede a la web ────────►│                           │                          │
   │                            │── GET / (Vite) ──────────►│                          │
   │                            │◄── index.html ────────────│                          │
   │                            │── fetch navbar/modals ────►│ (archivos estáticos)     │
   │                            │                           │                          │
   │── Clic "Comenzar" ────────►│── navigate('auth') ───────►│                          │
   │                            │── fetch auth.html ─────────►│                          │
   │                            │                           │                          │
   │── Completa registro ───────►│── POST /api/auth/register ►│                          │
   │                            │                           │── INSERT users ──────────►│
   │                            │                           │◄── User + JWT ────────────│
   │                            │◄── {access_token, user} ──│                          │
   │                            │── localStorage token/user  │                          │
   │                            │── navigate('profile') ─────►│                          │
   │                            │                           │                          │
   │── Completa perfil ─────────►│── POST /api/users/profile ►│                          │
   │                            │   (Bearer token)           │── INSERT skin_profiles ──►│
   │                            │◄── SkinProfileOut ─────────│                          │
   │                            │── navigate('capture') ──────►│                          │
   │                            │                           │                          │
   │── Sube foto ───────────────►│── POST /api/analysis/upload►│                          │
   │                            │   (multipart/form-data)    │── Validar imagen         │
   │                            │                           │── INSERT analyses (proc.)►│
   │                            │                           │── BackgroundTask:        │
   │                            │                           │   FaceCensor.process()   │
   │                            │◄── {analysis_id, status}──│                          │
   │                            │── navigate('analyzing') ───►│                          │
   │                            │                           │                          │
   │                            │── [POLLING] ───────────────►│                          │
   │                            │── GET /api/analysis/{id}/status                       │
   │                            │                           │   [Background completado] │
   │                            │                           │── UPDATE analyses ────────►│
   │                            │                           │── Guardar img censurada ──►│(FS)
   │                            │◄── {status: "completed"}──│                          │
   │                            │── navigate('dashboard') ───►│                          │
   │                            │                           │                          │
   │── Ve resultados ───────────►│── GET /api/analysis/{id} ─►│── SELECT analyses ───────►│
   │                            │── GET /api/routines/active ►│── SELECT routines ────────►│
   │                            │◄── Análisis + Rutina ──────│                          │
   │                            │── Renderiza dashboard      │                          │
   │                            │   (tabs: diagnóstico,      │                          │
   │                            │    rutina, gráficas,       │                          │
   │                            │    historial)              │                          │
```

---

## 11. Buenas Prácticas Implementadas

### 11.1 Separación de Responsabilidades

El sistema aplica el principio de separación de responsabilidades en múltiples niveles:

- **Frontend/Backend:** El frontend es puramente presentacional; toda la lógica de negocio, validación de seguridad y acceso a datos vive en el backend.
- **Routers/Core:** Los endpoints (`api/`) solo manejan entrada/salida HTTP. La lógica de procesamiento (censura, recomendaciones) está en `core/`.
- **Modelos/Schemas:** Los modelos SQLAlchemy representan la estructura de la BD; los schemas Pydantic representan los contratos de la API. Son independientes.

### 11.2 Privacidad por Diseño (Privacy by Design)

- La censura facial se aplica **antes** de cualquier almacenamiento persistente.
- Las imágenes originales solo existen temporalmente en `/app/uploads/`; nunca se persisten en la base de datos ni se devuelven al frontend.
- El consentimiento GDPR se registra explícitamente en el campo `gdpr_accepted` de la tabla `users` con fecha implícita en `created_at`.
- La respuesta de `POST /forgot-password` es siempre la misma, independientemente de si el email existe o no, evitando la enumeración de usuarios.

### 11.3 Seguridad

- **Argon2** para hashing de contraseñas (resistente a ataques de GPU).
- **JWT con expiración** de 30 minutos para limitar la ventana de riesgo ante robo de token.
- **Rate limiting** con SlowAPI: 60 req/min general, 5 req/min en endpoints de auth.
- **Validación de imágenes en tres capas:** MIME, tamaño y verificación con Pillow.
- **CORS restrictivo:** Solo el origen `http://localhost:3000` está permitido en desarrollo.
- **Separación de red Docker:** Los servicios internos (PostgreSQL) no son accesibles desde fuera de la red `tesis-network`.

### 11.4 Escalabilidad Progresiva

- Cada servicio es un contenedor independiente, escalable horizontalmente.
- El backend es stateless (no guarda estado entre peticiones); el estado vive en PostgreSQL.
- El sistema de archivos puede reemplazarse por S3 cambiando únicamente las operaciones de I/O en `analysis.py`.
- BackgroundTasks puede migrarse a Celery+Redis sin cambiar la interfaz de los endpoints.

### 11.5 Observabilidad

- Logs estructurados en JSON con timestamp, nivel, módulo y función.
- Logs persistidos en archivo (`/app/logs/backend.log`) y emitidos a stdout (visible en `docker logs`).
- Middleware HTTP que registra cada solicitud con su tiempo de procesamiento.
- Endpoints de health check (`GET /` y `GET /health/db`) para verificar disponibilidad del servicio y la conexión a la base de datos.

### 11.6 Experiencia de Usuario

- **Feedback inmediato:** Botones de carga con texto "Procesando..." y estado deshabilitado durante operaciones asíncronas.
- **Mensajes de error inline:** Sin alertas del navegador; los errores se muestran junto al formulario.
- **Auth guards en el frontend:** El router redirige automáticamente a usuarios no autenticados que intenten acceder a páginas protegidas.
- **Diseño accesible:** Uso de atributos `aria-label`, `role`, `aria-live` y `aria-modal` en los componentes HTML.

---

## 12. Observaciones, Limitaciones y Trabajo Futuro

### 12.1 Limitaciones Actuales

| Área | Limitación | Impacto |
|------|------------|---------|
| **IA / Análisis** | No existe modelo ONNX de análisis cutáneo real. El campo `result` del análisis contiene solo metadata de la censura. | El dashboard muestra datos mockeados en el historial |
| **Productos** | La tabla `products` está vacía. El scraper de INCIDecoder no está implementado. `GET /products/recommended` devuelve lista vacía. | La funcionalidad de recomendaciones no opera con datos reales |
| **Almacenamiento** | Las imágenes se guardan en el sistema de archivos local del contenedor. No hay S3 ni backup. | Pérdida de datos al recrear el contenedor |
| **Forgot password** | El endpoint existe pero no envía emails (no hay servidor de correo configurado). | El flujo de recuperación no es funcional en producción |
| **Dashboard** | Los datos del historial y gráficas en `dashboard.js` son hardcodeados (mock). No consumen `GET /api/analysis/history`. | El historial real no se muestra |
| **Seguridad** | `SECRET_KEY` y credenciales de PostgreSQL están hardcodeadas en el código fuente. | Riesgo de exposición en repositorios públicos |
| **Logout** | JWT es stateless; no hay blacklist de tokens. Un token robado sigue siendo válido hasta su expiración. | Ventana de 30 minutos de riesgo post-logout |

### 12.2 Trabajo Futuro (por Fases)

**Fase 3 — IA Real:**
- Integrar modelo ONNX de clasificación de acné y rosácea sobre las regiones faciales no censuradas.
- Implementar segmentación de zonas faciales (frente, mejillas, nariz, mentón) para análisis localizado.
- Generar el objeto `result` con campos estandarizados: `{ type, severity, confidence, zones, characteristics }`.

**Fase 3 — Infraestructura de datos:**
- Implementar scraper de INCIDecoder para poblar las tablas `products` e `ingredients`.
- Migrar almacenamiento de imágenes a AWS S3 con URLs presignadas.

**Fase 4 — Producción:**
- Configurar Nginx como proxy inverso con certificado SSL/TLS.
- Mover secretos a variables de entorno o AWS Secrets Manager.
- Implementar Celery + Redis para el procesamiento asíncrono.
- Agregar Redis caché para `GET /products/recommended` y `GET /api/analysis/history`.
- Conectar el dashboard al historial real (`GET /api/analysis/history`).
- Implementar envío de emails transaccionales (recuperación de contraseña, verificación de cuenta).

### 12.3 Retos Técnicos Identificados

1. **Compatibilidad de MediaPipe en Docker:** MediaPipe requiere dependencias específicas del sistema (`libgl1`, `libglib2.0-0`) y versiones precisas de NumPy (1.24.x) para funcionar correctamente en contenedores Linux headless. La solución fue fijar versiones exactas en el Dockerfile.

2. **Git lock en desarrollo con VSCode:** El editor mantiene procesos Git activos que impiden cambiar de rama con `git switch`. La solución es usar `git ls-tree` y `git show` para acceder a contenido de otras ramas sin necesidad de un checkout.

3. **Serialización de campos JSON en PostgreSQL:** Los campos `skin_conditions` y `allergies` se almacenan como texto JSON en PostgreSQL (no como JSONB) para mantener compatibilidad con SQLite en desarrollo. La deserialización automática se logra con un validator Pydantic que parsea el string al leer el modelo.

4. **Procesamiento asíncrono con sesión de BD:** La función de background de FastAPI no puede compartir la sesión SQLAlchemy de la petición HTTP (que ya está cerrada). La solución implementada es crear una sesión nueva dentro de la tarea background usando directamente `DATABASE_URL`.

5. **Validación de resolución adaptativa:** La censura facial con MediaPipe requiere una resolución mínima para detectar landmarks correctamente. La validación original rechazaba imágenes portrait de alta resolución porque comparaba ancho×alto con el mínimo 1280×720 de forma directa. La solución fue comparar el total de píxeles (~921,600) en lugar de dimensiones individuales.

---

*Documentación generada el 14 de abril de 2026.*  
*Estado del sistema: MVP funcional — Fase 7-8 completada.*
