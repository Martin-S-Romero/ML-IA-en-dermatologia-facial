# Propuesta de Estructura de Base de Datos — SkinAI
## Esquema completo por condición cutánea

> **Fuente:** lesiones-descripcion.md (base bibliográfica 2020–2025)
> **Convención:** tipos SQL estándar · valores permitidos separados por ` · `

---

## TABLA 1: `conditions`
Catálogo maestro de las 8 condiciones del sistema.

| Campo | Tipo | Restricción | Valores permitidos | Descripción |
|-------|------|-------------|-------------------|-------------|
| `condition_id` | INT | PK · NOT NULL · AUTO_INCREMENT | — | Identificador único |
| `condition_key` | VARCHAR(50) | UNIQUE · NOT NULL | `acne_comedonal` · `acne_excorie` · `acne_inflammatory` · `rosacea_etr` · `rosacea_inflammatory` · `perioral_dermatitis` · `seborrheic_dermatitis` · `healthy_skin` | Clave snake_case para programación |
| `condition_name` | VARCHAR(100) | NOT NULL | `"Acné Comedonal"` · `"Acné Excoriado"` · `"Acné Inflamatorio"` · `"Rosácea ETR"` · `"Rosácea Inflamatoria"` · `"Dermatitis Perioral"` · `"Dermatitis Seborreica"` · `"Piel Sana"` | Nombre legible para UI |
| `severity_level` | ENUM | NOT NULL | `'mild'` · `'moderate'` · `'severe'` · `'preventive'` | Severidad base de la condición |
| `is_inflammatory` | BOOLEAN | NOT NULL · DEFAULT FALSE | `TRUE` · `FALSE` | Indica si hay inflamación activa |
| `requires_medical_referral` | BOOLEAN | NOT NULL · DEFAULT FALSE | `TRUE` · `FALSE` | Si requiere derivación médica obligatoria |
| `has_psychological_component` | BOOLEAN | NOT NULL · DEFAULT FALSE | `TRUE` · `FALSE` | Si tiene componente conductual/psicológico relevante |
| `restriction_level` | ENUM | NOT NULL | `'minimal'` · `'moderate'` · `'strict'` · `'maximum'` | Qué tan restrictivo es el protocolo de ingredientes |

**Registros:**

| condition_key | severity_level | is_inflammatory | requires_medical_referral | has_psychological_component | restriction_level |
|--------------|---------------|:--------------:|:------------------------:|:--------------------------:|------------------|
| `acne_comedonal` | `'mild'` | FALSE | FALSE | FALSE | `'moderate'` |
| `acne_excorie` | `'moderate'` | FALSE | TRUE | TRUE | `'maximum'` |
| `acne_inflammatory` | `'moderate'` | TRUE | FALSE | FALSE | `'moderate'` |
| `rosacea_etr` | `'moderate'` | FALSE | FALSE | FALSE | `'strict'` |
| `rosacea_inflammatory` | `'severe'` | TRUE | TRUE | FALSE | `'maximum'` |
| `perioral_dermatitis` | `'moderate'` | TRUE | TRUE | FALSE | `'strict'` |
| `seborrheic_dermatitis` | `'moderate'` | FALSE | FALSE | FALSE | `'moderate'` |
| `healthy_skin` | `'preventive'` | FALSE | FALSE | FALSE | `'minimal'` |

---

## TABLA 2: `condition_repercussions`
Efectos clínicos en la piel por condición.

| Campo | Tipo | Restricción | Valores permitidos | Descripción |
|-------|------|-------------|-------------------|-------------|
| `repercussion_id` | INT | PK · NOT NULL · AUTO_INCREMENT | — | Identificador único |
| `condition_key` | VARCHAR(50) | FK → conditions · NOT NULL | Ver tabla 1 | Condición a la que pertenece |
| `repercussion_key` | VARCHAR(100) | NOT NULL | Ver registros | Clave snake_case de la repercusión |
| `label` | VARCHAR(200) | NOT NULL | — | Nombre legible para UI |
| `is_reversible` | BOOLEAN | NOT NULL | `TRUE` · `FALSE` | Si es reversible con tratamiento adecuado |
| `fototipo_risk` | VARCHAR(20) | NULL · DEFAULT NULL | `NULL` · `'I-II'` · `'III-IV'` · `'III-VI'` · `'V-VI'` | Fototipos con riesgo elevado; NULL = todos igual |
| `occurs_without_treatment` | BOOLEAN | NOT NULL · DEFAULT FALSE | `TRUE` · `FALSE` | Si ocurre inevitablemente sin tratamiento |

**Registros — `acne_comedonal`:**

| repercussion_key | label | is_reversible | fototipo_risk | occurs_without_treatment |
|-----------------|-------|:-------------:|:-------------:|:------------------------:|
| `dilated_pores` | Dilatación visible y permanente de poros foliculares | FALSE | NULL | TRUE |
| `rough_skin_texture` | Textura irregular con microrrelieve rugoso | TRUE | NULL | FALSE |
| `progression_to_inflammatory` | Evolución hacia acné inflamatorio por C. acnes | TRUE | NULL | TRUE |
| `hpi_risk` | Riesgo de hiperpigmentación post-inflamatoria | TRUE | `'III-VI'` | FALSE |
| `progressive_pore_enlargement` | Ensanchamiento progresivo de poros en piel grasa | FALSE | NULL | TRUE |

**Registros — `acne_excorie`:**

| repercussion_key | label | is_reversible | fototipo_risk | occurs_without_treatment |
|-----------------|-------|:-------------:|:-------------:|:------------------------:|
| `barrier_rupture_tewl` | Ruptura de barrera cutánea con TEWL elevada | TRUE | NULL | TRUE |
| `atrophic_hypertrophic_scar` | Cicatrices superficiales atróficas o hipertróficas | FALSE | NULL | TRUE |
| `hpi_severe` | Hiperpigmentación post-inflamatoria severa | TRUE | `'III-VI'` | TRUE |
| `chronic_erythema_hypersensitivity` | Eritema crónico e hipersensibilidad en zonas afectadas | TRUE | NULL | TRUE |
| `secondary_bacterial_infection` | Riesgo de sobreinfección bacteriana (S. aureus) | TRUE | NULL | FALSE |
| `any_active_irritates_barrier` | Cualquier activo puede irritar intensamente la barrera rota | TRUE | NULL | TRUE |

**Registros — `acne_inflammatory`:**

| repercussion_key | label | is_reversible | fototipo_risk | occurs_without_treatment |
|-----------------|-------|:-------------:|:-------------:|:------------------------:|
| `atrophic_scars_icepick_rolling_boxcar` | Cicatrices atróficas (icepick, rolling, boxcar) | FALSE | NULL | TRUE |
| `hpi_severe_inflammatory` | HPI severa post-inflamatoria | TRUE | `'III-VI'` | TRUE |
| `post_lesional_erythema` | Eritema post-lesional persistente por neovascularización | TRUE | NULL | TRUE |
| `microbiome_dysbiosis` | Disbiosis del microbioma cutáneo a favor de C. acnes virulento | TRUE | NULL | TRUE |
| `psychological_impact_severe` | Impacto psicológico equiparable a enfermedades crónicas | TRUE | NULL | FALSE |

**Registros — `rosacea_etr`:**

| repercussion_key | label | is_reversible | fototipo_risk | occurs_without_treatment |
|-----------------|-------|:-------------:|:-------------:|:------------------------:|
| `permanent_bilateral_erythema` | Eritema central bilateral permanente sin tratamiento | FALSE | NULL | TRUE |
| `telangiectasias_visible` | Telangiectasias visibles; solo reversibles con láser | FALSE | NULL | TRUE |
| `structural_barrier_weakness` | Barrera cutánea debilitada con menor contenido de ceramidas | TRUE | NULL | TRUE |
| `high_trigger_reactivity` | Alta reactividad a desencadenantes externos (triggers) | TRUE | NULL | TRUE |
| `progression_to_inflammatory_rosacea` | Progresión a rosácea inflamatoria sin control de triggers | TRUE | NULL | FALSE |
| `systemic_comorbidities` | Riesgo de comorbilidades sistémicas (cardiovascular, SII, Parkinson) | FALSE | NULL | FALSE |

**Registros — `rosacea_inflammatory`:**

| repercussion_key | label | is_reversible | fototipo_risk | occurs_without_treatment |
|-----------------|-------|:-------------:|:-------------:|:------------------------:|
| `sterile_pustules_marks` | Pústulas estériles que dejan marcas post-inflamatorias | TRUE | `'V-VI'` | TRUE |
| `deep_dermal_inflammation_phymatous` | Inflamación dérmica profunda pre-fimatosa | FALSE | NULL | TRUE |
| `telangiectasias_exacerbation` | Exacerbación de telangiectasias por vasodilatación repetida | FALSE | NULL | TRUE |
| `severely_deteriorated_barrier` | Barrera más deteriorada que en ETR pura | TRUE | NULL | TRUE |
| `psychosocial_stigma` | Impacto psicológico por confusión con acné; estigmatización | TRUE | NULL | FALSE |

**Registros — `perioral_dermatitis`:**

| repercussion_key | label | is_reversible | fototipo_risk | occurs_without_treatment |
|-----------------|-------|:-------------:|:-------------:|:------------------------:|
| `persistent_recurrent_eruption` | Erupción persistente o recurrente que puede cronificarse | TRUE | NULL | TRUE |
| `perioral_erythema_pustules` | Eritema, descamación fina y pústulas en zona perioral | TRUE | NULL | TRUE |
| `corticoid_dependency_cycle` | Paradoja del corticoide: mejora temporal + rebound severo al suspender | TRUE | NULL | FALSE |
| `occasional_scars` | Cicatrices ocasionales por manipulación o infección secundaria | FALSE | `'V-VI'` | FALSE |
| `aesthetic_impact_central` | Impacto estético significativo por localización central en rostro | TRUE | NULL | FALSE |

**Registros — `seborrheic_dermatitis`:**

| repercussion_key | label | is_reversible | fototipo_risk | occurs_without_treatment |
|-----------------|-------|:-------------:|:-------------:|:------------------------:|
| `greasy_or_dry_scaling` | Descamación grasa (amarillenta) o seca en zonas seborreicas | TRUE | NULL | TRUE |
| `seborrheic_erythema_plaques` | Eritema en placas en zonas seborreicas con bordes definidos | TRUE | NULL | TRUE |
| `variable_pruritus` | Prurito de intensidad variable, a veces severo | TRUE | NULL | TRUE |
| `chronic_relapsing_course` | Cronicidad con brotes periódicos ante estrés, frío o inmunodepresión | FALSE | NULL | TRUE |
| `hypo_hyperpigmentation_resolution` | Máculas hipo o hiperpigmentadas en resolución | TRUE | `'III-VI'` | FALSE |

**Registros — `healthy_skin`:**

| repercussion_key | label | is_reversible | fototipo_risk | occurs_without_treatment |
|-----------------|-------|:-------------:|:-------------:|:------------------------:|
| `accelerated_photoaging` | Aceleración del fotoenvejecimiento por daño UV acumulado | FALSE | `'I-II'` | TRUE |
| `ceramide_sebum_decline_age` | Disminución de ceramidas y sebo con la edad | FALSE | NULL | TRUE |
| `inflammatory_susceptibility` | Mayor susceptibilidad a condiciones inflamatorias externas | TRUE | NULL | TRUE |
| `oxidative_stress_pigmentation` | Estrés oxidativo que predispone a manchas y tono irregular | TRUE | `'III-VI'` | TRUE |

---

## TABLA 3: `condition_symptoms`
Síntomas subjetivos reportados por el usuario.

| Campo | Tipo | Restricción | Valores permitidos | Descripción |
|-------|------|-------------|-------------------|-------------|
| `symptom_id` | INT | PK · NOT NULL · AUTO_INCREMENT | — | Identificador único |
| `condition_key` | VARCHAR(50) | FK → conditions · NOT NULL | Ver tabla 1 | Condición a la que pertenece |
| `symptom_key` | VARCHAR(100) | NOT NULL | Ver registros | Clave snake_case del síntoma |
| `label` | VARCHAR(200) | NOT NULL | — | Nombre legible para UI |
| `is_primary` | BOOLEAN | NOT NULL · DEFAULT FALSE | `TRUE` · `FALSE` | TRUE si es el síntoma más representativo |
| `intensity` | ENUM | NOT NULL · DEFAULT `'none'` | `'none'` · `'mild'` · `'moderate'` · `'severe'` | Intensidad habitual |
| `is_physical` | BOOLEAN | NOT NULL · DEFAULT TRUE | `TRUE` · `FALSE` | FALSE si es síntoma psicológico/emocional |

**Registros — `acne_comedonal`:**

| symptom_key | label | is_primary | intensity | is_physical |
|------------|-------|:----------:|-----------|:-----------:|
| `asymptomatic` | Generalmente asintomático; sin dolor ni prurito | TRUE | `'none'` | TRUE |
| `rough_sandy_sensation` | Sensación de piel rugosa o arenosa al tacto | FALSE | `'mild'` | TRUE |
| `aesthetic_discomfort` | Incomodidad estética con impacto en autoestima | FALSE | `'mild'` | FALSE |
| `focal_sensitivity` | Ligera sensibilidad en nariz, frente, mentón | FALSE | `'mild'` | TRUE |

**Registros — `acne_excorie`:**

| symptom_key | label | is_primary | intensity | is_physical |
|------------|-------|:----------:|-----------|:-----------:|
| `urge_to_pick_itch_tension` | Prurito, ardor o tensión que precede al rascado ("urge to pick") | TRUE | `'moderate'` | TRUE |
| `temporary_relief_shame` | Alivio temporal seguido de vergüenza o culpa | FALSE | `'moderate'` | FALSE |
| `pain_erosions_crusts` | Dolor en erosiones activas y costras | FALSE | `'moderate'` | TRUE |
| `raw_skin_sensation` | Sensación de piel "en carne viva" en zonas excoriadas | FALSE | `'severe'` | TRUE |
| `psychological_isolation_depression` | Aislamiento social, evitación de espejos, depresión comórbida | FALSE | `'severe'` | FALSE |

**Registros — `acne_inflammatory`:**

| symptom_key | label | is_primary | intensity | is_physical |
|------------|-------|:----------:|-----------|:-----------:|
| `pain_nodules_cysts` | Dolor e hipersensibilidad local en nódulos y quistes | TRUE | `'moderate'` | TRUE |
| `heat_tension_active` | Sensación de calor y tensión en áreas activas | FALSE | `'moderate'` | TRUE |
| `pruritus_resolving_pustules` | Prurito en pústulas en resolución | FALSE | `'mild'` | TRUE |
| `contact_sensitivity_masks` | Sensibilidad al tacto; incomodidad con mascarillas o bufandas | FALSE | `'mild'` | TRUE |
| `systemic_symptoms_severe` | Fiebre leve y malestar en acné conglobata severo | FALSE | `'moderate'` | TRUE |

**Registros — `rosacea_etr`:**

| symptom_key | label | is_primary | intensity | is_physical |
|------------|-------|:----------:|-----------|:-----------:|
| `burning_heat_sensation` | Ardor, escozor o sensación de calor facial post-trigger | TRUE | `'moderate'` | TRUE |
| `episodic_flushing` | Flushing episódico: enrojecimiento repentino con calor por minutos u horas | TRUE | `'moderate'` | TRUE |
| `hypersensitive_reactive_skin` | Piel muy reactiva a temperatura, productos nuevos o emociones | FALSE | `'moderate'` | TRUE |
| `thin_skin_sensation` | Sensación de "piel fina" o hipersensible al contacto | FALSE | `'mild'` | TRUE |
| `psychosocial_impact_triggers` | Vergüenza social y ansiedad de anticipación ante triggers | FALSE | `'moderate'` | FALSE |

**Registros — `rosacea_inflammatory`:**

| symptom_key | label | is_primary | intensity | is_physical |
|------------|-------|:----------:|-----------|:-----------:|
| `burning_tension_pustules` | Ardor y tensión específicamente en las pústulas | TRUE | `'moderate'` | TRUE |
| `occasional_pruritus_active` | Prurito ocasional en áreas activas | FALSE | `'mild'` | TRUE |
| `identifiable_flare_sensation` | Mayor sensación de "brotes" que coinciden con triggers | FALSE | `'moderate'` | TRUE |
| `discomfort_product_application` | Desconfort al aplicar cualquier producto sobre pústulas activas | FALSE | `'moderate'` | TRUE |

**Registros — `perioral_dermatitis`:**

| symptom_key | label | is_primary | intensity | is_physical |
|------------|-------|:----------:|-----------|:-----------:|
| `burning_stinging_pruritus_perioral` | Ardor, escozor o prurito en la zona perioral | TRUE | `'moderate'` | TRUE |
| `skin_tension_perioral` | Sensación de tensión cutánea perioral | FALSE | `'mild'` | TRUE |
| `worsening_with_cortisone` | Empeoramiento evidente con cremas de cortisona | FALSE | `'moderate'` | TRUE |
| `aesthetic_shame_central_location` | Vergüenza estética por localización central visible | FALSE | `'moderate'` | FALSE |

**Registros — `seborrheic_dermatitis`:**

| symptom_key | label | is_primary | intensity | is_physical |
|------------|-------|:----------:|-----------|:-----------:|
| `scalp_face_pruritus` | Prurito intenso en cuero cabelludo y cara | TRUE | `'moderate'` | TRUE |
| `greasy_erythematous_skin_folds` | Sensación de piel "grasienta" y eritematosa en pliegues | FALSE | `'mild'` | TRUE |
| `itch_burn_scaling_zones` | Picor y ardor en zonas de descamación activa | FALSE | `'moderate'` | TRUE |
| `relapse_remission_cycle` | Ciclos de mejoría y recaída; remisión completa rara | FALSE | `'mild'` | TRUE |

**Registros — `healthy_skin`:**

| symptom_key | label | is_primary | intensity | is_physical |
|------------|-------|:----------:|-----------|:-----------:|
| `no_active_symptoms` | Sin síntomas activos; piel en estado basal normal | TRUE | `'none'` | TRUE |
| `seasonal_dryness_sensitivity` | Sequedad o sensibilidad estacional leve | FALSE | `'mild'` | TRUE |

---

## TABLA 4: `treatment_needs`
Necesidades terapéuticas por condición con nivel de evidencia.

| Campo | Tipo | Restricción | Valores permitidos | Descripción |
|-------|------|-------------|-------------------|-------------|
| `need_id` | INT | PK · NOT NULL · AUTO_INCREMENT | — | Identificador único |
| `condition_key` | VARCHAR(50) | FK → conditions · NOT NULL | Ver tabla 1 | Condición a la que pertenece |
| `need_key` | VARCHAR(100) | NOT NULL | Ver registros | Clave snake_case de la necesidad |
| `label` | VARCHAR(200) | NOT NULL | — | Nombre legible |
| `priority` | ENUM | NOT NULL | `'essential'` · `'high'` · `'moderate'` · `'optional'` | Prioridad clínica |
| `evidence_level` | ENUM | NOT NULL | `'very_high'` · `'high'` · `'moderate'` · `'low'` | Nivel de evidencia científica |
| `is_action` | BOOLEAN | NOT NULL · DEFAULT FALSE | `TRUE` · `FALSE` | TRUE si es una acción (no un ingrediente), ej. suspender corticoides |

**Registros — `acne_comedonal`:**

| need_key | label | priority | evidence_level | is_action |
|---------|-------|----------|----------------|:---------:|
| `follicular_exfoliation` | Exfoliación química del folículo | `'essential'` | `'high'` | FALSE |
| `keratinization_normalization` | Normalización de la queratinización folicular | `'essential'` | `'high'` | FALSE |
| `sebum_regulation` | Regulación de la producción sebácea | `'high'` | `'high'` | FALSE |
| `follicular_unblocking` | Desobstrucción activa del folículo ocluido | `'high'` | `'moderate'` | FALSE |
| `non_comedogenic_hydration` | Hidratación sin comedogenicidad | `'essential'` | `'high'` | FALSE |
| `photoprotection` | Fotoprotección diaria SPF 30+ | `'essential'` | `'high'` | FALSE |

**Registros — `acne_excorie`:**

| need_key | label | priority | evidence_level | is_action |
|---------|-------|----------|----------------|:---------:|
| `barrier_restoration` | Restauración de la barrera cutánea | `'essential'` | `'high'` | FALSE |
| `active_wound_healing` | Cicatrización activa de erosiones | `'essential'` | `'high'` | FALSE |
| `erythema_reduction` | Reducción del eritema post-lesional | `'high'` | `'high'` | FALSE |
| `soothing_hydration` | Calmante e hidratación profunda | `'essential'` | `'high'` | FALSE |
| `infection_prevention` | Prevención de sobreinfección bacteriana | `'high'` | `'moderate'` | FALSE |
| `hpi_reduction_post_healing` | Reducción de HPI (solo en piel cicatrizada) | `'moderate'` | `'high'` | FALSE |
| `psychological_referral` | Derivación a psicología/psiquiatría para BFRB | `'essential'` | `'high'` | TRUE |

**Registros — `acne_inflammatory`:**

| need_key | label | priority | evidence_level | is_action |
|---------|-------|----------|----------------|:---------:|
| `antibacterial_topical` | Antibacteriano tópico contra C. acnes | `'essential'` | `'high'` | FALSE |
| `anti_inflammatory_topical` | Antiinflamatorio tópico | `'essential'` | `'high'` | FALSE |
| `sebum_regulation_retinoid` | Regulación sebácea con retinoides | `'high'` | `'high'` | FALSE |
| `gentle_exfoliation` | Exfoliación suave (no sobre piel activa) | `'moderate'` | `'moderate'` | FALSE |
| `depigmenting_post_lesional` | Despigmentante post-lesional para HPI | `'high'` | `'high'` | FALSE |
| `barrier_soothing` | Barrera y calmante entre activos | `'essential'` | `'high'` | FALSE |
| `photoprotection_spf30_50` | Fotoprotección SPF 30–50 no comedogénico | `'essential'` | `'high'` | FALSE |

**Registros — `rosacea_etr`:**

| need_key | label | priority | evidence_level | is_action |
|---------|-------|----------|----------------|:---------:|
| `vascular_calming` | Calmante vascular | `'essential'` | `'high'` | FALSE |
| `barrier_reinforcement` | Refuerzo de barrera cutánea | `'essential'` | `'high'` | FALSE |
| `gentle_anti_inflammatory` | Antiinflamatorio suave (niacinamida baja dosis) | `'high'` | `'moderate'` | FALSE |
| `neurovascular_soothing` | Calmante neurovascular | `'high'` | `'high'` | FALSE |
| `mineral_photoprotection` | Fotoprotección SPF 30–50+ mineral exclusivamente | `'essential'` | `'high'` | FALSE |
| `trigger_free_hydration` | Hidratación sin irritantes ni fragancias | `'essential'` | `'high'` | FALSE |

**Registros — `rosacea_inflammatory`:**

| need_key | label | priority | evidence_level | is_action |
|---------|-------|----------|----------------|:---------:|
| `antiparasitic_antibacterial` | Antibacteriano/antiparasitario (metronidazol, ivermectina) | `'essential'` | `'very_high'` | FALSE |
| `anti_inflammatory_minimal` | Antiinflamatorio con ingredientes mínimos | `'essential'` | `'high'` | FALSE |
| `vascular_soothing_minimal` | Calmante vascular con fórmula ultramínima | `'essential'` | `'high'` | FALSE |
| `barrier_minimal_formula` | Barrera con texturas ultramínimas | `'essential'` | `'high'` | FALSE |
| `mineral_spf50_mandatory` | SPF 50+ mineral exclusivamente | `'essential'` | `'high'` | FALSE |
| `exhaustive_trigger_avoidance` | Evitar todos los triggers (lista exhaustiva) | `'essential'` | `'high'` | TRUE |

**Registros — `perioral_dermatitis`:**

| need_key | label | priority | evidence_level | is_action |
|---------|-------|----------|----------------|:---------:|
| `discontinue_topical_corticosteroids` | Suspensión inmediata de corticoides tópicos | `'essential'` | `'high'` | TRUE |
| `identify_remove_cause` | Identificar y eliminar el factor causal | `'essential'` | `'high'` | TRUE |
| `gentle_antibacterial` | Antibacteriano/antiinflamatorio suave | `'essential'` | `'high'` | FALSE |
| `minimal_cleanser` | Limpieza mínima sin irritantes ni perfume | `'essential'` | `'high'` | FALSE |
| `ultraminimal_hydration` | Hidratación ultramínima sin oclusivos pesados | `'high'` | `'high'` | FALSE |
| `avoid_perioral_occlusives` | Evitar oclusivos en zona perioral | `'essential'` | `'high'` | TRUE |

**Registros — `seborrheic_dermatitis`:**

| need_key | label | priority | evidence_level | is_action |
|---------|-------|----------|----------------|:---------:|
| `antifungal_topical` | Antifúngico tópico (piroctona, zinc piritiona) | `'essential'` | `'high'` | FALSE |
| `gentle_anti_inflammatory` | Antiinflamatorio suave | `'high'` | `'high'` | FALSE |
| `sebum_regulation` | Regulación sebácea | `'high'` | `'high'` | FALSE |
| `pruritus_calming` | Calmante del prurito | `'high'` | `'high'` | FALSE |
| `antifungal_exfoliation` | Exfoliación antifúngica (BHA + antifúngico) | `'moderate'` | `'moderate'` | FALSE |
| `light_barrier` | Barrera ligera sin oclusivos comedogénicos | `'high'` | `'high'` | FALSE |
| `photoprotection_non_comedogenic` | Fotoprotección no comedogénica | `'essential'` | `'high'` | FALSE |

**Registros — `healthy_skin`:**

| need_key | label | priority | evidence_level | is_action |
|---------|-------|----------|----------------|:---------:|
| `barrier_hydration` | Hidratación y refuerzo de barrera | `'essential'` | `'high'` | FALSE |
| `broad_spectrum_photoprotection` | Fotoprotección UVA/UVB SPF 30–50+ | `'essential'` | `'very_high'` | FALSE |
| `antioxidant_protection` | Protección antioxidante (vitamina C, E, niacinamida) | `'high'` | `'high'` | FALSE |
| `gentle_ph_cleansing` | Limpieza con pH 4.5–5.5 | `'high'` | `'high'` | FALSE |
| `preventive_cell_renewal` | Renovación celular preventiva (retinol, AHA) | `'moderate'` | `'high'` | FALSE |
| `tone_uniformity` | Uniformidad y luminosidad del tono cutáneo | `'moderate'` | `'moderate'` | FALSE |

---

## TABLA 5: `recommended_ingredients`
Ingredientes activos recomendados por condición y necesidad.

| Campo | Tipo | Restricción | Valores permitidos | Descripción |
|-------|------|-------------|-------------------|-------------|
| `ingredient_id` | INT | PK · NOT NULL · AUTO_INCREMENT | — | Identificador único |
| `condition_key` | VARCHAR(50) | FK → conditions · NOT NULL | Ver tabla 1 | Condición a la que pertenece |
| `need_key` | VARCHAR(100) | FK → treatment_needs · NOT NULL | Ver tabla 4 | Necesidad que cubre |
| `ingredient_key` | VARCHAR(100) | NOT NULL | Ver registros | Clave INCI o nombre estandarizado |
| `label` | VARCHAR(150) | NOT NULL | — | Nombre legible |
| `concentration_min` | DECIMAL(5,2) | NULL | — | Concentración mínima efectiva (%) |
| `concentration_max` | DECIMAL(5,2) | NULL | — | Concentración máxima recomendada (%) |
| `application_time` | SET | NOT NULL | `'AM'` · `'PM'` · `'AM,PM'` | Momento de aplicación |
| `contraindicated_if_pregnant` | BOOLEAN | NOT NULL · DEFAULT FALSE | `TRUE` · `FALSE` | Contraindicado en embarazo |
| `phase_restriction` | ENUM | NULL · DEFAULT NULL | `NULL` · `'active_only'` · `'healing_only'` · `'maintenance_only'` | Si aplica solo en cierta fase |

**Registros — `acne_comedonal`:**

| ingredient_key | label | conc_min | conc_max | application_time | contraindicated_if_pregnant | phase_restriction |
|---------------|-------|:--------:|:--------:|:----------------:|:---------------------------:|:-----------------:|
| `salicylic_acid` | Ácido salicílico (BHA) | 0.50 | 2.00 | `'PM'` | FALSE | NULL |
| `adapalene` | Adapaleno | 0.10 | 0.30 | `'PM'` | TRUE | NULL |
| `retinol_encapsulated` | Retinol encapsulado | 0.10 | 0.30 | `'PM'` | TRUE | NULL |
| `niacinamide` | Niacinamida | 4.00 | 5.00 | `'AM,PM'` | FALSE | NULL |
| `zinc_gluconate` | Zinc gluconato | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `azelaic_acid` | Ácido azelaico | 10.00 | 15.00 | `'AM,PM'` | FALSE | NULL |
| `hyaluronic_acid` | Ácido hialurónico | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `glycerin` | Glicerina | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `ceramides` | Ceramidas | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `spf_gel_fluid` | SPF 30+ gel o fluido no comedogénico | NULL | NULL | `'AM'` | FALSE | NULL |

**Registros — `acne_excorie`:**

| ingredient_key | label | conc_min | conc_max | application_time | contraindicated_if_pregnant | phase_restriction |
|---------------|-------|:--------:|:--------:|:----------------:|:---------------------------:|:-----------------:|
| `ceramides` | Ceramidas | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `free_fatty_acids` | Ácidos grasos libres | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `panthenol` | Pantenol (provitamina B5) | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `centella_asiatica` | Centella asiática | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `allantoin` | Alantoína | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `bisabolol` | Bisabolol | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `colloidal_oat` | Extracto de avena coloidal | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `beta_glucan` | Beta-glucano | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `hyaluronic_acid_low_mw` | Ácido hialurónico bajo peso molecular | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `zinc_oxide_1` | Zinc oxide 1% (prevención infección) | 1.00 | 1.00 | `'PM'` | FALSE | NULL |
| `niacinamide` | Niacinamida | 4.00 | 5.00 | `'AM,PM'` | FALSE | `'healing_only'` |
| `spf_50_mineral` | SPF 50+ mineral | NULL | NULL | `'AM'` | FALSE | NULL |

**Registros — `acne_inflammatory`:**

| ingredient_key | label | conc_min | conc_max | application_time | contraindicated_if_pregnant | phase_restriction |
|---------------|-------|:--------:|:--------:|:----------------:|:---------------------------:|:-----------------:|
| `benzoyl_peroxide` | Peróxido de benzoílo | 2.50 | 5.00 | `'PM'` | FALSE | NULL |
| `azelaic_acid` | Ácido azelaico | 15.00 | 20.00 | `'AM,PM'` | FALSE | NULL |
| `niacinamide` | Niacinamida | 4.00 | 5.00 | `'AM,PM'` | FALSE | NULL |
| `adapalene` | Adapaleno | 0.10 | 0.30 | `'PM'` | TRUE | NULL |
| `tretinoin` | Tretinoína (con prescripción) | 0.025 | 0.05 | `'PM'` | TRUE | NULL |
| `salicylic_acid` | Ácido salicílico | 0.50 | 2.00 | `'PM'` | FALSE | NULL |
| `alpha_arbutin` | Alpha-arbutin | 1.00 | 2.00 | `'AM,PM'` | FALSE | NULL |
| `kojic_acid` | Ácido kójico | 1.00 | 2.00 | `'PM'` | FALSE | NULL |
| `ceramides` | Ceramidas | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `panthenol` | Pantenol | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `spf_non_comedogenic` | SPF 30–50 no comedogénico | NULL | NULL | `'AM'` | FALSE | NULL |

**Registros — `rosacea_etr`:**

| ingredient_key | label | conc_min | conc_max | application_time | contraindicated_if_pregnant | phase_restriction |
|---------------|-------|:--------:|:--------:|:----------------:|:---------------------------:|:-----------------:|
| `azelaic_acid` | Ácido azelaico | 10.00 | 15.00 | `'AM,PM'` | FALSE | NULL |
| `metronidazole_topical` | Metronidazol tópico (médico) | 0.75 | 1.00 | `'PM'` | FALSE | NULL |
| `ceramides` | Ceramidas | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `niacinamide_low` | Niacinamida (dosis baja) | 2.00 | 4.00 | `'AM,PM'` | FALSE | NULL |
| `glycerin` | Glicerina | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `bisabolol` | Bisabolol | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `centella_asiatica` | Centella asiática | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `colloidal_oat` | Avena coloidal | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `mineral_spf_zno` | SPF mineral ZnO 15–20% | NULL | NULL | `'AM'` | FALSE | NULL |
| `panthenol` | Pantenol | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `hyaluronic_acid` | Ácido hialurónico | NULL | NULL | `'AM,PM'` | FALSE | NULL |

**Registros — `rosacea_inflammatory`:**

| ingredient_key | label | conc_min | conc_max | application_time | contraindicated_if_pregnant | phase_restriction |
|---------------|-------|:--------:|:--------:|:----------------:|:---------------------------:|:-----------------:|
| `metronidazole_topical` | Metronidazol tópico (médico) | 0.75 | 1.00 | `'PM'` | FALSE | NULL |
| `ivermectin_topical` | Ivermectina tópica 1% (médico) | 1.00 | 1.00 | `'PM'` | FALSE | NULL |
| `azelaic_acid` | Ácido azelaico | 15.00 | 15.00 | `'AM,PM'` | FALSE | NULL |
| `niacinamide_low` | Niacinamida (dosis muy baja) | 2.00 | 4.00 | `'AM,PM'` | FALSE | `'healing_only'` |
| `bisabolol` | Bisabolol | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `centella_asiatica` | Centella asiática | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `ceramides` | Ceramidas | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `panthenol` | Pantenol | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `mineral_spf50` | SPF 50+ mineral exclusivamente | NULL | NULL | `'AM'` | FALSE | NULL |

**Registros — `perioral_dermatitis`:**

| ingredient_key | label | conc_min | conc_max | application_time | contraindicated_if_pregnant | phase_restriction |
|---------------|-------|:--------:|:--------:|:----------------:|:---------------------------:|:-----------------:|
| `metronidazole_topical` | Metronidazol tópico (médico) | 0.75 | 1.00 | `'PM'` | FALSE | NULL |
| `azelaic_acid` | Ácido azelaico | 10.00 | 10.00 | `'AM,PM'` | FALSE | NULL |
| `hyaluronic_acid` | Ácido hialurónico | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `glycerin` | Glicerina | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `mineral_spf_fluid` | SPF mineral fluido o gel (zona perioral) | NULL | NULL | `'AM'` | FALSE | NULL |

**Registros — `seborrheic_dermatitis`:**

| ingredient_key | label | conc_min | conc_max | application_time | contraindicated_if_pregnant | phase_restriction |
|---------------|-------|:--------:|:--------:|:----------------:|:---------------------------:|:-----------------:|
| `piroctone_olamine` | Piroctona olamina | 0.50 | 1.00 | `'AM,PM'` | FALSE | NULL |
| `zinc_pyrithione` | Zinc piritiona | 1.00 | 2.00 | `'AM,PM'` | FALSE | NULL |
| `ketoconazole_topical` | Ketoconazol tópico | 1.00 | 2.00 | `'PM'` | FALSE | NULL |
| `niacinamide` | Niacinamida | 4.00 | 5.00 | `'AM,PM'` | FALSE | NULL |
| `azelaic_acid` | Ácido azelaico | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `zinc_gluconate` | Zinc gluconato | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `colloidal_oat` | Avena coloidal | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `allantoin` | Alantoína | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `panthenol` | Pantenol | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `salicylic_acid_antifungal` | Ácido salicílico (con antifúngico) | 1.00 | 2.00 | `'PM'` | FALSE | NULL |
| `ceramides_light` | Ceramidas ligeras | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `spf_non_comedogenic` | SPF 30+ no comedogénico | NULL | NULL | `'AM'` | FALSE | NULL |

**Registros — `healthy_skin`:**

| ingredient_key | label | conc_min | conc_max | application_time | contraindicated_if_pregnant | phase_restriction |
|---------------|-------|:--------:|:--------:|:----------------:|:---------------------------:|:-----------------:|
| `ceramides` | Ceramidas | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `hyaluronic_acid` | Ácido hialurónico | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `glycerin` | Glicerina | NULL | NULL | `'AM,PM'` | FALSE | NULL |
| `spf_30_50_broad_spectrum` | SPF 30–50+ UVA/UVB | NULL | NULL | `'AM'` | FALSE | NULL |
| `vitamin_c_stabilized` | Vitamina C estabilizada (ascorbil glucósido / L-ascórbico) | 10.00 | 20.00 | `'AM'` | FALSE | NULL |
| `vitamin_e` | Vitamina E (tocoferol) | NULL | NULL | `'PM'` | FALSE | NULL |
| `niacinamide` | Niacinamida | 5.00 | 5.00 | `'AM,PM'` | FALSE | NULL |
| `retinol_preventive` | Retinol preventivo | 0.10 | 1.00 | `'PM'` | TRUE | NULL |
| `glycolic_acid_weekly` | Ácido glicólico (uso semanal) | 5.00 | 8.00 | `'PM'` | FALSE | NULL |
| `alpha_arbutin` | Alpha-arbutin | 1.00 | 2.00 | `'AM,PM'` | FALSE | NULL |
| `squalane` | Escualano | NULL | NULL | `'PM'` | FALSE | NULL |
| `peptides` | Péptidos (uso > 25 años) | NULL | NULL | `'AM,PM'` | FALSE | NULL |

---

## TABLA 6: `avoided_ingredients`
Ingredientes y productos a evitar por condición.

| Campo | Tipo | Restricción | Valores permitidos | Descripción |
|-------|------|-------------|-------------------|-------------|
| `avoid_id` | INT | PK · NOT NULL · AUTO_INCREMENT | — | Identificador único |
| `condition_key` | VARCHAR(50) | FK → conditions · NOT NULL | Ver tabla 1 | Condición a la que aplica |
| `ingredient_key` | VARCHAR(100) | NOT NULL | Ver registros | Clave del ingrediente o formato a evitar |
| `label` | VARCHAR(200) | NOT NULL | — | Nombre legible |
| `avoid_reason_key` | VARCHAR(80) | FK → avoid_reasons · NOT NULL | Ver tabla 7 | Clave de la razón para evitar |
| `comedogenic_index` | DECIMAL(3,1) | NULL | `NULL` · `0.0`–`5.0` | Índice Kligman & Mills; NULL si no aplica |
| `severity` | ENUM | NOT NULL | `'mandatory'` · `'recommended'` · `'conditional'` | Obligatoriedad de la exclusión |
| `applies_only_if_skin_type` | VARCHAR(30) | NULL · DEFAULT NULL | `NULL` · `'oily'` · `'combination'` · `'dry'` · `'sensitive'` · `'normal'` | NULL = aplica a todos |
| `applies_only_if_pregnant` | BOOLEAN | NOT NULL · DEFAULT FALSE | `TRUE` · `FALSE` | TRUE si solo aplica en embarazo |
| `phase_restriction` | ENUM | NULL · DEFAULT NULL | `NULL` · `'active_only'` · `'healing_only'` | NULL = aplica en todas las fases |

**Registros — `acne_comedonal`:**

| ingredient_key | label | avoid_reason_key | comedogenic_index | severity | applies_only_if_skin_type | applies_only_if_pregnant |
|---------------|-------|-----------------|:-----------------:|----------|:-------------------------:|:------------------------:|
| `coconut_oil` | Aceite de coco | `'comedogenicity'` | 4.0 | `'mandatory'` | NULL | FALSE |
| `olive_oil_pure` | Aceite de oliva puro | `'comedogenicity'` | 2.5 | `'recommended'` | `'oily'` | FALSE |
| `shea_butter_unrefined` | Manteca de karité sin refinar | `'comedogenicity'` | 3.5 | `'mandatory'` | NULL | FALSE |
| `wheat_germ_oil` | Aceite de germen de trigo | `'comedogenicity'` | 5.0 | `'mandatory'` | NULL | FALSE |
| `lanolin` | Lanolina | `'comedogenicity'` | 3.5 | `'mandatory'` | NULL | FALSE |
| `isopropyl_myristate` | Miristato / Palmitato de isopropilo | `'comedogenicity'` | 4.5 | `'mandatory'` | NULL | FALSE |
| `mineral_oil_low_grade` | Aceite mineral baja pureza | `'comedogenicity'` | 2.5 | `'recommended'` | `'oily'` | FALSE |
| `heavy_ointment_base` | Bases en pomada densa | `'comedogenicity'` | NULL | `'mandatory'` | NULL | FALSE |
| `ethyl_alcohol_high` | Alcohol etílico / SD Alcohol >5% | `'barrier_disruption'` | NULL | `'mandatory'` | NULL | FALSE |
| `sls` | Lauril sulfato de sodio (SLS) | `'microbiome_alteration'` | NULL | `'mandatory'` | NULL | FALSE |
| `synthetic_fragrance` | Fragancias sintéticas y aceites esenciales | `'secondary_inflammation'` | NULL | `'mandatory'` | NULL | FALSE |
| `menthol_camphor` | Mentol y alcanfor | `'secondary_inflammation'` | NULL | `'mandatory'` | NULL | FALSE |
| `physical_scrub` | Scrubs físicos (microperlas, sal, azúcar) | `'mechanical_abrasion'` | NULL | `'mandatory'` | NULL | FALSE |
| `compact_makeup_grease_base` | Maquillaje en barra con base grasa | `'comedogenicity'` | NULL | `'recommended'` | `'oily'` | FALSE |
| `chemical_sunscreen_oil_base` | Fotoprotector químico en base oleosa | `'comedogenicity'` | NULL | `'recommended'` | `'oily'` | FALSE |
| `retinoids_all` | Todos los retinoides | `'teratogenicity'` | NULL | `'mandatory'` | NULL | TRUE |

**Registros — `acne_excorie`:**

| ingredient_key | label | avoid_reason_key | comedogenic_index | severity | applies_only_if_skin_type | applies_only_if_pregnant | phase_restriction |
|---------------|-------|-----------------|:-----------------:|----------|:-------------------------:|:------------------------:|:-----------------:|
| `aha_glycolic_lactic` | AHA (glicólico, láctico, mandélico) | `'barrier_disruption'` | NULL | `'mandatory'` | NULL | FALSE | `'active_only'` |
| `salicylic_acid_bha` | Ácido salicílico (BHA) | `'barrier_disruption'` | NULL | `'mandatory'` | NULL | FALSE | `'active_only'` |
| `retinoids_all` | Retinoides (retinol, adapaleno, tretinoína) | `'barrier_disruption'` | NULL | `'mandatory'` | NULL | FALSE | `'active_only'` |
| `benzoyl_peroxide` | Peróxido de benzoílo | `'barrier_disruption'` | NULL | `'mandatory'` | NULL | FALSE | `'active_only'` |
| `pure_vitamin_c_high` | Vitamina C L-ascórbica pura >5% | `'barrier_disruption'` | NULL | `'mandatory'` | NULL | FALSE | `'active_only'` |
| `ethyl_alcohol` | Alcohol etílico / SD Alcohol | `'barrier_disruption'` | NULL | `'mandatory'` | NULL | FALSE | NULL |
| `synthetic_fragrance` | Fragancias sintéticas y aceites esenciales | `'barrier_disruption'` | NULL | `'mandatory'` | NULL | FALSE | NULL |
| `high_concentration_preservatives` | Conservantes alta concentración (fenoxietanol >1%, MI/MCI) | `'barrier_disruption'` | NULL | `'mandatory'` | NULL | FALSE | `'active_only'` |
| `physical_exfoliant` | Exfoliantes físicos (scrubs, cepillos) | `'mechanical_abrasion'` | NULL | `'mandatory'` | NULL | FALSE | NULL |
| `kojic_acid_arbutin` | Ácido kójico y alpha-arbutin | `'secondary_inflammation'` | NULL | `'mandatory'` | NULL | FALSE | `'active_only'` |
| `astringent_toner` | Tónicos astringentes (hamamelis, alcohol, mentol) | `'barrier_disruption'` | NULL | `'mandatory'` | NULL | FALSE | NULL |
| `clay_mask_fast_dry` | Mascarillas de arcilla de secado rápido | `'mechanical_abrasion'` | NULL | `'mandatory'` | NULL | FALSE | `'active_only'` |

**Registros — `acne_inflammatory`:**

| ingredient_key | label | avoid_reason_key | comedogenic_index | severity | applies_only_if_skin_type | applies_only_if_pregnant |
|---------------|-------|-----------------|:-----------------:|----------|:-------------------------:|:------------------------:|
| `coconut_oil` | Aceite de coco | `'comedogenicity'` | 4.0 | `'mandatory'` | NULL | FALSE |
| `shea_butter_unrefined` | Manteca de karité sin refinar | `'comedogenicity'` | 3.5 | `'mandatory'` | NULL | FALSE |
| `isopropyl_myristate` | Miristato / Palmitato de isopropilo | `'comedogenicity'` | 4.5 | `'mandatory'` | NULL | FALSE |
| `ethyl_alcohol_high` | Alcohol etílico / SD Alcohol alta concentración | `'barrier_disruption'` | NULL | `'mandatory'` | NULL | FALSE |
| `synthetic_fragrance` | Fragancias sintéticas | `'secondary_inflammation'` | NULL | `'mandatory'` | NULL | FALSE |
| `sls` | Lauril sulfato de sodio (SLS) | `'microbiome_alteration'` | NULL | `'mandatory'` | NULL | FALSE |
| `menthol_camphor` | Mentol y alcanfor | `'secondary_inflammation'` | NULL | `'mandatory'` | NULL | FALSE |
| `physical_scrub_pustule` | Scrubs físicos sobre pústulas | `'mechanical_abrasion'` | NULL | `'mandatory'` | NULL | FALSE |
| `niacinamide_high_with_vit_c` | Niacinamida >10% con vitamina C ácida | `'active_interaction'` | NULL | `'recommended'` | NULL | FALSE |
| `glycolic_high_active_acne` | Ácido glicólico >10% sobre piel activa | `'barrier_disruption'` | NULL | `'recommended'` | NULL | FALSE |
| `bpo_tretinoin_same_time` | Peróxido de benzoílo + tretinoína simultáneos | `'active_interaction'` | NULL | `'mandatory'` | NULL | FALSE |
| `retinoids_all` | Todos los retinoides | `'teratogenicity'` | NULL | `'mandatory'` | NULL | TRUE |
| `salicylic_high_extensive` | Ácido salicílico >2% en área extensa | `'teratogenicity'` | NULL | `'mandatory'` | NULL | TRUE |
| `benzoyl_peroxide_high` | Peróxido de benzoílo >2.5% | `'teratogenicity'` | NULL | `'recommended'` | NULL | TRUE |

**Registros — `rosacea_etr`:**

| ingredient_key | label | avoid_reason_key | comedogenic_index | severity | applies_only_if_skin_type | applies_only_if_pregnant |
|---------------|-------|-----------------|:-----------------:|----------|:-------------------------:|:------------------------:|
| `glycolic_acid_any` | Ácido glicólico (AHA) sin aclimatación | `'trpv1_activation'` | NULL | `'mandatory'` | NULL | FALSE |
| `lactic_acid_high` | Ácido láctico >5% | `'trpv1_activation'` | NULL | `'mandatory'` | NULL | FALSE |
| `salicylic_active_erythema` | Ácido salicílico con eritema activo | `'vasodilation'` | NULL | `'mandatory'` | NULL | FALSE |
| `physical_scrub` | Scrubs físicos de cualquier tipo | `'trpv1_activation'` | NULL | `'mandatory'` | NULL | FALSE |
| `tretinoin_unsupervised` | Tretinoína sin supervisión médica | `'barrier_disruption'` | NULL | `'mandatory'` | NULL | FALSE |
| `retinol_high` | Retinol >0.3% sin aclimatación | `'barrier_disruption'` | NULL | `'mandatory'` | NULL | FALSE |
| `ethyl_alcohol` | Alcohol etílico / SD Alcohol | `'vasodilation'` | NULL | `'mandatory'` | NULL | FALSE |
| `menthol_camphor_eucalyptol` | Mentol, alcanfor, eucaliptol | `'trpv1_activation'` | NULL | `'mandatory'` | NULL | FALSE |
| `synthetic_fragrance` | Fragancias sintéticas (todas) | `'secondary_inflammation'` | NULL | `'mandatory'` | NULL | FALSE |
| `essential_oils_all` | Aceites esenciales (bergamota, jazmín, cítricos) | `'photosensitization'` | NULL | `'mandatory'` | NULL | FALSE |
| `thermogenic_cosmetics` | Cosméticos termogénicos (pimienta, canela, jengibre) | `'trpv1_activation'` | NULL | `'mandatory'` | NULL | FALSE |
| `oxybenzone` | Oxybenzone (benzophenone-3) | `'photosensitization'` | NULL | `'mandatory'` | NULL | FALSE |
| `pure_vitamin_c_high_acid` | Vitamina C L-ascórbica >10% | `'trpv1_activation'` | NULL | `'mandatory'` | NULL | FALSE |
| `sls_cleanser` | Lauril sulfato de sodio en limpiadores | `'microbiome_alteration'` | NULL | `'mandatory'` | NULL | FALSE |
| `niacinamide_first_use_high` | Niacinamida >5% en primer uso | `'vasodilation'` | NULL | `'recommended'` | NULL | FALSE |

**Registros — `rosacea_inflammatory`:**

| ingredient_key | label | avoid_reason_key | comedogenic_index | severity | applies_only_if_skin_type | applies_only_if_pregnant |
|---------------|-------|-----------------|:-----------------:|----------|:-------------------------:|:------------------------:|
| `benzoyl_peroxide_any` | Peróxido de benzoílo (cualquier concentración) | `'secondary_inflammation'` | NULL | `'mandatory'` | NULL | FALSE |
| `retinoids_unsupervised` | Retinoides sin supervisión dermatológica | `'secondary_inflammation'` | NULL | `'mandatory'` | NULL | FALSE |
| `salicylic_any` | Ácido salicílico a cualquier concentración | `'secondary_inflammation'` | NULL | `'mandatory'` | NULL | FALSE |
| `tea_tree_high` | Aceite de árbol de té >1% | `'secondary_inflammation'` | NULL | `'mandatory'` | NULL | FALSE |
| `vitamin_c_acid_any` | Vitamina C en forma ácida | `'trpv1_activation'` | NULL | `'mandatory'` | NULL | FALSE |
| `enzyme_exfoliant` | Enzimas exfoliantes (papaína, bromelina) | `'barrier_disruption'` | NULL | `'mandatory'` | NULL | FALSE |
| `niacinamide_high_start` | Niacinamida >4% como inicio | `'vasodilation'` | NULL | `'mandatory'` | NULL | FALSE |
| `alcohol_beverages` | Alcohol etílico en bebidas | `'vasodilation'` | NULL | `'mandatory'` | NULL | FALSE |
| `hot_drinks_60c` | Bebidas calientes >60°C | `'trpv1_activation'` | NULL | `'mandatory'` | NULL | FALSE |
| `capsaicin_spicy_food` | Comidas con capsaicina (picante) | `'trpv1_activation'` | NULL | `'mandatory'` | NULL | FALSE |
| `niacin_supplement_high` | Niacina suplemento >50 mg | `'vasodilation'` | NULL | `'mandatory'` | NULL | FALSE |
| `thermal_mask_steam` | Mascarillas calientes o de vapor | `'trpv1_activation'` | NULL | `'mandatory'` | NULL | FALSE |
| `ivermectin_topical` | Ivermectina tópica | `'teratogenicity'` | NULL | `'mandatory'` | NULL | TRUE |

**Registros — `perioral_dermatitis`:**

| ingredient_key | label | avoid_reason_key | comedogenic_index | severity | applies_only_if_skin_type | applies_only_if_pregnant |
|---------------|-------|-----------------|:-----------------:|----------|:-------------------------:|:------------------------:|
| `topical_corticosteroids` | Corticosteroides tópicos (hidrocortisona, betametasona, clobetasol) | `'steroid_rebound'` | NULL | `'mandatory'` | NULL | FALSE |
| `inhaled_corticosteroids_perioral` | Corticosteroides inhalados con contacto perioral | `'steroid_rebound'` | NULL | `'mandatory'` | NULL | FALSE |
| `high_fluoride_toothpaste` | Pasta dental con flúor >1450 ppm sin enjuagar | `'occlusion_perioral'` | NULL | `'mandatory'` | NULL | FALSE |
| `heavy_occlusive_perioral` | Vaselina, parafina, ceras espesas en zona perioral | `'occlusion_perioral'` | NULL | `'mandatory'` | NULL | FALSE |
| `dense_silicone_cream` | Cremas con silicona densa (Dimethicone 350+) | `'occlusion_perioral'` | NULL | `'mandatory'` | NULL | FALSE |
| `synthetic_fragrance_perioral` | Fragancias sintéticas en productos periorales | `'secondary_inflammation'` | NULL | `'mandatory'` | NULL | FALSE |
| `essential_oil_mint_cinnamon` | Aceites esenciales de menta, canela, citrus | `'secondary_inflammation'` | NULL | `'mandatory'` | NULL | FALSE |
| `whitening_toothpaste_peroxide` | Dentífrico blanqueador con peróxido de hidrógeno | `'secondary_inflammation'` | NULL | `'mandatory'` | NULL | FALSE |
| `aha_bha_perioral` | AHA y BHA directamente sobre zona perioral | `'secondary_inflammation'` | NULL | `'mandatory'` | NULL | FALSE |
| `retinoid_active_perioral` | Retinoides sin buffer sobre zona perioral activa | `'secondary_inflammation'` | NULL | `'mandatory'` | NULL | FALSE |
| `benzoyl_peroxide_perioral` | Peróxido de benzoílo en zona perioral | `'secondary_inflammation'` | NULL | `'mandatory'` | NULL | FALSE |
| `lanolin_lip_balm` | Bálsamos labiales con lanolina o ceras animales | `'occlusion_perioral'` | 3.5 | `'mandatory'` | NULL | FALSE |

**Registros — `seborrheic_dermatitis`:**

| ingredient_key | label | avoid_reason_key | comedogenic_index | severity | applies_only_if_skin_type | applies_only_if_pregnant |
|---------------|-------|-----------------|:-----------------:|----------|:-------------------------:|:------------------------:|
| `olive_oil_pure_seborrheic` | Aceite de oliva puro en zonas seborreicas | `'fungal_substrate'` | 2.5 | `'mandatory'` | NULL | FALSE |
| `coconut_oil_seborrheic` | Aceite de coco en zonas seborreicas | `'fungal_substrate'` | 4.0 | `'mandatory'` | NULL | FALSE |
| `sunflower_oil_pure` | Aceite de girasol puro | `'fungal_substrate'` | 2.0 | `'recommended'` | NULL | FALSE |
| `rich_vegetable_oil_cream` | Cremas ricas en aceites vegetales sobre zonas seborreicas | `'fungal_substrate'` | NULL | `'mandatory'` | NULL | FALSE |
| `heavy_occlusive_seborrheic` | Bases oclusivas pesadas en zonas seborreicas | `'fungal_substrate'` | NULL | `'mandatory'` | NULL | FALSE |
| `ethyl_alcohol_seborrheic` | Alcohol etílico en tónico o champú | `'microbiome_alteration'` | NULL | `'mandatory'` | NULL | FALSE |
| `sls_shampoo` | Lauril sulfato de sodio en champú | `'microbiome_alteration'` | NULL | `'mandatory'` | NULL | FALSE |
| `synthetic_fragrance_seborrheic` | Fragancias sintéticas en productos faciales y capilares | `'secondary_inflammation'` | NULL | `'mandatory'` | NULL | FALSE |
| `mit_cmit_preservative` | Metilisotiazolinona (MIT/CMIT) | `'secondary_inflammation'` | NULL | `'mandatory'` | NULL | FALSE |
| `propylene_glycol_high` | Propilenglicol >5% como vehículo principal | `'secondary_inflammation'` | NULL | `'recommended'` | NULL | FALSE |
| `fermented_lipid_ingredients` | Lípidos fermentados (galactomyces, bifida ferment) en DS activa | `'fungal_substrate'` | NULL | `'recommended'` | NULL | FALSE |
| `biotin_supplement_high` | Suplementos de biotina >5 mg/día | `'microbiome_alteration'` | NULL | `'recommended'` | NULL | FALSE |
| `alcohol_diet` | Alcohol etílico en bebidas | `'fungal_substrate'` | NULL | `'mandatory'` | NULL | FALSE |
| `simple_sugars_excess` | Azúcares simples en exceso en dieta | `'fungal_substrate'` | NULL | `'recommended'` | NULL | FALSE |

**Registros — `healthy_skin`:**

| ingredient_key | label | avoid_reason_key | comedogenic_index | severity | applies_only_if_skin_type | applies_only_if_pregnant |
|---------------|-------|-----------------|:-----------------:|----------|:-------------------------:|:------------------------:|
| `ethyl_alcohol_main_ingredient` | Alcohol etílico como ingrediente principal | `'barrier_disruption'` | NULL | `'mandatory'` | NULL | FALSE |
| `sls_daily_cleanser` | SLS en limpiador de uso diario | `'microbiome_alteration'` | NULL | `'mandatory'` | NULL | FALSE |
| `alkaline_soap_ph7plus` | Jabón de barra alcalino pH >7 | `'microbiome_alteration'` | NULL | `'mandatory'` | NULL | FALSE |
| `abrasive_physical_scrub` | Exfoliantes físicos abrasivos (sal, azúcar, cáscaras) | `'mechanical_abrasion'` | NULL | `'recommended'` | NULL | FALSE |
| `spf_under_15_uvb_only` | SPF <15 o solo espectro UVB | `'photosensitization'` | NULL | `'mandatory'` | NULL | FALSE |
| `oxidized_vitamin_c` | Vitamina C en formulación oxidada (suero anaranjado/marrón) | `'secondary_inflammation'` | NULL | `'mandatory'` | NULL | FALSE |
| `phototoxic_oils_sun` | Aceites fototóxicos aplicados antes del sol (bergamota, lima, limón) | `'photosensitization'` | NULL | `'mandatory'` | NULL | FALSE |
| `retinoids_all` | Retinoides en cualquier forma | `'teratogenicity'` | NULL | `'mandatory'` | NULL | TRUE |
| `kojic_acid_extensive` | Ácido kójico en uso extensivo | `'teratogenicity'` | NULL | `'recommended'` | NULL | TRUE |
| `hydroquinone` | Hidroquinona 2–4% | `'teratogenicity'` | NULL | `'mandatory'` | NULL | TRUE |
| `chemical_uv_filter_systemic` | Filtros UV con alta absorción sistémica (oxybenzone, octinoxate) | `'teratogenicity'` | NULL | `'recommended'` | NULL | TRUE |
| `comedogenic_oils` | Aceites comedogénicos (coco, oliva, germen de trigo) | `'comedogenicity'` | 3.5 | `'mandatory'` | `'oily'` | FALSE |
| `synthetic_fragrance_sensitive` | Fragancias sintéticas | `'secondary_inflammation'` | NULL | `'mandatory'` | `'sensitive'` | FALSE |
| `topical_steroid_selfmed` | Esteroides tópicos sin prescripción | `'steroid_rebound'` | NULL | `'mandatory'` | NULL | FALSE |

---

## TABLA 7: `avoid_reasons`
Catálogo de razones clínicas de exclusión de ingredientes.

| Campo | Tipo | Restricción | Valores permitidos | Descripción |
|-------|------|-------------|-------------------|-------------|
| `reason_id` | INT | PK · NOT NULL · AUTO_INCREMENT | — | Identificador único |
| `reason_key` | VARCHAR(80) | UNIQUE · NOT NULL | Ver registros | Clave snake_case |
| `label` | VARCHAR(150) | NOT NULL | — | Nombre legible |
| `description` | TEXT | NOT NULL | — | Explicación clínica completa |

**Registros:**

| reason_key | label | description |
|-----------|-------|-------------|
| `comedogenicity` | Comedogenicidad | Obstruye el folículo piloso; perpetúa la formación de nuevos comedones |
| `barrier_disruption` | Irritación / ruptura de barrera | Destruye el manto hidrolipídico o el estrato córneo; genera rebote sebáceo o impide cicatrización |
| `microbiome_alteration` | Alteración del microbioma | Eleva el pH cutáneo o elimina flora protectora; favorece patógenos (C. acnes, Malassezia) |
| `secondary_inflammation` | Inflamación secundaria | Inflama la piel sin relación con la condición principal; amplifica la respuesta inflamatoria existente |
| `mechanical_abrasion` | Abrasión mecánica | Daño físico sobre piel comprometida; dispersa bacterias o rompe estructuras en cicatrización |
| `teratogenicity` | Teratogenicidad | Contraindicado en embarazo por riesgo de malformaciones fetales (categoría X o sin datos de seguridad) |
| `vasodilation` | Vasodilatación | Provoca vasodilatación directa o refleja; desencadena o intensifica el flushing en rosácea |
| `trpv1_activation` | Activación de TRPV1/TRPA1 | Activa receptores termosensibles dérmicos; provoca ardor, enrojecimiento y flushing en pieles reactivas |
| `photosensitization` | Fotosensibilización | Aumenta la reactividad de la piel a la radiación UV; riesgo de quemaduras, manchas o daño crónico |
| `fungal_substrate` | Sustrato fúngico | Aporta lípidos o azúcares que alimentan la proliferación de Malassezia en dermatitis seborreica |
| `occlusion_perioral` | Oclusión perioral | Crea ambiente oclusivo en zona perioral que favorece la disbiosis local y la erupción perioral |
| `steroid_rebound` | Rebote por corticoides | El uso crónico de esteroides tópicos genera dependencia; la suspensión provoca rebound severo |
| `active_interaction` | Interacción entre activos | Combinación de ingredientes activos que se inactivan mutuamente o generan sobre-exfoliación |
| `ph_disruption` | Alteración de pH cutáneo | Eleva el pH superficial por encima del rango ácido protector (4.5–5.5); favorece infecciones |

---

## TABLA 8: `comedogenic_index_scale`
Escala de comedogenicidad de referencia (Kligman & Mills).

| Campo | Tipo | Restricción | Valores permitidos | Descripción |
|-------|------|-------------|-------------------|-------------|
| `index_id` | INT | PK · NOT NULL | — | Identificador del nivel |
| `index_value` | DECIMAL(3,1) | UNIQUE · NOT NULL | `0.0` · `1.0` · `2.0` · `3.0` · `4.0` · `5.0` | Valor numérico |
| `risk_level` | ENUM | NOT NULL | `'none'` · `'minimal'` · `'low'` · `'moderate'` · `'high'` · `'very_high'` | Nivel de riesgo |
| `recommendation` | ENUM | NOT NULL | `'safe'` · `'generally_safe'` · `'use_with_caution'` · `'avoid_oily_skin'` · `'avoid'` · `'always_avoid'` | Recomendación de uso |
| `max_allowed_skin_type` | SET | NOT NULL | `'all'` · `'dry,normal,sensitive'` · `'dry,normal'` · `'none'` | Tipos de piel en los que se permite |
| `example_ingredients` | TEXT | NOT NULL | — | Ingredientes representativos del nivel |

**Registros:**

| index_value | risk_level | recommendation | max_allowed_skin_type | example_ingredients |
|:-----------:|-----------|----------------|----------------------|---------------------|
| 0.0 | `'none'` | `'safe'` | `'all'` | Ácido hialurónico, glicerina, niacinamida, escualano refinado, dimeticona, pantenol |
| 1.0 | `'minimal'` | `'generally_safe'` | `'all'` | Aceite de jojoba, aceite de argán, aceite de rosa mosqueta refinado, vitamina E pura |
| 2.0 | `'low'` | `'use_with_caution'` | `'all'` | Aceite de almendras dulces, manteca de mango refinada, aceite de girasol, aceite mineral cosmético |
| 3.0 | `'moderate'` | `'avoid_oily_skin'` | `'dry,normal,sensitive'` | Aceite de sésamo, aceite de oliva refinado, lanolina, aceite de coco fraccional |
| 4.0 | `'high'` | `'avoid'` | `'none'` | Aceite de coco, miristato de isopropilo, manteca de karité sin refinar, lard |
| 5.0 | `'very_high'` | `'always_avoid'` | `'none'` | Aceite de germen de trigo, palmitato de isopropilo, aceite de linaza en cosmética |

---

## TABLA 9: `skin_profile_modifiers`
Variables del perfil del usuario que modifican las recomendaciones.

| Campo | Tipo | Restricción | Valores permitidos | Descripción |
|-------|------|-------------|-------------------|-------------|
| `modifier_id` | INT | PK · NOT NULL · AUTO_INCREMENT | — | Identificador único |
| `modifier_key` | VARCHAR(80) | UNIQUE · NOT NULL | Ver registros | Clave snake_case |
| `label` | VARCHAR(150) | NOT NULL | — | Nombre legible para UI |
| `data_type` | ENUM | NOT NULL | `'ENUM'` · `'BOOLEAN'` · `'INT'` · `'SET'` · `'DECIMAL'` | Tipo de dato |
| `allowed_values` | TEXT | NOT NULL | — | Valores posibles |
| `default_value` | VARCHAR(50) | NULL | — | Valor por defecto |
| `is_required` | BOOLEAN | NOT NULL · DEFAULT TRUE | `TRUE` · `FALSE` | Si es obligatorio en el perfil |
| `constraint_type` | ENUM | NOT NULL | `'NOT NULL'` · `'NULL'` · `'NOT NULL DEFAULT'` | Restricción SQL equivalente |
| `source` | ENUM | NOT NULL | `'user_input'` · `'derived'` | Si lo declara el usuario o se calcula |

**Registros:**

| modifier_key | label | data_type | allowed_values | default_value | is_required | constraint_type | source |
|-------------|-------|-----------|----------------|:-------------:|:-----------:|-----------------|--------|
| `skin_type` | Tipo de piel | `'ENUM'` | `'oily'` · `'combination'` · `'dry'` · `'sensitive'` · `'normal'` | NULL | TRUE | `'NOT NULL'` | `'user_input'` |
| `fitzpatrick` | Fototipo Fitzpatrick | `'ENUM'` | `'I'` · `'II'` · `'III'` · `'IV'` · `'V'` · `'VI'` · `'unknown'` | `'unknown'` | TRUE | `'NOT NULL DEFAULT'` | `'user_input'` |
| `age` | Edad | `'INT'` | `12` – `90` | NULL | TRUE | `'NOT NULL'` | `'user_input'` |
| `age_group` | Grupo etario | `'ENUM'` | `'teen'` (12–18) · `'young_adult'` (19–29) · `'adult'` (30–44) · `'adult_mature'` (45+) | NULL | FALSE | `'NULL'` | `'derived'` |
| `sex` | Sexo biológico | `'ENUM'` | `'male'` · `'female'` · `'other'` | NULL | TRUE | `'NOT NULL'` | `'user_input'` |
| `has_menstrual_cycle` | Tiene ciclo menstrual activo | `'BOOLEAN'` | `TRUE` · `FALSE` | `FALSE` | TRUE | `'NOT NULL DEFAULT'` | `'user_input'` |
| `is_pregnant` | Está embarazada | `'BOOLEAN'` | `TRUE` · `FALSE` | `FALSE` | TRUE | `'NOT NULL DEFAULT'` | `'user_input'` |
| `is_breastfeeding` | Está en período de lactancia | `'BOOLEAN'` | `TRUE` · `FALSE` | `FALSE` | TRUE | `'NOT NULL DEFAULT'` | `'user_input'` |
| `is_smoker` | Fumadora/or activo/a | `'BOOLEAN'` | `TRUE` · `FALSE` | `FALSE` | TRUE | `'NOT NULL DEFAULT'` | `'user_input'` |
| `sun_exposure` | Nivel de exposición solar diaria | `'ENUM'` | `'low'` · `'moderate'` · `'high'` | NULL | TRUE | `'NOT NULL'` | `'user_input'` |
| `hydration_level` | Nivel de ingesta de agua | `'ENUM'` | `'low'` · `'adequate'` · `'high'` | NULL | TRUE | `'NOT NULL'` | `'user_input'` |
| `ac_exposure` | Exposición a A/C o calefacción | `'ENUM'` | `'never'` · `'sometimes'` · `'constant'` | NULL | TRUE | `'NOT NULL'` | `'user_input'` |
| `has_allergies` | Declaró alergias a ingredientes | `'BOOLEAN'` | `TRUE` · `FALSE` | `FALSE` | TRUE | `'NOT NULL DEFAULT'` | `'user_input'` |
| `allergy_fragrance` | Alergia a fragancias | `'BOOLEAN'` | `TRUE` · `FALSE` | `FALSE` | FALSE | `'NULL'` | `'user_input'` |
| `allergy_paraben` | Alergia a parabenos | `'BOOLEAN'` | `TRUE` · `FALSE` | `FALSE` | FALSE | `'NULL'` | `'user_input'` |
| `allergy_salicylic_acid` | Sensibilidad a ácido salicílico | `'BOOLEAN'` | `TRUE` · `FALSE` | `FALSE` | FALSE | `'NULL'` | `'user_input'` |
| `allergy_lanolin` | Alergia a lanolina | `'BOOLEAN'` | `TRUE` · `FALSE` | `FALSE` | FALSE | `'NULL'` | `'user_input'` |
| `allergy_benzoyl_peroxide` | Alergia a peróxido de benzoílo | `'BOOLEAN'` | `TRUE` · `FALSE` | `FALSE` | FALSE | `'NULL'` | `'user_input'` |
| `allergy_propylene_glycol` | Sensibilidad a propilenglicol | `'BOOLEAN'` | `TRUE` · `FALSE` | `FALSE` | FALSE | `'NULL'` | `'user_input'` |
| `allergy_chemical_uv_filter` | Alergia a filtros UV químicos | `'BOOLEAN'` | `TRUE` · `FALSE` | `FALSE` | FALSE | `'NULL'` | `'user_input'` |
| `has_pcos` | Síndrome de ovario poliquístico | `'BOOLEAN'` | `TRUE` · `FALSE` | `FALSE` | FALSE | `'NULL'` | `'user_input'` |
| `is_menopausal` | En período de menopausia | `'BOOLEAN'` | `TRUE` · `FALSE` | `FALSE` | FALSE | `'NULL'` | `'user_input'` |
| `is_immunocompromised` | Inmunocomprometida/o | `'BOOLEAN'` | `TRUE` · `FALSE` | `FALSE` | FALSE | `'NULL'` | `'user_input'` |
| `country` | País de residencia | `'ENUM'` | `'Panama'` · `'Mexico'` · `'Colombia'` · `'Argentina'` · `'CostaRica'` · `'Guatemala'` · `'Peru'` · `'Chile'` · `'Venezuela'` · `'Other'` | NULL | TRUE | `'NOT NULL'` | `'user_input'` |
| `city` | Ciudad | `'VARCHAR(100)'` | — | NULL | FALSE | `'NULL'` | `'user_input'` |

---

## TABLA 10: `condition_phases`
Fases de evolución del proceso de la piel por condición.

| Campo | Tipo | Restricción | Valores permitidos | Descripción |
|-------|------|-------------|-------------------|-------------|
| `phase_id` | INT | PK · NOT NULL · AUTO_INCREMENT | — | Identificador único |
| `condition_key` | VARCHAR(50) | FK → conditions · NOT NULL | Ver tabla 1 | Condición a la que pertenece |
| `phase_key` | VARCHAR(80) | NOT NULL | Ver registros | Clave snake_case de la fase |
| `label` | VARCHAR(150) | NOT NULL | — | Nombre legible |
| `phase_order` | INT | NOT NULL | `1` · `2` · `3` · `4` | Orden lógico en el proceso |
| `trigger_condition` | TEXT | NOT NULL | — | Condición lógica que activa esta fase |
| `protocol_summary` | TEXT | NOT NULL | — | Resumen del protocolo indicado |
| `spf_minimum` | INT | NULL | `NULL` · `30` · `50` | SPF mínimo requerido en esta fase |

**Registros — `acne_comedonal`:**

| phase_key | label | phase_order | trigger_condition | protocol_summary | spf_minimum |
|----------|-------|:-----------:|-------------------|-----------------|:-----------:|
| `active` | Fase comedonal activa | 1 | Comedones presentes, sin inflamación | BHA + retinoide + niacinamida + SPF | 30 |
| `progression_risk` | Riesgo de progresión inflamatoria | 2 | Comedones + pápulas ocasionales | Añadir BPO 2.5% puntual; monitorear | 30 |
| `maintenance` | Mantenimiento post-tratamiento | 3 | Condición mejorada; continuar tratamiento | Retinoide 1–2x/semana + SPF diario | 30 |
| `improved` | Mejoría sostenida | 4 | Sin comedones nuevos ≥4 semanas | Exfoliante semanal + SPF | 30 |

**Registros — `acne_excorie`:**

| phase_key | label | phase_order | trigger_condition | protocol_summary | spf_minimum |
|----------|-------|:-----------:|-------------------|-----------------|:-----------:|
| `active_erosions` | Erosiones activas (barrera abierta) | 1 | Erosiones y costras presentes | Solo ceramidas + pantenol + oclusivo suave. CERO activos | 50 |
| `healing` | Cicatrización (piel cerrada, sensible) | 2 | Piel cerrada pero hipersensible | Añadir centella + bisabolol + zinc oxide 1% | 50 |
| `post_healing_hpi` | Post-cicatrización con HPI | 3 | Cicatrices cerradas + manchas visibles | Introducir niacinamida 4% gradualmente | 50 |
| `maintenance_bfrb` | Mantenimiento con apoyo conductual | 4 | Sin lesiones activas; control del patrón BFRB | Barrera preventiva + TCC activa | 50 |

**Registros — `acne_inflammatory`:**

| phase_key | label | phase_order | trigger_condition | protocol_summary | spf_minimum |
|----------|-------|:-----------:|-------------------|-----------------|:-----------:|
| `active_inflammatory` | Acné inflamatorio activo | 1 | Pápulas, pústulas y/o nódulos presentes | BPO + retinoide (PM) + niacinamida + barrera + SPF | 30 |
| `nodular_cystic` | Acné noduloquístico (derivar) | 2 | Nódulos y quistes múltiples | Derivar médico; soporte tópico con BPO + barrera | 50 |
| `resolution` | Resolución con HPI residual | 3 | Lesiones activas en reducción | Añadir despigmentante (alpha-arbutin, niacinamida 5%) | 50 |
| `maintenance` | Mantenimiento | 4 | Sin lesiones activas | Retinoide + SPF; vigilar brotes perimenstrales | 30 |

**Registros — `rosacea_etr`:**

| phase_key | label | phase_order | trigger_condition | protocol_summary | spf_minimum |
|----------|-------|:-----------:|-------------------|-----------------|:-----------:|
| `active_flushing` | Flushing activo frecuente | 1 | Episodios de flushing ≥3/semana | Azelaico + ceramidas + SPF mineral. Identificar triggers | 50 |
| `controlled` | ETR controlada | 2 | Flushing <1/semana con control de triggers | Mantener rutina mínima; SPF mineral diario | 30 |
| `progression_to_inflammatory` | Riesgo de progresión | 3 | Aparición de pústulas junto al eritema | Añadir metronidazol (médico); no introducir activos nuevos | 50 |
| `maintenance_trigger_free` | Mantenimiento libre de triggers | 4 | Sin flushing activo; control sostenido | Barrera + SPF + control dietético de triggers | 30 |

**Registros — `rosacea_inflammatory`:**

| phase_key | label | phase_order | trigger_condition | protocol_summary | spf_minimum |
|----------|-------|:-----------:|-------------------|-----------------|:-----------:|
| `active_pustular` | Brote papulopustuloso activo | 1 | Pústulas activas + eritema basal | Metronidazol/ivermectina (médico) + ceramidas + SPF 50+ mineral | 50 |
| `controlled_minimal` | Controlada con rutina mínima | 2 | Pústulas en remisión; eritema persistente | Ceramidas + pantenol + SPF 50+ mineral únicamente | 50 |
| `maintenance_strict` | Mantenimiento estricto | 3 | Sin pústulas activas; control total de triggers | Rutina ultramínima + evitación exhaustiva de triggers | 50 |

**Registros — `perioral_dermatitis`:**

| phase_key | label | phase_order | trigger_condition | protocol_summary | spf_minimum |
|----------|-------|:-----------:|-------------------|-----------------|:-----------:|
| `active_cause_present` | Causa activa presente | 1 | Corticoide/oclusivo/flúor aún en uso | SUSPENDER causa + limpiador suave + glicerina únicamente | 30 |
| `rebound_phase` | Fase de rebote (post-suspensión corticoide) | 2 | 1–3 semanas post-suspensión de corticoide | Tolerar empeoramiento transitorio; mantener rutina mínima | 30 |
| `resolution` | Resolución con tratamiento | 3 | Metronidazol activo o DP en resolución | Continuar tratamiento médico; reforzar causa-identificación | 30 |
| `maintenance` | Mantenimiento libre de causas | 4 | Sin erupción activa | Mantener higiene perioral mínima; no volver a usar causas | 30 |

**Registros — `seborrheic_dermatitis`:**

| phase_key | label | phase_order | trigger_condition | protocol_summary | spf_minimum |
|----------|-------|:-----------:|-------------------|-----------------|:-----------:|
| `active_flare` | Brote activo | 1 | Descamación + eritema + prurito activos | Antifúngico diario (piroctona/zinc piritiona) + no aceites | 30 |
| `controlled` | Controlada | 2 | Síntomas reducidos | Antifúngico 2–3x/semana + ceramidas ligeras | 30 |
| `maintenance` | Mantenimiento crónico | 3 | Asintomática; riesgo de recaída | Antifúngico 1x/semana preventivo + dieta baja en azúcar | 30 |

**Registros — `healthy_skin`:**

| phase_key | label | phase_order | trigger_condition | protocol_summary | spf_minimum |
|----------|-------|:-----------:|-------------------|-----------------|:-----------:|
| `baseline_prevention` | Prevención base | 1 | Piel sana sin condición activa | Limpieza gentil + hidratante + SPF diario | 30 |
| `active_antioxidant` | Antioxidación activa (>18 años) | 2 | Edad ≥18 + exposición solar o tabaquismo | Añadir vitamina C AM + niacinamida | 30 |
| `antiaging_preventive` | Antienvejecimiento preventivo (>25 años) | 3 | Edad ≥25 | Añadir retinol PM gradual + péptidos | 30 |
| `intensive_mature` | Rutina intensiva (>40 años) | 4 | Edad ≥40 + signos de envejecimiento | Retinol + ceramidas + péptidos + SPF 50+ | 50 |

---

*Documento generado para SkinAI — Proyecto de Tesis, Ingeniería de Software, UTP.*
*Fuente: lesiones-descripcion.md · Base bibliográfica: 2020–2025.*
