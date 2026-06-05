"""
skinai_analizar_v3.py  —  SkinAI
==================================
Analizador de imagen v3 — pipeline completo.

Flujo:
  1. Censurar ojos y extraer métricas zonales  (face_censor_v3.FaceCensor)
  2. Cargar modelo EfficientNetB3 (lazy, una sola vez por proceso)
  3. Predecir condición con TTA×5
  4. Ajustar probabilidades por perfil clínico  (ajustar_por_perfil)
  5. Ajustar probabilidades por métricas zonales (face_censor_v3.ajustar_por_zona)
  6. Aplicar umbral de confianza ≥10%
  7. Construir resultado JSON completo
  8. Calcular delta respecto al análisis anterior (si existe)

USO:
    python skinai_analizar_v3.py                   ← interactivo
    python skinai_analizar_v3.py imagen.jpg        ← directo
    python skinai_analizar_v3.py imagen.jpg --sin-perfil

SALIDA:
    - imagen_censurada.jpg       (ojos difuminados)
    - Consola: diagnóstico + métricas zonales
    - result_<timestamp>.json    (para integración con BD)

REFERENCIAS:
    - Eritema 0.50 / Comedones 0.30 / Escamas 0.20:
      Dreno et al. 2022, JEADV.
    - Umbral confianza 0.10: Guo et al. 2017, ICML — softmax calibration.
    - Multiplicadores de perfil: ver docstring de ajustar_por_perfil().
"""

import sys
import json
import argparse
import numpy as np
import torch
import torch.nn as nn
from pathlib import Path
from datetime import datetime
from torchvision import transforms
from PIL import Image as PILImage

from face_censor_v3 import FaceCensor, ajustar_por_zona
from skinai_config import (
    # inferencia
    CONFIDENCE_THRESHOLD, SEVERITY_TREND_THRESHOLD,
    # modelo
    IMG_SIZE, IMAGENET_MEAN, IMAGENET_STD,
    MODEL_HIDDEN_SIZE, MODEL_DROPOUT_1, MODEL_DROPOUT_2,
    # TTA
    TTA_SEED_MULTIPLIER, TTA_ROTATION_DEGREES, TTA_CROP_SCALE_MIN,
    TTA_BRIGHTNESS_JITTER, TTA_FLIP_PROB,
    # boosts de perfil
    BOOST_PERFIL_ROSACEA_ETR, BOOST_PERFIL_ROSACEA_INFL,
    BOOST_PERFIL_ACNE_INFL, BOOST_PERFIL_ACNE_COMEDONAL, BOOST_PERFIL_ACNE_EXCORIADO,
    BOOST_PERFIL_DERMATITIS,
    BOOST_PIEL_SENSIBLE_ROSACEA, BOOST_PIEL_SENSIBLE_SEBORRHEIC,
    BOOST_PIEL_GRASA_COMEDONAL, BOOST_PIEL_GRASA_INFL, BOOST_PIEL_SECA_SEBORRHEIC,
    BOOST_FOTOTIPO_BAJO_ROSACEA, BOOST_FOTOTIPO_BAJO_ROSACEA_INFL, BOOST_FOTOTIPO_ALTO_ROSACEA,
    EDAD_UMBRAL_JOVEN, EDAD_UMBRAL_ADULTO, EDAD_DEFAULT,
    BOOST_EDAD_JOVEN_INFL, BOOST_EDAD_JOVEN_COMEDONAL,
    BOOST_EDAD_ADULTO_ROSACEA, BOOST_EDAD_ADULTO_ROSACEA_INFL,
    BOOST_AC_SEBORRHEIC, BOOST_FEMENINO_EXCORIATED,
    # salida
    CONSOLE_BAR_WIDTH, CONSOLE_LINE_WIDTH,
    # modelo y TTA
    MODEL_ARCH, TTA_CROP_SCALE_MAX,
    # defaults del perfil
    PERFIL_DEFAULT_EDAD, PERFIL_DEFAULT_SEXO,
    PERFIL_DEFAULT_FOTOTIPO, PERFIL_DEFAULT_TIPO_PIEL, PERFIL_DEFAULT_EXPOSICION,
    # zonas
    ZONAS_DISPLAY, ZONE_SCHEMA_VERSION,
    # continuidad diagnóstica
    BOOST_CONTINUIDAD_BASE, BOOST_CONTINUIDAD_MIN_CONF,
    PENALTY_TRANSICION_IMPROBABLE, TRANSICIONES_IMPROBABLES,
    DIAGNOSTIC_NOTE_LOW_CONF_FACTOR,
)

# ── Rutas de artefactos del modelo ────────────────────────────────────────────
BASE_DIR      = Path(__file__).parent
MODEL_PATH    = BASE_DIR / 'SkinAI_opcionA-v3.pth'
LABELS_PATH   = BASE_DIR / 'labels_opcionA-v3.json'

# ── Parámetros de inferencia ──────────────────────────────────────────────────
# IMG_SIZE, IMAGENET_MEAN, IMAGENET_STD se importan de skinai_config.
DEVICE        = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# ── Cache del modelo (se carga una sola vez por proceso) ──────────────────────
_modelo_cache : torch.nn.Module | None = None
_clases_cache : list[str] | None       = None

# ── Datos clínicos por condición ──────────────────────────────────────────────

DESCRIPCIONES = {
    'acne-comedonal':        'Acné comedonal — puntos negros/blancos, zona T',
    'acne-excoriated':       'Acné excoriado — marcas de rascado, mejillas/mentón',
    'acne-inflammatory':     'Acné inflamatorio — pústulas/nódulos, cara',
    'perioral-dermatitis':   'Dermatitis perioral — zona alrededor de la boca',
    'rosacea-etr':           'Rosácea eritematotelangiectásica — mejillas simétricas',
    'rosacea-inflammatory':  'Rosácea inflamatoria — centro facial',
    'seborrheic-dermatitis': 'Dermatitis seborreica — cejas, nariz, zona T',
    'healthy-skin':          'Piel sin lesiones detectables',
}

MENSAJES_ALERTA = {
    'acne-excoriated': (
        'Este patrón puede beneficiarse de apoyo profesional para el manejo '
        'del hábito de rascado. Consulta a tu médico.'
    ),
    'perioral-dermatitis': (
        'La dermatitis perioral puede agravarse con corticosteroides tópicos. '
        'Consulta a un dermatólogo antes de aplicar cualquier tratamiento.'
    ),
    'rosacea-inflammatory': (
        'La rosácea inflamatoria requiere evaluación médica. Evita desencadenantes '
        'como calor, alcohol y productos con fragancia.'
    ),
    'seborrheic-dermatitis': (
        'La dermatitis seborreica crónica o severa puede confundirse con psoriasis. '
        'Consulta a un dermatólogo si los síntomas persisten o se extienden.'
    ),
}

# Ingredientes recomendados por condición detectada
# Ref: Zaenglein 2022 (acné), Alexis 2020 (rosácea), Borda 2015 (derm. seb.)
INGREDIENTES_OBJETIVO = {
    'acne-comedonal':        ['Salicylic Acid', 'Niacinamide', 'Zinc PCA', 'Adapalene'],
    'acne-excoriated':       ['Centella Asiatica', 'Panthenol', 'Azelaic Acid'],
    'acne-inflammatory':     ['Benzoyl Peroxide', 'Azelaic Acid', 'Niacinamide'],
    'perioral-dermatitis':   ['Zinc Oxide', 'Niacinamide'],
    'rosacea-etr':           ['Azelaic Acid', 'Niacinamide', 'Zinc Oxide', 'Titanium Dioxide'],
    'rosacea-inflammatory':  ['Azelaic Acid', 'Centella Asiatica'],
    'seborrheic-dermatitis': ['Zinc Pyrithione', 'Piroctone Olamine', 'Selenium Sulfide'],
    'healthy-skin':          ['Tocopherol', 'Glycerin', 'Zinc Oxide'],
}

# Ingredientes a evitar por condición detectada
INGREDIENTES_EVITAR = {
    'acne-comedonal':        ['fragrance', 'coconut oil', 'isopropyl myristate'],
    'acne-excoriated':       ['fragrance', 'alcohol denat', 'glycolic acid'],
    'acne-inflammatory':     ['fragrance', 'coconut oil'],
    'perioral-dermatitis':   ['hydrocortisone', 'betamethasone', 'fragrance'],
    'rosacea-etr':           ['alcohol denat', 'linalool', 'fragrance', 'glycolic acid'],
    'rosacea-inflammatory':  ['alcohol denat', 'fragrance', 'glycolic acid'],
    'seborrheic-dermatitis': ['coconut oil', 'olive oil', 'fragrance'],
    'healthy-skin':          [],
}


# =============================================================================
# PASO 1 — CENSURA Y ANÁLISIS ZONAL
# =============================================================================

def censurar_y_analizar(ruta_imagen: str) -> tuple[str, dict | None]:
    """
    Censura los ojos con FaceCensor y extrae métricas zonales.

    Retorna (ruta_censurada, analisis_zonal).
    Si la censura falla, retorna la imagen original y None
    para que el pipeline pueda continuar sin bloquear el análisis.
    """
    ruta_path   = Path(ruta_imagen)
    ruta_salida = str(
        ruta_path.parent / f'{ruta_path.stem}_censurada{ruta_path.suffix}'
    )
    censor    = FaceCensor(mode='blur')
    resultado = censor.process_image(ruta_imagen, ruta_salida)

    if resultado is None:
        print('  [!] Censura falló — usando imagen original')
        return ruta_imagen, None

    print(f'  Imagen censurada: {ruta_salida}')
    if censor.ultimo_analisis_zonal:
        censor.imprimir_analisis_zonal()
    else:
        print('  [!] No se detectó rostro para análisis zonal')

    return ruta_salida, censor.ultimo_analisis_zonal


# =============================================================================
# PASO 2 — CARGA DE MODELO (lazy, una sola vez por proceso)
# =============================================================================

def _cargar_modelo_desde_disco() -> tuple[torch.nn.Module, list[str]]:
    """
    Instancia EfficientNetB3, carga los pesos entrenados y el archivo de labels.
    No se llama directamente: usar get_modelo() para aprovechar el cache.
    """
    try:
        import timm
    except ImportError:
        print('[ERROR] timm no instalado: pip install timm')
        sys.exit(1)

    for ruta, nombre in [(MODEL_PATH, 'Modelo'), (LABELS_PATH, 'Labels')]:
        if not ruta.exists():
            print(f'[ERROR] {nombre} no encontrado: {ruta}')
            sys.exit(1)

    with open(LABELS_PATH, 'r') as f:
        labels_dict = json.load(f)
    clases_lista = [k for k, v in sorted(labels_dict.items(), key=lambda x: x[1])]
    n_clases     = len(clases_lista)

    modelo = timm.create_model(MODEL_ARCH, pretrained=False, num_classes=0)
    n_feat = modelo.num_features
    modelo.classifier = nn.Sequential(
        nn.BatchNorm1d(n_feat),
        nn.Dropout(p=MODEL_DROPOUT_1),
        nn.Linear(n_feat, MODEL_HIDDEN_SIZE),
        nn.ReLU(),
        nn.Dropout(p=MODEL_DROPOUT_2),
        nn.Linear(MODEL_HIDDEN_SIZE, n_clases),
    )
    modelo.load_state_dict(
        torch.load(str(MODEL_PATH), map_location=DEVICE, weights_only=True)
    )
    modelo = modelo.to(DEVICE)
    modelo.eval()
    print(f'  Modelo cargado: {n_clases} clases · {DEVICE}')
    return modelo, clases_lista


def get_modelo() -> tuple[torch.nn.Module, list[str]]:
    """
    Retorna el modelo y la lista de clases.
    Carga desde disco solo la primera vez; en llamadas sucesivas usa el cache.
    """
    global _modelo_cache, _clases_cache
    if _modelo_cache is None:
        _modelo_cache, _clases_cache = _cargar_modelo_desde_disco()
    return _modelo_cache, _clases_cache


# =============================================================================
# PASO 3 — PREDICCIÓN CON TTA×5
# =============================================================================

def predecir_con_tta(modelo: torch.nn.Module, ruta_imagen: str,
                     n_aug: int = 5) -> np.ndarray:
    """
    Promedia N+1 inferencias con variaciones leves (Test-Time Augmentation).

    Pasada 1: imagen original sin augmentation (reproducible).
    Pasadas 2…N+1: variaciones con seeds fijas (0, 13, 26, 39, 52),
    lo que garantiza resultados reproducibles entre ejecuciones.
    Para aleatoriedad verdadera, eliminar torch.manual_seed().
    """
    val_t = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])
    tta_t = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.RandomHorizontalFlip(p=TTA_FLIP_PROB),
        transforms.RandomRotation(degrees=TTA_ROTATION_DEGREES),
        transforms.RandomResizedCrop(IMG_SIZE, scale=(TTA_CROP_SCALE_MIN, TTA_CROP_SCALE_MAX)),
        transforms.ColorJitter(brightness=TTA_BRIGHTNESS_JITTER),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])

    img = PILImage.open(ruta_imagen).convert('RGB')

    with torch.no_grad():
        probs = torch.softmax(
            modelo(val_t(img).unsqueeze(0).to(DEVICE)), dim=1
        ).cpu().numpy()[0]

    for seed in range(n_aug):
        torch.manual_seed(seed * TTA_SEED_MULTIPLIER)
        with torch.no_grad():
            probs += torch.softmax(
                modelo(tta_t(img).unsqueeze(0).to(DEVICE)), dim=1
            ).cpu().numpy()[0]

    return probs / (n_aug + 1)


# =============================================================================
# PASO 4 — AJUSTE POR PERFIL CLÍNICO
# =============================================================================

def ajustar_por_perfil(probs_raw: np.ndarray, perfil: dict,
                       class_indices: dict,
                       result_anterior: dict | None = None) -> np.ndarray:
    """
    Aplica multiplicadores a las probabilidades según el perfil del usuario
    y, si existe, el resultado del análisis anterior (continuidad diagnóstica).

    Capas de ajuste:
    1. Perfil clínico declarado: historial, tipo de piel, fototipo, edad, AC, sexo.
    2. Continuidad diagnóstica: la condición previa actúa como prior bayesiano.
       - Boost de continuidad proporcional a la confianza del análisis anterior.
       - Penalización de transiciones clínicamente improbables entre sesiones.

    Los factores y sus referencias clínicas están junto a cada _boost()
    como única fuente de verdad.
    """
    probs = probs_raw.copy()

    def _boost(clase, factor):
        if clase in class_indices:
            probs[class_indices[clase]] *= factor

    edad       = perfil.get('edad', EDAD_DEFAULT)
    sexo       = perfil.get('sexo', '')
    fototipo   = perfil.get('fototipo', 'Desconocido')
    tipo_piel  = perfil.get('tipo_piel', '')
    historial  = perfil.get('historial', [])
    exposicion = perfil.get('exposicion_ac', 'No')

    if 'Rosácea'    in historial:
        _boost('rosacea-etr', BOOST_PERFIL_ROSACEA_ETR)
        _boost('rosacea-inflammatory', BOOST_PERFIL_ROSACEA_INFL)
    if 'Acné'       in historial:
        _boost('acne-inflammatory', BOOST_PERFIL_ACNE_INFL)
        _boost('acne-comedonal', BOOST_PERFIL_ACNE_COMEDONAL)
        _boost('acne-excoriated', BOOST_PERFIL_ACNE_EXCORIADO)
    if 'Dermatitis' in historial:
        _boost('seborrheic-dermatitis', BOOST_PERFIL_DERMATITIS)

    if tipo_piel == 'Sensible':
        _boost('rosacea-etr', BOOST_PIEL_SENSIBLE_ROSACEA)
        _boost('seborrheic-dermatitis', BOOST_PIEL_SENSIBLE_SEBORRHEIC)
    if tipo_piel == 'Grasa':
        _boost('acne-comedonal', BOOST_PIEL_GRASA_COMEDONAL)
        _boost('acne-inflammatory', BOOST_PIEL_GRASA_INFL)
    if tipo_piel == 'Seca':
        _boost('seborrheic-dermatitis', BOOST_PIEL_SECA_SEBORRHEIC)

    if fototipo in ['I', 'II']:
        _boost('rosacea-etr', BOOST_FOTOTIPO_BAJO_ROSACEA)
        _boost('rosacea-inflammatory', BOOST_FOTOTIPO_BAJO_ROSACEA_INFL)
    if fototipo in ['IV', 'V', 'VI']:
        _boost('rosacea-etr', BOOST_FOTOTIPO_ALTO_ROSACEA)

    if edad < EDAD_UMBRAL_JOVEN:
        _boost('acne-inflammatory', BOOST_EDAD_JOVEN_INFL)
        _boost('acne-comedonal', BOOST_EDAD_JOVEN_COMEDONAL)
    if edad >= EDAD_UMBRAL_ADULTO:
        _boost('rosacea-etr', BOOST_EDAD_ADULTO_ROSACEA)
        _boost('rosacea-inflammatory', BOOST_EDAD_ADULTO_ROSACEA_INFL)

    if exposicion == 'Sí, siempre':
        _boost('seborrheic-dermatitis', BOOST_AC_SEBORRHEIC)
    if sexo == 'Femenino':
        _boost('acne-excoriated', BOOST_FEMENINO_EXCORIATED)

    # ── Continuidad diagnóstica (si existe análisis anterior) ─────────────────
    if result_anterior:
        cond_previa  = result_anterior.get('condition')
        conf_previa  = result_anterior.get('confidence', 0.0)

        # Boost de continuidad: condición crónica previamente diagnosticada
        # tiene mayor probabilidad de persistir. Solo aplica si la confianza
        # previa supera el umbral mínimo de credibilidad.
        if cond_previa and conf_previa >= BOOST_CONTINUIDAD_MIN_CONF:
            factor_continuidad = round(1.0 + conf_previa * BOOST_CONTINUIDAD_BASE, 3)
            _boost(cond_previa, factor_continuidad)

        # Penalización de transiciones clínicamente improbables:
        # si la condición previa está en el mapa de incompatibilidades,
        # las condiciones listadas reciben una penalización para que
        # necesiten evidencia visual más fuerte antes de sustituir el diagnóstico previo.
        if cond_previa in TRANSICIONES_IMPROBABLES:
            for cond_incompatible in TRANSICIONES_IMPROBABLES[cond_previa]:
                _boost(cond_incompatible, PENALTY_TRANSICION_IMPROBABLE)

    total = probs.sum()
    return probs / total if total > 0 else probs


# =============================================================================
# PASO 5 — CONSTRUIR RESULTADO COMPLETO
# =============================================================================

def construir_resultado_completo(probs_array: np.ndarray,
                                 clases_lista: list[str],
                                 analisis_zonal: dict | None,
                                 perfil: dict | None = None,
                                 result_anterior: dict | None = None) -> dict:
    """
    Construye el dict completo que se guarda en analyses.result en la BD.

    Estructura del resultado
    ------------------------
    {
      condition, confidence, top_n,
      severity_score, worst_zone, affected_zones_count,
      zones_display:    {zona: {erythema, comedones, scales, severity}},
      zones_diagnostic: {zona: {erythema, comedones, scales, severity}},
      profile_consistency, historical_consistency,
      diagnostic_note (opcional, solo cuando cambia la condición con baja confianza),
      target_ingredients, avoid_ingredients,
      model, tta_passes, zone_schema_version, timestamp
    }

    Notas
    -----
    - zones_display: zonas principales que renderiza el dashboard.
    - zones_diagnostic: subzonas usadas internamente por ajustar_por_zona.
    - worst_zone: solo entre zonas de display (no subzonas).
    - profile_consistency: coherencia con historial declarado.
    - historical_consistency: coherencia con el análisis anterior (0.0 si es el primero).
    - diagnostic_note: advertencia cuando la condición cambia con confianza baja.

    References
    ----------
    Severity weights: Dreno et al. 2022, JEADV.
    Confidence threshold: Guo et al. 2017, ICML.
    """
    sorted_idx = np.argsort(probs_array)[::-1]
    top_n = [
        {'label': clases_lista[i], 'prob': round(float(probs_array[i]), 4)}
        for i in sorted_idx
        if probs_array[i] >= CONFIDENCE_THRESHOLD
    ]

    top1_label = top_n[0]['label'] if top_n else 'healthy-skin'
    top1_conf  = top_n[0]['prob']  if top_n else 0.0

    # Métricas zonales separadas en display y diagnostic.
    # severity por zona se lee de zone_severity — ya calculado por
    # face_censor._analizar_zonas() con los mismos pesos. No recalcular.
    zones_display    = {}
    zones_diagnostic = {}
    if analisis_zonal:
        zone_severity = analisis_zonal.get('zone_severity', {})
        for zona in analisis_zonal['eritema']:
            entry = {
                'erythema':  analisis_zonal['eritema'].get(zona,   0.0),
                'comedones': analisis_zonal['comedones'].get(zona, 0.0),
                'scales':    analisis_zonal['escamas'].get(zona,   0.0),
                'severity':  zone_severity.get(zona,               0.0),
            }
            if zona in ZONAS_DISPLAY:
                zones_display[zona] = entry
            else:
                zones_diagnostic[zona] = entry

    severity_score       = float(analisis_zonal['severity_score']) \
                           if analisis_zonal else 0.0
    worst_zone           = analisis_zonal['worst_zone']           \
                           if analisis_zonal else None
    affected_zones_count = analisis_zonal['affected_zones_count'] \
                           if analisis_zonal else 0

    # Consistencia con perfil declarado
    # Si no hay historial, usa confianza de top1 como proxy
    profile_consistency = 0.0
    if perfil:
        historial_mapping = {
            'Acné':       ['acne-comedonal', 'acne-inflammatory', 'acne-excoriated'],
            'Rosácea':    ['rosacea-etr', 'rosacea-inflammatory'],
            'Dermatitis': ['seborrheic-dermatitis', 'perioral-dermatitis'],
        }
        historial = perfil.get('historial', [])
        if historial:
            for condicion, clases in historial_mapping.items():
                if condicion in historial:
                    prob_sum = sum(p['prob'] for p in top_n if p['label'] in clases)
                    profile_consistency = round(max(profile_consistency, prob_sum), 4)
        else:
            # Sin historial: la confianza del top1 es el mejor proxy disponible
            profile_consistency = round(top1_conf, 4)

    # Consistencia con el análisis anterior (historical_consistency)
    # Mide qué tan probable es la condición actual dado el diagnóstico previo.
    # 1.0 = misma condición que antes · 0.0 = no hay análisis anterior.
    historical_consistency = 0.0
    diagnostic_note        = None
    if result_anterior:
        cond_previa = result_anterior.get('condition')
        conf_previa = result_anterior.get('confidence', 0.0)
        if cond_previa:
            # Probabilidad que el modelo asignó a la condición previa en este análisis
            prob_cond_previa = next(
                (p['prob'] for p in top_n if p['label'] == cond_previa), 0.0
            )
            # Ponderada por la confianza que tenía ese diagnóstico anterior
            historical_consistency = round(prob_cond_previa * conf_previa, 4)

            # Advertencia cuando la condición cambia con confianza baja:
            # sugiere oscilación del modelo, no cambio real de la piel.
            umbral_nota = CONFIDENCE_THRESHOLD * DIAGNOSTIC_NOTE_LOW_CONF_FACTOR
            if top1_label != cond_previa and top1_conf < umbral_nota:
                diagnostic_note = (
                    f'El diagnóstico cambió de {cond_previa} '
                    f'(confianza anterior {conf_previa*100:.0f}%) '
                    f'a {top1_label} con confianza baja ({top1_conf*100:.0f}%). '
                    f'Se recomienda una nueva captura con mejor iluminación '
                    f'o en condiciones similares a la sesión anterior.'
                )

    result = {
        'condition':              top1_label,
        'confidence':             top1_conf,
        'top_n':                  top_n,
        'severity_score':         round(severity_score, 4),
        'worst_zone':             worst_zone,
        'affected_zones_count':   affected_zones_count,
        'zones_display':          zones_display,
        'zones_diagnostic':       zones_diagnostic,
        'profile_consistency':    profile_consistency,
        'historical_consistency': historical_consistency,
        'target_ingredients':     INGREDIENTES_OBJETIVO.get(top1_label, []),
        'avoid_ingredients':      INGREDIENTES_EVITAR.get(top1_label, []),
        'model':                  MODEL_ARCH,
        'tta_passes':             5,
        'zone_schema_version':    ZONE_SCHEMA_VERSION,
        'timestamp':              datetime.now().isoformat(),
    }
    if diagnostic_note:
        result['diagnostic_note'] = diagnostic_note
    return result


# =============================================================================
# PASO 6 — DELTA ENTRE ANÁLISIS
# =============================================================================

def calcular_delta(result_anterior: dict, result_actual: dict) -> dict:
    """
    Calcula diferencias numéricas entre dos resultados consecutivos.
    Alimenta los gráficos de comparación del dashboard.

    Incluye detección de incompatibilidad de versiones de esquema de zonas:
    si result_anterior fue generado con v2 (5 zonas) y result_actual con v3
    (9 zonas), se añade 'schema_mismatch': True al delta como advertencia.

    Métricas
    --------
    severity_delta      : diferencia absoluta del score global
    severity_delta_pct  : cambio porcentual
    severity_trend      : 'improving' | 'stable' | 'worsening'
      Umbral ±0.05 — equivale a 1/5 del rango IGA scale.
      Ref: Zaenglein et al. 2022, JAAD.
    zones               : por zona → erythema_delta, comedones_delta,
                          scales_delta, erythema_pct
    condition_changed   : bool
    affected_zones_delta: int
    inci_score_delta    : si ambos resultados tienen inci_safety_score
    """
    delta: dict = {}

    # Advertencia de incompatibilidad de esquema de zonas
    v_prev = result_anterior.get('zone_schema_version', 'v2')
    v_curr = result_actual.get('zone_schema_version', ZONE_SCHEMA_VERSION)
    if v_prev != v_curr:
        delta['schema_mismatch'] = True
        delta['schema_warning']  = (
            f'Esquemas de zonas incompatibles: '
            f'análisis anterior={v_prev}, actual={v_curr}. '
            f'El delta de zonas es parcial.'
        )

    # Severidad global
    sev_prev = result_anterior.get('severity_score', 0.0)
    sev_curr = result_actual.get('severity_score',   0.0)
    sev_diff = round(sev_curr - sev_prev, 4)
    delta['severity_delta']     = sev_diff
    delta['severity_delta_pct'] = round(
        (sev_diff / sev_prev * 100) if sev_prev > 0 else 0.0, 2
    )
    delta['severity_trend'] = (
        'improving' if sev_diff < -SEVERITY_TREND_THRESHOLD else
        'worsening' if sev_diff >  SEVERITY_TREND_THRESHOLD else
        'stable'
    )

    # Delta por zona — solo zones_display para consistencia con el dashboard
    zones_prev = result_anterior.get('zones_display', result_anterior.get('zones', {}))
    zones_curr = result_actual.get('zones_display',   result_actual.get('zones', {}))
    delta['zones'] = {}
    for zona in zones_curr:
        if zona in zones_prev:
            e_d = round(zones_curr[zona]['erythema']  - zones_prev[zona]['erythema'],  4)
            c_d = round(zones_curr[zona]['comedones'] - zones_prev[zona]['comedones'], 4)
            s_d = round(zones_curr[zona]['scales']    - zones_prev[zona]['scales'],    4)
            delta['zones'][zona] = {
                'erythema_delta':  e_d,
                'comedones_delta': c_d,
                'scales_delta':    s_d,
                'erythema_pct':    round(
                    (e_d / zones_prev[zona]['erythema'] * 100)
                    if zones_prev[zona]['erythema'] > 0 else 0.0, 2
                ),
            }

    # Cambio de condición
    delta['condition_changed'] = (
        result_anterior.get('condition') != result_actual.get('condition')
    )
    delta['condition_prev'] = result_anterior.get('condition')
    delta['condition_curr'] = result_actual.get('condition')

    # Cambio en zonas activas
    delta['affected_zones_delta'] = (
        result_actual.get('affected_zones_count', 0) -
        result_anterior.get('affected_zones_count', 0)
    )

    # Delta INCI safety score (si ambos resultados lo tienen)
    if 'inci_safety_score' in result_anterior and 'inci_safety_score' in result_actual:
        delta['inci_score_delta'] = round(
            result_actual['inci_safety_score'] -
            result_anterior['inci_safety_score'], 2
        )

    return delta


# =============================================================================
# MOSTRAR RESULTADO EN CONSOLA
# =============================================================================

def mostrar_resultado(result: dict) -> None:
    """Imprime el resultado completo de forma legible en consola."""
    condicion = result['condition']
    print(f'\n{"─"*CONSOLE_LINE_WIDTH}')
    print(f'  Diagnóstico       : {condicion}')
    print(f'  Descripción       : {DESCRIPCIONES.get(condicion, "")}')
    print(f'  Confianza         : {result["confidence"]*100:.1f}%')
    print(f'  Severity score    : {result["severity_score"]:.3f}  (0=sana, 1=severa)')
    print(f'  Zona más afectada : {result["worst_zone"]}')
    print(f'  Zonas activas     : {result["affected_zones_count"]}')

    hist = result.get('historical_consistency', 0.0)
    if hist > 0.0:
        print(f'  Consist. histórica: {hist*100:.1f}%  (coherencia con análisis anterior)')

    if condicion in MENSAJES_ALERTA:
        print(f'\n  [!] {MENSAJES_ALERTA[condicion]}')

    if result.get('diagnostic_note'):
        print(f'\n  [ATENCIÓN] {result["diagnostic_note"]}')

    print(f'\n  Condiciones detectadas (≥{CONFIDENCE_THRESHOLD*100:.0f}%):')
    for i, item in enumerate(result['top_n']):
        barra = '█' * int(item['prob'] * CONSOLE_BAR_WIDTH)
        print(f'    #{i+1}  {item["label"]:<35} {item["prob"]*100:5.1f}%  {barra}')

    if result.get('target_ingredients'):
        print(f'\n  Ingredientes recomendados : '
              f'{", ".join(result["target_ingredients"])}')
    if result.get('avoid_ingredients'):
        print(f'  Ingredientes a evitar     : '
              f'{", ".join(result["avoid_ingredients"])}')

    print(f'{"─"*60}')


# =============================================================================
# PIPELINE PRINCIPAL
# =============================================================================

def analizar(ruta_imagen: str, perfil: dict | None = None,
             result_anterior: dict | None = None) -> tuple[dict | None, dict | None]:
    """
    Pipeline completo de análisis.

    Parámetros
    ----------
    ruta_imagen     : str — ruta de la imagen a analizar
    perfil          : dict | None — perfil clínico del usuario
                      {edad, sexo, fototipo, tipo_piel, historial, exposicion_ac}
    result_anterior : dict | None — resultado previo para calcular delta

    Retorna
    -------
    (result, delta) — ambos None si la imagen no existe o el modelo falla.
    """
    ruta = str(ruta_imagen)
    if not Path(ruta).exists():
        print(f'[ERROR] Imagen no encontrada: {ruta}')
        return None, None

    print(f'\nAnalizando: {Path(ruta).name}')
    print('─' * CONSOLE_LINE_WIDTH)

    print('Paso 1 — Censurando ojos y extrayendo métricas zonales...')
    ruta_censurada, analisis_zonal = censurar_y_analizar(ruta)

    print('\nPaso 2 — Cargando modelo...')
    modelo, clases_lista = get_modelo()
    class_indices = {c: i for i, c in enumerate(clases_lista)}

    print('\nPaso 3 — Predicción con TTA×5...')
    probs_raw = predecir_con_tta(modelo, ruta_censurada, n_aug=5)

    if perfil:
        print('\nPaso 4 — Ajustando por perfil clínico...')
        probs_raw = ajustar_por_perfil(
            probs_raw, perfil, class_indices,
            result_anterior=result_anterior,
        )
    elif result_anterior:
        # Sin perfil clínico pero con historial: aplicar solo continuidad diagnóstica
        print('\nPaso 4 — Aplicando continuidad diagnóstica (sin perfil clínico)...')
        probs_raw = ajustar_por_perfil(
            probs_raw, {}, class_indices,
            result_anterior=result_anterior,
        )

    if analisis_zonal:
        print('\nPaso 5 — Ajustando por métricas zonales...')
        probs_dict = {clases_lista[i]: float(probs_raw[i])
                      for i in range(len(clases_lista))}
        probs_dict = ajustar_por_zona(probs_dict, analisis_zonal, verbose=True)
        probs_raw  = np.array([probs_dict.get(c, 0.0) for c in clases_lista])

    print('\nPaso 6 — Construyendo resultado...')
    result = construir_resultado_completo(
        probs_raw, clases_lista, analisis_zonal, perfil,
        result_anterior=result_anterior,
    )

    mostrar_resultado(result)

    delta = None
    if result_anterior:
        print('\nPaso 7 — Calculando delta vs análisis anterior...')
        delta = calcular_delta(result_anterior, result)
        if delta.get('schema_mismatch'):
            print(f'  [!] {delta["schema_warning"]}')
        print(f'  Tendencia       : {delta["severity_trend"]}')
        print(f'  Δ severity      : {delta["severity_delta"]:+.4f}  '
              f'({delta["severity_delta_pct"]:+.1f}%)')
        print(f'  Condición cambió: {"SÍ" if delta["condition_changed"] else "NO"}')
        if delta['condition_changed']:
            print(f'    {delta["condition_prev"]} → {delta["condition_curr"]}')

    ts          = datetime.now().strftime('%Y%m%d_%H%M%S')
    nombre_json = Path(ruta).parent / f'result_{ts}.json'
    output_dict = {'result': result}
    if delta:
        output_dict['delta'] = delta
    with open(nombre_json, 'w', encoding='utf-8') as f:
        json.dump(output_dict, f, indent=2, ensure_ascii=False)
    print(f'\n  Resultado guardado: {nombre_json}')

    return result, delta


# =============================================================================
# INTERFAZ DE CONSOLA
# =============================================================================

def _preguntar(pregunta, opciones=None, defecto=None, tipo=str):
    """
    Solicita un valor al usuario con validación y valor por defecto.
    Acepta Enter para usar el defecto.
    """
    if opciones:
        opts_str = ' / '.join(f'[{o}]' if o == defecto else o for o in opciones)
        sufijo   = f'  ({opts_str}): '
    elif defecto is not None:
        sufijo = f'  [Enter = {defecto}]: '
    else:
        sufijo = ': '

    while True:
        respuesta = input(f'  {pregunta}{sufijo}').strip()
        if respuesta == '':
            return defecto
        try:
            valor = tipo(respuesta)
        except (ValueError, TypeError):
            print('    Valor inválido. Intenta de nuevo.')
            continue
        if opciones and str(valor) not in [str(o) for o in opciones]:
            print(f'    Opciones válidas: {", ".join(str(o) for o in opciones)}')
            continue
        return valor


def _preguntar_multiple(pregunta, opciones, defecto=None):
    """
    Solicita una selección múltiple numerada.
    Acepta entradas como '1 3', '1,3' o '1, 3'.
    """
    print(f'\n  {pregunta}')
    for i, op in enumerate(opciones, 1):
        print(f'    {i}) {op}')
    print(f'    [Enter = {"Ninguna" if not defecto else defecto}]')

    while True:
        respuesta = input(
            '  Tu selección (números separados por espacio o coma): '
        ).strip()
        if respuesta == '':
            return defecto if defecto else []
        partes = [p.strip() for p in respuesta.replace(',', ' ').split() if p.strip()]
        try:
            indices = [int(p) for p in partes]
        except ValueError:
            print('    Ingresa solo números.')
            continue
        if not all(1 <= i <= len(opciones) for i in indices):
            print(f'    Números válidos: 1 al {len(opciones)}.')
            continue
        return [opciones[i - 1] for i in indices]


def pedir_perfil() -> dict:
    """
    Solicita todos los campos del perfil clínico por consola.
    Cada campo tiene un valor por defecto para agilizar pruebas.
    """
    print('\n' + '═' * CONSOLE_LINE_WIDTH)
    print('  PERFIL CLÍNICO  (Enter para usar el valor por defecto)')
    print('═' * CONSOLE_LINE_WIDTH)

    perfil = {
        'edad':   _preguntar('Edad', defecto=PERFIL_DEFAULT_EDAD, tipo=int),
        'sexo':   _preguntar('Sexo biológico',
                             opciones=['Masculino', 'Femenino'],
                             defecto=PERFIL_DEFAULT_SEXO),
        'fototipo': _preguntar('Fototipo de Fitzpatrick',
                               opciones=['I', 'II', 'III', 'IV', 'V', 'VI', 'Desconocido'],
                               defecto=PERFIL_DEFAULT_FOTOTIPO),
        'tipo_piel': _preguntar('Tipo de piel',
                                opciones=['Grasa', 'Mixta', 'Seca', 'Sensible', 'Normal'],
                                defecto=PERFIL_DEFAULT_TIPO_PIEL),
        'historial': _preguntar_multiple(
            'Historial dermatológico (selecciona uno o varios, o Enter para Ninguna):',
            opciones=['Acné', 'Rosácea', 'Dermatitis', 'Psoriasis', 'Eccema'],
            defecto=[],
        ),
        'exposicion_ac': _preguntar(
            'Exposición a aire acondicionado / calefacción',
            opciones=['Sí, siempre', 'A veces', 'No'],
            defecto=PERFIL_DEFAULT_EXPOSICION,
        ),
    }

    print('\n  Perfil registrado:')
    for k, v in perfil.items():
        print(f'    {k:<15}: {v}')
    print('─' * CONSOLE_LINE_WIDTH)
    return perfil


def main():
    parser = argparse.ArgumentParser(
        description='SkinAI v3 — Análisis dermatológico con IA')
    parser.add_argument('imagen', nargs='?', help='Ruta de la imagen')
    parser.add_argument('--sin-perfil', action='store_true',
                        help='Analizar sin ajuste de perfil clínico')
    args = parser.parse_args()

    print('SkinAI v3 — Analizador de imágenes dermatológicas')
    print('=' * CONSOLE_LINE_WIDTH)

    ruta   = args.imagen or input('\nRuta de la imagen (o arrástrala aquí): ').strip().strip('"')
    perfil = None if args.sin_perfil else pedir_perfil()

    if args.sin_perfil:
        print('\n  [!] Modo sin perfil — sin ajuste clínico.')

    analizar(ruta, perfil=perfil)


if __name__ == '__main__':
    main()
