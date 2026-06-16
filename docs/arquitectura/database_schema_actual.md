# Esquema de Base de Datos — Estado Actual

Tablas y campos definidos en los modelos SQLAlchemy (`backend/app/db_scheme/`).

---

## Índice

1. [users](#1-users)
2. [skin_profiles](#2-skin_profiles)
3. [consents](#3-consents)
4. [password_reset_tokens](#4-password_reset_tokens)
5. [analyses](#5-analyses)
6. [routines](#6-routines)
7. [routine_steps](#7-routine_steps)
8. [skin_checks](#8-skin_checks)
9. [products](#9-products)
10. [ingredients](#10-ingredients)
11. [product_ingredients](#11-product_ingredients)

---

## 1. `users`

| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER PK | No | Identificador único |
| `email` | VARCHAR(255) UNIQUE | No | Correo electrónico |
| `hashed_password` | VARCHAR(255) | No | Contraseña hasheada (bcrypt) |
| `full_name` | VARCHAR(255) | Sí | Nombre completo |
| `gdpr_accepted` | BOOLEAN | No | Aceptación del aviso legal |
| `is_active` | BOOLEAN | No | Cuenta activa / suspendida |
| `created_at` | TIMESTAMPTZ | No | Fecha de registro |
| `updated_at` | TIMESTAMPTZ | No | Última modificación |

---

## 2. `skin_profiles`

Relación 1-a-1 con `users`.

| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER PK | No | Identificador único |
| `user_id` | INTEGER FK → users | No | Usuario propietario |
| `birth_date` | DATE | Sí | Fecha de nacimiento |
| `gender` | VARCHAR(20) | Sí | Género (`male`, `female`, `non-binary`, `prefer_not_to_say`) |
| `fitzpatrick` | VARCHAR(5) | Sí | Fototipo de Fitzpatrick (I–VI) |
| `skin_type` | VARCHAR(20) | Sí | Tipo de piel (`seca`, `grasa`, `mixta`, `normal`, `sensible`) |
| `skin_conditions` | JSONB | Sí | Condiciones activas (`["acne", "rosácea"]`) |
| `allergies` | JSONB | Sí | Ingredientes alérgicos conocidos |
| `country` | VARCHAR(100) | Sí | País de residencia |
| `city` | VARCHAR(100) | Sí | Ciudad de residencia |
| `updated_at` | TIMESTAMPTZ | No | Última actualización del perfil |

---

## 3. `consents`

Historial de consentimientos aceptados por el usuario.

| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER PK | No | Identificador único |
| `user_id` | INTEGER FK → users | No | Usuario al que pertenece |
| `gdpr_accepted` | BOOLEAN | No | Aceptación RGPD/GDPR |
| `data_processing` | BOOLEAN | No | Consentimiento para procesar datos |
| `image_storage` | BOOLEAN | No | Consentimiento para almacenar imágenes |
| `ai_analysis` | BOOLEAN | No | Consentimiento para análisis con IA |
| `ip_address` | VARCHAR(45) | Sí | IP desde donde se aceptó (IPv4 / IPv6) |
| `accepted_at` | TIMESTAMPTZ | No | Momento exacto de aceptación |

---

## 4. `password_reset_tokens`

Tokens de restablecimiento de contraseña.

| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER PK | No | Identificador único |
| `user_id` | INTEGER FK → users | No | Usuario propietario del token |
| `token` | VARCHAR(64) UNIQUE | No | Token aleatorio |
| `used` | BOOLEAN | No | Si el token ya fue utilizado |
| `expires_at` | TIMESTAMPTZ | No | Fecha de expiración |
| `created_at` | TIMESTAMPTZ | No | Fecha de creación |

---

## 5. `analyses`

Cada análisis de imagen enviado por el usuario.

| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER PK | No | Identificador único |
| `user_id` | INTEGER FK → users | No | Usuario que realizó el análisis |
| `original_filename` | VARCHAR(255) | Sí | Nombre del archivo original (se borra tras procesar — GDPR) |
| `censored_filename` | VARCHAR(255) | Sí | Imagen con ojos/fondo censurado |
| `face_censored` | BOOLEAN | No | Si la imagen fue censurada correctamente |
| `lighting` | VARCHAR(50) | Sí | Condición de luz (`natural`, `artificial`, `low`, `unknown`) |
| `device` | VARCHAR(255) | Sí | Dispositivo/navegador del usuario |
| `status` | VARCHAR(20) | No | Estado (`processing`, `completed`, `failed`) |
| `error_message` | VARCHAR(500) | Sí | Mensaje de error si `status = failed` |
| `top1_label` | VARCHAR(50) | Sí | Etiqueta de la predicción principal |
| `top1_confidence` | FLOAT | Sí | Confianza de la predicción principal (0–1) |
| `model_version` | VARCHAR(50) | Sí | Versión del modelo IA usado |
| `result` | JSONB | Sí | Resultado completo del modelo (`all_scores`, `tta_passes`, `compute`) |
| `created_at` | TIMESTAMPTZ | No | Fecha de creación del análisis |
| `completed_at` | TIMESTAMPTZ | Sí | Fecha de finalización del análisis |

---

## 6. `routines`

Rutina de cuidado facial asociada a un análisis.

| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER PK | No | Identificador único |
| `user_id` | INTEGER FK → users | No | Usuario propietario |
| `analysis_id` | INTEGER FK → analyses | Sí | Análisis que originó la rutina |
| `is_active` | BOOLEAN | No | Si esta rutina está activa actualmente |
| `created_at` | TIMESTAMPTZ | No | Fecha de creación |
| `updated_at` | TIMESTAMPTZ | No | Última modificación |

---

## 7. `routine_steps`

Pasos individuales de una rutina.

| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER PK | No | Identificador único |
| `routine_id` | INTEGER FK → routines | No | Rutina a la que pertenece |
| `step_order` | INTEGER | No | Orden del paso dentro de la rutina |
| `time_of_day` | VARCHAR(10) | No | Momento de uso (`am`, `pm`, `both`) |
| `product_name` | VARCHAR(255) | No | Nombre del producto sugerido por la IA |
| `product_category` | VARCHAR(50) | Sí | Categoría (`cleanser`, `moisturizer`, `spf`, `serum`, etc.) |
| `reason` | VARCHAR(500) | Sí | Por qué la IA recomienda este producto/paso |
| `product_id` | INTEGER FK → products | Sí | Producto concreto de la BD (si existe coincidencia) |
| `ai_suggested` | BOOLEAN | No | Si fue generado por la IA |
| `user_replaced` | BOOLEAN | No | Si el usuario reemplazó el producto sugerido |
| `replaced_with` | VARCHAR(255) | Sí | Nombre del producto con el que lo reemplazó |
| `is_active` | BOOLEAN | No | Si este paso sigue activo |

---

## 8. `skin_checks`

Registro de seguimiento diario de la rutina.

| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER PK | No | Identificador único |
| `user_id` | INTEGER FK → users | No | Usuario que registra |
| `routine_id` | INTEGER FK → routines | No | Rutina sobre la que hace el check |
| `followed_routine` | BOOLEAN | No | Si siguió la rutina ese día |
| `notes` | VARCHAR(500) | Sí | Notas libres del usuario |
| `created_at` | TIMESTAMPTZ | No | Fecha del registro |

---

## 9. `products`

Catálogo de productos de cosmética.

| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER PK | No | Identificador único |
| `name` | VARCHAR(255) | No | Nombre del producto |
| `brand` | VARCHAR(100) | Sí | Marca del producto |
| `category` | VARCHAR(50) | Sí | Categoría (`cleanser`, `moisturizer`, `spf`, `serum`, etc.) |
| `description` | TEXT | Sí | Descripción del producto |
| `highlights` | JSONB | Sí | Destacados (`["#alcohol-free", "#fragrance-free"]`) |
| `suitable_for` | JSONB | Sí | Tipos de piel compatibles (`["seca", "sensible"]`) |
| `source_url` | VARCHAR(512) UNIQUE | No | URL de origen (scraping) |
| `last_scraped_at` | TIMESTAMPTZ | Sí | Última vez que se actualizó por scraping |
| `created_at` | TIMESTAMPTZ | No | Fecha de inserción |

---

## 10. `ingredients`

Diccionario de ingredientes INCI.

| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER PK | No | Identificador único |
| `inci_name` | VARCHAR(255) UNIQUE | No | Nombre INCI oficial |
| `function` | VARCHAR(255) | Sí | Función cosmética (`solvent`, `emollient`, `moisturizer`) |
| `rating` | VARCHAR(50) | Sí | Valoración (`Superstar`, `Good stuff`, `OK`, `Caution`) |
| `description` | TEXT | Sí | Descripción del ingrediente |
| `created_at` | TIMESTAMPTZ | No | Fecha de inserción |

---

## 11. `product_ingredients`

Tabla intermedia que vincula productos con sus ingredientes.

| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER PK | No | Identificador único |
| `product_id` | INTEGER FK → products | No | Producto |
| `ingredient_id` | INTEGER FK → ingredients | No | Ingrediente |
| `position` | INTEGER | No | Posición en la lista (1 = primero, mayor concentración) |
| `irr_com` | VARCHAR(20) | Sí | Marcador de irritancia / comedogenicidad |
