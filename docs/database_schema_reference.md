# Referencia de Esquema de Base de Datos

Documento de referencia completo con los campos actuales y los campos propuestos para cada tabla. Los campos marcados con `[PROPUESTO]` no existen todavía en el modelo.

---

## Índice

1. [users](#1-users)
2. [skin_profiles](#2-skin_profiles)
3. [consents](#3-consents)
4. [analyses](#4-analyses)
5. [routines](#5-routines)
6. [routine_steps](#6-routine_steps)
7. [skin_checks](#7-skin_checks)
8. [products](#8-products)
9. [ingredients](#9-ingredients)
10. [product_ingredients](#10-product_ingredients)
11. [Tablas propuestas nuevas](#11-tablas-propuestas-nuevas)

---

## 1. `users`

Identidad y acceso de cada cuenta registrada.

| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER PK | No | Identificador único |
| `email` | VARCHAR(255) UNIQUE | No | Correo electrónico |
| `hashed_password` | VARCHAR(255) | No | Contraseña hasheada (bcrypt) |
| `full_name` | VARCHAR(255) | Sí | Nombre completo |
| `gdpr_accepted` | BOOLEAN | No | Aceptación del aviso legal (snapshot) |
| `is_active` | BOOLEAN | No | Cuenta activa / suspendida |
| `created_at` | TIMESTAMPTZ | No | Fecha de registro |
| `updated_at` | TIMESTAMPTZ | No | Última modificación |
| `last_login_at` | TIMESTAMPTZ | Sí | `[PROPUESTO]` Fecha del último inicio de sesión |
| `email_verified` | BOOLEAN | No | `[PROPUESTO]` Si el correo fue verificado |
| `email_verified_at` | TIMESTAMPTZ | Sí | `[PROPUESTO]` Cuándo se verificó el correo |
| `preferred_language` | VARCHAR(10) | Sí | `[PROPUESTO]` Idioma preferido (`es`, `en`, `fr`…) |
| `avatar_url` | VARCHAR(512) | Sí | `[PROPUESTO]` URL de foto de perfil |
| `role` | VARCHAR(20) | No | `[PROPUESTO]` Rol del usuario (`user`, `admin`, `dermatologist`) |
| `deleted_at` | TIMESTAMPTZ | Sí | `[PROPUESTO]` Soft-delete (baja sin destruir datos) |

---

## 2. `skin_profiles`

Perfil dermatológico y contextual del usuario (1-a-1 con `users`).

| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER PK | No | Identificador único |
| `user_id` | INTEGER FK → users | No | Usuario propietario |
| `birth_date` | DATE | Sí | Fecha de nacimiento |
| `gender` | VARCHAR(20) | Sí | Género (`male`, `female`, `non-binary`, `prefer_not_to_say`) |
| `fitzpatrick` | VARCHAR(5) | Sí | Fototipo de Fitzpatrick (I–VI) |
| `skin_type` | VARCHAR(20) | Sí | Tipo de piel (`seca`, `grasa`, `mixta`, `normal`, `sensible`) |
| `skin_conditions` | JSONB | Sí | Condiciones activas (`["acne", "rosácea"]`) | VER CÓMO AJUSTARLO.
| `allergies` | JSONB | Sí | Ingredientes alérgicos conocidos |
| `country` | VARCHAR(100) | Sí | País de residencia |
| `city` | VARCHAR(100) | Sí | Ciudad de residencia |
| `updated_at` | TIMESTAMPTZ | No | Última actualización del perfil |
| `sun_exposure_daily_hours` | SMALLINT | Sí | `[PROPUESTO]` Horas promedio de exposición solar al día |
| `sunscreen_habit` | VARCHAR(20) | Sí | `[PROPUESTO]` Frecuencia de uso de protector solar (`daily`, `occasional`, `never`) |
| `smoking_status` | VARCHAR(20) | Sí | `[PROPUESTO]` Hábito de fumar (`never`, `former`, `current`) |
| `stress_level_avg` | SMALLINT | Sí | `[PROPUESTO]` Nivel de estrés promedio (1–5) |
| `sleep_hours_avg` | NUMERIC(3,1) | Sí | `[PROPUESTO]` Horas de sueño promedio |
| `water_intake_liters` | NUMERIC(3,1) | Sí | `[PROPUESTO]` Ingesta diaria de agua en litros |
| `diet_type` | VARCHAR(30) | Sí | `[PROPUESTO]` Tipo de dieta (`omnivore`, `vegetarian`, `vegan`, `mediterranean`) |
| `exercise_frequency` | VARCHAR(20) | Sí | `[PROPUESTO]` Frecuencia de ejercicio (`sedentary`, `1-2x_week`, `3-5x_week`, `daily`) |
| `hormonal_treatment` | BOOLEAN | Sí | `[PROPUESTO]` Si usa tratamiento hormonal activo |
| `medications` | JSONB | Sí | `[PROPUESTO]` Medicamentos que pueden afectar la piel (`["isotretinoína"]`) |
| `occupation_exposure` | VARCHAR(30) | Sí | `[PROPUESTO]` Tipo de exposición laboral (`outdoor`, `office`, `industrial`) |
| `menstrual_skin_changes` | BOOLEAN | Sí | `[PROPUESTO]` Si la piel cambia con el ciclo menstrual |

---

## 3. `consents`

Historial auditable de cada versión de consentimientos aceptados.

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
| `consent_version` | VARCHAR(20) | No | `[PROPUESTO]` Versión del documento de términos aceptado (`v1.0`, `v1.2`…) |
| `user_agent` | TEXT | Sí | `[PROPUESTO]` Navegador / dispositivo desde el que se aceptó |
| `revoked_at` | TIMESTAMPTZ | Sí | `[PROPUESTO]` Si el usuario revocó el consentimiento y cuándo |
| `marketing_emails` | BOOLEAN | No | `[PROPUESTO]` Consentimiento para emails de marketing |
| `research_data` | BOOLEAN | No | `[PROPUESTO]` Consentimiento para usar datos en investigación anonimizada |

---

## 4. `analyses`

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
| `result` | JSONB | Sí | Resultado completo del modelo (all_scores, tta_passes, compute) |
| `created_at` | TIMESTAMPTZ | No | Fecha de creación del análisis |
| `completed_at` | TIMESTAMPTZ | Sí | Fecha de finalización del análisis |
| `top2_label` | VARCHAR(50) | Sí | `[PROPUESTO]` Segunda predicción más probable |
| `top2_confidence` | FLOAT | Sí | `[PROPUESTO]` Confianza de la segunda predicción |
| `top3_label` | VARCHAR(50) | Sí | `[PROPUESTO]` Tercera predicción más probable |
| `top3_confidence` | FLOAT | Sí | `[PROPUESTO]` Confianza de la tercera predicción |
| `severity_score` | NUMERIC(4,2) | Sí | `[PROPUESTO]` Puntuación de severidad (0–10) |
| `affected_area_pct` | NUMERIC(5,2) | Sí | `[PROPUESTO]` Porcentaje de la cara afectada (0–100) |
| `image_quality_score` | NUMERIC(4,3) | Sí | `[PROPUESTO]` Calidad de imagen detectada por el modelo (0–1) |
| `face_zone` | VARCHAR(30) | Sí | `[PROPUESTO]` Zona analizada (`full_face`, `t_zone`, `cheek`, `forehead`, `chin`) |
| `processing_time_ms` | INTEGER | Sí | `[PROPUESTO]` Tiempo de inferencia en milisegundos |
| `image_width` | SMALLINT | Sí | `[PROPUESTO]` Ancho original de la imagen en píxeles |
| `image_height` | SMALLINT | Sí | `[PROPUESTO]` Alto original de la imagen en píxeles |
| `user_rating` | SMALLINT | Sí | `[PROPUESTO]` Valoración del usuario sobre la precisión del análisis (1–5) |
| `user_feedback` | TEXT | Sí | `[PROPUESTO]` Texto libre del usuario sobre el resultado |
| `dermatologist_confirmed` | BOOLEAN | Sí | `[PROPUESTO]` Si un dermatólogo revisó y confirmó el diagnóstico |
| `dermatologist_note` | TEXT | Sí | `[PROPUESTO]` Nota del dermatólogo que lo revisó |
| `for_research` | BOOLEAN | No | `[PROPUESTO]` Si el usuario consintió usar este análisis en investigación anonimizada |

---

## 5. `routines`

Rutina de cuidado facial asociada a un análisis.

| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER PK | No | Identificador único |
| `user_id` | INTEGER FK → users | No | Usuario propietario |
| `analysis_id` | INTEGER FK → analyses | Sí | Análisis que originó la rutina |
| `is_active` | BOOLEAN | No | Si esta rutina está activa actualmente |
| `created_at` | TIMESTAMPTZ | No | Fecha de creación |
| `updated_at` | TIMESTAMPTZ | No | Última modificación |
| `name` | VARCHAR(100) | Sí | `[PROPUESTO]` Nombre personalizado dado por el usuario |
| `routine_type` | VARCHAR(20) | No | `[PROPUESTO]` Origen de la rutina (`ai_generated`, `manual`, `professional`) |
| `target_condition` | VARCHAR(50) | Sí | `[PROPUESTO]` Condición que busca tratar (`acne`, `hyperpigmentation`) |
| `notes` | TEXT | Sí | `[PROPUESTO]` Notas del usuario sobre la rutina |
| `deactivated_at` | TIMESTAMPTZ | Sí | `[PROPUESTO]` Cuándo se desactivó la rutina |
| `effectiveness_score` | NUMERIC(4,2) | Sí | `[PROPUESTO]` Puntuación calculada de efectividad basada en skin_checks (0–10) |

---

## 6. `routine_steps`

Pasos individuales de una rutina (cada producto y su momento de uso).

| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER PK | No | Identificador único |
| `routine_id` | INTEGER FK → routines | No | Rutina a la que pertenece |
| `step_order` | INTEGER | No | Orden del paso dentro de la rutina |
| `time_of_day` | VARCHAR(10) | No | Momento de uso (`am`, `pm`, `both`) |
| `product_name` | VARCHAR(255) | No | Nombre del producto sugerido por la IA |
| `product_category` | VARCHAR(50) | Sí | Categoría (`cleanser`, `moisturizer`, `spf`, `serum`, etc.) |
| `reason` | VARCHAR(500) | Sí | Por qué la IA recomienda este producto/paso |
| `product_id` | INTEGER FK → products | Sí | Producto concreto de la base de datos (si existe coincidencia) |
| `ai_suggested` | BOOLEAN | No | Si fue generado por la IA |
| `user_replaced` | BOOLEAN | No | Si el usuario reemplazó el producto sugerido |
| `replaced_with` | VARCHAR(255) | Sí | Nombre del producto con el que lo reemplazó |
| `is_active` | BOOLEAN | No | Si este paso sigue activo |
| `frequency` | VARCHAR(20) | Sí | `[PROPUESTO]` Frecuencia de uso (`daily`, `2x_week`, `weekly`) |
| `application_method` | VARCHAR(50) | Sí | `[PROPUESTO]` Cómo se aplica (`massage`, `pat`, `leave-on`, `wash-off`) |
| `amount_description` | VARCHAR(50) | Sí | `[PROPUESTO]` Cantidad orientativa (`pea-sized`, `a few drops`, `coin-sized`) |
| `wait_time_minutes` | SMALLINT | Sí | `[PROPUESTO]` Minutos de espera antes del siguiente paso |
| `notes` | VARCHAR(500) | Sí | `[PROPUESTO]` Notas específicas de la IA para este paso |
| `product_alternative_id` | INTEGER FK → products | Sí | `[PROPUESTO]` Producto alternativo sugerido |

---

## 7. `skin_checks`

Registro diario de seguimiento de la rutina y estado de la piel.

| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER PK | No | Identificador único |
| `user_id` | INTEGER FK → users | No | Usuario que registra |
| `routine_id` | INTEGER FK → routines | No | Rutina sobre la que hace el check |
| `followed_routine` | BOOLEAN | No | Si siguió la rutina ese día |
| `notes` | VARCHAR(500) | Sí | Notas libres del usuario |
| `created_at` | TIMESTAMPTZ | No | Fecha del registro |
| `skin_overall_rating` | SMALLINT | Sí | `[PROPUESTO]` Valoración general de la piel (1–10) |
| `skin_dryness` | SMALLINT | Sí | `[PROPUESTO]` Nivel de sequedad (1–5) |
| `skin_oiliness` | SMALLINT | Sí | `[PROPUESTO]` Nivel de grasa (1–5) |
| `skin_sensitivity` | SMALLINT | Sí | `[PROPUESTO]` Nivel de sensibilidad/irritación (1–5) |
| `new_breakout` | BOOLEAN | Sí | `[PROPUESTO]` Si apareció un nuevo brote ese día |
| `new_breakout_zone` | VARCHAR(30) | Sí | `[PROPUESTO]` Zona donde apareció el brote (`forehead`, `chin`, `cheek`) |
| `photo_analysis_id` | INTEGER FK → analyses | Sí | `[PROPUESTO]` Análisis fotográfico opcional del día |
| `stress_level` | SMALLINT | Sí | `[PROPUESTO]` Nivel de estrés ese día (1–5) |
| `sleep_hours` | NUMERIC(3,1) | Sí | `[PROPUESTO]` Horas de sueño la noche anterior |
| `menstrual_day` | SMALLINT | Sí | `[PROPUESTO]` Día del ciclo menstrual (1–35, null si no aplica) |
| `diet_notes` | VARCHAR(255) | Sí | `[PROPUESTO]` Notas sobre la alimentación de ese día |
| `weather_humidity_pct` | SMALLINT | Sí | `[PROPUESTO]` Humedad ambiente ese día (0–100%) |
| `weather_temp_celsius` | SMALLINT | Sí | `[PROPUESTO]` Temperatura ambiente ese día |

---

## 8. `products`

Catálogo de productos de cosmética con información scrappeada.

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
| `price_range` | VARCHAR(10) | Sí | `[PROPUESTO]` Rango de precio (`budget`, `mid`, `luxury`) |
| `price_eur` | NUMERIC(8,2) | Sí | `[PROPUESTO]` Precio aproximado en euros |
| `size_ml` | NUMERIC(7,2) | Sí | `[PROPUESTO]` Contenido del producto en ml |
| `fragrance_free` | BOOLEAN | Sí | `[PROPUESTO]` Sin fragancia |
| `alcohol_free` | BOOLEAN | Sí | `[PROPUESTO]` Sin alcohol |
| `paraben_free` | BOOLEAN | Sí | `[PROPUESTO]` Sin parabenos |
| `cruelty_free` | BOOLEAN | Sí | `[PROPUESTO]` No testado en animales |
| `vegan` | BOOLEAN | Sí | `[PROPUESTO]` Fórmula vegana |
| `spf_value` | SMALLINT | Sí | `[PROPUESTO]` Valor SPF si aplica (ej. 30, 50) |
| `ph_level` | NUMERIC(3,1) | Sí | `[PROPUESTO]` pH del producto |
| `texture` | VARCHAR(30) | Sí | `[PROPUESTO]` Textura (`gel`, `cream`, `oil`, `foam`, `balm`) |
| `finish` | VARCHAR(20) | Sí | `[PROPUESTO]` Acabado (`matte`, `dewy`, `natural`) |
| `ean` | VARCHAR(20) | Sí | `[PROPUESTO]` Código de barras EAN para escaneo |
| `is_available` | BOOLEAN | No | `[PROPUESTO]` Si el producto sigue disponible en el mercado |
| `country_of_origin` | VARCHAR(50) | Sí | `[PROPUESTO]` País de fabricación |

---

## 9. `ingredients`

Diccionario de ingredientes INCI con información de seguridad.

| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER PK | No | Identificador único |
| `inci_name` | VARCHAR(255) UNIQUE | No | Nombre INCI oficial |
| `function` | VARCHAR(255) | Sí | Función cosmética (`solvent`, `emollient`, `moisturizer`) |
| `rating` | VARCHAR(50) | Sí | Valoración (`Superstar`, `Good stuff`, `OK`, `Caution`) |
| `description` | TEXT | Sí | Descripción del ingrediente |
| `created_at` | TIMESTAMPTZ | No | Fecha de inserción |
| `comedogenicity_rating` | SMALLINT | Sí | `[PROPUESTO]` Nivel de comedogenicidad (0–5) |
| `irritancy_rating` | SMALLINT | Sí | `[PROPUESTO]` Nivel de irritancia (0–5) |
| `ewg_score` | SMALLINT | Sí | `[PROPUESTO]` Puntuación EWG Skin Deep (1–10) |
| `cas_number` | VARCHAR(30) | Sí | `[PROPUESTO]` Número CAS (identificador químico único) |
| `synonyms` | JSONB | Sí | `[PROPUESTO]` Nombres alternativos del ingrediente |
| `benefits` | JSONB | Sí | `[PROPUESTO]` Lista de beneficios (`["antioxidante", "hidratante"]`) |
| `contraindications` | JSONB | Sí | `[PROPUESTO]` Cuándo no usar (`["embarazo", "piel sensible"]`) |
| `ph_optimal_min` | NUMERIC(3,1) | Sí | `[PROPUESTO]` pH mínimo óptimo para el ingrediente |
| `ph_optimal_max` | NUMERIC(3,1) | Sí | `[PROPUESTO]` pH máximo óptimo para el ingrediente |
| `typical_concentration_pct` | NUMERIC(5,2) | Sí | `[PROPUESTO]` Concentración habitual en fórmulas (%) |
| `pregnancy_safe` | BOOLEAN | Sí | `[PROPUESTO]` Seguro durante el embarazo |

---

## 10. `product_ingredients`

Tabla intermedia que vincula productos con sus ingredientes en orden de fórmula.

| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER PK | No | Identificador único |
| `product_id` | INTEGER FK → products | No | Producto |
| `ingredient_id` | INTEGER FK → ingredients | No | Ingrediente |
| `position` | INTEGER | No | Posición en la lista (1 = primero, mayor concentración) |
| `irr_com` | VARCHAR(20) | Sí | Marcador de irritancia / comedogenicidad específico de esta combinación |

---

## 11. Tablas propuestas nuevas

### 11.1 `notifications` `[PROPUESTO]`

Notificaciones push o email enviadas al usuario.

| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER PK | No | Identificador único |
| `user_id` | INTEGER FK → users | No | Destinatario |
| `type` | VARCHAR(30) | No | Tipo (`routine_reminder`, `analysis_ready`, `tip`) |
| `channel` | VARCHAR(10) | No | Canal (`push`, `email`) |
| `title` | VARCHAR(100) | No | Título de la notificación |
| `body` | TEXT | Sí | Cuerpo del mensaje |
| `is_read` | BOOLEAN | No | Si fue leída |
| `sent_at` | TIMESTAMPTZ | Sí | Cuándo fue enviada |
| `read_at` | TIMESTAMPTZ | Sí | Cuándo fue leída |
| `created_at` | TIMESTAMPTZ | No | Fecha de creación |

---

### 11.2 `user_product_reviews` `[PROPUESTO]`

Valoraciones de los usuarios sobre los productos de sus rutinas.

| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER PK | No | Identificador único |
| `user_id` | INTEGER FK → users | No | Usuario que valora |
| `product_id` | INTEGER FK → products | No | Producto valorado |
| `routine_step_id` | INTEGER FK → routine_steps | Sí | Paso de rutina en el que usó el producto |
| `rating` | SMALLINT | No | Valoración general (1–5) |
| `effectiveness` | SMALLINT | Sí | Valoración de efectividad (1–5) |
| `tolerability` | SMALLINT | Sí | Valoración de tolerabilidad (1–5) |
| `comment` | TEXT | Sí | Comentario libre |
| `would_recommend` | BOOLEAN | Sí | Si lo recomendaría |
| `created_at` | TIMESTAMPTZ | No | Fecha de la valoración |

---

### 11.3 `skin_trends` `[PROPUESTO]`

Resúmenes semanales/mensuales del estado de la piel calculados a partir de skin_checks.

| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER PK | No | Identificador único |
| `user_id` | INTEGER FK → users | No | Usuario |
| `period_start` | DATE | No | Inicio del período (lunes de la semana, 1ro del mes) |
| `period_type` | VARCHAR(10) | No | Granularidad (`weekly`, `monthly`) |
| `avg_skin_rating` | NUMERIC(4,2) | Sí | Media de valoraciones de piel |
| `adherence_pct` | NUMERIC(5,2) | Sí | Porcentaje de días que siguió la rutina (0–100) |
| `breakout_count` | SMALLINT | Sí | Número de brotes registrados en el período |
| `avg_stress` | NUMERIC(3,2) | Sí | Media de nivel de estrés |
| `avg_sleep_hours` | NUMERIC(3,1) | Sí | Media de horas de sueño |
| `snapshot_analysis_id` | INTEGER FK → analyses | Sí | Análisis fotográfico representativo del período |
| `computed_at` | TIMESTAMPTZ | No | Cuándo se calculó el resumen |

---

### 11.4 `educational_content` `[PROPUESTO]`

Artículos, consejos y recursos educativos vinculados a condiciones dermatológicas.

| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER PK | No | Identificador único |
| `condition_tag` | VARCHAR(50) | No | Condición a la que aplica (`acne`, `rosácea`, `hiperpigmentación`) |
| `title` | VARCHAR(255) | No | Título del artículo o consejo |
| `body` | TEXT | No | Contenido |
| `language` | VARCHAR(10) | No | Idioma (`es`, `en`) |
| `source_url` | VARCHAR(512) | Sí | Fuente externa si aplica |
| `is_published` | BOOLEAN | No | Si es visible para los usuarios |
| `created_at` | TIMESTAMPTZ | No | Fecha de creación |
| `updated_at` | TIMESTAMPTZ | No | Última actualización |

---

## Notas de diseño

- Los campos `[PROPUESTO]` requieren migración Alembic antes de ser utilizados.
- Los campos JSONB (`skin_conditions`, `allergies`, `result`, `highlights`, `suitable_for`) permiten flexibilidad pero no son indexables fácilmente; considerar columnas dedicadas para filtros frecuentes.
- El campo `for_research` en `analyses` debe coordinarse con el campo `research_data` en `consents` para garantizar coherencia legal.
- Los campos de condición ambiental en `skin_checks` (`weather_humidity_pct`, `weather_temp_celsius`) podrían obtenerse automáticamente mediante una API de clima en lugar de pedírselos al usuario.
- La tabla `skin_trends` puede calcularse como una vista materializada en vez de una tabla física si el volumen de skin_checks es alto.
