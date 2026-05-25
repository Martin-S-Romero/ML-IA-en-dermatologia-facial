# Diseño e Implementación de la Base de Datos del Sistema SkinAI

**Proyecto:** Sistema Integral de Dermatología Facial basado en Inteligencia Artificial  
**Fecha de implementación:** Mayo 2026  
**Motor de base de datos:** PostgreSQL 15  
**ORM:** SQLAlchemy 2.x  
**Herramienta de migraciones:** Alembic  

---

## 1. Introducción

La base de datos constituye el componente central de persistencia del sistema SkinAI. Su diseño responde a los requerimientos funcionales del sistema: almacenamiento de información de usuarios, perfiles dermatológicos, resultados de análisis de imágenes por inteligencia artificial, rutinas de cuidado personalizadas y un catálogo de productos de skincare.

El esquema fue diseñado siguiendo principios de normalización relacional, integridad referencial, y aprovechando capacidades específicas de PostgreSQL como el tipo de dato `JSONB` para información semiestructurada y el soporte de timestamps con zona horaria para garantizar consistencia temporal en entornos distribuidos.

---

## 2. Tecnologías Utilizadas

### 2.1 PostgreSQL 15

PostgreSQL fue seleccionado como motor de base de datos por las siguientes razones técnicas:

- **Soporte nativo de JSONB:** Permite almacenar datos semiestructurados (listas de condiciones dermatológicas, resultados de modelos de IA) con capacidad de indexación y consulta directa desde SQL, sin necesidad de deserialización en la capa de aplicación.
- **Timestamps con zona horaria (`TIMESTAMPTZ`):** Garantiza consistencia temporal independientemente del entorno de ejecución, evitando problemas de conversión entre zonas horarias en sistemas distribuidos con Docker.
- **Row Level Security (RLS):** Mecanismo de seguridad a nivel de fila que permite restringir el acceso a datos por usuario directamente en el motor de base de datos, como capa adicional de protección más allá de la lógica de la aplicación.
- **Integridad referencial con `ON DELETE CASCADE`:** Simplifica la eliminación de datos de usuario garantizando que los registros dependientes se eliminen automáticamente, cumpliendo con requisitos de privacidad (GDPR).

### 2.2 SQLAlchemy

SQLAlchemy actúa como ORM (Object-Relational Mapper), permitiendo definir el esquema de la base de datos mediante clases Python (modelos) en lugar de SQL directo. Esto ofrece:

- Independencia del dialecto SQL en la capa de aplicación
- Tipado estático de columnas para detección temprana de errores
- Gestión automática del ciclo de vida de sesiones de base de datos
- Generación automática de migraciones a través de Alembic

### 2.3 Alembic

Alembic es la herramienta de migraciones de esquema para SQLAlchemy. Permite versionar la estructura de la base de datos de la misma manera en que Git versiona el código fuente. Sus ventajas en el contexto de este proyecto son:

- **Reproducibilidad:** El esquema puede recrearse en cualquier entorno ejecutando `alembic upgrade head`
- **Trazabilidad:** Cada modificación al esquema queda registrada como un archivo versionado en el repositorio
- **Reversibilidad:** Cada migración incluye una función `downgrade()` que permite revertir cambios
- **Evolución incremental:** Permite agregar columnas o tablas nuevas (por ejemplo, cuando el modelo de Deep Learning se integre) sin perder datos existentes

---

## 3. Organización del Código de Modelos

Los modelos de la base de datos se organizaron en el módulo `backend/app/db_scheme/`, siguiendo el principio de responsabilidad única, con un archivo por dominio:

```
backend/app/db_scheme/
├── __init__.py          # Re-exporta todas las clases para imports limpios
├── base.py              # Clase Base de SQLAlchemy con convención de nombres
├── user.py              # Tablas: users, skin_profiles
├── analysis.py          # Tabla: analyses
├── routine.py           # Tablas: routines, routine_steps, skin_checks
└── product.py           # Tablas: products, ingredients, product_ingredients
```

Esta separación permite que cada dominio funcional del sistema sea comprensible de forma aislada, facilita el mantenimiento y la colaboración, y es coherente con la arquitectura en capas del backend.

El archivo `base.py` define la clase `Base` de SQLAlchemy con una convención de nombres estandarizada para constraints:

```python
_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
}
```

Esta convención garantiza que todos los índices, claves foráneas y restricciones de unicidad tengan nombres predecibles y únicos, lo cual es requerido por Alembic para generar migraciones correctas.

---

## 4. Diseño del Esquema Relacional

### 4.1 Diagrama de Entidades

```
users (1) ──────────── (1) skin_profiles
  │
  ├── (1) ──────────── (N) analyses
  │                         │
  ├── (1) ──────────── (N) routines ── (N) ── routine_steps
  │                         │
  └── (1) ──────────── (N) skin_checks (referencia a routine)

products (N) ── (N) ingredients     [tabla intermedia: product_ingredients]
```

### 4.2 Descripción de Tablas

#### Tabla `users`

Almacena las cuentas de usuario del sistema.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| `id` | `INTEGER` | PK, índice | Identificador único autoincremental |
| `email` | `VARCHAR(255)` | UNIQUE, NOT NULL, índice | Correo electrónico, usado para autenticación |
| `hashed_password` | `VARCHAR(255)` | NOT NULL | Contraseña hasheada con Argon2 |
| `full_name` | `VARCHAR(255)` | nullable | Nombre completo del usuario |
| `gdpr_accepted` | `BOOLEAN` | NOT NULL | Consentimiento de tratamiento de datos |
| `is_active` | `BOOLEAN` | NOT NULL | Estado de la cuenta |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, server_default | Fecha de registro con zona horaria |

El campo `hashed_password` almacena el resultado del algoritmo Argon2, considerado el estándar más seguro para hashing de contraseñas según la competencia Password Hashing Competition (PHC) de 2015. Nunca se almacena la contraseña en texto plano.

---

#### Tabla `skin_profiles`

Almacena el perfil dermatológico de cada usuario, recopilado durante el proceso de registro.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| `id` | `INTEGER` | PK | Identificador único |
| `user_id` | `INTEGER` | FK → users.id, UNIQUE, CASCADE | Relación 1:1 con users |
| `age` | `INTEGER` | nullable | Edad del usuario |
| `gender` | `VARCHAR(20)` | nullable | Género |
| `fitzpatrick` | `VARCHAR(5)` | nullable | Fototipo de piel (escala Fitzpatrick I–VI) |
| `skin_type` | `VARCHAR(20)` | nullable | Tipo de piel (seca, grasa, mixta, normal, sensible) |
| `skin_conditions` | `JSONB` | nullable | Lista de condiciones cutáneas (ej. `["acne", "rosácea"]`) |
| `allergies` | `JSONB` | nullable | Lista de alergias conocidas |
| `country` | `VARCHAR(100)` | nullable | País de residencia |
| `city` | `VARCHAR(100)` | nullable | Ciudad de residencia |
| `updated_at` | `TIMESTAMPTZ` | server_default, onupdate | Última actualización del perfil |

**Decisión de diseño — uso de JSONB para `skin_conditions` y `allergies`:** Estas columnas almacenan listas de longitud variable (`["acne", "manchas", "poros dilatados"]`). Se optó por `JSONB` en lugar de una tabla de relación separada o texto serializado (`TEXT`) por las siguientes razones:

1. Las condiciones dermatológicas son datos de entrada del usuario, no entidades que requieran relaciones propias.
2. `JSONB` permite consultas directas desde SQL (ej. `skin_conditions @> '["acne"]'`) sin deserialización en Python.
3. Simplifica el esquema sin sacrificar capacidad de consulta.
4. SQLAlchemy serializa y deserializa listas Python automáticamente al escribir/leer `JSONB`, eliminando la necesidad de `json.dumps()` / `json.loads()` en el código de la aplicación.

La escala de Fitzpatrick es un sistema de clasificación dermatológica que categoriza el fototipo de piel en seis tipos (I al VI) según su respuesta a la exposición solar, siendo relevante para el análisis de afecciones cutáneas en distintos tonos de piel.

---

#### Tabla `analyses`

Registra cada análisis de imagen facial realizado por el sistema de IA.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| `id` | `INTEGER` | PK, índice | Identificador único |
| `user_id` | `INTEGER` | FK → users.id, índice, CASCADE | Usuario propietario del análisis |
| `original_filename` | `VARCHAR(255)` | NOT NULL | Nombre UUID de la imagen original subida |
| `censored_filename` | `VARCHAR(255)` | nullable | Nombre UUID de la imagen censurada |
| `status` | `VARCHAR(20)` | NOT NULL | Estado: `processing` / `completed` / `failed` |
| `error_message` | `VARCHAR(500)` | nullable | Mensaje de error si el análisis falló |
| `result` | `JSONB` | nullable | Resultado del análisis de IA en formato estructurado |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, server_default | Momento de creación |
| `completed_at` | `TIMESTAMPTZ` | nullable | Momento de finalización del análisis |

**Decisión de diseño — `result` como JSONB:** El resultado del modelo de Deep Learning es un objeto semiestructurado cuyo esquema interno evolucionará durante el desarrollo. Se utilizó `JSONB` para permitir esta evolución sin necesidad de migraciones de esquema en cada iteración del modelo. Cuando el modelo de clasificación esté finalizado, se agregarán columnas tipadas específicas (condiciones detectadas, puntuaciones de confianza, versión del modelo) mediante una migración de Alembic.

**Decisión de diseño — `completed_at`:** La columna `completed_at` permite calcular el tiempo de procesamiento de cada análisis (`completed_at - created_at`), métrica relevante para la evaluación de rendimiento del sistema presentada en la tesis.

**Privacidad (GDPR):** Los nombres de archivo se generan como UUIDs aleatorios, no relacionados con la identidad del usuario. La imagen original es eliminada del servidor tras la generación de la imagen censurada, conservando únicamente la versión procesada donde los rasgos identificativos (ojos y boca) han sido anonimizados mediante desenfoque gaussiano usando MediaPipe FaceMesh.

---

#### Tabla `routines`

Registra las rutinas de cuidado facial personalizadas generadas para cada usuario.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| `id` | `INTEGER` | PK, índice | Identificador único |
| `user_id` | `INTEGER` | FK → users.id, CASCADE | Usuario dueño de la rutina |
| `analysis_id` | `INTEGER` | FK → analyses.id, SET NULL | Análisis que originó la rutina (nullable) |
| `is_active` | `BOOLEAN` | NOT NULL | Indica si es la rutina vigente |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | Fecha de creación |

El campo `analysis_id` usa `ON DELETE SET NULL` en lugar de `CASCADE`: si el análisis fuente es eliminado, la rutina se conserva (solo pierde la referencia al análisis), ya que la rutina representa un plan de tratamiento valioso independientemente de su origen.

---

#### Tabla `routine_steps`

Almacena los pasos individuales de cada rutina.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| `id` | `INTEGER` | PK, índice | Identificador único |
| `routine_id` | `INTEGER` | FK → routines.id, CASCADE | Rutina a la que pertenece |
| `step_order` | `INTEGER` | NOT NULL | Posición del paso en la secuencia |
| `time_of_day` | `VARCHAR(10)` | NOT NULL | Momento: `am` / `pm` / `both` |
| `product_name` | `VARCHAR(255)` | NOT NULL | Nombre del producto recomendado |
| `product_category` | `VARCHAR(50)` | nullable | Categoría (cleanser, moisturizer, spf, etc.) |
| `reason` | `VARCHAR(500)` | nullable | Justificación dermatológica del paso |
| `is_active` | `BOOLEAN` | NOT NULL | Permite desactivar pasos sin eliminarlos |

---

#### Tabla `skin_checks`

Registra si el usuario siguió su rutina activa antes de cada análisis.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | `INTEGER` | PK |
| `user_id` | `INTEGER` | FK → users.id |
| `routine_id` | `INTEGER` | FK → routines.id |
| `followed_routine` | `BOOLEAN` | Indica si siguió la rutina ese día |
| `notes` | `VARCHAR(500)` | Observaciones opcionales del usuario |
| `created_at` | `TIMESTAMPTZ` | Fecha del registro |

Esta tabla permite al sistema evaluar la correlación entre la adherencia a la rutina de cuidado y la evolución de las condiciones cutáneas a lo largo del tiempo, dato de valor para el análisis longitudinal presentado en la tesis.

---

#### Tablas `products`, `ingredients`, `product_ingredients`

Conforman el catálogo de productos de skincare obtenido mediante scraping de fuentes especializadas en análisis de ingredientes cosméticos.

**`products`**

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | `INTEGER` | PK |
| `name` | `VARCHAR(255)` | Nombre del producto |
| `brand` | `VARCHAR(100)` | Marca, con índice para búsqueda |
| `category` | `VARCHAR(50)` | Categoría (cleanser, moisturizer, spf, serum, etc.) |
| `description` | `TEXT` | Descripción del producto |
| `highlights` | `JSONB` | Características destacadas (ej. `["#alcohol-free", "#fragrance-free"]`) |
| `source_url` | `VARCHAR(512)` | URL de origen, UNIQUE |
| `created_at` | `TIMESTAMPTZ` | Fecha de scraping |

**`ingredients`**

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | `INTEGER` | PK |
| `inci_name` | `VARCHAR(255)` | Nombre INCI del ingrediente, UNIQUE con índice |
| `function` | `VARCHAR(255)` | Función cosmética (emollient, solvent, etc.) |
| `rating` | `VARCHAR(50)` | Calificación de seguridad (Superstar, Good stuff, OK, Caution) |
| `description` | `TEXT` | Descripción técnica del ingrediente |
| `created_at` | `TIMESTAMPTZ` | Fecha de inserción |

La nomenclatura INCI (International Nomenclature of Cosmetic Ingredients) es el estándar internacional para la identificación de ingredientes cosméticos, garantizando consistencia en la base de datos independientemente del idioma de la fuente.

**`product_ingredients`** (tabla intermedia)

Implementa la relación muchos-a-muchos entre productos e ingredientes, almacenando adicionalmente el orden de aparición del ingrediente en la fórmula (la posición es relevante porque los ingredientes se listan en orden decreciente de concentración) y datos de irritancia y comedogenicidad.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `product_id` | `INTEGER` | FK → products.id, CASCADE |
| `ingredient_id` | `INTEGER` | FK → ingredients.id |
| `position` | `INTEGER` | Posición en la lista INCI (1 = mayor concentración) |
| `irr_com` | `VARCHAR(20)` | Irritancia / comedogenicidad |

---

## 5. Estrategia de Migraciones con Alembic

### 5.1 Configuración

Alembic se configuró en el directorio `backend/`, con la siguiente estructura:

```
backend/
├── alembic.ini                          # Configuración general
└── alembic/
    ├── env.py                           # Entorno de ejecución (lee DATABASE_URL)
    ├── script.py.mako                   # Plantilla para nuevas migraciones
    └── versions/
        └── 9a61d17817dd_initial_schema.py   # Migración inicial
```

El archivo `env.py` importa `Base` y todos los modelos del módulo `db_scheme`, permitiendo que Alembic compare el estado de los modelos Python con el esquema real de PostgreSQL para detectar diferencias automáticamente.

### 5.2 Migración Inicial

La migración inicial (`9a61d17817dd_initial_schema.py`) fue generada automáticamente el 24 de mayo de 2026 mediante el comando:

```bash
docker compose exec backend alembic revision --autogenerate -m "initial_schema"
```

Y aplicada mediante:

```bash
docker compose exec backend alembic upgrade head
```

El output de aplicación confirmó la creación exitosa de las 9 tablas:

```
INFO  [alembic.runtime.migration] Running upgrade  -> 9a61d17817dd, initial_schema
```

Alembic registra el estado actual de las migraciones en la tabla `alembic_version` dentro de PostgreSQL, que contiene el ID de la última migración aplicada (`9a61d17817dd`).

### 5.3 Flujo de Trabajo para Cambios Futuros

Cuando el esquema requiera modificaciones (por ejemplo, al integrar el modelo de Deep Learning), el proceso es:

```bash
# 1. Modificar el modelo Python correspondiente en db_scheme/
# 2. Generar la migración automáticamente
docker compose exec backend alembic revision --autogenerate -m "descripcion_del_cambio"

# 3. Revisar el archivo generado en alembic/versions/
# 4. Aplicar la migración
docker compose exec backend alembic upgrade head
```

Este flujo garantiza que los cambios al esquema sean reproducibles en cualquier entorno (desarrollo, pruebas, demo de tesis) sin pérdida de datos.

### 5.4 Integración con Docker

El servicio `backend` en `docker-compose.yml` ejecuta las migraciones automáticamente en cada arranque, antes de iniciar el servidor:

```yaml
command: >
  sh -c "alembic upgrade head &&
         uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
```

Si no hay migraciones nuevas, Alembic no realiza ninguna acción y el servidor inicia normalmente. Si hay migraciones pendientes, las aplica antes de aceptar tráfico.

---

## 6. Decisiones de Diseño Técnico

### 6.1 Integridad Referencial con ON DELETE CASCADE

Todas las claves foráneas desde tablas de datos hacia `users` utilizan `ON DELETE CASCADE`. Esto garantiza que al eliminar un usuario, todos sus datos asociados (análisis, perfil de piel, rutinas, registros de seguimiento) sean eliminados automáticamente por el motor de base de datos, sin necesidad de lógica explícita en la aplicación. Este comportamiento es requerido por el Reglamento General de Protección de Datos (GDPR) en su artículo 17 ("derecho al olvido").

### 6.2 Timestamps con Zona Horaria

Todas las columnas de fecha/hora utilizan `DateTime(timezone=True)` en SQLAlchemy, que se mapea a `TIMESTAMPTZ` en PostgreSQL. La generación de valores por defecto se delega al servidor mediante `server_default=func.now()`, garantizando que el timestamp sea el del servidor de base de datos y no el del proceso de aplicación, lo cual es más confiable en entornos con múltiples réplicas o workers.

### 6.3 Convención de Nombres de Constraints

La convención de nombres definida en `base.py` produce nombres de constraints predecibles y únicos, por ejemplo:

- Índice en `users.email` → `ix_users_email`
- Unicidad en `skin_profiles.user_id` → `uq_skin_profiles_user_id`
- Clave foránea `analyses.user_id → users.id` → `fk_analyses_user_id_users`

Esta convención es un requisito de Alembic para la detección correcta de cambios en constraints al generar migraciones en PostgreSQL.

### 6.4 Seguridad a Nivel de Fila (Row Level Security)

El sistema implementa Row Level Security (RLS) de PostgreSQL como capa adicional de seguridad. Mediante la variable de sesión `app.current_user_id`, establecida en cada conexión al momento de la autenticación, PostgreSQL puede filtrar automáticamente las filas accesibles por cada usuario. La variable se establece usando `set_config()` con parámetros vinculados para prevenir inyección SQL:

```python
db.execute(
    text("SELECT set_config('app.current_user_id', :uid, false)"),
    {"uid": str(user.id)}
)
```

---

## 7. Persistencia con Docker

Los datos de la base de datos se persisten mediante un volumen Docker nombrado (`postgres_data`), independiente del ciclo de vida de los contenedores. Las imágenes subidas por usuarios se almacenan en dos volúmenes separados:

- `uploads`: imágenes originales (eliminadas tras el procesamiento por cumplimiento GDPR)
- `processed`: imágenes censuradas (conservadas para consulta del usuario)

Esta separación garantiza que los datos sobrevivan a reinicios, reconstrucciones de imagen y actualizaciones del sistema.

---

## 8. Resumen del Esquema Implementado

| Tabla | Registros esperados | Propósito |
|-------|---------------------|-----------|
| `users` | 1 por cuenta | Autenticación y datos de identidad |
| `skin_profiles` | 1 por usuario | Perfil dermatológico inicial |
| `analyses` | N por usuario | Resultados de análisis de IA |
| `routines` | N por usuario (1 activa) | Planes de tratamiento personalizados |
| `routine_steps` | N por rutina | Pasos individuales de la rutina |
| `skin_checks` | N por usuario | Seguimiento de adherencia a la rutina |
| `products` | Catálogo completo | Productos de skincare recomendables |
| `ingredients` | Catálogo completo | Ingredientes cosméticos INCI |
| `product_ingredients` | N por producto | Composición de cada producto |
| `alembic_version` | 1 fila | Control de versiones del esquema |

===================
Todos los contenedores están corriendo (puntos verdes). Perfecto. Te explico cada uno:

Contenedor	Qué es	Para qué sirve
db-1 - PostgreSQL - La base de datos. Aquí se guardan usuarios, análisis, rutinas, productos
redis-1	- Redis	 - Una memoria temporal. Actúa como "sala de espera" para las tareas del análisis de IA
ai_worker-1	- Celery Worker	- El proceso que hace el trabajo pesado: censura la foto con MediaPipe y corre el análisis de piel
backend-1 - FastAPI	- La API REST. Recibe peticiones del frontend, las valida, las responde
frontend-1	- Vite / JS	- La interfaz web que ve el usuario en el navegador