# SkinAI — Propuesta Final de Base de Datos
## Arquitectura relacional unificada · PostgreSQL

> **Fuente:** BD actual + propuesta-estructura-lesion.md + output del modelo IA
> **Convención:** `snake_case` · tipos nativos PostgreSQL
> **Versión:** 1.0 · Junio 2026

---

## Resumen de tablas

| # | Tabla | Tipo | Descripción |
|---|-------|------|-------------|
| 1 | `users` | Transaccional | Cuentas y autenticación |
| 2 | `consents` | Transaccional | Historial de consentimientos GDPR |
| 3 | `password_reset_tokens` | Transaccional | Tokens de recuperación de contraseña |
| 4 | `skin_profiles` | Transaccional | Perfil dermatológico del usuario (ampliado) |
| 5 | `analyses` | Transaccional | Análisis de imagen con resultado del modelo IA |
| 6 | `analysis_zone_metrics` | Transaccional | Métricas por zona facial de cada análisis |
| 7 | `routines` | Transaccional | Rutinas de cuidado generadas por análisis |
| 8 | `routine_steps` | Transaccional | Pasos individuales de una rutina |
| 9 | `skin_checks` | Transaccional | Seguimiento diario de adherencia a la rutina |
| 10 | `products` | Catálogo | Productos cosméticos (fuente: INCIapi) |
| 11 | `ingredients` | Catálogo | Diccionario INCI de ingredientes |
| 12 | `product_ingredients` | Catálogo | Relación producto ↔ ingrediente con posición |
| 13 | `conditions` | Referencia | Catálogo de las 8 condiciones detectables |
| 14 | `condition_repercussions` | Referencia | Efectos clínicos por condición |
| 15 | `condition_symptoms` | Referencia | Síntomas subjetivos por condición |
| 16 | `condition_phases` | Referencia | Fases de evolución por condición |
| 17 | `treatment_needs` | Referencia | Necesidades terapéuticas por condición |
| 18 | `recommended_ingredients` | Referencia | Activos recomendados por condición y fase |
| 19 | `avoided_ingredients` | Referencia | Ingredientes a evitar por condición y perfil |
| 20 | `avoid_reasons` | Referencia | Catálogo de razones clínicas de exclusión |
| 21 | `comedogenic_index_scale` | Referencia | Escala Kligman & Mills 0–5 |

---

## Grupos funcionales

```
AUTENTICACIÓN & USUARIO          CATÁLOGO CLÍNICO (Referencia)
  users                            conditions
  consents                         condition_repercussions
  password_reset_tokens            condition_symptoms
  skin_profiles                    condition_phases
        │                          treatment_needs
        │                          recommended_ingredients
  ANÁLISIS & IA                    avoided_ingredients
  analyses ────────────────────►   avoid_reasons
  analysis_zone_metrics            comedogenic_index_scale
        │
        │                        CATÁLOGO DE PRODUCTOS
  RUTINA & SEGUIMIENTO             products
  routines                         ingredients
  routine_steps ──────────────►    product_ingredients
  skin_checks
```

---

## GRUPO 1 — Autenticación y Usuario

---

### 1. `users`
Cuentas de usuario y autenticación.

| Campo | Tipo PostgreSQL | Nulo | Restricción | Descripción |
|-------|----------------|------|-------------|-------------|
| `id` | `SERIAL` | No | PK | Identificador único autoincremental |
| `email` | `VARCHAR(255)` | No | UNIQUE · NOT NULL | Correo electrónico (identificador de login) |
| `hashed_password` | `VARCHAR(255)` | No | NOT NULL | Contraseña hasheada (Argon2) |
| `full_name` | `VARCHAR(255)` | Sí | NULL | Nombre completo del usuario |
| `is_active` | `BOOLEAN` | No | NOT NULL · DEFAULT TRUE | Cuenta activa o suspendida |
| `created_at` | `TIMESTAMPTZ` | No | NOT NULL · DEFAULT NOW() | Fecha de registro |
| `updated_at` | `TIMESTAMPTZ` | No | NOT NULL · DEFAULT NOW() | Última modificación |

> `gdpr_accepted` se elimina de `users` y se gestiona completamente en `consents` para tener historial y no solo un flag.

---

### 2. `consents`
Historial de consentimientos GDPR por usuario.

| Campo | Tipo PostgreSQL | Nulo | Restricción | Descripción |
|-------|----------------|------|-------------|-------------|
| `id` | `SERIAL` | No | PK | Identificador único |
| `user_id` | `INTEGER` | No | FK → users(id) · NOT NULL | Usuario al que pertenece |
| `gdpr_accepted` | `BOOLEAN` | No | NOT NULL | Aceptación RGPD/GDPR |
| `data_processing` | `BOOLEAN` | No | NOT NULL | Consentimiento para procesamiento de datos |
| `image_storage` | `BOOLEAN` | No | NOT NULL | Consentimiento para almacenamiento de imágenes |
| `ai_analysis` | `BOOLEAN` | No | NOT NULL | Consentimiento para análisis con IA |
| `ip_address` | `INET` | Sí | NULL | IP desde donde se aceptó (IPv4/IPv6 nativo) |
| `accepted_at` | `TIMESTAMPTZ` | No | NOT NULL · DEFAULT NOW() | Momento exacto de aceptación |

---

### 3. `password_reset_tokens`
Tokens de restablecimiento de contraseña.

| Campo | Tipo PostgreSQL | Nulo | Restricción | Descripción |
|-------|----------------|------|-------------|-------------|
| `id` | `SERIAL` | No | PK | Identificador único |
| `user_id` | `INTEGER` | No | FK → users(id) · NOT NULL | Usuario propietario del token |
| `token` | `VARCHAR(64)` | No | UNIQUE · NOT NULL | Token aleatorio seguro |
| `used` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Si el token ya fue consumido |
| `expires_at` | `TIMESTAMPTZ` | No | NOT NULL | Fecha de expiración |
| `created_at` | `TIMESTAMPTZ` | No | NOT NULL · DEFAULT NOW() | Fecha de creación |

---

### 4. `skin_profiles`
Perfil dermatológico del usuario. Relación 1-a-1 con `users`. **Ampliado** con variables clínicas requeridas por el motor de recomendación.

| Campo | Tipo PostgreSQL | Nulo | Restricción | Descripción |
|-------|----------------|------|-------------|-------------|
| `id` | `SERIAL` | No | PK | Identificador único |
| `user_id` | `INTEGER` | No | FK → users(id) · UNIQUE · NOT NULL | Usuario propietario (1-a-1) |
| `birth_date` | `DATE` | Sí | NULL | Fecha de nacimiento (para calcular edad exacta) |
| `sex` | `VARCHAR(20)` | Sí | NULL | Sexo biológico: `male` · `female` · `other` · `prefer_not_to_say` |
| `fitzpatrick` | `VARCHAR(5)` | Sí | NULL | Fototipo: `I` · `II` · `III` · `IV` · `V` · `VI` · `unknown` |
| `skin_type` | `VARCHAR(20)` | Sí | NULL | Tipo de piel: `oily` · `combination` · `dry` · `sensitive` · `normal` |
| `skin_conditions` | `JSONB` | Sí | NULL | Condiciones declaradas p.ej. `["acne","rosacea"]` |
| `allergies` | `JSONB` | Sí | NULL | Ingredientes alérgicos libres declarados |
| `allergy_fragrance` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Alergia documentada a fragancias |
| `allergy_paraben` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Alergia documentada a parabenos |
| `allergy_salicylic_acid` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Sensibilidad al ácido salicílico |
| `allergy_lanolin` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Alergia a lanolina |
| `allergy_benzoyl_peroxide` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Alergia al peróxido de benzoílo |
| `allergy_propylene_glycol` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Sensibilidad al propilenglicol |
| `allergy_chemical_uv_filter` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Alergia a filtros UV químicos |
| `is_pregnant` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Embarazo activo |
| `is_breastfeeding` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Lactancia activa |
| `has_menstrual_cycle` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Ciclo menstrual activo |
| `has_pcos` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Síndrome de ovario poliquístico |
| `is_menopausal` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Menopausia activa |
| `is_smoker` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Fumador/a activo/a |
| `is_immunocompromised` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Estado de inmunocompromiso |
| `sun_exposure` | `VARCHAR(20)` | Sí | NULL | Exposición solar: `low` · `moderate` · `high` |
| `hydration_level` | `VARCHAR(20)` | Sí | NULL | Ingesta de agua: `low` · `adequate` · `high` |
| `ac_exposure` | `VARCHAR(20)` | Sí | NULL | Exposición a A/C o calefacción: `never` · `sometimes` · `constant` |
| `country` | `VARCHAR(100)` | Sí | NULL | País de residencia |
| `city` | `VARCHAR(100)` | Sí | NULL | Ciudad de residencia |
| `updated_at` | `TIMESTAMPTZ` | No | NOT NULL · DEFAULT NOW() | Última actualización del perfil |

> **Campos eliminados vs. BD actual:** `gender` → renombrado a `sex` para alinear con nomenclatura clínica de la propuesta.
> **Campos nuevos:** alergias específicas booleanas, `is_pregnant`, `is_breastfeeding`, `has_menstrual_cycle`, `has_pcos`, `is_menopausal`, `is_smoker`, `is_immunocompromised`, `sun_exposure`, `hydration_level`, `ac_exposure`.

---

## GRUPO 2 — Análisis e IA

---

### 5. `analyses`
Cada análisis de imagen enviado. Almacena el resultado completo del modelo.

| Campo | Tipo PostgreSQL | Nulo | Restricción | Descripción |
|-------|----------------|------|-------------|-------------|
| `id` | `SERIAL` | No | PK | Identificador único |
| `user_id` | `INTEGER` | No | FK → users(id) · NOT NULL | Usuario que realizó el análisis |
| `censored_filename` | `VARCHAR(255)` | Sí | NULL | Imagen censurada almacenada (ojos/boca) |
| `face_censored` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Si la imagen fue censurada correctamente |
| `lighting` | `VARCHAR(50)` | Sí | NULL | Condición de luz: `natural` · `artificial` · `low` · `unknown` |
| `device` | `VARCHAR(255)` | Sí | NULL | Dispositivo/navegador del usuario |
| `status` | `VARCHAR(20)` | No | NOT NULL · DEFAULT 'processing' | Estado: `processing` · `completed` · `failed` |
| `error_message` | `VARCHAR(500)` | Sí | NULL | Mensaje de error si `status = failed` |
| `top1_label` | `VARCHAR(50)` | Sí | NULL | Etiqueta principal predicha (ej. `seborrheic_dermatitis`) |
| `top1_confidence` | `NUMERIC(6,4)` | Sí | NULL | Confianza de la predicción principal (0.0000–1.0000) |
| `top_n_predictions` | `JSONB` | Sí | NULL | Array con todas las predicciones `[{label, prob}, ...]` |
| `severity_score` | `NUMERIC(6,4)` | Sí | NULL | Score global de severidad del modelo (0.0–1.0) |
| `worst_zone` | `VARCHAR(50)` | Sí | NULL | Zona facial con mayor severidad (ej. `mejilla_der`) |
| `affected_zones_count` | `SMALLINT` | Sí | NULL | Cantidad de zonas afectadas detectadas |
| `profile_consistency` | `NUMERIC(6,4)` | Sí | NULL | Consistencia entre resultado IA y perfil declarado (0.0–1.0) |
| `condition_key` | `VARCHAR(50)` | Sí | FK → conditions(condition_key) · NULL | Condición clínica mapeada desde top1_label |
| `condition_phase_key` | `VARCHAR(80)` | Sí | NULL | Fase de la condición asignada por el motor de recomendación |
| `model_version` | `VARCHAR(50)` | Sí | NULL | Versión del modelo IA (ej. `efficientnet_b3`) |
| `tta_passes` | `SMALLINT` | Sí | NULL | Número de pasadas TTA usadas |
| `zone_schema_version` | `VARCHAR(10)` | Sí | NULL | Versión del esquema de zonas (ej. `v3`) |
| `result_raw` | `JSONB` | Sí | NULL | JSON completo sin procesar del modelo |
| `created_at` | `TIMESTAMPTZ` | No | NOT NULL · DEFAULT NOW() | Fecha de creación |
| `completed_at` | `TIMESTAMPTZ` | Sí | NULL | Fecha de finalización del análisis |

> **Campos eliminados vs. BD actual:** `original_filename` (GDPR — nunca persistir) · `lighting` se conserva · `device` se conserva.
> **Campos nuevos desde el output del modelo:** `top_n_predictions`, `severity_score`, `worst_zone`, `affected_zones_count`, `profile_consistency`, `condition_key`, `condition_phase_key`, `tta_passes`, `zone_schema_version`, `result_raw`.
> **Renombrado:** `result` → `result_raw` para claridad semántica.

---

### 6. `analysis_zone_metrics`
Métricas detalladas por zona facial de cada análisis. Normaliza el JSON `zones_display` y `zones_diagnostic` del modelo.

| Campo | Tipo PostgreSQL | Nulo | Restricción | Descripción |
|-------|----------------|------|-------------|-------------|
| `id` | `SERIAL` | No | PK | Identificador único |
| `analysis_id` | `INTEGER` | No | FK → analyses(id) · NOT NULL | Análisis al que pertenece |
| `zone_name` | `VARCHAR(50)` | No | NOT NULL | Nombre de la zona: `frente` · `mejilla_izq` · `mejilla_der` · `nariz` · `menton` · `ceja_izq` · `ceja_der` · `nariz_lat_izq` · `nariz_lat_der` · `mandibula_izq` · `mandibula_der` · `zona_perioral` |
| `zone_type` | `VARCHAR(20)` | No | NOT NULL | `display` (visible al usuario) · `diagnostic` (uso interno del modelo) |
| `erythema` | `NUMERIC(6,4)` | Sí | NULL | Score de eritema en la zona (0.0–1.0) |
| `comedones` | `NUMERIC(6,4)` | Sí | NULL | Score de comedones en la zona (0.0–1.0) |
| `scales` | `NUMERIC(6,4)` | Sí | NULL | Score de escamas en la zona (0.0–1.0) |
| `severity` | `NUMERIC(6,4)` | Sí | NULL | Score de severidad compuesto en la zona (0.0–1.0) |

> Esta tabla permite comparar evolución por zona entre análisis sin depender del JSON completo.

---

## GRUPO 3 — Rutina y Seguimiento

---

### 7. `routines`
Rutinas de cuidado generadas a partir de un análisis.

| Campo | Tipo PostgreSQL | Nulo | Restricción | Descripción |
|-------|----------------|------|-------------|-------------|
| `id` | `SERIAL` | No | PK | Identificador único |
| `user_id` | `INTEGER` | No | FK → users(id) · NOT NULL | Usuario propietario |
| `analysis_id` | `INTEGER` | Sí | FK → analyses(id) · NULL | Análisis que originó esta rutina |
| `condition_key` | `VARCHAR(50)` | Sí | FK → conditions(condition_key) · NULL | Condición principal de la rutina |
| `condition_phase_key` | `VARCHAR(80)` | Sí | NULL | Fase de la condición en el momento de creación |
| `is_active` | `BOOLEAN` | No | NOT NULL · DEFAULT TRUE | Si esta es la rutina activa del usuario |
| `locked` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Rutina bloqueada: no se reemplazará en próximo análisis si el usuario tiene productos activos |
| `created_at` | `TIMESTAMPTZ` | No | NOT NULL · DEFAULT NOW() | Fecha de creación |
| `updated_at` | `TIMESTAMPTZ` | No | NOT NULL · DEFAULT NOW() | Última modificación |

> **Campo clave nuevo: `locked`** — Resuelve el problema de pérdida de dinero del usuario. Si `locked = TRUE` el motor de recomendación **no reemplaza** los productos actuales a menos que el nuevo análisis detecte un cambio severo de condición. La lógica de negocio evalúa delta de condición antes de proponer cambios.

---

### 8. `routine_steps`
Pasos individuales de una rutina.

| Campo | Tipo PostgreSQL | Nulo | Restricción | Descripción |
|-------|----------------|------|-------------|-------------|
| `id` | `SERIAL` | No | PK | Identificador único |
| `routine_id` | `INTEGER` | No | FK → routines(id) · NOT NULL | Rutina a la que pertenece |
| `step_order` | `SMALLINT` | No | NOT NULL | Orden del paso dentro de la rutina |
| `time_of_day` | `VARCHAR(10)` | No | NOT NULL | Momento de uso: `am` · `pm` · `both` |
| `product_category` | `VARCHAR(50)` | Sí | NULL | Categoría: `cleanser` · `moisturizer` · `spf` · `serum` · `treatment` · `eye_cream` |
| `ingredient_key` | `VARCHAR(100)` | Sí | FK → recommended_ingredients(ingredient_key) · NULL | Activo clínico recomendado para este paso |
| `product_id` | `INTEGER` | Sí | FK → products(id) · NULL | Producto concreto de catálogo (si existe) |
| `product_name` | `VARCHAR(255)` | Sí | NULL | Nombre del producto (libre, si no hay match en catálogo) |
| `reason` | `VARCHAR(500)` | Sí | NULL | Justificación clínica de este paso |
| `concentration_suggested` | `NUMERIC(5,2)` | Sí | NULL | Concentración sugerida del activo (%) |
| `ai_suggested` | `BOOLEAN` | No | NOT NULL · DEFAULT TRUE | Si fue generado por la IA |
| `user_replaced` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Si el usuario reemplazó el producto sugerido |
| `replaced_with_product_id` | `INTEGER` | Sí | FK → products(id) · NULL | ID del producto con el que lo reemplazó |
| `replaced_with_name` | `VARCHAR(255)` | Sí | NULL | Nombre libre del producto reemplazado |
| `is_active` | `BOOLEAN` | No | NOT NULL · DEFAULT TRUE | Si este paso sigue activo |

> **Eliminado vs. BD actual:** `replaced_with VARCHAR` → dividido en `replaced_with_product_id` (FK) y `replaced_with_name` (libre) para soportar ambos casos.

---

### 9. `skin_checks`
Registro de seguimiento diario de adherencia a la rutina.

| Campo | Tipo PostgreSQL | Nulo | Restricción | Descripción |
|-------|----------------|------|-------------|-------------|
| `id` | `SERIAL` | No | PK | Identificador único |
| `user_id` | `INTEGER` | No | FK → users(id) · NOT NULL | Usuario que registra |
| `routine_id` | `INTEGER` | No | FK → routines(id) · NOT NULL | Rutina sobre la que hace el check |
| `followed_routine` | `BOOLEAN` | No | NOT NULL | Si siguió la rutina ese día |
| `notes` | `VARCHAR(500)` | Sí | NULL | Notas libres del usuario |
| `created_at` | `TIMESTAMPTZ` | No | NOT NULL · DEFAULT NOW() | Fecha del registro |

---

## GRUPO 4 — Catálogo de Productos

---

### 10. `products`
Catálogo de productos cosméticos (scrapeados desde INCIapi).

| Campo | Tipo PostgreSQL | Nulo | Restricción | Descripción |
|-------|----------------|------|-------------|-------------|
| `id` | `SERIAL` | No | PK | Identificador único |
| `name` | `VARCHAR(255)` | No | NOT NULL | Nombre del producto |
| `brand` | `VARCHAR(100)` | Sí | NULL | Marca del producto |
| `category` | `VARCHAR(50)` | Sí | NULL | Categoría: `cleanser` · `moisturizer` · `spf` · `serum` · `treatment` |
| `description` | `TEXT` | Sí | NULL | Descripción del producto |
| `highlights` | `JSONB` | Sí | NULL | Etiquetas: `["#alcohol-free", "#fragrance-free", "#non-comedogenic"]` |
| `suitable_for` | `JSONB` | Sí | NULL | Tipos de piel compatibles: `["dry", "sensitive"]` |
| `suitable_conditions` | `JSONB` | Sí | NULL | Condiciones para las que aplica: `["acne_comedonal", "seborrheic_dermatitis"]` |
| `fragrance_free` | `BOOLEAN` | Sí | NULL | Sin fragancias (derivado de highlights o scraping) |
| `alcohol_free` | `BOOLEAN` | Sí | NULL | Sin alcohol (derivado de highlights) |
| `non_comedogenic` | `BOOLEAN` | Sí | NULL | No comedogénico (derivado de highlights) |
| `spf_value` | `SMALLINT` | Sí | NULL | Factor SPF si aplica (ej. `30`, `50`) |
| `spf_type` | `VARCHAR(20)` | Sí | NULL | Tipo de filtro SPF: `mineral` · `chemical` · `mixed` |
| `comedogenic_index_max` | `NUMERIC(3,1)` | Sí | NULL | Índice comedogénico máximo de la fórmula (calculado) |
| `pregnancy_safe` | `BOOLEAN` | Sí | NULL | Marcado como seguro en embarazo |
| `source_url` | `VARCHAR(512)` | No | UNIQUE · NOT NULL | URL de origen del scraping (INCIapi) |
| `last_scraped_at` | `TIMESTAMPTZ` | Sí | NULL | Última actualización por scraping |
| `created_at` | `TIMESTAMPTZ` | No | NOT NULL · DEFAULT NOW() | Fecha de inserción |

> **Campos nuevos desde INCIapi:** `suitable_conditions`, `fragrance_free`, `alcohol_free`, `non_comedogenic`, `spf_value`, `spf_type`, `comedogenic_index_max`, `pregnancy_safe`.

---

### 11. `ingredients`
Diccionario de ingredientes INCI.

| Campo | Tipo PostgreSQL | Nulo | Restricción | Descripción |
|-------|----------------|------|-------------|-------------|
| `id` | `SERIAL` | No | PK | Identificador único |
| `inci_name` | `VARCHAR(255)` | No | UNIQUE · NOT NULL | Nombre INCI oficial |
| `common_name` | `VARCHAR(255)` | Sí | NULL | Nombre común o comercial |
| `function` | `VARCHAR(255)` | Sí | NULL | Función cosmética (ej. `emollient` · `solvent` · `moisturizer`) |
| `rating` | `VARCHAR(50)` | Sí | NULL | Valoración INCIapi: `Superstar` · `Good stuff` · `OK` · `Caution` |
| `comedogenic_index` | `NUMERIC(3,1)` | Sí | NULL | Índice Kligman & Mills (0.0–5.0) |
| `is_fragrance` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Si es agente de fragancia |
| `is_alcohol` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Si es alcohol desnaturalizado |
| `is_paraben` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Si pertenece a la familia de parabenos |
| `pregnancy_risk` | `VARCHAR(20)` | Sí | NULL | Categoría FDA de riesgo en embarazo: `A` · `B` · `C` · `D` · `X` · `unknown` |
| `avoid_reason_key` | `VARCHAR(80)` | Sí | FK → avoid_reasons(reason_key) · NULL | Razón clínica principal de exclusión (si aplica) |
| `description` | `TEXT` | Sí | NULL | Descripción del ingrediente |
| `created_at` | `TIMESTAMPTZ` | No | NOT NULL · DEFAULT NOW() | Fecha de inserción |

> **Campos nuevos:** `common_name`, `comedogenic_index`, `is_fragrance`, `is_alcohol`, `is_paraben`, `pregnancy_risk`, `avoid_reason_key`.

---

### 12. `product_ingredients`
Relación producto ↔ ingrediente con posición en la fórmula.

| Campo | Tipo PostgreSQL | Nulo | Restricción | Descripción |
|-------|----------------|------|-------------|-------------|
| `id` | `SERIAL` | No | PK | Identificador único |
| `product_id` | `INTEGER` | No | FK → products(id) · NOT NULL | Producto |
| `ingredient_id` | `INTEGER` | No | FK → ingredients(id) · NOT NULL | Ingrediente |
| `position` | `SMALLINT` | No | NOT NULL | Posición en la lista INCI (1 = primer ingrediente = mayor concentración) |
| `irr_com` | `VARCHAR(20)` | Sí | NULL | Marcador de irritancia/comedogenicidad del ingrediente en este producto |

---

## GRUPO 5 — Catálogo Clínico (Referencia)

> Tablas de solo lectura. Se poblan una vez y son consumidas por el motor de recomendación.

---

### 13. `conditions`
Catálogo maestro de las 8 condiciones detectables.

| Campo | Tipo PostgreSQL | Nulo | Restricción | Descripción |
|-------|----------------|------|-------------|-------------|
| `id` | `SERIAL` | No | PK | Identificador único |
| `condition_key` | `VARCHAR(50)` | No | UNIQUE · NOT NULL | Clave snake_case: `acne_comedonal` · `acne_excorie` · `acne_inflammatory` · `rosacea_etr` · `rosacea_inflammatory` · `perioral_dermatitis` · `seborrheic_dermatitis` · `healthy_skin` |
| `model_label` | `VARCHAR(50)` | No | UNIQUE · NOT NULL | Etiqueta del modelo IA: `acne-comedonal` · `acne-excoriated` · `acne-inflammatory` · `rosacea-etr` · `rosacea-inflammatory` · `perioral-dermatitis` · `seborrheic-dermatitis` · `healthy-skin` |
| `model_index` | `SMALLINT` | No | UNIQUE · NOT NULL | Índice numérico del modelo: `0`–`7` |
| `condition_name` | `VARCHAR(100)` | No | NOT NULL | Nombre legible en español para UI |
| `severity_level` | `VARCHAR(20)` | No | NOT NULL | Severidad base: `mild` · `moderate` · `severe` · `preventive` |
| `is_inflammatory` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Si hay inflamación activa |
| `requires_medical_referral` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Si requiere derivación médica |
| `has_psychological_component` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Si tiene componente conductual/psicológico relevante |
| `restriction_level` | `VARCHAR(20)` | No | NOT NULL | Nivel de restricción de ingredientes: `minimal` · `moderate` · `strict` · `maximum` |

> **Campo clave nuevo: `model_label` y `model_index`** — Mapeo directo entre el output del modelo IA y el catálogo clínico. Permite que `analyses.top1_label` resuelva automáticamente a `condition_key`.

---

### 14. `condition_repercussions`
Efectos clínicos en la piel por condición.

| Campo | Tipo PostgreSQL | Nulo | Restricción | Descripción |
|-------|----------------|------|-------------|-------------|
| `id` | `SERIAL` | No | PK | Identificador único |
| `condition_key` | `VARCHAR(50)` | No | FK → conditions(condition_key) · NOT NULL | Condición a la que pertenece |
| `repercussion_key` | `VARCHAR(100)` | No | NOT NULL | Clave snake_case de la repercusión |
| `label` | `VARCHAR(200)` | No | NOT NULL | Descripción legible |
| `is_reversible` | `BOOLEAN` | No | NOT NULL | Si es reversible con tratamiento |
| `fototipo_risk` | `VARCHAR(20)` | Sí | NULL | Fototipos con riesgo elevado (ej. `III-VI`); NULL = todos por igual |
| `occurs_without_treatment` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Si ocurre inevitablemente sin tratamiento |

---

### 15. `condition_symptoms`
Síntomas subjetivos por condición.

| Campo | Tipo PostgreSQL | Nulo | Restricción | Descripción |
|-------|----------------|------|-------------|-------------|
| `id` | `SERIAL` | No | PK | Identificador único |
| `condition_key` | `VARCHAR(50)` | No | FK → conditions(condition_key) · NOT NULL | Condición a la que pertenece |
| `symptom_key` | `VARCHAR(100)` | No | NOT NULL | Clave snake_case del síntoma |
| `label` | `VARCHAR(200)` | No | NOT NULL | Descripción legible |
| `is_primary` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Si es el síntoma más representativo |
| `intensity` | `VARCHAR(20)` | No | NOT NULL · DEFAULT 'none' | Intensidad: `none` · `mild` · `moderate` · `severe` |
| `is_physical` | `BOOLEAN` | No | NOT NULL · DEFAULT TRUE | FALSE si es síntoma psicológico/emocional |

---

### 16. `condition_phases`
Fases de evolución por condición.

| Campo | Tipo PostgreSQL | Nulo | Restricción | Descripción |
|-------|----------------|------|-------------|-------------|
| `id` | `SERIAL` | No | PK | Identificador único |
| `condition_key` | `VARCHAR(50)` | No | FK → conditions(condition_key) · NOT NULL | Condición a la que pertenece |
| `phase_key` | `VARCHAR(80)` | No | NOT NULL | Clave snake_case de la fase |
| `label` | `VARCHAR(150)` | No | NOT NULL | Nombre legible |
| `phase_order` | `SMALLINT` | No | NOT NULL | Orden lógico en el proceso (1–4) |
| `trigger_condition` | `TEXT` | No | NOT NULL | Condición lógica que activa esta fase |
| `protocol_summary` | `TEXT` | No | NOT NULL | Resumen del protocolo indicado |
| `spf_minimum` | `SMALLINT` | Sí | NULL | SPF mínimo requerido en esta fase (30 o 50) |

---

### 17. `treatment_needs`
Necesidades terapéuticas por condición.

| Campo | Tipo PostgreSQL | Nulo | Restricción | Descripción |
|-------|----------------|------|-------------|-------------|
| `id` | `SERIAL` | No | PK | Identificador único |
| `condition_key` | `VARCHAR(50)` | No | FK → conditions(condition_key) · NOT NULL | Condición a la que pertenece |
| `need_key` | `VARCHAR(100)` | No | NOT NULL | Clave snake_case de la necesidad |
| `label` | `VARCHAR(200)` | No | NOT NULL | Nombre legible |
| `priority` | `VARCHAR(20)` | No | NOT NULL | Prioridad: `essential` · `high` · `moderate` · `optional` |
| `evidence_level` | `VARCHAR(20)` | No | NOT NULL | Evidencia: `very_high` · `high` · `moderate` · `low` |
| `is_action` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | TRUE si es una acción (no un ingrediente) |

---

### 18. `recommended_ingredients`
Activos recomendados por condición, necesidad y fase.

| Campo | Tipo PostgreSQL | Nulo | Restricción | Descripción |
|-------|----------------|------|-------------|-------------|
| `id` | `SERIAL` | No | PK | Identificador único |
| `condition_key` | `VARCHAR(50)` | No | FK → conditions(condition_key) · NOT NULL | Condición a la que pertenece |
| `need_key` | `VARCHAR(100)` | No | FK → treatment_needs(need_key) · NOT NULL | Necesidad que cubre |
| `ingredient_key` | `VARCHAR(100)` | No | NOT NULL | Clave INCI o nombre estandarizado |
| `label` | `VARCHAR(150)` | No | NOT NULL | Nombre legible |
| `concentration_min` | `NUMERIC(5,2)` | Sí | NULL | Concentración mínima efectiva (%) |
| `concentration_max` | `NUMERIC(5,2)` | Sí | NULL | Concentración máxima recomendada (%) |
| `application_time` | `VARCHAR(10)` | No | NOT NULL | Momento: `am` · `pm` · `am_pm` |
| `contraindicated_if_pregnant` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Contraindicado en embarazo |
| `phase_restriction` | `VARCHAR(30)` | Sí | NULL | Fase en que aplica: NULL (todas) · `active_only` · `healing_only` · `maintenance_only` |

---

### 19. `avoided_ingredients`
Ingredientes a evitar por condición y perfil del usuario.

| Campo | Tipo PostgreSQL | Nulo | Restricción | Descripción |
|-------|----------------|------|-------------|-------------|
| `id` | `SERIAL` | No | PK | Identificador único |
| `condition_key` | `VARCHAR(50)` | No | FK → conditions(condition_key) · NOT NULL | Condición a la que aplica |
| `ingredient_key` | `VARCHAR(100)` | No | NOT NULL | Clave del ingrediente o formato a evitar |
| `label` | `VARCHAR(200)` | No | NOT NULL | Nombre legible |
| `avoid_reason_key` | `VARCHAR(80)` | No | FK → avoid_reasons(reason_key) · NOT NULL | Razón clínica de exclusión |
| `comedogenic_index` | `NUMERIC(3,1)` | Sí | NULL | Índice Kligman & Mills; NULL si no aplica |
| `severity` | `VARCHAR(20)` | No | NOT NULL | Obligatoriedad: `mandatory` · `recommended` · `conditional` |
| `applies_only_if_skin_type` | `VARCHAR(30)` | Sí | NULL | NULL = todos los tipos de piel |
| `applies_only_if_pregnant` | `BOOLEAN` | No | NOT NULL · DEFAULT FALSE | Solo aplica si el usuario está embarazada |
| `phase_restriction` | `VARCHAR(30)` | Sí | NULL | NULL = todas las fases · `active_only` · `healing_only` |

---

### 20. `avoid_reasons`
Catálogo de razones clínicas de exclusión de ingredientes.

| Campo | Tipo PostgreSQL | Nulo | Restricción | Descripción |
|-------|----------------|------|-------------|-------------|
| `id` | `SERIAL` | No | PK | Identificador único |
| `reason_key` | `VARCHAR(80)` | No | UNIQUE · NOT NULL | Clave snake_case: `comedogenicity` · `barrier_disruption` · `microbiome_alteration` · `secondary_inflammation` · `mechanical_abrasion` · `teratogenicity` · `vasodilation` · `trpv1_activation` · `photosensitization` · `fungal_substrate` · `occlusion_perioral` · `steroid_rebound` · `active_interaction` · `ph_disruption` |
| `label` | `VARCHAR(150)` | No | NOT NULL | Nombre legible |
| `description` | `TEXT` | No | NOT NULL | Explicación clínica completa |

---

### 21. `comedogenic_index_scale`
Escala de comedogenicidad de referencia (Kligman & Mills, 0–5).

| Campo | Tipo PostgreSQL | Nulo | Restricción | Descripción |
|-------|----------------|------|-------------|-------------|
| `id` | `SERIAL` | No | PK | Identificador único |
| `index_value` | `NUMERIC(3,1)` | No | UNIQUE · NOT NULL | Valor: `0.0` · `1.0` · `2.0` · `3.0` · `4.0` · `5.0` |
| `risk_level` | `VARCHAR(20)` | No | NOT NULL | Nivel de riesgo: `none` · `minimal` · `low` · `moderate` · `high` · `very_high` |
| `recommendation` | `VARCHAR(30)` | No | NOT NULL | Recomendación: `safe` · `generally_safe` · `use_with_caution` · `avoid_oily_skin` · `avoid` · `always_avoid` |
| `max_allowed_skin_type` | `TEXT` | No | NOT NULL | Tipos de piel que lo permiten (CSV): `all` · `dry,normal,sensitive` · `dry,normal` · `none` |
| `example_ingredients` | `TEXT` | No | NOT NULL | Ingredientes representativos del nivel |

---

## Notas de diseño y decisiones clave

### Problema: pérdida de dinero por cambio de rutina entre análisis
**Solución implementada:** campo `locked` en `routines` (BOOLEAN, DEFAULT FALSE).

- Cuando el usuario confirma que compró productos → `locked = TRUE`.
- El motor de recomendación, antes de generar una rutina nueva, evalúa:
  1. ¿Cambió la condición principal (`condition_key`)? Si el delta es bajo (misma condición, diferente fase) → **ajusta** los pasos existentes sin reemplazar productos.
  2. ¿Cambió la condición a una diferente? → Notifica al usuario y propone cambios graduales, priorizando ingredientes compatibles con los productos que ya tiene.
  3. `locked = TRUE` + mismo condition_key → solo actualiza `condition_phase_key` en la rutina y agrega/quita pasos sin tocar productos con `user_replaced = TRUE`.

### Mapeo entre modelo IA y condiciones clínicas
`conditions.model_label` y `conditions.model_index` permiten resolver directamente:
```
"seborrheic-dermatitis" (output modelo) → condition_key = "seborrheic_dermatitis"
```
Sin transformaciones en el backend aparte del lookup en la tabla.

### Columnas eliminadas con justificación
| Campo eliminado | Tabla origen | Razón |
|----------------|-------------|-------|
| `original_filename` | `analyses` | GDPR — nunca persistir el nombre del archivo original |
| `gdpr_accepted` | `users` | Trasladado completamente a `consents` para tener historial |
| `gender` | `skin_profiles` | Renombrado a `sex` por alineación con nomenclatura clínica |
| `result` (JSON) | `analyses` | Renombrado a `result_raw`; campos principales extraídos a columnas propias |
| `replaced_with VARCHAR` | `routine_steps` | Dividido en FK `replaced_with_product_id` + `replaced_with_name` |

