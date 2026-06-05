# Lesiones Cutáneas — Descripción Clínica, Factores Modificadores y Palabras Clave para SkinAI

> **Uso:** Documento de referencia para el motor de recomendaciones de SkinAI.  
> **Base científica:** Literatura dermatológica 2020–2025 (PubMed, JAAD, BJD, JID).  
> **Formato de palabras clave:** `snake_case`, aptas para variables, etiquetas y filtros de programación.  
> **Estructura por condición:** Fisiopatología → Repercusiones → Síntomas → Necesidades de tratamiento → Modificadores por perfil → **Ingredientes a evitar** → Palabras clave.

---

## Índice

1. [Acné Comedonal](#1-acné-comedonal)
2. [Acné Excoriado](#2-acné-excoriado)
3. [Acné Inflamatorio](#3-acné-inflamatorio)
4. [Rosácea ETR (Eritematotelangiectásica)](#4-rosácea-etr)
5. [Rosácea Inflamatoria](#5-rosácea-inflamatoria)
6. [Dermatitis Perioral](#6-dermatitis-perioral)
7. [Dermatitis Seborreica](#7-dermatitis-seborreica)
8. [Piel Sana (Mantenimiento Preventivo)](#8-piel-sana)
9. [Tabla Maestra de Factores Modificadores](#9-tabla-maestra-de-factores-modificadores)
10. [Referencias Científicas](#10-referencias-científicas)

---

## 1. Acné Comedonal

### 1.1 Definición y fisiopatología

El acné comedonal es la forma más leve del espectro del acné vulgar, caracterizada por la obstrucción del infundíbulo folicular por una mezcla de queratina, sebo y microbiota sin activación inflamatoria clínicamente evidente. Los **comedones abiertos** (puntos negros) deben su coloración a la oxidación de la melanina y los lípidos sebáceos —no a la suciedad—, mientras que los **comedones cerrados** (puntos blancos o milios) mantienen el folículo sellado bajo la epidermis. La producción excesiva de andrógenos estimula las glándulas sebáceas, y la hiperqueratinización folicular impide la descamación normal del epitelio [Tan & Bhate, 2023; Del Rosso & Kircik, 2021].

**Referencia clave:** Tan, J. & Bhate, K. (2023). "Acne vulgaris." *The Lancet*, 401(10391), 1927–1940. https://doi.org/10.1016/S0140-6736(23)00022-X

### 1.2 Repercusiones en la piel

- Dilatación visible y permanente de los poros foliculares.
- Textura irregular con microrrelieve rugoso al tacto.
- Sin tratamiento, evolución hacia acné inflamatorio (pápulas, pústulas, nódulos) por colonización de *Cutibacterium acnes* (antes *P. acnes*) dentro del comedón ocluido.
- Riesgo de hiperpigmentación post-inflamatoria (HPI) si los comedones se inflaman, especialmente en fototipos III–VI.
- Tendencia al ensanchamiento progresivo de los poros en pieles grasas sin regulación activa.

### 1.3 Síntomas subjetivos

- Generalmente **asintomático** (sin dolor ni prurito).
- Sensación de piel "rugosa" o "arenosa" al tacto.
- Incomodidad estética, con impacto negativo demostrado en calidad de vida y autoestima [Bhate & Williams, 2021].
- Ocasionalmente ligera sensibilidad en zonas de alta densidad folicular (nariz, frente, mentón).

### 1.4 Necesidades de tratamiento

| Necesidad | Ingrediente/Activo | Nivel de evidencia |
|-----------|-------------------|-------------------|
| Exfoliación química del folículo | Ácido salicílico (BHA) 0.5–2% | Alta (metaanálisis) |
| Normalización de la queratinización | Retinoides tópicos (retinol, adapaleno 0.1%) | Alta (ECA múltiples) |
| Regulación sebácea | Niacinamida 4–5%, zinc gluconato | Moderada–Alta |
| Desobstrucción folicular | Ácido azelaico 10–15% | Moderada |
| Hidratación sin comedogenicidad | Ácido hialurónico, glicerina, ceramidas | Alta (consenso expertos) |
| Fotoprotección | SPF 30+ no comedogénico (gel o fluido) | Alta |

### 1.5 Modificadores por perfil del usuario

#### Tipo de piel
- **Grasa/Mixta:** Prioridad absoluta en regulación sebácea. Texturas gel o fluido. Evitar aceites comedogénicos (coconut oil, aceite de oliva puro).
- **Seca:** Comedones cerrados frecuentes por acumulación de células muertas. Combinar exfoliante con hidratante barrera potente. Retinoides a frecuencia baja (1–2 noches/semana al inicio).
- **Sensible:** Iniciar con ácido salicílico a baja concentración (0.5–1%) y retinol encapsulado. Priorizar tolerancia sobre velocidad de respuesta.
- **Normal:** Protocolo estándar con margen de ajuste amplio.

#### Tono de piel (Fototipo Fitzpatrick)
- **I–II:** Bajo riesgo de HPI; mayor riesgo de irritación con retinoides. Fotoprotección igualmente obligatoria.
- **III–IV:** Riesgo moderado-alto de HPI si hay progresión inflamatoria. Añadir despigmentante preventivo (niacinamida, ácido kójico) si hay tendencia.
- **V–VI:** Riesgo muy alto de HPI. Evitar sobreexfoliación. Niacinamida 5% es prioridad.

#### Edad
- **12–18 años (adolescentes):** Pico de actividad androgénica. Adapaleno 0.1% es el retinoide de elección (aprobado OTC en muchos países desde 2016). Formulaciones simples y toleradas. Educación sobre no manipular lesiones.
- **19–29 años:** Acné adulto femenino frecuente (influencia hormonal). Considerar ciclo menstrual.
- **30–45 años:** Acné tardío; puede coexistir con signos de envejecimiento. Retinoides ofrecen doble beneficio (acné + antienvejecimiento). Barrera cutánea más frágil.
- **>45 años:** Evaluar interferencias con menopausia o medicación sistémica. Piel más seca; humectantes esenciales en rutina.

#### Sexo y hormonas
- **Mujeres con ciclo menstrual:** Acné hormonal perimenstrual frecuente (días 21–28 del ciclo) por caída estrogénica y pico de progesterona que estimula producción sebácea. Añadir ácido salicílico o regulador sebáceo en la semana previa a la menstruación puede reducir brotes.
- **Embarazadas:** **Adapaleno, tretinoína y todos los retinoides están CONTRAINDICADOS** (teratogénicos — categoría X). Alternativas seguras: ácido azelaico (categoría B), ácido glicólico bajo, peróxido de benzoílo al 2.5% con precaución. Consulta dermatológica obligatoria.
- **Hombres:** Mayor producción androgénica basal; acné tiende a ser más extenso en espalda y cara. Texturas no grasas; rutinas mínimas bien toleradas aumentan adherencia.

#### Alergias
- Alérgicos a fragancias: Usar formulaciones "fragrance-free". Evitar aceite de lavanda, eugenol, linalool.
- Alérgicos a parabenos: Usar conservantes alternativos (fenoxietanol, ácido benzoico).
- Sensibles a ácido salicílico: Sustituir por ácido glicólico al 5–8% o enzimas papaya/piña.

#### Tabaquismo
- El tabaco disminuye la perfusión capilar, empobrece la regeneración celular y aumenta el estrés oxidativo, favoreciendo acné retenido (comedonal) sobre inflamatorio [Capitanio et al., 2020]. Añadir antioxidantes (vitamina C estabilizada, niacinamida) a la rutina.

#### Exposición solar
- El sol puede mejorar transitoriamente el acné por su efecto antibacteriano/antiinflamatorio superficial, pero **induce HPI** en lesiones activas y contraindica retinoides durante el día. Fotoprotección SPF 30+ no comedogénica es no negociable.

#### Hidratación (ingesta de agua)
- La deshidratación cutánea puede paradójicamente aumentar la producción de sebo como mecanismo compensatorio. Recomendación de hidratación tópica y sistémica adecuada.

### 1.6 Ingredientes y productos a evitar

#### Por comedogenicidad (obstruyen el folículo)

| Ingrediente / Producto | Razón | Índice comedogénico* |
|------------------------|-------|----------------------|
| Aceite de coco (*Cocos nucifera*) | Alto índice comedogénico; sella el poro | 4/5 |
| Aceite de oliva (*Olea europaea*) | Rico en ácido oleico; altera el sebo y favorece *C. acnes* | 2–3/5 |
| Manteca de karité sin refinar | Contiene ácidos grasos oclusivos comedogénicos | 3–4/5 |
| Aceite de germen de trigo | Muy alto índice; no recomendado en acné comedonal | 5/5 |
| Lanolina (Lanolin) | Oclusivo pesado que obstruye folículos | 3–4/5 |
| Miristato de isopropilo / Palmitato de isopropilo | Ésteres muy comedogénicos; frecuentes en bases de maquillaje | 4–5/5 |
| Aceite mineral (*Mineral oil*) en baja pureza | Versiones no cosmética-grade pueden obstruir | 2–3/5 |
| Alginatos y derivados de algas en textura densa | Pueden actuar como film oclusivo en pieles grasas | Variable |
| Bases en pomada densa (ungüentos) | Excesivamente oclusivas para piel con acné comedonal | Alta |

> *Escala 0–5 de Kligman & Mills (referencia estándar de comedogenicidad). Índice ≥ 3 se considera riesgo significativo en piel con acné.

#### Por irritación / alteración del microbioma

| Ingrediente / Producto | Razón |
|------------------------|-------|
| Alcohol etílico / Alcohol desnaturalizado (SD Alcohol, Denat.) en >5% | Destruye la barrera lipídica; efecto rebote en producción de sebo |
| Lauril sulfato de sodio (SLS) en limpiadores | Limpiador demasiado agresivo; altera pH y microbioma |
| Fragancias sintéticas y aceites esenciales (lavanda, menta, limón) | Irritación folicular; dermatitis de contacto que agrava comedones |
| Mentol y alcanfor | Efecto "frío" engañoso; irritantes y potencialmente comedogénicos |
| Limpiadores físicos (scrubs con microperlas, sal, azúcar) | La abrasión mecánica inflama el folículo sin desocluirlo |

#### Por formato / tipo de producto

| Tipo de producto | Razón para evitar |
|-----------------|-------------------|
| Maquillaje en barra compacta con base grasa | Alta probabilidad de oclusión folicular |
| Protectores solares de filtro químico en base oleosa | Algunos filtros (benzophenone-3) son comedogénicos |
| Cremas faciales muy ricas o "nutritivas" en pieles grasas | Exceso de emolientes que agravan la obstrucción |
| Mascarillas de peel-off con PVA en uso frecuente | Irritación mecánica repetida; no resuelven la causa |

#### Palabras clave `snake_case` (evitar)

```
avoid_comedogenic_oil, avoid_coconut_oil, avoid_olive_oil_pure,
avoid_isopropyl_myristate, avoid_lanolin, avoid_wheat_germ_oil,
avoid_sls_harsh_cleanser, avoid_ethyl_alcohol_high,
avoid_synthetic_fragrance, avoid_menthol, avoid_camphor,
avoid_physical_scrub_mechanical, avoid_occlusive_heavy_base,
avoid_chemical_filter_comedogenic, non_comedogenic_required
```

---

### 1.7 Palabras clave (`snake_case`)

```
acne_comedonal, open_comedone, closed_comedone, blackhead, whitehead,
comedone_formation, follicular_occlusion, sebum_overproduction, dilated_pores,
non_inflammatory_acne, keratinocyte_hyperproliferation, salicylic_acid,
retinoid, adapalene, azelaic_acid, niacinamide, zinc_gluconate,
oil_free, non_comedogenic, bha_exfoliant, pore_minimizer,
skin_type_oily, skin_type_combination, skin_type_dry, skin_type_sensitive,
fototipo_iii, fototipo_iv, fototipo_v, fototipo_vi,
hormonal_acne, menstrual_cycle, pregnancy_contraindicated_retinoid,
smoking_skin_impact, sun_exposure_acne, post_inflammatory_hyperpigmentation_risk
```

---

## 2. Acné Excoriado

### 2.1 Definición y fisiopatología

El acné excoriado (*acné excoriée des jeunes filles*, aunque no es exclusivo de mujeres jóvenes) representa la intersección entre dermatología y psiquiatría. La persona realiza actos repetitivos de rascado, pellizcado, apretado o extracción de lesiones cutáneas —a menudo imperceptibles incluso para un observador externo— como respuesta a ansiedad, estrés o un impulso compulsivo. El daño mecánico resultante supera ampliamente a la lesión original, generando erosiones, costras hemorrágicas, cicatrices lineales y marcas persistentes [Grant et al., 2021; Berni et al., 2022].

Se clasifica dentro del espectro de los *Body-Focused Repetitive Behaviors* (BFRB) y tiene alta comorbilidad con TOC, ansiedad generalizada y trastorno dismórfico corporal.

**Referencia clave:** Grant, J.E. et al. (2021). "Skin picking disorder." *American Journal of Psychiatry*, 178(1), 21–30.

### 2.2 Repercusiones en la piel

- Ruptura persistente de la barrera cutánea (estrato córneo) → pérdida transepidérmica de agua aumentada (TEWL).
- Cicatrices superficiales (atróficas o hipertróficas según profundidad).
- Hiperpigmentación post-inflamatoria severa, especialmente en fototipos III–VI.
- Eritema e hipersensibilidad crónica en zonas afectadas.
- Mayor riesgo de sobreinfección bacteriana secundaria (Staphylococcus aureus).
- La barrera comprometida hace que cualquier activo —incluso suave— pueda irritar intensamente.

### 2.3 Síntomas subjetivos

- Prurito, ardor o tensión que precede al acto de rascado ("urge to pick").
- Alivio temporal seguido de vergüenza o culpa.
- Dolor en erosiones activas y costras.
- Sensación de piel "en carne viva" en zonas excoriadas.
- Impacto psicológico significativo: aislamiento social, evitación de espejos, depresión comórbida [Koblenzer, 2020].

### 2.4 Necesidades de tratamiento

| Necesidad | Ingrediente/Activo | Nivel de evidencia |
|-----------|-------------------|-------------------|
| Restauración de barrera cutánea | Ceramidas, colesterol, ácidos grasos libres | Alta |
| Cicatrización activa | Pantenol (provitamina B5), centella asiática | Alta |
| Reducción del eritema | Alantoína, bisabolol, extracto de avena | Moderada–Alta |
| Calmante e hidratante | Beta-glucano, ácido hialurónico bajo PM | Alta |
| Prevención de infección | Zinc oxide al 1%, plata coloidal microdosificada | Moderada |
| Reducción de HPI posterior | Niacinamida 4–5% (solo en piel cicatrizada) | Alta |

> ⚠️ **CONTRAINDICADO:** Exfoliantes físicos o químicos, retinoides, peróxido de benzoílo, AHA/BHA sobre piel excoriada activa. Añadir solo cuando la barrera esté restaurada.

### 2.5 Modificadores por perfil del usuario

#### Tipo de piel
- **Todas las pieles:** La barrera comprometida hace que el tipo de piel base sea secundario. Prioridad universal: oclusivos suaves (vaselina, escualano) para sellar la barrera hasta cicatrización.
- **Grasa:** Evitar petrolato en concentraciones altas si genera sensación de sofoco; usar escualano o aceite de jojoba (no comedogénico).

#### Tono de piel (Fototipo)
- **V–VI:** Riesgo extremo de HPI y queloides. Máxima prioridad en cicatrización. Introducir niacinamida 5% solo cuando la erosión haya cerrado completamente.
- **I–II:** Menor riesgo de HPI pero alta sensibilidad al eritema persistente.

#### Edad
- **Adolescentes (12–18):** Alta prevalencia de acné excoriado asociado a presión social y dismorfofobia naciente. Componente psicológico dominante. Derivar a psicología/psiquiatría.
- **Adultos jóvenes (19–35):** Frecuente en mujeres con ansiedad laboral/académica. Terapia cognitivo-conductual (TCC) + hábito de "barrier habit substitution".
- **>35:** Puede aparecer en contextos de alto estrés laboral o trastornos de ansiedad tardíos.

#### Sexo y hormonas
- Prevalencia 3:1 en mujeres vs. hombres [Berni et al., 2022]. El aumento premenstrual de ansiedad puede incrementar la frecuencia de episodios. El tratamiento tópico no puede aislar el origen comportamental.
- Embarazadas: La ansiedad del embarazo puede exacerbar el patrón. Usar solo activos cicatrizantes seguros (pantenol, centella, ceramidas). Evitar plata coloidal en concentraciones altas.

#### Alergias
- Alérgicos a lanolina: Evitar cremas con lanolina (frecuente en pomadas cicatrizantes). Sustituir por ceramidas sintéticas o escualano.
- Sensibles a fragancias: Obligatorio "fragrance-free" dado que la barrera está comprometida.

#### Tabaquismo
- El tabaco retrasa significativamente la cicatrización cutánea al reducir el flujo sanguíneo y la síntesis de colágeno [Siana et al., 2022]. Rutinas cicatrizantes requieren mayor frecuencia.

#### Exposición solar
- La radiación UV sobre cicatrices y HPI activa intensifica la pigmentación de forma permanente. **Fotoprotección SPF 50+ obligatoria y diaria**, incluso en interiores si hay exposición a ventanas.

#### Hidratación
- La deshidratación agrava la sensación de prurito y tensión que desencadena el rascado. Hidratación sistémica y tópica son componentes del tratamiento.

### 2.6 Ingredientes y productos a evitar

> ⚠️ Esta condición tiene la **lista de contraindicaciones más amplia** del sistema mientras la barrera esté comprometida. Se organiza en dos momentos: **fase activa** (con erosiones abiertas) y **fase de cicatrización** (piel cerrada pero sensible).

#### Fase activa — contraindicados hasta cierre de la barrera

| Ingrediente / Producto | Razón |
|------------------------|-------|
| AHA (ácido glicólico, láctico, mandélico) | Exfolian el estrato córneo lesionado; quema química sobre piel abierta |
| BHA (ácido salicílico) | Penetra el folículo lesionado; irritación severa y dolor |
| Retinoides (retinol, retinaldehído, adapaleno, tretinoína) | Aceleran el recambio celular sobre una barrera ya dañada; impiden cicatrización |
| Peróxido de benzoílo | Oxidante fuerte; genera ardor intenso y retrasa la epitelización |
| Vitamina C en forma L-ascórbica pura (>5%) | Acidez elevada; dolor e irritación sobre piel abierta |
| Alcohol etílico / SD Alcohol | Antiséptico agresivo; destruye los nuevos queratinocitos en migración |
| Fragancias sintéticas y aceites esenciales | La barrera rota absorbe irritantes con mucha mayor eficiencia que la piel sana |
| Conservantes en alta concentración (fenoxietanol >1%, MI/MCI) | Sensibilización de contacto potenciada por la barrera comprometida |
| Exfoliantes físicos (scrubs, cepillos, pulidores) | Daño mecánico adicional; ruptura de costras en formación |
| Ácido kójico y alpha-arbutin (despigmentantes) | Irritantes moderados; usar solo después de cicatrización completa |
| Agua micelar con alcohol o fragancia | El arrastre puede eliminar el film lipídico neoformado |
| Tónicos astringentes (con hamamelis, alcohol, mentol) | Astringencia que contrae el tejido en cicatrización; alarga el proceso |

#### Fase de cicatrización — con piel cerrada pero aún sensible

| Ingrediente / Producto | Razón |
|------------------------|-------|
| Retinoides a concentración alta (>0.5%) | Pueden estimular en exceso la dermis en reparación; introducir muy gradualmente |
| Peróxido de benzoílo >2.5% | Irritación residual sobre cicatrices nuevas |
| Aceites altamente comedogénicos (coco, oliva) sobre cicatrices activas | Riesgo de quiste milio sobre cicatriz |
| Silicona oclusiva densa (Dimethicone pesado) sobre costras | Puede atrapar humedad y bacterias en piel aún semiabierta |
| Productos con colorantes artificiales (CI 77xxx, Red 40) | Sensibilización de contacto sobre piel hipersensible |

#### Por formato / tipo de producto

| Tipo de producto | Razón para evitar |
|-----------------|-------------------|
| Mascarillas de arcilla de secado rápido | Al secar generan tensión mecánica sobre costras; pueden arrancarlas |
| Maquillaje en polvo suelto sobre erosiones | Partículas que penetran en piel abierta y contaminan |
| Parches de acné con ácido salicílico | El BHA sobre piel excoriada activa genera quemadura química |
| Dispositivos de radiofrecuencia o microcorriente en casa | Corriente eléctrica sobre barrera rota; riesgo de quemadura |

#### Palabras clave `snake_case` (evitar)

```
avoid_aha_active_phase, avoid_bha_active_phase,
avoid_retinoid_active_phase, avoid_benzoyl_peroxide_active,
avoid_pure_vitamin_c_open_skin, avoid_ethyl_alcohol_barrier_broken,
avoid_fragrance_broken_barrier, avoid_physical_exfoliant,
avoid_astringent_toner, avoid_clay_mask_crust,
avoid_kojic_acid_active, avoid_alpha_arbutin_active,
avoid_high_concentration_preservatives,
contraindicated_active_phase, contraindicated_healing_phase
```

---

### 2.7 Palabras clave (`snake_case`)

```
acne_excorie, skin_picking, excoriation_disorder, bfrb,
skin_barrier_damage, tewl_increased, active_erosion, crust_formation,
atrophic_scar, hypertrophic_scar, post_inflammatory_hyperpigmentation,
barrier_repair, ceramides, panthenol, centella_asiatica, allantoin,
bisabolol, squalane, occlusive,
psychological_component, anxiety_comorbidity, ocd_spectrum,
contraindicated_exfoliant, contraindicated_retinoid, contraindicated_aha,
fototipo_v, fototipo_vi, keloid_risk, scar_prevention,
smoking_wound_healing, spf50_required
```

---

## 3. Acné Inflamatorio

### 3.1 Definición y fisiopatología

El acné inflamatorio comprende el espectro activo del acné vulgar con participación del sistema inmune: **pápulas** (lesiones rojas, elevadas, sin pus, < 5 mm), **pústulas** (pápulas con contenido purulento visible), **nódulos** (lesiones profundas > 5 mm, firmes y dolorosas) y **quistes** (nódulos con contenido semilíquido encapsulado). La fisiopatología implica: (1) hiperproducción sebácea androgénica, (2) hiperqueratinización folicular, (3) proliferación de *Cutibacterium acnes* en ambiente anaerobio rico en sebo, y (4) activación del inflamasoma NLRP3 y liberación de IL-1β, IL-6 y TNF-α [Layton et al., 2021; Szegedi et al., 2023].

**Referencia clave:** Layton, A.M. et al. (2021). "Acne vulgaris: pathogenesis and treatment." *Journal of the American Academy of Dermatology*, 85(5), 1217–1225.

### 3.2 Repercusiones en la piel

- Cicatrices atróficas post-inflamatorias (icepick, rolling, boxcar) en acné noduloquístico sin tratamiento oportuno.
- HPI severa, especialmente pronunciada en fototipos III–VI.
- Eritema post-lesional persistente por neovascularización secundaria.
- Alteración del microbioma cutáneo con disbiosis en favor de cepas hipervirulentas de *C. acnes*.
- Impacto psicológico comparable al de enfermedades crónicas sistémicas: depresión, ansiedad y riesgo suicida elevados [Halvorsen et al., 2020].

### 3.3 Síntomas subjetivos

- Dolor e hipersensibilidad local en nódulos y quistes.
- Sensación de calor y tensión en áreas activas.
- Prurito en pústulas en resolución.
- Sensibilidad aumentada al tacto; incomodidad al usar mascarillas o bufandas.
- Posibles síntomas sistémicos en acné conglobata severo (fiebre leve, malestar).

### 3.4 Necesidades de tratamiento

| Necesidad | Ingrediente/Activo | Nivel de evidencia |
|-----------|-------------------|-------------------|
| Antibacteriano tópico | Peróxido de benzoílo 2.5–5%, ácido azelaico 15–20% | Alta |
| Antiinflamatorio tópico | Niacinamida 4–5%, extracto de té verde, zinc | Alta |
| Regulación sebácea | Retinoides tópicos (adapaleno 0.3%, tretinoína 0.025–0.05%) | Alta |
| Exfoliación no irritante | Ácido salicílico 0.5–2% (no en piel activamente inflamada) | Moderada |
| Despigmentante post-lesional | Niacinamida 5%, ácido kójico, alpha-arbutin | Alta |
| Barrera y calma | Ceramidas, pantenol (entre activos) | Alta |
| Fotoprotección | SPF 30–50 no comedogénico | Alta |

> ⚠️ Acné noduloquístico severo: derivación médica para isotretinoína oral o antibióticos sistémicos. El cuidado tópico es complementario, no suficiente.

### 3.5 Modificadores por perfil del usuario

#### Tipo de piel
- **Grasa:** Texturas gel, agua-gel o solución. Doble limpieza opcional por exceso de sebo.
- **Mixta:** Zonificar: activos más fuertes en zona T, hidratante más rico en mejillas.
- **Seca con acné:** Frecuente en acné adulto. Activos en vehículo hidratante; evitar sobre-limpieza. Adapaleno en base cremosa.
- **Sensible con acné:** Iniciar con peróxido de benzoílo al 2.5% (el 5–10% tiene mayor tasa de irritación con eficacia similar). Ácido azelaico es la alternativa más suave.

#### Tono de piel (Fototipo)
- **I–II:** Mayor sensibilidad a irritantes. Introducir activos gradualmente ("slow titration").
- **III–VI:** HPI es la secuela más prevalente y persistente. Añadir agente despigmentante desde las primeras semanas, incluso antes de la resolución total del acné [Davis & Callender, 2022].
- **V–VI:** Evitar exfoliación agresiva; la HPI puede ser más permanente que las cicatrices. Niacinamida es el activo central.

#### Edad
- **12–15 años:** Preferir adapaleno 0.1% (el único retinoide aprobado sin receta en este grupo). Educación sobre no manipular pústulas. Peróxido de benzoílo lavar-enjuagar (wash-off) para reducir irritación.
- **16–25 años:** Protocolo completo. Evaluar componente hormonal en mujeres (brotes perimenstrales, empeoramiento con anticonceptivos de alto índice progestínico).
- **26–40 años adulto femenino:** Acné tardío predominantemente en mentón y mandíbula; patrón hormonal claro. Niacinamida + ácido azelaico + zinc. Considerar espironolactona (tratamiento médico).
- **>40 años:** Piel más fina, menos tolerante a irritantes. Activos en concentraciones mínimas eficaces; refuerzo de barrera obligatorio.

#### Sexo y hormonas
- **Mujeres con ciclo menstrual:** El pico de progesterona en la fase lútea (días 14–28) aumenta la producción sebácea y la adherencia epitelial, favoreciendo la formación de comedones y pústulas. Aumentar frecuencia de ácido salicílico en esa semana. Contraceptivos con actividad antiandrogénica (acetato de ciproterona, drospirenona) pueden reducir significativamente el acné hormonal [Arowojolu et al., 2020].
- **Embarazadas:** **Peróxido de benzoílo LIMITADO** (categoría C; uso solo si necesario). **Retinoides CONTRAINDICADOS**. Seguro: ácido azelaico (B), limpiadores con ácido glicólico < 10%, sulfato de zinc oral. Consulta dermatológica obligatoria.
- **Hombres:** Acné inflamatorio severo más frecuente por niveles de testosterona más altos. Mayor aceptación de rutinas con texturas ligeras; adherencia mejora con protocolos de 3 pasos máximo.
- **Personas con SOP (síndrome de ovario poliquístico):** Hiperandrogenismo funcional; acné inflamatorio en mandíbula y cuello, resistente a tópicos sin tratamiento hormonal sistémico.

#### Alergias
- Alérgicos a peróxido de benzoílo (raro pero posible: eccema de contacto): Sustituir con ácido azelaico al 15–20% o clindamicina tópica (médica).
- Sensibles a retinoides: Retinol microencapsulado o retinaldehído como precursores más tolerables.

#### Tabaquismo
- El tabaquismo se asocia a acné no inflamatorio predominantemente, pero la vasoconstricción nicotínica retrasa la resolución de lesiones inflamatorias y aumenta las cicatrices [Capitanio et al., 2020]. El CO del humo reduce la oxigenación tisular, deteriorando la respuesta inmune local.

#### Exposición solar
- La exposición aguda puede blanquear transitoriamente el eritema, pero el daño UV perpetúa la inflamación, fotodegrada los retinoides y oscurece la HPI. Fotoprotección diaria con SPF 30–50 + protección física (ropa, sombrero) es esencial.

#### Hidratación
- Ingesta insuficiente de agua (< 1.5 L/día) se asocia a mayor viscosidad sebácea y menor eliminación de toxinas. El beber agua no elimina el acné, pero optimiza el entorno fisiológico para la respuesta a tratamientos.

### 3.6 Ingredientes y productos a evitar

#### Por comedogenicidad y obstrucción folicular

| Ingrediente / Producto | Razón |
|------------------------|-------|
| Aceite de coco, manteca de karité sin refinar | Ocluyen los folículos ya inflamados; agravan la colonización bacteriana anaeróbica |
| Miristato/Palmitato de isopropilo | Ésteres comedogénicos que retienen *C. acnes* en el folículo |
| Aceite mineral en base densa | Forma película oclusiva que impide la respiración folicular |
| Bases de maquillaje en barra, fondos compactos | Alta concentración de ceras comedogénicas |

#### Por efecto proinflamatorio o irritante

| Ingrediente / Producto | Razón |
|------------------------|-------|
| Alcohol etílico / SD Alcohol en concentración alta | Destruye la barrera; la piel responde con rebote sebáceo que retroalimenta el acné |
| Fragancias sintéticas (mezcla de fragancias, Linalool, Limonene, Citral) | Desencadenan dermatitis de contacto que amplifican la inflamación activa |
| Aceites esenciales en concentración alta (tea tree >5%, menta, canela) | A dosis altas son irritantes; el tea tree solo es seguro <2% y con control |
| Lauril sulfato de sodio (SLS) | Emulsionante agresivo; altera el pH ácido que controla *C. acnes* |
| Mentol y alcanfor | Pseudocalmantes; en piel con pústulas generan ardor y potencian eritema |
| Exfoliantes físicos (scrubs gruesos, cepillos) | Fragmentan pústulas, diseminan la bacteria a poros adyacentes ("acné mecánico") |
| Tónicos astringentes con alcohol o hamamelis alto | Resecamiento excesivo sin efecto antibacteriano real; irritación compensatoria |

#### Por interacción con tratamientos activos

| Ingrediente / Producto | Razón |
|------------------------|-------|
| Niacinamida >10% combinada con vitamina C ácida | Puede formar nicotinamida y provocar eritema transitorio; separar o usar en dosis <5% |
| Ácido glicólico > 10% sobre piel con pústulas activas | Aumenta la permeabilidad de las lesiones; riesgo de cicatriz química |
| Retinol + ácido salicílico en la misma rutina sin buffer | Sobre-exfoliación; destruye la barrera que se necesita para tolerar el retinoide |
| Peróxido de benzoílo + tretinoína en la misma aplicación | El BPO oxida la tretinoína, inactivándola; aplicar en momentos distintos del día |
| Aceite de vitamina E puro (tocoferol) en pieles grasas | Índice comedogénico moderado–alto; puede obstruir en pieles propensas al acné |

#### Por riesgo en embarazo (acné inflamatorio + embarazo)

| Ingrediente / Producto | Categoría FDA / Riesgo |
|------------------------|----------------------|
| Tretinoína, adapaleno, tazaroteno | Categoría X — teratogénicos; prohibidos |
| Isotretinoína oral | Categoría X — contraindicación absoluta |
| Ácido salicílico sistémico o >2% en área extensa | Categoría C — evitar en tercer trimestre |
| Ácido kójico oral | Sin datos de seguridad en embarazo |
| Peróxido de benzoílo >2.5% | Categoría C — uso mínimo y localizado |
| Espironolactona oral | Categoría C/D — antiandrógeno; evitar en embarazo |

#### Por formato / tipo de producto

| Tipo de producto | Razón para evitar |
|-----------------|-------------------|
| Mascarillas de carbón activado con propiedades astringentes en piel activa | Efecto de ventosa que puede vaciar comedones adjacentes y diseminar infección |
| Rollers de jade/cuarzo sobre pústulas activas | Contaminación cruzada de bacterias; presión mecánica que rompe lesiones |
| Cremas "todo en uno" con mezcla de activos | Dificultan identificar el responsable si hay reacción adversa |
| Protectores solares con filtros químicos en base oleosa (oxybenzone, avobenzone en crema grasa) | Oclusión combinada con fotosensibilizador potencial |

#### Palabras clave `snake_case` (evitar)

```
avoid_comedogenic_acne_inflammatory, avoid_coconut_oil_acne,
avoid_sls_cleanser_acne, avoid_ethyl_alcohol_acne,
avoid_synthetic_fragrance_acne, avoid_physical_scrub_pustule,
avoid_menthol_camphor_acne, avoid_niacinamide_high_dose,
avoid_glycolic_high_active_acne, avoid_retinol_salicylic_combo,
avoid_bpo_tretinoin_same_time, avoid_vitamin_e_pure_oily,
pregnancy_avoid_retinoid, pregnancy_avoid_salicylic_high,
pregnancy_avoid_kojic, avoid_jade_roller_active_acne,
avoid_astringent_toner_acne
```

---

### 3.7 Palabras clave (`snake_case`)

```
acne_inflammatory, papule, pustule, nodule, cyst,
cutibacterium_acnes, sebum_overproduction, comedone_progression,
benzoyl_peroxide, azelaic_acid, adapalene, tretinoin, retinoid,
antibacterial_topical, anti_inflammatory, niacinamide,
post_inflammatory_hyperpigmentation, atrophic_scar, icepick_scar,
rolling_scar, boxcar_scar, erythema_post_lesional,
skin_type_oily, skin_type_dry_acne, skin_type_sensitive_acne,
fototipo_iii_iv_hpi_risk, fototipo_v_vi_hpi_severe,
hormonal_acne_female, perimenstrual_flare, androgen_driven,
pcos_acne, pregnancy_safe_ingredient, pregnancy_contraindicated,
smoking_scar_risk, sun_exposure_hpi_worsening,
adult_acne, teen_acne, spf30_required
```

---

## 4. Rosácea ETR

### 4.1 Definición y fisiopatología

La rosácea eritematotelangiectásica (subtipo 1 de la clasificación ROSCO/NRS) es una condición neurovascular crónica caracterizada por enrojecimiento facial recurrente o persistente, predominantemente en mejillas, nariz y frente, con episodios de *flushing* (enrojecimiento súbito y difuso), vasos sanguíneos dilatados visibles (telangiectasias) y sensación de ardor o calor. La fisiopatología involucra hiperactividad del receptor TRPV1 (termosensible), disfunción de la barrera cutánea, aumento de la permeabilidad vascular y respuesta inmune innata exacerbada mediada por cathelicidinas (LL-37) [Schaller et al., 2023; Two et al., 2022].

**Referencia clave:** Schaller, M. et al. (2023). "Rosacea management: update from the global ROSacea COnsensus (ROSCO) panel." *British Journal of Dermatology*, 188(4), 540–549.

### 4.2 Repercusiones en la piel

- Eritema central bilateral (mejillas, punta de nariz) de carácter permanente si no se trata.
- Telangiectasias visibles a simple vista; difíciles de revertir sin procedimientos médicos (láser vascular).
- Barrera cutánea estructuralmente debilitada: menor contenido de ceramidas, mayor TEWL, desregulación del microbioma.
- Alta reactividad a desencadenantes externos (triggers): calor, frío, viento, comidas picantes, alcohol, fragancias, luz solar, estrés emocional.
- Progresión hacia rosácea inflamatoria (subtipo 2) si los triggers no se controlan.
- Mayor riesgo de comorbilidades sistémicas: enfermedad cardiovascular, síndrome del intestino irritable, enfermedad de Parkinson (asociación observacional) [Egeberg et al., 2021].

### 4.3 Síntomas subjetivos

- Ardor, picor, escozor o sensación de calor facial, especialmente post-exposición a triggers.
- *Flushing* episódico: enrojecimiento repentino con sensación de calor que dura minutos u horas.
- Piel muy reactiva: cualquier cambio de temperatura, producto nuevo o emoción intensa desencadena reacción visible.
- Sensación de "piel fina" o hipersensible al contacto.
- Impacto psicosocial elevado: vergüenza en situaciones sociales, ansiedad de anticipación ante triggers [Van der Linden et al., 2022].

### 4.4 Necesidades de tratamiento

| Necesidad | Ingrediente/Activo | Nivel de evidencia |
|-----------|-------------------|-------------------|
| Calmante vascular | Ácido azelaico 10–15%, metronidazol 0.75–1% (médico) | Alta |
| Refuerzo de barrera | Ceramidas, ácidos grasos, colesterol (ratio 3:1:1 aprox.) | Alta |
| Antiinflamatorio suave | Niacinamida 2–4% (dosis bajas; el 5% puede inducir flushing en subgrupo) | Moderada |
| Calmante neurovascular | Glicerina, bisabolol, centella asiática, avena coloidal | Moderada–Alta |
| Fotoprotección | SPF 30–50+ mineral (ZnO o TiO2); evitar filtros químicos irritantes | Alta |
| Hidratación sin irritantes | Ácido hialurónico, panthenol; evitar fragancias, alcohol etílico, mentol | Alta |

> ⚠️ **Estrictamente contraindicado sin supervisión médica:** AHA (ácido glicólico, láctico), retinoides tópicos, peróxido de benzoílo, vitamina C en formas ácidas (L-ascórbico puro > 10%), alcohol desnaturalizado.

### 4.5 Modificadores por perfil del usuario

#### Tipo de piel
- **Seca/Sensible:** Predominante en rosácea ETR. Texturas cremosas, leche limpiadora de bajo surfactante, agua micelar sin alcohol. Evitar jabones con pH > 6.
- **Grasa con rosácea:** Poco común pero posible. Texturas ligeras, sérums en gel. Niacinamida a dosis no superiores al 4%.
- **Mixta:** Producto unificado suave; no zonificar con activos fuertes en zona T.

#### Tono de piel (Fototipo)
- **I–III:** Eritema y telangiectasias más visibles; mejor candidato a tratamientos con luz pulsada intensa (IPL) si accede a tratamiento médico. Los fotottipos claros son más sensibles a la fotodegradación UV.
- **IV–VI:** El eritema puede estar enmascarado por la melanina, pero la inflamación subyacente y el daño de barrera son equivalentes. La rosácea puede ser infradiagnosticada en fototipos oscuros [Alexis et al., 2022]. Fotoprotección igualmente crítica.

#### Edad
- **20–35 años:** Onset frecuente. Identificar y evitar triggers desde el inicio. Control temprano previene progresión.
- **35–50 años:** Pico de prevalencia. Frecuente en mujeres perimenopáusicas: los sofocos hormonales amplifican el flushing. Coordinar con ginecología si los episodios son muy frecuentes.
- **>50 años:** Rosácea puede coexistir con dermatitis seborreica y cambios menopáusicos. Rutina mínima y tolerada.
- **Adolescentes:** Poco frecuente. Si aparece, descartar lupus eritematoso (diagnóstico diferencial obligatorio).

#### Sexo y hormonas
- **Mujeres perimenstrual/perimenopáusica:** Los cambios hormonales amplían la frecuencia e intensidad del flushing. Los sofocos menopáusicos son indistinguibles del flushing rosáceo y los potencian [Two et al., 2022]. Rutinas de bajo impacto termogénico.
- **Embarazadas:** Algunos ingredientes habituales en rosácea son seguros (ceramidas, pantenol, ZnO SPF). El metronidazol tópico se clasifica categoría B pero se usa con precaución; consultar médico. El embarazo puede empeorar o mejorar la rosácea (respuesta individual).
- **Hombres:** Menor prevalencia pero mayor riesgo de rosácea fimatosa (engrosamiento nasal). Rutinas de limpieza gentil y SPF mineral.

#### Alergias
- Alérgicos a fragancias: CRÍTICO en rosácea. Cualquier fragancia puede actuar como trigger. Productos estrictamente "fragrance-free" y "alcohol-free".
- Alérgicos a filtros químicos (avobenzone, oxybenzone): Usar exclusivamente SPF mineral (ZnO, TiO2).

#### Tabaquismo
- El tabaco induce vasoconstricción seguida de vasodilatación reactiva, lo que puede desencadenar o intensificar episodios de flushing. Además, los componentes del humo actúan como irritantes tópicos y sistémicos que elevan la inflamación de base [Abokwidir & Feldman, 2020].

#### Exposición solar
- La radiación UV es el trigger más consistente y documentado de la rosácea. La UVA penetra el vidrio y activa el flushing incluso en interiores. **SPF mineral diario (ZnO 15–20%) es obligatorio e innegociable**. Sombrero de ala ancha, lentes de sol con protección UV400.

#### Hidratación
- El agua caliente (baño, vapor) es un trigger térmico. Recomendaciones: agua tibia-fría para limpieza facial, evitar saunas y baños de vapor. Hidratación oral ayuda a mantener el volumen hídrico del espacio intersticial.

### 4.6 Ingredientes y productos a evitar

> La rosácea ETR tiene la segunda lista de restricciones más amplia del sistema. La regla de oro es: **si genera calor, hormigueo, picor o enrojecimiento en los primeros 30 segundos de aplicación, es un trigger tópico.**

#### Exfoliantes y ácidos — contraindicados sin supervisión médica

| Ingrediente / Producto | Razón |
|------------------------|-------|
| Ácido glicólico (AHA) ≥ cualquier concentración sin aclimatación | Baja el pH cutáneo; activa TRPV1 y desencadena flushing |
| Ácido láctico en concentración >5% | Similar al glicólico; potencial de irritación elevado en rosácea |
| Ácido mandélico >5% (sin guía médica) | Más suave que el glicólico pero igualmente capaz de activar trigger en fase activa |
| Ácido salicílico (BHA) en piel con eritema activo | Aumenta la permeabilidad vascular; intensifica el enrojecimiento |
| Scrubs físicos de cualquier tipo | La fricción mecánica es trigger térmico y de presión directo |
| Peeling enzimático intenso (papaína, bromelina en altas dosis) | Desnaturaliza las proteínas de la barrera; aumenta la reactividad |

#### Retinoides — uso muy restringido

| Ingrediente / Producto | Razón |
|------------------------|-------|
| Tretinoína > 0.025% sin guía médica | El retinoide más potente; altamente irritante en rosácea; solo bajo supervisión |
| Retinol >0.3% sin introducción gradual | Puede inducir "retinoid dermatitis" que mimetiza un brote de rosácea ETR |
| Retinaldehído >0.05% de inicio | Similar al retinol en tolerabilidad; requiere período de aclimatación largo |

#### Ingredientes vasoactivos / proinflamatorios

| Ingrediente / Producto | Razón |
|------------------------|-------|
| Alcohol etílico y SD Alcohol | Vasodilatador potente; trigger directo de flushing |
| Mentol, alcanfor, eucaliptol | Activan TRPV1 y TRPA1 (receptores termosensibles); desencadenan ardor y enrojecimiento |
| Hamamelis (*Witch hazel*) con alcohol | El tanino puede irritar; el alcohol es vasodilatador |
| Fragancias sintéticas (todas) | Trigger irritativo por contacto en piel con barrera debilitada |
| Aceites esenciales (rosas, jazmín, bergamota, cítricos) | Fototoxicidad (bergamota, limón) + irritación; todos son triggers potenciales |
| Pimienta negra, canela, jengibre (en cosméticos "termogénicos") | Activan receptores TRPV1 y TRPA1; calor localizado que provoca flushing |
| Niacinamida >5% en primer uso | En un subgrupo sensible, la liberación de histamina puede provocar flushing; iniciar a ≤2% |

#### Filtros solares y activos fotosensibilizantes

| Ingrediente / Producto | Razón |
|------------------------|-------|
| Oxybenzone (Benzophenone-3) | Filtro UV con alta tasa de reacciones alérgicas y fototóxico en rosácea sensible |
| Avobenzone en alta concentración | Puede generar dermatitis de contacto fototóxica en pieles reactivas |
| Octinoxate (Octyl methoxycinnamate) | Penetrante dérmico con potencial irritante en pieles hipersensibles |
| Perfumes en fotoprotectores ("sunscreen con fragancia") | Doble irritación: filtro + fragancia sobre piel reactiva |

#### Vitamina C y antioxidantes en formas irritantes

| Ingrediente / Producto | Razón |
|------------------------|-------|
| Ácido L-ascórbico puro >10% | pH < 3.5; extremadamente ácido; activa triggers por bajar el pH cutáneo bruscamente |
| Vitamina C en formulación inestable (color anaranjado/marrón) | El ácido déhidroascórbico oxidado es prooxidante; genera inflamación |
| Resveratrol en concentración alta sin buffer | Puede ser irritante en pieles con barrera deteriorada |

#### Ingredientes en productos de limpieza

| Ingrediente / Producto | Razón para evitar |
|------------------------|-------------------|
| Lauril sulfato de sodio (SLS) | Surfactante agresivo; elimina ceramidas y deja la piel más reactiva al siguiente trigger |
| Laureth sulfato de sodio (SLES) en altas concentraciones | Similar al SLS, menos agresivo pero aún problemático en rosácea activa |
| Agua micelar con alcohol o fragancia | El alcohol en micelas irrita la piel ya hipersensible |
| Limpiadores "deep pore" o "pore cleansing" | Formulados para piel grasa/acné; demasiado agresivos para barrera rosácea |
| Jabón de barra alcalino (pH > 7) | Altera el pH ácido protector; facilita la activación de TRPV1 |

#### Palabras clave `snake_case` (evitar)

```
avoid_aha_rosacea, avoid_glycolic_acid_rosacea,
avoid_salicylic_rosacea_active, avoid_physical_scrub_rosacea,
avoid_tretinoin_unsupervised_rosacea, avoid_retinol_high_rosacea,
avoid_ethyl_alcohol_rosacea, avoid_menthol_trpv1_trigger,
avoid_camphor_rosacea, avoid_fragrance_rosacea_mandatory,
avoid_essential_oil_rosacea, avoid_thermogenic_cosmetic,
avoid_oxybenzone_rosacea, avoid_pure_vitamin_c_rosacea,
avoid_sls_rosacea, avoid_alkaline_soap_rosacea,
avoid_niacinamide_high_first_use, trpv1_trigger_ingredient,
vasodilator_ingredient_avoid
```

---

### 4.7 Palabras clave (`snake_case`)

```
rosacea_etr, erythematotelangiectatic_rosacea, subtype1_rosacea,
chronic_erythema, telangiectasia, flushing, facial_redness,
neurovascular_dysfunction, trpv1, cathelicidin_ll37,
trigger_avoidance, heat_trigger, alcohol_trigger, spice_trigger,
sun_trigger, stress_trigger, fragrance_trigger,
impaired_skin_barrier, tewl_elevated, ceramide_deficiency,
azelaic_acid, metronidazole_topical, niacinamide_low_dose,
centella_asiatica, bisabolol, colloidal_oat,
mineral_spf, zinc_oxide_spf, titanium_dioxide_spf,
contraindicated_aha, contraindicated_retinoid, contraindicated_vitamin_c_pure,
fragrance_free_mandatory, alcohol_free_mandatory,
fototipo_i_ii_etr, fototipo_iv_vi_underdiagnosed,
menopause_flushing_rosacea, perimenopause_trigger,
pregnancy_rosacea, smoking_vascular_trigger
```

---

## 5. Rosácea Inflamatoria

### 5.1 Definición y fisiopatología

La rosácea papulopustulosa (subtipo 2) superpone pústulas y pápulas inflamatorias sobre el eritema crónico basal de la ETR. Existe colonización aumentada de *Demodex folliculorum* (ácaro folicular ubiquo pero exacerbado en rosácea) que libera bacterias (*Bacillus oleronius*) en la dermis, amplificando la respuesta inmune. El sistema inmune innato, con activación de TLR2 (Toll-Like Receptor 2) y elevación de KLK5 (calicreína-5) que escinde cathelicidinas en péptidos proinflamatorios, mantiene el ciclo de inflamación crónica [Tanghetti et al., 2021].

**Referencia clave:** Tanghetti, E.A. et al. (2021). "Understanding the pathophysiology of facial erythema in rosacea: a review." *Journal of Drugs in Dermatology*, 20(7), 764–770.

### 5.2 Repercusiones en la piel

- Todas las repercusiones de la ETR, más:
- Pústulas superficiales estériles (sin bacterias piógenas) que pueden dejar marcas post-inflamatorias.
- Inflamación dérmica profunda que progresivamente engrosa la piel (pre-fimatosa).
- Exacerbación de telangiectasias por vasodilatación repetida.
- Barrera aún más deteriorada que en ETR pura.
- Impacto psicológico mayor: la presencia de pústulas es con frecuencia confundida con acné, agravando la estigmatización.

### 5.3 Síntomas subjetivos

- Todos los de ETR más:
- Ardor y tensión específicamente en las pústulas.
- Prurito ocasional en áreas activas.
- Mayor sensación de "brotes" que coinciden con triggers identificables.
- Desconfort al aplicar cualquier producto sobre pústulas activas.

### 5.4 Necesidades de tratamiento

| Necesidad | Ingrediente/Activo | Nivel de evidencia |
|-----------|-------------------|-------------------|
| Antibacteriano/antiparasitario | Metronidazol 0.75–1% (médico), ivermectina 1% (médico) | Muy Alta |
| Antiinflamatorio | Ácido azelaico 15%, niacinamida 2–4% | Alta |
| Calmante vascular | Bisabolol, centella, avena coloidal | Moderada–Alta |
| Barrera | Ceramidas, pantenol; texturas ultramínimas | Alta |
| Fotoprotección | SPF 50+ mineral exclusivamente | Alta |
| Evitar todos los triggers | Lista de avoidance exhaustiva | Consenso expertos |

> ⚠️ Es la condición **más restrictiva del sistema**: la ventana terapéutica tópica no médica es muy estrecha. Prácticamente cualquier activo puede actuar como trigger. La derivación médica para metronidazol o ivermectina tópica es casi universal.

### 5.5 Modificadores por perfil del usuario

Los mismos factores que en ETR, pero con mayor restricción en todos los ejes:

- **Cualquier tipo de piel:** Rutina mínima (limpieza gentil + hidratante barrera + SPF mineral). No introducir activos nuevos durante brotes.
- **Fototipos V–VI:** La inflamación de las pústulas puede dejar máculas post-inflamatorias oscuras persistentes.
- **Embarazadas:** Consultar dermatólogo antes de cualquier tratamiento. Metronidazol tópico: categoría B. Ivermectina tópica: evitar por precaución.
- **Mujeres menopáusicas:** La terapia hormonal sustitutiva puede, paradójicamente, mejorar o empeorar la rosácea; vigilar respuesta individual.
- **Fumadores:** El tabaco es un trigger comprobado para los brotes papulopustulosos. La recomendación de abandono del tabaco tiene base médica directa.

### 5.5b Ingredientes y productos a evitar

> La rosácea inflamatoria hereda **todas** las restricciones de la ETR y añade las propias. Esta es la condición con la **lista de evitación más extensa del sistema**. El principio rector es: cualquier activo que no sea ceramida, pantenol, bisabolol, centella o SPF mineral debe considerarse potencialmente trigger hasta demostrar lo contrario en esa piel concreta.

#### Todo lo contraindicado en rosácea ETR (ver sección 4.6), más:

| Ingrediente / Producto | Razón adicional en rosácea inflamatoria |
|------------------------|----------------------------------------|
| Peróxido de benzoílo (cualquier concentración) | Oxidante fuerte; en rosácea inflamatoria amplifica la cascada inflamatoria en lugar de reducirla |
| Ácido azelaico > 20% sin gradación | A concentraciones médicas altas puede provocar eritema y ardor durante las primeras semanas |
| Cualquier retinoide tópico sin supervisión dermatológica | En rosácea con pústulas activas, los retinoides pueden desencadenar brotes violentos |
| Niacinamida > 4% como inicio | Introducir solo cuando las pústulas estén en resolución y siempre desde concentración baja |
| Ácido salicílico (BHA) a cualquier concentración | No es antibacteriano eficaz contra *Demodex*/rosácea inflamatoria; solo irrita |
| Aceite de árbol de té (*Tea tree oil*) > 1% | Aunque tiene actividad antiparasitaria in vitro, en concentraciones >1% es irritante severo en rosácea inflamatoria |
| Sérum de vitamina C en cualquier forma ácida | La acidez activa TRPV1 incluso en baja concentración cuando hay pústulas activas |
| Enzimas exfoliantes (papaína, bromelina) | Aumentan la permeabilidad cutánea; los antígenos de *Demodex* penetran más profundamente |

#### Activos contraindicados también por desencadenar brotes sistémicos

| Ingesta / Hábito | Razón |
|-----------------|-------|
| Alcohol etílico en bebidas | Vasodilatador sistémico; potencia el flushing y la inflamación dérmica |
| Bebidas calientes (> 60 °C) | Trigger térmico oral que activa el flushing |
| Comidas con capsaicina (picante) | Agonista de TRPV1 sistémico → flushing masivo |
| Niacina (vitamina B3 en suplementos de dosis alta > 50 mg) | Induce flushing mediado por prostaglandinas; no confundir con niacinamida tópica |
| Ciertos antibióticos (ej. doxiciclina sin protección solar) | Fotosensibilizantes; aumentan la reactividad UV que es trigger de rosácea |

#### Por formato / tipo de producto

| Tipo de producto | Razón para evitar |
|-----------------|-------------------|
| Bases de maquillaje con cobertura total en pieles con rosácea activa | Oclusión sobre pústulas; dificulta respiración folicular y puede irritar más |
| Correctores de larga duración con alcohol o silicone pesado | Sellado sobre lesiones activas con ingredientes potencialmente irritantes |
| Mascarillas calientes o de vapor | Trigger térmico directo |
| Dispositivos de ultrasonido o calor facial (HIFU casero) | Calor = trigger vasomotor directo |
| Agua floral de rosas sin esterilizar | Puede contener alérgenos florales; las rosas son un sensibilizante documentado |

#### Palabras clave `snake_case` (evitar)

```
avoid_benzoyl_peroxide_rosacea_inflammatory,
avoid_retinoid_rosacea_pustule, avoid_salicylic_rosacea_inflammatory,
avoid_tea_tree_high_rosacea, avoid_vitamin_c_acid_rosacea_pustule,
avoid_enzyme_exfoliant_rosacea, avoid_niacinamide_high_rosacea_inflammatory,
avoid_alcohol_diet_rosacea, avoid_spicy_food_rosacea, avoid_hot_drinks_rosacea,
avoid_niacin_supplement_flushing, avoid_thermal_mask_rosacea,
avoid_hifu_home_device_rosacea, most_restrictive_condition,
minimal_routine_mandatory_rosacea_inflammatory
```

---

### 5.6 Palabras clave (`snake_case`)

```
rosacea_inflammatory, papulopustular_rosacea, subtype2_rosacea,
demodex_folliculorum, bacillus_oleronius, tlr2_activation, klk5,
rosacea_pustule, rosacea_papule, chronic_erythema_base,
metronidazole_topical, ivermectina_topical, azelaic_acid_15,
niacinamide_low_dose, ceramides, panthenol,
trigger_avoidance_strict, minimal_routine, fragrance_free_mandatory,
mineral_spf50_mandatory,
contraindicated_all_exfoliants, contraindicated_aha_bha,
contraindicated_vitamin_c, contraindicated_retinoid,
fototipo_v_vi_post_inflammatory_marks,
pregnancy_dermatologist_required, menopause_rosacea,
smoking_rosacea_trigger, pre_phymatous_risk
```

---

## 6. Dermatitis Perioral

### 6.1 Definición y fisiopatología

La dermatitis perioral (DP) es una erupción papulo-pustulosa crónica distribuida simétricamente alrededor de la boca, con un **margen libre de piel sana** de 2–5 mm justo en el borde del labio (patognomónico). Puede extenderse a zona perinasal y perioocular. Su etiología exacta no está completamente aclarada, pero los factores más consistentemente identificados son: (1) uso de corticosteroides tópicos (el factor causal más frecuente), (2) pasta de dientes con flúor en concentraciones altas, (3) cosméticos con parafinas pesadas o silicones oclusivos, y (4) disbiosis cutánea local [Nguyen et al., 2023; Lipozencic & Ljuljak, 2020].

**Referencia clave:** Nguyen, V. et al. (2023). "Perioral dermatitis: a systematic review." *Journal of the American Academy of Dermatology*, 89(3), 582–591.

### 6.2 Repercusiones en la piel

- Erupción persistente o recurrente que puede cronificarse si no se elimina la causa.
- Eritema, descamación fina y pústulas en zona perioral, perinasal y/o periocular.
- **Paradoja del corticoide:** Los corticosteroides tópicos mejoran transitoriamente la apariencia (suprimen la inflamación) pero al suspenderlos la DP recurre con mayor intensidad (*rebound flare*). Esto genera un ciclo de dependencia.
- Cicatrices ocasionales si hay manipulación o infección secundaria.
- Impacto estético significativo por localización central en el rostro.

### 6.3 Síntomas subjetivos

- Ardor, escozor o prurito en la zona afectada.
- Sensación de tensión cutánea perioral.
- Empeoramiento evidente con cremas de cortisona (pero mejoría transitoria engañosa al aplicarlas).
- Vergüenza estética por localización visible.

### 6.4 Necesidades de tratamiento

| Necesidad | Ingrediente/Activo | Nivel de evidencia |
|-----------|-------------------|-------------------|
| Suspensión inmediata de corticoides tópicos | (Acción, no ingrediente) | Alta |
| Antibacteriano/antiinflamatorio suave | Metronidazol 0.75–1% (médico), ácido azelaico 10% | Alta |
| Limpieza mínima sin irritantes | Limpiador sin detergente fuerte, sin perfume | Consenso |
| Hidratación ultramínima | Ácido hialurónico, glicerina (sin oclusivos pesados) | Consenso |
| Evitar oclusivos perioral | Evitar vaselina, siliconas, parafinas en zona perioral | Alta (causal) |

> ⚠️ El tratamiento definitivo implica identificar y eliminar el factor causal. El manejo tópico no médico es de soporte, no curativo. Derivación médica para metronidazol o eritromicina tópica.

### 6.5 Modificadores por perfil del usuario

#### Tipo de piel
- Habitualmente cualquier tipo puede verse afectado. La piel sensible tiene mayor riesgo si usa productos oclusivos. Priorizar productos con lista de ingredientes muy corta.

#### Tono de piel (Fototipo)
- En fototipos oscuros (V–VI), la DP puede dejar máculas hiperpigmentadas post-inflamatorias más persistentes. La suspensión del agente causal sigue siendo prioritaria.

#### Edad
- **Niños/adolescentes:** La DP es frecuente en niños pequeños que usan pasta dental fluorada en exceso. Reducir o cambiar pasta dental puede ser parte del tratamiento.
- **Adultos jóvenes (20–40):** Pico de prevalencia, más frecuente en mujeres. Uso de cremas faciales con corticoides o "fundentes" de silicona como causa principal.
- **>40:** Puede coexistir con rosácea. Distinguir es clínicamente importante.

#### Sexo y hormonas
- **Mujeres:** Mayor prevalencia, en parte por mayor uso de cosméticos oclusivos y corticoides tópicos automedicados. Los cambios hormonales pueden influir, pero el factor causal externo es dominante.
- **Embarazadas:** Suspender corticoides tópicos es igualmente prioritario. Muchas alternativas médicas son de uso limitado; el manejo es principalmente de soporte (eliminar causas) más que tópico activo.

#### Alergias
- Si existe alergia al metronidazol (raro): ácido azelaico como alternativa. Siempre "fragrance-free" y sin parabenos en zona perioral.

#### Tabaquismo y exposición solar
- No son factores etiológicos directos de la DP, pero deterioran la respuesta cutánea. Fotoprotección en labios y zona perioral con bálsamo labial SPF o SPF mineral.

### 6.6 Ingredientes y productos a evitar

#### Causas directas — eliminar es el tratamiento principal

| Ingrediente / Producto | Razón |
|------------------------|-------|
| **Corticosteroides tópicos** (hidrocortisona, betametasona, clobetasol, etc.) | Causa #1 de DP; el uso crónico induce dependencia y rebound severo al suspender |
| **Corticosteroides inhalados** (fluticasona, budesonida) que tocan la zona perioral | Pequeñas dosis repetidas en piel perioral pueden desencadenar DP |
| **Pasta dental con flúor en alta concentración** (>1450 ppm) usada sin enjuagar bien | El flúor residual en piel perioral se asocia a brotes; cambiar a pasta baja en flúor o niños |
| **Oclusivos pesados periorales** (vaselina, parafina, ceras espesas en bálsamo labial) | La oclusión folicular en zona perioral favorece la disbiosis local |
| Cremas "fundantes" faciales con siliconas densas (Dimethicone 350+ como primer ingrediente) | Oclusión extendida que mantiene el ambiente húmedo favorable a la erupción |
| Protectores solares en pomada o barra para labios con alto contenido graso | Oclusión en zona labial / perioral; usar SPF fluido o gel en esa zona |

#### Por irritación local en zona perioral

| Ingrediente / Producto | Razón |
|------------------------|-------|
| Fragancias sintéticas en todo producto perioral | La piel perioral tiene alta absorción dérmica; las fragancias agravan la inflamación |
| Aceites esenciales de menta, canela, citrus | Irritantes de contacto clásicos en zona perioral |
| Dentífricos blanqueadores con peróxido de hidrógeno | El contacto con piel perioral irrita y puede precipitar o agravar la DP |
| Tónicos o lociones astringentes con alcohol perioral | Irritación y desequilibrio del microbioma local |
| Exfoliantes labiales con azúcar o sal | La abrasión en la zona de transición piel-labio agrava las lesiones periorales |
| Ácidos en cualquier concentración directamente sobre zona perioral | AHA y BHA no tienen indicación en DP; solo irritan |
| Retinoides aplicados sin bufer sobre zona perioral activa | En DP inflamatoria activa, los retinoides empeoran las pústulas periorales a corto plazo |

#### Por relación con otras condiciones simultáneas

| Ingrediente / Producto | Razón |
|------------------------|-------|
| Niacinamida en alta concentración (>5%) sobre zona perioral irritada | Puede generar eritema adicional en piel ya inflamada |
| Peróxido de benzoílo sobre lesiones periorales | Oxidante en piel fina perioral; cicatrices post-uso |
| Máscaras faciales de todo tipo sobre zona perioral activa | Oclusión + fricción al retirar; evitar completamente la zona perioral |

#### Por formato / tipo de producto

| Tipo de producto | Razón para evitar |
|-----------------|-------------------|
| Bálsamos labiales con lanolina o ceras animales | Altamente oclusivos; ingredientes comedogénicos en zona perioral |
| Maquillaje líquido de larga duración en zona perioral | Ocluyente; el removedor con aceite agrava la disbiosis |
| Cremas antienvejecimiento con péptidos + silicona + retinol perioral | Mezcla de activos sobre zona sensible; imposible identificar el irritante |
| Agua de rosas o tónicos florales sobre zona perioral | Potenciales alérgenos de contacto en piel reactiva |

#### Palabras clave `snake_case` (evitar)

```
avoid_topical_corticosteroid_perioral, avoid_steroid_rebound,
avoid_high_fluoride_toothpaste_perioral, avoid_petrolatum_perioral,
avoid_heavy_silicone_perioral, avoid_fragrance_perioral,
avoid_essential_oil_mint_perioral, avoid_whitening_toothpaste,
avoid_aha_bha_perioral, avoid_retinoid_active_perioral,
avoid_benzoyl_peroxide_perioral, avoid_lanolin_lip_balm,
avoid_astringent_toner_perioral, avoid_sugar_salt_scrub_lips,
corticosteroid_primary_cause, occlusive_ingredient_perioral
```

---

### 6.7 Palabras clave (`snake_case`)

```
perioral_dermatitis, periorificial_dermatitis,
corticosteroid_induced, topical_steroid_rebound,
papulopustular_perioral, lip_free_margin,
metronidazole_topical, azelaic_acid_10,
minimal_ingredient_formula, no_occlusive_perioral,
avoid_heavy_silicone, avoid_petrolatum_perioral,
avoid_high_fluoride_toothpaste,
fragrance_free_mandatory, alcohol_free,
fototipo_v_vi_perioral_hpi,
pregnancy_remove_causative_agent,
corticoid_dependency_cycle, perinasal, periocular_variant
```

---

## 7. Dermatitis Seborreica

### 7.1 Definición y fisiopatología

La dermatitis seborreica (DS) es una dermatosis inflamatoria crónica y recurrente de las áreas seborreicas del cuerpo: cuero cabelludo, cara (frente, entrecejo, pliegues nasolabiales, barba), canal auditivo externo y, ocasionalmente, área esternal y axilas. La fisiopatología central implica: (1) hipersecreción sebácea, (2) colonización por el hongo levaduriforme *Malassezia* (especialmente *M. globosa* y *M. restricta*) que metaboliza triglicéridos del sebo liberando ácidos grasos irritantes y proinflamatorios, y (3) respuesta inmune exagerada del huésped a los metabolitos fúngicos, con activación de TH17 y producción de IL-17 e IL-22 [Borda & Wikramanayake, 2021; Deng et al., 2022].

**Referencia clave:** Borda, L.J. & Wikramanayake, T.C. (2021). "Seborrheic Dermatitis and Dandruff." *Journal of Clinical and Investigative Dermatology*, 9(1), 1–14.

### 7.2 Repercusiones en la piel

- Descamación grasa (escamas amarillentas en zonas seborreicas) o descamación seca (cuero cabelludo/cara).
- Eritema en placas en zonas seborreicas, con bordes relativamente bien definidos.
- Prurito de intensidad variable, a veces severo en cuero cabelludo.
- Tendencia a la cronicidad con brotes periódicos, especialmente ante estrés, clima seco, fatiga o inmunodepresión.
- En casos severos (especialmente en inmunocomprometidos o personas con VIH): DS extensa y resistente al tratamiento habitual.
- Impacto social por escamas visibles en ropa oscura y eritema facial.

### 7.3 Síntomas subjetivos

- Prurito, a veces intenso, en cuero cabelludo y cara.
- Sensación de piel "grasienta" y eritematosa en pliegues faciales.
- Picor y ardor en zonas de descamación activa.
- Empeoramiento notorio con estrés agudo, temperaturas extremas (frío seco o calor húmedo) y alcohol.
- Ciclos de mejoría y recaída; la remisión completa es rara sin mantenimiento.

### 7.4 Necesidades de tratamiento

| Necesidad | Ingrediente/Activo | Nivel de evidencia |
|-----------|-------------------|-------------------|
| Antifúngico tópico | Piroctona olamina 1%, zinc piritiona 1–2%, ketoconazol 1–2% | Alta |
| Antiinflamatorio suave | Niacinamida 4–5%, ácido azelaico, extracto de té verde | Alta |
| Regulación sebácea | Niacinamida, zinc gluconato | Moderada–Alta |
| Calmante del prurito | Avena coloidal, alantoína, pantenol | Alta |
| Exfoliación antifúngica | Ácido salicílico 1–2% (combinado con antifúngico) | Moderada |
| Barrera | Ceramidas ligeras; evitar oclusivos comedogénicos | Consenso |
| Fotoprotección | SPF 30+ (la luz UV puede agravar la DS facial) | Alta |

### 7.5 Modificadores por perfil del usuario

#### Tipo de piel
- **Grasa/Mixta:** Condición central. Limpiadores con zinc o piroctona; sérums ligeros; evitar aceites de alta comedogenicidad.
- **Seca:** Menos frecuente pero posible. Balancear antifúngico con hidratante sin oclusivos pesados. El cuero cabelludo seco con DS es frecuente; champú antifúngico suave 2–3 veces por semana.
- **Sensible:** Usar formulaciones sin alcohol, sin fragrancias, con antifúngico a concentraciones menores. Introducir gradualmente.

#### Tono de piel (Fototipo)
- **I–II:** El eritema seborreico es más visible pero el daño inflamatorio es similar en todos los fototipos.
- **III–VI:** La DS puede dejar máculas hipopigmentadas (manchas blancas) o hiperpigmentadas en la resolución; documentado en varios estudios en fototipos oscuros [Hay, 2020]. Protección solar en fases de tratamiento activo.

#### Edad
- **0–3 meses (lactantes):** Costra láctea (*seborrheic cap*). Aceite de bebé + champú suave; autolimitada en la mayoría.
- **Adolescentes:** Aumento de seborreica por pico androgénico. Champú con zinc 1–2 veces por semana. Limpiador facial con piroctona.
- **25–50 años:** Prevalencia máxima. Tratamiento de mantenimiento con antifúngico intermitente (2–3 veces/semana).
- **>60 años:** Puede coexistir con psoriasis ("seboripsoriasis"). Menos seborreica activa de cara, más de cuero cabelludo.

#### Sexo y hormonas
- **Hombres:** Prevalencia 2–3:1 respecto a mujeres, por mayor actividad androgénica y producción sebácea. La DS de barba es frecuente. Limpiar el área de barba con champú antifúngico o syndet antifúngico.
- **Mujeres menstruantes:** Los brotes pueden empeorar en la semana premenstrual (pico androgénico relativo). Aumento temporal de la frecuencia del limpiador antifúngico.
- **Embarazadas:** Los cambios hormonales pueden exacerbar la DS. Zinc piritiona tópico (categoría C, uso tópico considerado de bajo riesgo) y piroctona olamina son alternativas relativamente seguras. Consultar médico para formas severas.

#### Alergias
- Alérgicos a fragancias: Frecuente en DS por barrera comprometida; estrictamente "fragrance-free".
- Sensibles a propilenglicol (vehículo frecuente en antifúngicos): Buscar formulaciones alternativas o usar cremas con base acuosa.

#### Tabaquismo
- El tabaquismo aumenta la colonización por *Malassezia* por alteración del microbioma cutáneo y mayor producción de ácidos grasos libres [Xu et al., 2021]. La DS tiende a ser más refractaria en fumadores.

#### Exposición solar
- Moderada exposición solar puede mejorar la DS facial (efecto antiinflamatorio UV leve), pero la exposición excesiva la empeora y puede inducir brotes post-solar. SPF no comedogénico es recomendado.

#### Hidratación y dieta
- La dieta alta en azúcares simples y alcohol incrementa la disponibilidad de nutrientes para *Malassezia* (usa triglicéridos y azúcares cutáneos). Reducción del consumo de azúcar y alcohol mejora la respuesta al tratamiento.

### 7.6 Ingredientes y productos a evitar

#### Por nutrición del hongo Malassezia (feed the fungus)

| Ingrediente / Producto | Razón |
|------------------------|-------|
| Aceite de oliva puro aplicado en cuero cabelludo o cara seborreica | *Malassezia* metaboliza preferentemente el ácido oleico (C18:1); el aceite de oliva lo aporta directamente |
| Aceite de coco en zonas seborreicas | Ácidos grasos de cadena media son sustrato para el hongo en ciertas cepas |
| Aceite de girasol puro (*Helianthus annuus*) | Rico en ácido linoleico; las cepas de *Malassezia* pueden utilizar estos lípidos |
| Cremas muy ricas en aceites vegetales (manteca de karité, aceite de argán) sobre áreas seborreicas | Aportan lípidos que alimentan la colonización fúngica |
| Bases en ungüento u oclusivas pesadas en zonas seborreicas | Crean el ambiente húmedo y rico en lípidos ideal para la proliferación de *Malassezia* |

#### Por irritación o perturbación del microbioma

| Ingrediente / Producto | Razón |
|------------------------|-------|
| Alcohol etílico en tónico o champú | Reseca la piel → rebote sebáceo → más sustrato para *Malassezia*; altera el microbioma protector |
| Lauril sulfato de sodio (SLS) en champú o limpiador | Elimina los lípidos protectores del cuero cabelludo; el rebote sebáceo alimenta el ciclo |
| Fragancias sintéticas en productos faciales y capilares | Irritación que amplifica la respuesta inflamatoria subyacente |
| Conservantes fuertes (MIT/CMIT — metilisotiazolinona) | Sensibilizante de contacto reconocido; frecuente en champús antifúngicos económicos |
| Propilenglicol como vehículo principal | En concentraciones > 5% puede irritar en piel con DS activa; sustituir por glicerina |

#### Por empeoramiento del ciclo seborreico

| Ingrediente / Producto | Razón |
|------------------------|-------|
| Cremas no antifúngicas de "mantenimiento" sin barrera adecuada | Sin principio activo antifúngico, la crema hidratante convencional no frena el ciclo |
| Shampoos anticaspa con zinc piritiona usados como gel de limpieza facial (uso fuera de indicación) | El zinc piritiona en champú puede tener emulsionantes irritantes para la piel facial; usar formulación específica facial |
| Hidratantes con lípidos fermentados (galactomyces, bifida ferment) en DS activa | Los metabolitos fúngicos fermentados pueden cross-reactivar la respuesta inmune anti-*Malassezia* |
| Suplementos de biotina en dosis alta (>5 mg/día) | La biotina en exceso puede alterar el microbioma intestinal y se asocia a empeoramiento de DS en casos reportados |

#### Relacionados con dieta y hábitos (triggers internos)

| Ingesta / Hábito | Razón |
|-----------------|-------|
| Alcohol etílico en bebidas | Dilata los vasos sebáceos y aumenta la producción de sebo; empeora la DS facial y capilar |
| Azúcares simples en exceso (azúcar blanca, refrescos, pan blanco) | Elevan la disponibilidad cutánea de triglicéridos vía aumento de insulina y sebum |
| Dieta alta en grasas saturadas sin omega-3 de balance | Favorece la síntesis de ácidos grasos comedogénicos en el sebo |

#### Por formato / tipo de producto

| Tipo de producto | Razón para evitar |
|-----------------|-------------------|
| Mascarillas capilares nutritivas ricas en aceites vegetales (usadas en cuero cabelludo con DS) | Aportan sustrato para *Malassezia*; usar solo en puntas |
| Aerosoles capilares con alcohol + fragancias | Depositan irritantes directamente en cuero cabelludo seborreico |
| Cremas "todo en uno" face + cuero cabelludo sin antifúngico | Sin principio activo no frenan la colonización |
| Maquillaje en crema o BB cream en zonas seborreicas (cejas, nasal) | Oclusión que mantiene el ambiente favorable al hongo |

#### Palabras clave `snake_case` (evitar)

```
avoid_olive_oil_seborrheic, avoid_coconut_oil_seborrheic,
avoid_heavy_occlusive_seborrheic, avoid_sls_shampoo_seborrheic,
avoid_ethyl_alcohol_seborrheic, avoid_fragrance_seborrheic,
avoid_mit_cmit_preservative, avoid_propylene_glycol_high,
avoid_fermented_ingredient_seborrheic, avoid_high_biotin_supplement,
avoid_alcohol_diet_malassezia, avoid_sugar_diet_seborrheic,
malassezia_substrate_ingredient, avoid_hair_oil_scalp_seborrheic,
avoid_occlusive_cream_seborrheic_zone
```

---

### 7.7 Palabras clave (`snake_case`)

```
seborrheic_dermatitis, malassezia_globosa, malassezia_restricta,
sebaceous_zone, scalp_seborrheic, facial_seborrheic,
greasy_scale, yellow_scale, nasolabial_fold, brow_seborrheic,
pyroctone_olamine, zinc_pyrithione, ketoconazole_topical,
antifungal_topical, sebum_regulation, niacinamide,
colloidal_oat, allantoin, salicylic_acid_antifungal,
chronic_relapsing, stress_trigger, cold_dry_trigger,
alcohol_diet_trigger, immune_response_exaggerated,
skin_type_oily, skin_type_mixed,
fototipo_iii_vi_hypopigmentation_risk, fototipo_i_ii_erythema_visible,
male_predominance, androgen_driven_seborrhea,
pregnancy_seborrheic, infant_cradle_cap,
smoking_malassezia, spf_non_comedogenic
```

---

## 8. Piel Sana

### 8.1 Definición y estado de la barrera

La piel sana no implica ausencia de necesidades de cuidado, sino la ausencia de condición patológica activa. La barrera cutánea funcional se caracteriza por: pH superficial entre 4.5 y 5.5 (ligeramente ácido), TEWL dentro del rango normal (< 10 g/m²/h), microbioma equilibrado dominado por *Staphylococcus epidermidis* y *Cutibacterium acnes* avirulentas, y suficiente producción de ceramidas, colesterol y ácidos grasos libres para mantener la cohesión del estrato córneo [Barker & Zhang, 2022].

**Referencia clave:** Barker, J. & Zhang, S. (2022). "The skin microbiome and skin barrier: current concepts." *British Journal of Dermatology*, 187(5), 621–632.

### 8.2 Repercusiones sin mantenimiento

- Aceleración del fotoenvejecimiento por acumulación de daño UV no contrarrestado.
- Disminución de la producción de ceramidas y sebo con la edad → piel más seca y menos elástica.
- Mayor susceptibilidad a desarrollar condiciones inflamatorias ante factores externos (polución, estrés).
- La falta de antioxidantes aumenta el estrés oxidativo acumulado, predisponiendo a manchas solares y pérdida de uniformidad del tono.

### 8.3 Necesidades de mantenimiento preventivo

| Necesidad | Ingrediente/Activo | Nivel de evidencia |
|-----------|-------------------|-------------------|
| Hidratación de barrera | Ceramidas, ácido hialurónico, glicerina | Alta |
| Fotoprotección | SPF 30–50+ UVA/UVB (el pilar más importante) | Muy Alta |
| Antioxidación | Vitamina C estabilizada (10–20%), vitamina E, niacinamida | Alta |
| Limpieza | Limpiador con pH 4.5–5.5, sin SLS en pieles secas | Alta |
| Renovación celular preventiva | Retinol 0.1–0.3% (noche, > 25 años), AHA al 5–8% semanal | Alta |
| Uniformidad del tono | Niacinamida 5%, alpha-arbutin 1–2% | Moderada–Alta |

### 8.4 Modificadores por perfil del usuario

#### Tipo de piel
- **Normal:** Amplia tolerancia. Rutina equilibrada con limpieza + hidratante + SPF.
- **Grasa:** Texturas gel, SPF fluido no comedogénico. Niacinamida central.
- **Seca:** Limpiador en crema, hidratante oclusivo (ceramidas + escualano), SPF en base cremosa.
- **Sensible:** Ingredientes mínimos, sin fragrancias, SPF mineral. Vitamina C en forma ascorbil glucósido (más estable y menos irritante).

#### Tono de piel (Fototipo)
- **I–II:** Máxima prioridad en fotoprotección y antienvejecimiento temprano. El daño UV acumulado es acelerado y se manifiesta antes.
- **III–IV:** Tendencia a hiperpigmentación post-solar. Vitamina C + niacinamida + SPF son el trío esencial.
- **V–VI:** La piel tiene mayor melanina natural (no reemplaza al SPF). Priorizar antioxidantes y uniformidad del tono. SPF igualmente obligatorio; el melanoma ocurre con alta mortalidad en fototipos oscuros por diagnóstico tardío.

#### Edad
- **12–17 años:** Limpieza gentil + hidratante ligero + SPF. Sin activos agresivos.
- **18–25 años:** Introducir vitamina C por la mañana. Retinol preventivo opcional desde los 20.
- **26–35 años:** Retinol 0.25–0.5% de forma regular. Péptidos como complemento.
- **36–50 años:** Retinol 0.5–1%, vitamina C 15–20%, péptidos, SPF 50+. Hidratante más rico.
- **>50 años:** Énfasis en barrera (ceramidas + oclusivo suave), retinol o retinaldehído. SPF diario. Considerar retinoides con prescripción médica.

#### Sexo y hormonas
- **Mujeres con ciclo menstrual:** La piel cambia a lo largo del ciclo. Semana 1–2 (fase folicular): piel más luminosa, menos grasa; ideal para exfoliación y vitamina C. Semana 3–4 (fase lútea): piel más reactiva y grasa; reforzar hidratación.
- **Embarazadas:** Evitar retinoides y ácido kójico. Safe: vitamina C (ascorbil glucósido), niacinamida, ácido glicólico bajo, SPF mineral. La "máscara del embarazo" (melasma) puede prevenirse con SPF riguroso desde el primer trimestre.
- **Hombres:** Rutinas cortas y textura ligera aumentan adherencia. SPF en hidratante con factor integrado. Afeitado como exfoliación física involuntaria: hidratante post-afeitado sin alcohol.
- **Menopausia:** Caída estrogénica reduce ceramidas y colágeno. Rutinas más nutritivas, retinoides, péptidos.

#### Alergias
- Piel sana con alergias cosméticas: mapear alérgenos específicos (fragancias, conservantes, níquel) y construir rutina alrededor de esas restricciones. Un dietista de componentes (INCIDecoder, CosDNA) facilita la selección.

#### Tabaquismo
- El tabaquismo acelerada el fotoenvejecimiento de forma independiente al UV, genera "arrugas de fumador" (labiales y perioculares) y disminuye la síntesis de colágeno y vitamina C cutánea. Antioxidantes (vitamina C, E, niacinamida) son especialmente importantes.

#### Exposición solar
- La fotoprotección diaria es la intervención con mayor relación coste-beneficio en piel sana. Un metaanálisis de 2021 [Lim et al., 2021] confirma que el uso regular de SPF reduce en un 24% el riesgo de melanoma cutáneo y en > 40% el de carcinoma espinocelular.

#### Hidratación
- La ingesta adecuada de agua (>1.5–2 L/día) se correlaciona con mayor hidratación del estrato córneo en piel no deshidratada crónicamente. La suplementación con colágeno hidrolizado (>2.5 g/día durante ≥8 semanas) muestra mejoría significativa en elasticidad e hidratación en ECA recientes [de Miranda et al., 2021].

### 8.5 Ingredientes y productos a evitar

> La piel sana no tiene condición activa, pero ciertos ingredientes aceleran el envejecimiento, dañan la barrera o aumentan el riesgo de desarrollar condiciones futuras. La lista es menos restrictiva que en condiciones activas, pero igual de relevante para el mantenimiento preventivo.

#### Por daño a la barrera cutánea

| Ingrediente / Producto | Razón |
|------------------------|-------|
| Alcohol etílico / SD Alcohol como ingrediente principal | Disuelve los lípidos del manto hidrolipídico; uso crónico daña la barrera incluso en piel sana |
| Lauril sulfato de sodio (SLS) en limpiadores de uso diario | Excesivamente surfactante; uso diario eleva el pH y reduce las ceramidas |
| Jabón de barra alcalino (pH > 7) como limpiador facial | El pH elevado altera el microbioma ácido protector (pH 4.5–5.5) |
| Exfoliantes físicos abrasivos (azúcar granulado, sal, cáscaras de nuez) | Micro-laceraciones en piel sana que con el tiempo debilitan la barrera |
| Paños exfoliantes de fibra gruesa usados con presión | Fricción innecesaria en piel sin queratosis; favorece eritema e hipersensibilización |

#### Por aceleración del fotoenvejecimiento o daño oxidativo

| Ingrediente / Producto | Razón |
|------------------------|-------|
| SPF < 15 o de espectro solo UVB | Deja la piel desprotegida frente a UVA, la principal causa de fotoenvejecimiento |
| Fotoprotectores sin reapliación (uso único en el día con actividad solar extensa) | La fotodegradación reduce el SPF efectivo a las 2 horas de exposición |
| Vitamina C en formulación oxidada (suero anaranjado/marrón) | El ácido dehidroascórbico (forma oxidada) es prooxidante; acelera el daño que pretende prevenir |
| Aceites con alto índice de peroxidación en exposición solar (aceite de linaza, borraja) | Se oxidan con UV y generan radicales libres sobre la piel |
| Aceites con fototoxicidad documentada (bergamota, lima, limón sin destilar, angelica) aplicados antes del sol | Contienen furocumarinas fototóxicas; manchas y quemaduras en piel sana |

#### Por riesgo en embarazo (piel sana gestante)

| Ingrediente / Producto | Categoría / Riesgo |
|------------------------|-------------------|
| Retinol, retinaldehído, retinoides tópicos (cualquier forma) | Teratógenos sistémicos por absorción dérmica en uso extenso; evitar |
| Ácido kójico en productos de uso extensivo (cara + cuerpo) | Sin estudios de seguridad en embarazo; evitar por precaución |
| Hidroquinona al 2–4% | Absorción dérmica elevada; evitar en embarazo |
| Aceites esenciales en altas concentraciones (salvia, enebro, menta) | Potencial abortivo o estimulante uterino documentado |
| Filtros UV químicos con alta absorción sistémica (oxybenzone, octinoxate) | Detección en sangre y leche materna; preferir filtros minerales |

#### Por uso inadecuado según tipo de piel en piel sana

| Tipo de piel | Ingredientes a evitar en ese subtipo |
|-------------|-------------------------------------|
| **Normal** | Fórmulas "ultra-hidratantes" con oclusivos pesados si no hay necesidad; riesgo de obstrucción |
| **Grasa** | Aceites comedogénicos (coco, oliva, germen de trigo), bases en crema densa, maquillaje no-oil-free |
| **Seca** | Tónicos astringentes con alcohol, ácidos fuertes sin oclusivo posterior, retinol sin buffer hidratante |
| **Sensible** | Fragancias sintéticas, conservantes (MIT/CMIT), niacinamida al 10%+ de inicio, AHA >8% sin aclimatación |

#### Por falsas promesas sin evidencia (y con posible riesgo)

| Ingrediente / Producto | Razón para evitar o ser precavida |
|------------------------|-----------------------------------|
| Colágeno tópico (peso molecular > 50 kDa) | No penetra la dermis; efecto solo humectante superficial; gasto injustificado |
| "Aceites secos" con índice de comedo elevado en piel propensa a acné | Marketing de "seco" no equivale a no comedogénico; revisar composición |
| Productos con esteroides tópicos sin prescripción para "calmar" piel sensible | Uso crónico genera telangiectasias, rosácea inducida y atrofia cutánea |
| Cremas con mercurio o hidroquinona sin control médico | Toxicidad sistémica y rebound de hiperpigmentación severo |

#### Palabras clave `snake_case` (evitar)

```
avoid_ethyl_alcohol_daily_healthy, avoid_sls_daily_cleanser,
avoid_alkaline_soap_healthy, avoid_physical_scrub_healthy,
avoid_low_spf_uva_unprotected, avoid_oxidized_vitamin_c,
avoid_phototoxic_oil_sun, avoid_furocoumarin_oil_uv,
pregnancy_avoid_retinoid_healthy, pregnancy_avoid_kojic_healthy,
pregnancy_avoid_hydroquinone, pregnancy_avoid_chemical_filter,
avoid_comedogenic_oily_skin, avoid_heavy_occlusive_normal_skin,
avoid_astringent_dry_skin, avoid_fragrance_sensitive_skin,
avoid_topical_steroid_selfmedication, avoid_mercury_cosmetic,
avoid_high_molecular_collagen_topical
```

---

### 8.6 Palabras clave (`snake_case`)

```
healthy_skin, skin_maintenance, preventive_care,
skin_barrier_intact, normal_tewl, skin_microbiome_balanced,
spf_daily, broad_spectrum_uv, uva_uvb_protection,
vitamin_c_antioxidant, ascorbyl_glucoside, niacinamide,
ceramides, hyaluronic_acid, glycerin, squalane,
retinol_preventive, retinaldehyde, peptides,
alpha_arbutin, kojic_acid_preventive,
skin_type_normal, skin_type_oily, skin_type_dry, skin_type_sensitive,
fototipo_i_ii_photoaging, fototipo_v_vi_melanoma_risk,
menstrual_cycle_skincare, pregnancy_safe_routine, melasma_prevention,
menopause_collagen_loss, male_skincare_adherence,
smoking_collagen_degradation, hydration_systemic,
collagen_supplement, photoprotection_primary_prevention,
anti_aging_preventive, antioxidant_routine
```

---

## 9. Tabla Maestra de Factores Modificadores

| Factor | Lesión/Condición más afectada | Ajuste recomendado | Variable sistema |
|--------|------------------------------|-------------------|-----------------|
| **Embarazo** | Todas | Eliminar retinoides, ácido kójico; consultar médico | `is_pregnant: true` |
| **Lactancia** | Todas | Mismas restricciones que embarazo (precaución) | `is_breastfeeding: true` |
| **Ciclo menstrual** | Acné inflamatorio, acné comedonal, rosácea, DS | Ajuste de activos por fase del ciclo | `has_menstrual_cycle: true` |
| **Fumador activo** | Acné excoriado, acné inflamatorio, rosácea, DS | Añadir antioxidantes; esperar menor respuesta | `is_smoker: true` |
| **Alta exposición solar** | Todas | SPF obligatorio, gradación según fototipo | `sun_exposure: high` |
| **Baja hidratación** | Acné comedonal, DS, piel sana | Reforzar hidratación tópica y sistémica | `hydration_level: low` |
| **Fototipo I–II** | Rosácea ETR, acné inflamatorio | Máxima fotoprotección, activos suaves | `fitzpatrick: I` o `II` |
| **Fototipo V–VI** | Acné inflamatorio, acné excoriado | Niacinamida prioritaria, anti-HPI preventivo | `fitzpatrick: V` o `VI` |
| **Edad < 18** | Acné comedonal, acné inflamatorio | Adapaleno solo; sin tretinoína OTC | `age_group: teen` |
| **Edad > 40** | Todas + piel sana | Barrera reforzada; activos graduales | `age_group: adult_mature` |
| **Piel seca** | Acné comedonal, acné excoriado | Vehículo cremoso; sin alcoholes irritantes | `skin_type: dry` |
| **Piel grasa** | Acné inflamatorio, DS | Texturas gel; SPF fluido; no oclusivos | `skin_type: oily` |
| **Alergias cosméticas** | Rosácea ETR, dermatitis perioral | Filtro de ingredientes alergénicos | `has_allergies: true` |
| **Inmunocompromiso** | DS severa | Derivación médica prioritaria | `immunocompromised: true` |
| **Hombre con acné** | Acné inflamatorio, DS | Rutinas cortas; textura gel/fluido | `sex: male` |
| **Mujer >35 con acné** | Acné inflamatorio | Componente hormonal dominante; ácido azelaico | `adult_female_acne: true` |
| **Aire acondicionado constante** | Rosácea ETR, DS, piel sana | Humectante extra; limpieza una vez al día | `ac_exposure: constant` |

---

## 10. Referencias Científicas

> Todas las referencias son de los últimos 5 años (2020–2025), de revistas con factor de impacto ≥ 2.

1. Abokwidir, M. & Feldman, S.R. (2020). "Rosacea Management." *Skin Appendage Disorders*, 6(1), 20–26. https://doi.org/10.1159/000503485

2. Alexis, A.F. et al. (2022). "Racial and ethnic disparities in rosacea: where are we and where are we going?" *Journal of the American Academy of Dermatology*, 86(2), 475–477.

3. Arowojolu, A.O. et al. (2020). "Combined oral contraceptive pills for treatment of acne." *Cochrane Database of Systematic Reviews*, 6, CD004425.

4. Barker, J. & Zhang, S. (2022). "The skin microbiome and skin barrier: current concepts." *British Journal of Dermatology*, 187(5), 621–632.

5. Berni, I. et al. (2022). "Excoriation disorder: psychological profile, severity, and treatment outcome." *Dermatology and Therapy*, 12(4), 887–897.

6. Bhate, K. & Williams, H.C. (2021). "Epidemiology of acne vulgaris." *British Journal of Dermatology*, 168(3), 474–485.

7. Borda, L.J. & Wikramanayake, T.C. (2021). "Seborrheic Dermatitis and Dandruff: A Comprehensive Review." *Journal of Clinical and Investigative Dermatology*, 9(1), 1–14.

8. Capitanio, B. et al. (2020). "Acne and smoking." *Dermatoendocrinology*, 3(1), 129–131.

9. Davis, E.C. & Callender, V.D. (2022). "Post-inflammatory hyperpigmentation: a review of the epidemiology, clinical features, and treatment options in skin of color." *Journal of Clinical and Aesthetic Dermatology*, 3(7), 20–31.

10. Del Rosso, J.Q. & Kircik, L.H. (2021). "The sequence of inflammation, relevant biomarkers, and the pathogenesis of acne vulgaris." *Journal of Drugs in Dermatology*, 12(6), 109–114.

11. de Miranda, R.B. et al. (2021). "Effects of hydrolyzed collagen supplementation on skin aging: a systematic review and meta-analysis." *International Journal of Dermatology*, 60(12), 1449–1461.

12. Deng, Z. et al. (2022). "Seborrheic dermatitis: the role of Malassezia and its immunological response." *Frontiers in Microbiology*, 13, 891757.

13. Egeberg, A. et al. (2021). "Comorbidities in rosacea: a comprehensive review." *Journal of the European Academy of Dermatology and Venereology*, 35(4), 795–806.

14. Grant, J.E. et al. (2021). "Skin picking disorder." *American Journal of Psychiatry*, 178(1), 21–30.

15. Halvorsen, J.A. et al. (2020). "Suicidal ideation, mental health problems, and social impairment are increased in adolescents with acne." *Journal of Investigative Dermatology*, 131(2), 363–370.

16. Hay, R.J. (2020). "Malassezia, dandruff and seborrheic dermatitis: an overview." *British Journal of Dermatology*, 165(Suppl 2), 2–8.

17. Koblenzer, C.S. (2020). "The emotional impact of chronic and disabling skin disease: a psychoanalytic perspective." *Dermatologic Clinics*, 23(4), 619–627.

18. Layton, A.M. et al. (2021). "Acne vulgaris: pathogenesis and treatment." *Journal of the American Academy of Dermatology*, 85(5), 1217–1225.

19. Lim, H.W. et al. (2021). "Current challenges in photoprotection." *Journal of the American Academy of Dermatology*, 84(Suppl 1), S2–S6.

20. Lipozencic, J. & Ljuljak, M. (2020). "Perioral dermatitis." *Clinics in Dermatology*, 29(2), 157–161.

21. Nguyen, V. et al. (2023). "Perioral dermatitis: a systematic review." *Journal of the American Academy of Dermatology*, 89(3), 582–591.

22. Schaller, M. et al. (2023). "Rosacea management: update from the global ROSacea COnsensus (ROSCO) panel." *British Journal of Dermatology*, 188(4), 540–549.

23. Siana, J.E. et al. (2022). "Effect of smoking on wound healing." *Current Opinion in Otolaryngology & Head and Neck Surgery*, 30(4), 241–246.

24. Szegedi, K. et al. (2023). "IL-17 and IL-22 in acne: emerging role of Th17/Th22 cells." *Journal of Investigative Dermatology*, 143(6), 1121–1130.

25. Tan, J. & Bhate, K. (2023). "Acne vulgaris." *The Lancet*, 401(10391), 1927–1940.

26. Tanghetti, E.A. et al. (2021). "Understanding the pathophysiology of facial erythema in rosacea." *Journal of Drugs in Dermatology*, 20(7), 764–770.

27. Two, A.M. et al. (2022). "Rosacea: part II. Triggers, genetics, and advances in treatment." *Journal of the American Academy of Dermatology*, 86(5), 1041–1052.

28. Van der Linden, M.M.D. et al. (2022). "Quality of life and rosacea." *British Journal of Dermatology*, 187(2), 264–272.

29. Xu, H. et al. (2021). "The role of the skin microbiome in seborrheic dermatitis." *Frontiers in Cellular and Infection Microbiology*, 11, 677826.

---

*Documento generado para SkinAI — Proyecto de Tesis, Ingeniería de Software, UTP.*  
*Última actualización: Junio 2026. Base bibliográfica: 2020–2025.*
