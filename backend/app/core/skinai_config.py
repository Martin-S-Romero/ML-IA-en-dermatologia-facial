"""
skinai_config.py  —  SkinAI
============================
Única fuente de verdad para todas las constantes del sistema.

Cualquier valor numérico que controle comportamiento vive aquí.
Los archivos face_censor_v3.py y skinai_analizar_v3.py importan
desde aquí — nunca definen sus propios literales configurables.

Referencias de los pesos de severidad:
  - Eritema 0.50 / Comedones 0.30 / Escamas 0.20:
    Dreno et al. 2022, JEADV — erythema = signo inflamatorio primario.
  - Umbral confianza 0.10: Guo et al. 2017, ICML — softmax calibration.
  - Umbrales IGA eritema: Zaenglein et al. 2022, JAAD.
"""

# =============================================================================
# SEVERITY SCORE
# =============================================================================

ERYTHEMA_W  = 0.50
COMEDONES_W = 0.30
SCALES_W    = 0.20

# =============================================================================
# UMBRALES CLÍNICOS DE ERITEMA  (IGA scale, Zaenglein 2022)
# =============================================================================

ERYTHEMA_THRESHOLD_MILD     = 0.08   # eritema leve
ERYTHEMA_THRESHOLD_MODERATE = 0.15   # eritema moderado/alto

# Umbrales de eritema por contexto clínico
ERYTHEMA_MIN_ZONA_T      = 0.06   # mínimo en frente/nariz para co-activar seborrheic
ERYTHEMA_MIN_PERIORAL    = 0.12   # en mentón para activar perioral-dermatitis
ERYTHEMA_MIN_EXCORIATED  = 0.12   # difuso en mejillas para activar acne-excoriated
ERYTHEMA_MIN_HEALTHY     = 0.06   # por debajo del cual se considera piel sana
ERYTHEMA_MIN_SYMMETRY    = 0.6    # simetría bilateral mínima para activar rosacea-etr

# =============================================================================
# UMBRALES DE COMEDONES
# =============================================================================

COMEDONES_ZONA_T   = 0.15   # en frente/nariz para activar acne-comedonal
COMEDONES_MEJILLAS = 0.10   # en mejillas para co-activar acne-inflammatory

# =============================================================================
# UMBRALES DE ESCAMAS
# =============================================================================

SCALES_ZONA_T         = 0.10   # en zona T para activar seborrheic boost base
SCALES_CEJAS          = 0.10   # en cejas para activar seborrheic boost cejas
SCALES_ZONA_T_PENALTY = 0.20   # en zona T para activar penalización de rosácea
SCALES_CEJAS_PENALTY  = 0.15   # en cejas para activar penalización de rosácea

# =============================================================================
# UMBRALES COMBINADOS
# =============================================================================

ERITEMA_COMEDONES_MEJILLAS = 0.10   # umbral compartido eritema+comedones en mejillas

# =============================================================================
# FACTORES DE BOOST ZONAL  (ajustar_por_zona)
# =============================================================================

BOOST_ROSACEA_ETR_BILATERAL    = 1.4
BOOST_ROSACEA_INFL_BILATERAL   = 1.2
BOOST_ACNE_COMEDONAL_ZONA_T    = 1.3
BOOST_ACNE_INFL_MEJILLAS       = 1.3
BOOST_SEBORRHEIC_ZONA_T_BASE   = 1.3   # base de la fórmula proporcional
BOOST_SEBORRHEIC_ZONA_T_SCALE  = 0.7   # escala de la fórmula proporcional
BOOST_SEBORRHEIC_CEJAS_BASE    = 1.2   # base de la fórmula de cejas
BOOST_SEBORRHEIC_CEJAS_SCALE   = 0.5   # escala de la fórmula de cejas
PENALTY_ROSACEA_SCALE          = 0.3   # factor de la fórmula de penalización
PENALTY_ROSACEA_MAX            = 0.40  # cap máximo de penalización
BOOST_PERIORAL                 = 1.5
BOOST_ACNE_EXCORIATED_ZONA     = 1.2
BOOST_HEALTHY_SKIN             = 1.5

# =============================================================================
# FACTORES DE BOOST DE PERFIL  (ajustar_por_perfil)
# =============================================================================

# Historial
BOOST_PERFIL_ROSACEA_ETR       = 1.6
BOOST_PERFIL_ROSACEA_INFL      = 1.4
BOOST_PERFIL_ACNE_INFL         = 1.4
BOOST_PERFIL_ACNE_COMEDONAL    = 1.3
BOOST_PERFIL_ACNE_EXCORIADO    = 1.2
BOOST_PERFIL_DERMATITIS        = 1.5

# Tipo de piel
BOOST_PIEL_SENSIBLE_ROSACEA    = 1.2
BOOST_PIEL_SENSIBLE_SEBORRHEIC = 1.1
BOOST_PIEL_GRASA_COMEDONAL     = 1.3
BOOST_PIEL_GRASA_INFL          = 1.2
BOOST_PIEL_SECA_SEBORRHEIC     = 1.2

# Fototipo
BOOST_FOTOTIPO_BAJO_ROSACEA    = 1.3
BOOST_FOTOTIPO_BAJO_ROSACEA_INFL = 1.1
BOOST_FOTOTIPO_ALTO_ROSACEA    = 0.7   # penalización: menor prevalencia

# Edad
EDAD_UMBRAL_JOVEN              = 25    # edad < 25 → boost acné
EDAD_UMBRAL_ADULTO             = 30    # edad >= 30 → boost rosácea
EDAD_DEFAULT                   = 25
BOOST_EDAD_JOVEN_INFL          = 1.2
BOOST_EDAD_JOVEN_COMEDONAL     = 1.1
BOOST_EDAD_ADULTO_ROSACEA      = 1.2
BOOST_EDAD_ADULTO_ROSACEA_INFL = 1.1

# Exposición a AC/calefacción
BOOST_AC_SEBORRHEIC            = 1.15

# Sexo
BOOST_FEMENINO_EXCORIATED      = 1.2

# =============================================================================
# MEDIAPIPE  (FaceMesh)
# =============================================================================

FACEMESH_MAX_FACES             = 1
FACEMESH_DETECTION_CONFIDENCE  = 0.5
FACEMESH_TRACKING_CONFIDENCE   = 0.5

# Índices de landmarks de ojos para censura
LANDMARK_LEFT_EYE              = [33, 133]
LANDMARK_RIGHT_EYE             = [362, 263]

# =============================================================================
# RESOLUCIÓN DE IMAGEN
# =============================================================================

MIN_IMG_WIDTH   = 430
MIN_IMG_HEIGHT  = 360

# =============================================================================
# PARÁMETROS DE CENSURA (FaceCensor defaults)
# =============================================================================

DEFAULT_BLUR_STRENGTH  = 55
DEFAULT_EXPAND_PX      = 10
DEFAULT_PIXEL_SIZE     = 10
BLUR_SIGMA             = 30

# =============================================================================
# MÉTRICAS VISUALES  (cálculo de señales)
# =============================================================================

ADAPTIVE_BLOCK_SIZE         = 31    # ventana del umbral adaptativo de comedones
ADAPTIVE_C                  = 10    # offset del umbral adaptativo
COMEDONES_AMPLIFIER         = 3.0   # amplifica dark_ratio → rango útil [0,1]
SCALES_NORMALIZATION_FACTOR = 300.0 # satura la varianza del Laplaciano en escamas severas

# =============================================================================
# MODELO DE IA  (EfficientNetB3)
# =============================================================================

IMG_SIZE             = 300
IMAGENET_MEAN        = [0.485, 0.456, 0.406]
IMAGENET_STD         = [0.229, 0.224, 0.225]
MODEL_HIDDEN_SIZE    = 256
MODEL_DROPOUT_1      = 0.3
MODEL_DROPOUT_2      = 0.2

# =============================================================================
# TEST-TIME AUGMENTATION  (TTA)
# =============================================================================

TTA_SEED_MULTIPLIER  = 13     # produce seeds reproducibles: 0,13,26,39,52
TTA_ROTATION_DEGREES = 10
TTA_CROP_SCALE_MIN   = 0.93
TTA_BRIGHTNESS_JITTER = 0.10
TTA_FLIP_PROB        = 0.5

# =============================================================================
# INFERENCIA Y SALIDA
# =============================================================================

CONFIDENCE_THRESHOLD     = 0.10   # mínima probabilidad para incluir en top-N
SEVERITY_TREND_THRESHOLD = 0.05   # ±0.05 para clasificar improving/stable/worsening
CONSOLE_BAR_WIDTH        = 30     # ancho en caracteres de las barras de probabilidad
CONSOLE_LINE_WIDTH       = 60     # ancho de los separadores de línea en consola

# =============================================================================
# ZONAS FACIALES
# =============================================================================

ZONAS_DISPLAY    = {'frente', 'mejilla_izq', 'mejilla_der', 'nariz', 'menton'}
ZONAS_DIAGNOSTIC = {
    'ceja_izq', 'ceja_der',
    'nariz_lat_izq', 'nariz_lat_der',
    'mandibula_izq', 'mandibula_der',
    'zona_perioral',
}

ZONA_WEIGHTS = {
    'frente':        0.20,
    'mejilla_izq':   0.16,
    'mejilla_der':   0.16,
    'nariz':         0.11,
    'menton':        0.09,
    'ceja_izq':      0.06,
    'ceja_der':      0.06,
    'nariz_lat_izq': 0.03,
    'nariz_lat_der': 0.03,
    'mandibula_izq': 0.03,
    'mandibula_der': 0.03,
    'zona_perioral': 0.04,
}

# =============================================================================
# VERSIONADO
# =============================================================================

ZONE_SCHEMA_VERSION = 'v3'   # v2=5 zonas, v3=9 zonas

# =============================================================================
# FÓRMULAS PROPORCIONALES  (caps de intensidad)
# =============================================================================

CAP_INTENSIDAD           = 1.0   # cap máximo de intensidad en fórmulas proporcionales
                                  # min(señal, CAP_INTENSIDAD) evita que valores > 1.0
                                  # rompan la escala de los boosts calculados

# =============================================================================
# ARQUITECTURA DEL MODELO
# =============================================================================

MODEL_ARCH               = 'efficientnet_b3'   # arquitectura timm del modelo

# =============================================================================
# DEFAULTS DEL PERFIL (interfaz de consola)
# =============================================================================

PERFIL_DEFAULT_EDAD      = 25          # usado también como EDAD_DEFAULT en ajustar_por_perfil
PERFIL_DEFAULT_SEXO      = 'Femenino'
PERFIL_DEFAULT_FOTOTIPO  = 'III'
PERFIL_DEFAULT_TIPO_PIEL = 'Mixta'
PERFIL_DEFAULT_EXPOSICION = 'A veces'

# =============================================================================
# TTA — límite superior del recorte aleatorio
# =============================================================================

TTA_CROP_SCALE_MAX       = 1.0   # escala máxima del RandomResizedCrop

# Umbrales para zonas nuevas (mandíbula y zona perioral)
ERYTHEMA_MIN_MANDIBULA   = 0.10   # eritema en mandíbula para activar acne-inflammatory
COMEDONES_MANDIBULA      = 0.12   # comedones en mandíbula para co-activar acne-inflammatory
ERYTHEMA_PERIORAL_DIRECT = 0.10   # eritema en zona_perioral para activar perioral-dermatitis
ERYTHEMA_PERIORAL_MAX_MEJILLAS = 0.08  # mejillas deben estar bajo este valor para confirmar perioral

# Boosts para las nuevas zonas
BOOST_ACNE_INFL_MANDIBULA  = 1.3   # eritema + comedones en mandíbula → acne-inflammatory
BOOST_PERIORAL_DIRECT      = 1.6   # eritema en zona perioral directa (más específico que mentón)
# =============================================================================
# CONTINUIDAD DIAGNÓSTICA  (análisis secuenciales)
# =============================================================================

# Boost de continuidad: la condición diagnosticada en el análisis anterior
# tiene mayor probabilidad de persistir (condiciones crónicas).
# Factor proporcional a la confianza previa: boost = 1 + conf_previa * BASE
# Con conf=0.90 → boost ×1.45 | conf=0.56 → boost ×1.28 | conf=0.25 → boost ×1.125
BOOST_CONTINUIDAD_BASE       = 0.5

# Umbral mínimo de confianza previa para aplicar el boost de continuidad.
# Por debajo de este valor el análisis anterior se considera poco confiable
# y no influye en el siguiente.
BOOST_CONTINUIDAD_MIN_CONF   = 0.20

# Penalización aplicada a condiciones cuyo cambio desde el análisis anterior
# es clínicamente inverosímil en el corto plazo.
PENALTY_TRANSICION_IMPROBABLE = 0.75

# Mapa de transiciones clínicamente improbables entre análisis consecutivos.
# Clave: condición diagnosticada en análisis anterior.
# Valor: lista de condiciones que requieren evidencia extra para sustituirla.
# Justificación: condiciones crónicas no desaparecen ni se intercambian
# entre sesiones próximas. Un cambio brusco indica oscilación del modelo,
# no evolución real de la piel.
TRANSICIONES_IMPROBABLES = {
    'seborrheic-dermatitis': ['rosacea-etr', 'rosacea-inflammatory', 'healthy-skin'],
    'rosacea-etr':           ['seborrheic-dermatitis', 'acne-comedonal', 'healthy-skin'],
    'rosacea-inflammatory':  ['seborrheic-dermatitis', 'healthy-skin'],
    'acne-inflammatory':     ['healthy-skin', 'rosacea-etr'],
    'acne-comedonal':        ['healthy-skin', 'rosacea-etr'],
    'perioral-dermatitis':   ['healthy-skin', 'rosacea-etr'],
}

# Umbral de confianza bajo el cual se emite diagnostic_note cuando
# la condición cambia respecto al análisis anterior.
# 2 × CONFIDENCE_THRESHOLD = 0.20 por defecto.
DIAGNOSTIC_NOTE_LOW_CONF_FACTOR = 2
