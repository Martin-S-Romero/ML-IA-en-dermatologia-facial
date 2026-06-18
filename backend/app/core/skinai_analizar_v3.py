"""
skinai_analizar_v3.py  —  SkinAI  (librería de lógica clínica)
==============================================================
Modelo v12 · EfficientNetB2 · 7 clases.

Este módulo NO carga el modelo ni ejecuta TTA: eso vive en ai_runner.py.
Aquí solo residen las funciones de lógica clínica y los diccionarios de
datos por condición. ai_runner.py importa y orquesta estas tres funciones:

    - ajustar_por_perfil()           ajuste por perfil + continuidad diagnóstica
    - construir_resultado_completo() arma el dict que se guarda en la BD
    - calcular_delta()               compara dos análisis consecutivos

"""

import numpy as np
from datetime import datetime

from .skinai_config import (
    # inferencia / salida
    CONFIDENCE_THRESHOLD, SEVERITY_TREND_THRESHOLD,
    DIAGNOSTIC_NOTE_LOW_CONF_FACTOR,
    # modelo / zonas (para metadata del resultado)
    MODEL_ARCH, ZONAS_DISPLAY, ZONE_SCHEMA_VERSION,
    # boosts de perfil
    BOOST_PERFIL_ROSACEA_ETR, BOOST_PERFIL_ROSACEA_INFL,
    BOOST_PERFIL_ACNE_INFL, BOOST_PERFIL_ACNE_COMEDONAL, BOOST_PERFIL_ACNE_EXCORIADO,
    BOOST_PERFIL_PERIORAL,
    BOOST_PIEL_SENSIBLE_ROSACEA,
    BOOST_PIEL_GRASA_COMEDONAL, BOOST_PIEL_GRASA_INFL,
    BOOST_FOTOTIPO_BAJO_ROSACEA, BOOST_FOTOTIPO_BAJO_ROSACEA_INFL, BOOST_FOTOTIPO_ALTO_ROSACEA,
    EDAD_UMBRAL_JOVEN, EDAD_UMBRAL_ADULTO, EDAD_DEFAULT,
    BOOST_EDAD_JOVEN_INFL, BOOST_EDAD_JOVEN_COMEDONAL,
    BOOST_EDAD_ADULTO_ROSACEA, BOOST_EDAD_ADULTO_ROSACEA_INFL,
    BOOST_FEMENINO_EXCORIATED,
    # continuidad diagnóstica
    BOOST_CONTINUIDAD_BASE, BOOST_CONTINUIDAD_MIN_CONF,
    PENALTY_TRANSICION_IMPROBABLE, TRANSICIONES_IMPROBABLES,
)


# =============================================================================
# DATOS CLÍNICOS POR CONDICIÓN  (7 clases — v12)
# =============================================================================

DESCRIPCIONES = {
    'acne-comedonal':        'Acné comedonal — puntos negros/blancos, zona T',
    'acne-excoriated':       'Acné excoriado — marcas de rascado, mejillas/mentón',
    'acne-inflammatory':     'Acné inflamatorio — pústulas/nódulos, cara',
    'perioral-dermatitis':   'Dermatitis perioral — zona alrededor de la boca',
    'rosacea-etr':           'Rosácea eritematotelangiectásica — mejillas simétricas',
    'rosacea-inflammatory':  'Rosácea inflamatoria — centro facial',
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
}


# =============================================================================
# AJUSTE POR PERFIL CLÍNICO + CONTINUIDAD DIAGNÓSTICA
# =============================================================================

def ajustar_por_perfil(probs_raw: np.ndarray, perfil: dict,
                       class_indices: dict,
                       result_anterior: dict | None = None) -> np.ndarray:
    """
    Aplica multiplicadores a las probabilidades según el perfil del usuario
    y, si existe, el resultado del análisis anterior (continuidad diagnóstica).
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
        # La única dermatitis en el modelo de 7 clases es la perioral.
        _boost('perioral-dermatitis', BOOST_PERFIL_PERIORAL)

    if tipo_piel == 'Sensible':
        _boost('rosacea-etr', BOOST_PIEL_SENSIBLE_ROSACEA)
    if tipo_piel == 'Grasa':
        _boost('acne-comedonal', BOOST_PIEL_GRASA_COMEDONAL)
        _boost('acne-inflammatory', BOOST_PIEL_GRASA_INFL)
    # 'Seca' ya no ajusta ninguna clase (su único efecto era boost seborreico).

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

    if sexo == 'Femenino':
        _boost('acne-excoriated', BOOST_FEMENINO_EXCORIATED)
    # 'exposicion_ac' ya no ajusta ninguna clase (su efecto era boost seborreico).

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
# CONSTRUIR RESULTADO COMPLETO
# =============================================================================

def construir_resultado_completo(probs_array: np.ndarray,
                                 clases_lista: list[str],
                                 analisis_zonal: dict | None,
                                 perfil: dict | None = None,
                                 result_anterior: dict | None = None,
                                 tta_passes: int = 5) -> dict:

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
            'Dermatitis': ['perioral-dermatitis'],
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
        'model':                  MODEL_ARCH,
        'tta_passes':             tta_passes,
        'zone_schema_version':    ZONE_SCHEMA_VERSION,
        'timestamp':              datetime.now().isoformat(),
    }
    if diagnostic_note:
        result['diagnostic_note'] = diagnostic_note
    return result



# =============================================================================
# DELTA ENTRE ANÁLISIS
# =============================================================================

def calcular_delta(result_anterior: dict, result_actual: dict) -> dict:
    """
    Calcula diferencias numéricas entre dos resultados consecutivos.
    Alimenta los gráficos de comparación del dashboard.
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

