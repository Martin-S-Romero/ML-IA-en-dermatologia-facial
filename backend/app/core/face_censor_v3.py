"""
Censura facial con MediaPipe FaceMesh y extracción de métricas zonales.

"""

import cv2
import numpy as np
import os
import sys

from skinai_config import (
    # severity
    ERYTHEMA_W, COMEDONES_W, SCALES_W,
    # umbrales de eritema
    ERYTHEMA_THRESHOLD_MILD, ERYTHEMA_THRESHOLD_MODERATE,
    ERYTHEMA_MIN_ZONA_T, ERYTHEMA_MIN_PERIORAL,
    ERYTHEMA_MIN_EXCORIATED, ERYTHEMA_MIN_HEALTHY, ERYTHEMA_MIN_SYMMETRY,
    ERYTHEMA_MIN_MANDIBULA, ERYTHEMA_PERIORAL_DIRECT, ERYTHEMA_PERIORAL_MAX_MEJILLAS,
    # umbrales de comedones y escamas
    COMEDONES_ZONA_T, COMEDONES_MEJILLAS,
    SCALES_ZONA_T, SCALES_CEJAS, SCALES_ZONA_T_PENALTY, SCALES_CEJAS_PENALTY,
    ERITEMA_COMEDONES_MEJILLAS,
    COMEDONES_MANDIBULA,
    # boosts zonales
    BOOST_ROSACEA_ETR_BILATERAL, BOOST_ROSACEA_INFL_BILATERAL,
    BOOST_ACNE_COMEDONAL_ZONA_T, BOOST_ACNE_INFL_MEJILLAS,
    BOOST_SEBORRHEIC_ZONA_T_BASE, BOOST_SEBORRHEIC_ZONA_T_SCALE,
    BOOST_SEBORRHEIC_CEJAS_BASE, BOOST_SEBORRHEIC_CEJAS_SCALE,
    PENALTY_ROSACEA_SCALE, PENALTY_ROSACEA_MAX,
    BOOST_PERIORAL, BOOST_ACNE_EXCORIATED_ZONA, BOOST_HEALTHY_SKIN,
    BOOST_ACNE_INFL_MANDIBULA, BOOST_PERIORAL_DIRECT,
    # mediapipe
    FACEMESH_MAX_FACES, FACEMESH_DETECTION_CONFIDENCE, FACEMESH_TRACKING_CONFIDENCE,
    LANDMARK_LEFT_EYE, LANDMARK_RIGHT_EYE,
    # resolución y censura
    MIN_IMG_WIDTH, MIN_IMG_HEIGHT,
    DEFAULT_BLUR_STRENGTH, DEFAULT_EXPAND_PX, DEFAULT_PIXEL_SIZE, BLUR_SIGMA,
    # métricas visuales
    ADAPTIVE_BLOCK_SIZE, ADAPTIVE_C, COMEDONES_AMPLIFIER, SCALES_NORMALIZATION_FACTOR,
    # zonas
    CAP_INTENSIDAD,
    ZONA_WEIGHTS, ZONAS_DISPLAY,
)

# ── MediaPipe — importación con fallback ──────────────────────────────────────
try:
    import mediapipe as mp
    if not hasattr(mp, 'solutions'):
        try:
            import mediapipe.python.solutions as solutions
            mp.solutions = solutions
        except ImportError:
            pass
    FaceMesh = mp.solutions.face_mesh.FaceMesh
except Exception as e:
    print(f'[!] Error inicializando MediaPipe (import estándar): {e}', file=sys.stderr)
    try:
        from mediapipe.python.solutions.face_mesh import FaceMesh
    except Exception as e2:
        print(f'[ERROR] No se pudo importar MediaPipe: {e2}', file=sys.stderr)
        raise e2

# ── Índices de landmarks por zona facial (MediaPipe FaceMesh 468 puntos) ──────
# Ref: MediaPipe Face Mesh topology — Google 2020
# https://github.com/google/mediapipe/blob/master/mediapipe/modules/face_geometry/
#      data/canonical_face_model_uv_visualization.png
LANDMARKS_ZONAS = {
    'frente':        [10, 67, 69, 104, 108, 151, 299, 337, 338],
    'ceja_izq':      [46, 53, 52, 65, 55, 70, 63, 105, 66, 107],
    'ceja_der':      [276, 283, 282, 295, 285, 300, 293, 334, 296, 336],
    'mejilla_izq':   [116, 123, 147, 187, 207, 213, 192, 214],
    'mejilla_der':   [345, 352, 376, 411, 427, 433, 416, 434],
    'nariz':         [1, 2, 4, 5, 6, 19, 94, 168, 195, 197],
    'nariz_lat_izq': [60, 166, 239, 240, 241, 242],
    'nariz_lat_der': [289, 305, 459, 460, 461, 462],
    'menton':        [152, 175, 199, 200, 208, 428, 396, 369],
    'mandibula_izq': [136, 150, 149, 176, 148, 172],
    'mandibula_der': [365, 379, 378, 400, 377, 397],
    'zona_perioral': [61, 185, 40, 39, 37, 267, 269, 270, 409, 291, 308, 78, 95, 88, 178, 87, 14, 317, 402, 318, 324],
}

# Índices de ojos para censura
# Los landmarks de ojos y la resolución mínima se importan de skinai_config.


class FaceCensor:

    def __init__(self, mode='blur',
                 blur_strength=DEFAULT_BLUR_STRENGTH,
                 expand=DEFAULT_EXPAND_PX,
                 pixel_size=DEFAULT_PIXEL_SIZE,
                 cut=False):
        self.mode          = mode
        self.blur_strength = blur_strength
        self.expand        = expand
        self.pixel_size    = pixel_size
        self.cut           = cut
        self.ultimo_analisis_zonal = None

        self._face_mesh = FaceMesh(
            max_num_faces=FACEMESH_MAX_FACES,
            refine_landmarks=True,
            min_detection_confidence=FACEMESH_DETECTION_CONFIDENCE,
            min_tracking_confidence=FACEMESH_TRACKING_CONFIDENCE,
        )

    # ── Utilidades de bounding box ─────────────────────────────────────────────

    def _get_box(self, points):
        """Retorna (x1, y1, x2, y2) del bounding box de una lista de puntos."""
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        return min(xs), min(ys), max(xs), max(ys)

    def _safe_box(self, x1, y1, x2, y2, img_w, img_h):
        """Clamp del bounding box dentro de los límites de la imagen."""
        return (max(x1, 0), max(y1, 0), min(x2, img_w), min(y2, img_h))

    # ── Censura de una región ──────────────────────────────────────────────────

    def _apply_censor(self, image, points):
        """Aplica el efecto de censura sobre la región delimitada por `points`."""
        x1, y1, x2, y2 = self._safe_box(
            *[v + d for v, d in zip(self._get_box(points),
                                    [-self.expand, -self.expand,
                                      self.expand,  self.expand])],
            image.shape[1], image.shape[0],
        )
        roi = image[y1:y2, x1:x2]
        if roi.size == 0:
            return image

        if self.mode == 'blur':
            k = self.blur_strength if self.blur_strength % 2 == 1 \
                else self.blur_strength + 1
            roi = cv2.GaussianBlur(roi, (k, k), BLUR_SIGMA)
        elif self.mode == 'black':
            roi[:] = (0, 0, 0)
        elif self.mode == 'pixelate':
            h, w   = roi.shape[:2]
            px     = max(1, min(self.pixel_size, min(h, w)))
            small  = cv2.resize(roi, (px, px), interpolation=cv2.INTER_LINEAR)
            roi    = cv2.resize(small, (w, h),  interpolation=cv2.INTER_NEAREST)

        image[y1:y2, x1:x2] = roi
        return image

    # ── Métricas visuales por zona ─────────────────────────────────────────────

    def _calcular_eritema(self, roi_bgr):

        if roi_bgr.size == 0:
            return 0.0
        b, g, r = cv2.split(roi_bgr.astype(np.float32))
        ratio = np.mean(r) / (np.mean(g) + 1e-6)
        return float(np.clip((ratio - 1.0) / 1.0, 0.0, 1.0))

    def _calcular_comedones(self, roi_bgr):

        if roi_bgr.size == 0:
            return 0.0
        gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            blockSize=ADAPTIVE_BLOCK_SIZE,
            C=ADAPTIVE_C,
        )
        dark_ratio = np.sum(thresh > 0) / (thresh.size + 1e-6)
        return float(np.clip(dark_ratio * COMEDONES_AMPLIFIER, 0.0, 1.0))

    def _calcular_escamas(self, roi_bgr):

        if roi_bgr.size == 0:
            return 0.0
        gray    = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
        lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        return float(np.clip(lap_var / SCALES_NORMALIZATION_FACTOR, 0.0, 1.0))

    # ── Análisis zonal ─────────────────────────────────────────────────────────

    def _analizar_zonas(self, frame, landmarks, img_w, img_h):

        eritema_dict  = {}
        comedones_dict = {}
        escamas_dict  = {}
        severity_dict = {}

        for zona, idxs in LANDMARKS_ZONAS.items():
            pts = [landmarks[i] for i in idxs if i < len(landmarks)]
            if len(pts) < 3:
                eritema_dict[zona] = comedones_dict[zona] = escamas_dict[zona] = 0.0
                severity_dict[zona] = 0.0
                continue

            x1, y1, x2, y2 = self._safe_box(
                *[v + d for v, d in zip(self._get_box(pts),
                                        [-5, -5, 5, 5])],
                img_w, img_h,
            )
            roi = frame[y1:y2, x1:x2]

            e = self._calcular_eritema(roi)
            c = self._calcular_comedones(roi)
            s = self._calcular_escamas(roi)

            eritema_dict[zona]   = round(e, 4)
            comedones_dict[zona] = round(c, 4)
            escamas_dict[zona]   = round(s, 4)
            severity_dict[zona]  = round(
                ERYTHEMA_W * e + COMEDONES_W * c + SCALES_W * s, 4
            )

        # Severity global ponderado por área de zona
        global_severity = round(
            sum(severity_dict.get(z, 0.0) * ZONA_WEIGHTS.get(z, 0.0)
                for z in LANDMARKS_ZONAS),
            4,
        )

        # worst_zone solo entre zonas del dashboard (no subzonas diagnósticas)
        display_severities = {
            z: severity_dict[z] for z in ZONAS_DISPLAY if z in severity_dict
        }
        worst_zone = (
            max(display_severities, key=display_severities.get)
            if display_severities else None
        )

        affected = sum(
            1 for v in eritema_dict.values()
            if v >= ERYTHEMA_THRESHOLD_MILD
        )

        return {
            'eritema':              eritema_dict,
            'comedones':            comedones_dict,
            'escamas':              escamas_dict,
            'zone_severity':        severity_dict,
            'severity_score':       global_severity,
            'worst_zone':           worst_zone,
            'affected_zones_count': affected,
        }

    # ── Procesamiento de frame ─────────────────────────────────────────────────

    def _process_frame(self, frame):
        """
        1. Detecta landmarks con FaceMesh.
        2. Copia el frame antes de censurar (métricas sobre imagen limpia).
        3. Censura ambos ojos.
        4. Extrae métricas zonales sobre la copia limpia.
        5. Recorta al rostro si cut=True.
        """
        rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            self.ultimo_analisis_zonal = None
            return frame

        h, w, _ = frame.shape

        for face_landmarks in results.multi_face_landmarks:
            landmarks = [
                (int(lm.x * w), int(lm.y * h))
                for lm in face_landmarks.landmark
            ]

            # Copia limpia antes de censurar (métricas no contaminadas por blur)
            frame_limpio = frame.copy()

            frame = self._apply_censor(frame, [landmarks[i] for i in LANDMARK_LEFT_EYE])
            frame = self._apply_censor(frame, [landmarks[i] for i in LANDMARK_RIGHT_EYE])

            self.ultimo_analisis_zonal = self._analizar_zonas(
                frame_limpio, landmarks, w, h
            )

            if self.cut:
                fx1, fy1, fx2, fy2 = self._safe_box(
                    *[v + d for v, d in zip(self._get_box(landmarks),
                                            [-self.expand, -self.expand,
                                              self.expand,  self.expand])],
                    w, h,
                )
                if fx2 > fx1 and fy2 > fy1:
                    frame = frame[fy1:fy2, fx1:fx2]

            break  # solo el primer rostro detectado

        return frame


    def process_image(self, input_path, output_path=None):
        """
        Procesa una imagen: valida resolución, censura ojos,
        extrae métricas zonales y opcionalmente guarda el resultado.

        """
        image = cv2.imread(input_path)
        if image is None:
            print(f'[ERROR] No se pudo leer la imagen: {input_path}')
            return None

        h, w = image.shape[:2]
        _min_px = MIN_IMG_WIDTH * MIN_IMG_HEIGHT
        if w * h < _min_px:
            print(f'[!] Resolución insuficiente ({w}x{h} = {w*h}px). '
                  f'Mínimo {_min_px}px.')
            return None
        print(f'[ok] Resolución válida: {w}x{h}')

        result = self._process_frame(image)

        if output_path:
            folder = os.path.dirname(output_path)
            if folder:
                os.makedirs(folder, exist_ok=True)
            cv2.imwrite(output_path, result)
            print(f'[saved] Imagen censurada: {output_path}')

        return result

    def imprimir_analisis_zonal(self):
        """Imprime la tabla de métricas zonales en consola (depuración)."""
        if self.ultimo_analisis_zonal is None:
            print('  Sin análisis zonal (no se detectó rostro).')
            return
        a = self.ultimo_analisis_zonal
        print(f'\n  {"Zona":<20} {"Eritema":>8}  {"Comedones":>9}  '
              f'{"Escamas":>8}  {"Severidad":>9}  Nivel')
        print(f'  {"-"*68}')
        for zona in a['eritema']:
            e   = a['eritema'][zona]
            c   = a['comedones'].get(zona, 0)
            s   = a['escamas'].get(zona, 0)
            sv  = a['zone_severity'].get(zona, 0)
            nivel = ('ALTO'  if e >= ERYTHEMA_THRESHOLD_MODERATE else
                     'MEDIO' if e >= ERYTHEMA_THRESHOLD_MILD    else 'bajo')
            print(f'  {zona:<20} {e:>8.3f}  {c:>9.3f}  {s:>8.3f}  {sv:>9.3f}  {nivel}')
        print(f'\n  Severity global : {a["severity_score"]:.3f}')
        print(f'  Zona más afect. : {a["worst_zone"]}')
        print(f'  Zonas activas   : {a["affected_zones_count"]}')


# ── Ajuste de probabilidades por métricas zonales ─────────────────────────────

def ajustar_por_zona(probs_dict, analisis_zonal, verbose=False):
    """
    Ajusta las probabilidades del modelo usando métricas visuales por zona.
    No modifica el modelo — aplica multiplicadores basados en señales objetivas.

    """
    probs     = dict(probs_dict)
    eritema   = analisis_zonal.get('eritema',   {})
    comedones = analisis_zonal.get('comedones', {})
    escamas   = analisis_zonal.get('escamas',   {})

    def _boost(clase, factor, razon=''):
        if clase in probs:
            probs[clase] *= factor
            if verbose:
                print(f'  [zona boost] {clase:<35} ×{factor:.2f}  {razon}')

    # Rosácea ETR: eritema simétrico bilateral en mejillas
    e_mej_izq = eritema.get('mejilla_izq', 0)
    e_mej_der = eritema.get('mejilla_der', 0)
    simetria  = 1 - abs(e_mej_izq - e_mej_der) / (max(e_mej_izq, e_mej_der) + 1e-6)
    if e_mej_izq >= ERYTHEMA_THRESHOLD_MILD and e_mej_der >= ERYTHEMA_THRESHOLD_MILD and simetria > ERYTHEMA_MIN_SYMMETRY:
        _boost('rosacea-etr',          BOOST_ROSACEA_ETR_BILATERAL, 'eritema bilateral simétrico en mejillas')
        _boost('rosacea-inflammatory', BOOST_ROSACEA_INFL_BILATERAL, 'eritema bilateral')

    # Acné comedonal: comedones altos en zona T
    c_frente = comedones.get('frente', 0)
    c_nariz  = comedones.get('nariz',  0)
    if c_frente >= COMEDONES_ZONA_T or c_nariz >= COMEDONES_ZONA_T:
        _boost('acne-comedonal', BOOST_ACNE_COMEDONAL_ZONA_T, 'comedones en zona T')

    # Acné inflamatorio: eritema + comedones en mejillas
    e_mejillas_media = (e_mej_izq + e_mej_der) / 2
    c_mejillas_media = (
        comedones.get('mejilla_izq', 0) + comedones.get('mejilla_der', 0)
    ) / 2
    if e_mejillas_media >= ERITEMA_COMEDONES_MEJILLAS and c_mejillas_media >= ERITEMA_COMEDONES_MEJILLAS:
        _boost('acne-inflammatory', BOOST_ACNE_INFL_MEJILLAS, 'eritema + comedones en mejillas')

    # Acné inflamatorio: eritema + comedones en mandíbula (subtipo hormonal)
    # Ref: Zeichner et al. 2017, JDD — distribución mandibular en acné adulto femenino
    e_mandibula_media = (eritema.get('mandibula_izq', 0) + eritema.get('mandibula_der', 0)) / 2
    c_mandibula_media = (comedones.get('mandibula_izq', 0) + comedones.get('mandibula_der', 0)) / 2
    if e_mandibula_media >= ERYTHEMA_MIN_MANDIBULA and c_mandibula_media >= COMEDONES_MANDIBULA:
        _boost('acne-inflammatory', BOOST_ACNE_INFL_MANDIBULA, 'eritema + comedones en mandíbula')

    # Dermatitis seborreica: escamas proporcionales en zona T
    s_frente     = escamas.get('frente', 0)
    s_nariz      = escamas.get('nariz',  0)
    s_nariz_lat  = (
        escamas.get('nariz_lat_izq', 0) + escamas.get('nariz_lat_der', 0)
    ) / 2
    e_frente     = eritema.get('frente', 0)
    e_nariz      = eritema.get('nariz',  0)
    zona_T_escamas = max(s_frente, s_nariz, s_nariz_lat)

    if zona_T_escamas >= SCALES_ZONA_T and (e_frente >= ERYTHEMA_MIN_ZONA_T or e_nariz >= ERYTHEMA_MIN_ZONA_T):
        factor_base = BOOST_SEBORRHEIC_ZONA_T_BASE + min(zona_T_escamas, CAP_INTENSIDAD) * BOOST_SEBORRHEIC_ZONA_T_SCALE
        _boost('seborrheic-dermatitis', round(factor_base, 2),
               f'escamas zona T (intensidad {zona_T_escamas:.2f})')

    # Dermatitis seborreica: escamas en cejas
    s_cejas = (escamas.get('ceja_izq', 0) + escamas.get('ceja_der', 0)) / 2
    if s_cejas >= SCALES_CEJAS:
        factor_cejas = BOOST_SEBORRHEIC_CEJAS_BASE + min(s_cejas, CAP_INTENSIDAD) * BOOST_SEBORRHEIC_CEJAS_SCALE
        _boost('seborrheic-dermatitis', round(factor_cejas, 2),
               f'escamas en cejas (intensidad {s_cejas:.2f})')

    # Penalización de rosácea cuando hay escamas altas
    if zona_T_escamas >= SCALES_ZONA_T_PENALTY or s_cejas >= SCALES_CEJAS_PENALTY:
        penalizacion = round(
            1.0 - min((zona_T_escamas + s_cejas) * PENALTY_ROSACEA_SCALE, PENALTY_ROSACEA_MAX), 2
        )
        _boost('rosacea-etr',          penalizacion,
               'penalización: escamas incompatibles con rosácea')
        _boost('rosacea-inflammatory', penalizacion,
               'penalización: escamas incompatibles con rosácea')

    # Dermatitis perioral: eritema concentrado en mentón
    e_menton = eritema.get('menton', 0)
    if e_menton >= ERYTHEMA_MIN_PERIORAL and e_mejillas_media < ERYTHEMA_THRESHOLD_MILD:
        _boost('perioral-dermatitis', BOOST_PERIORAL, 'eritema concentrado en mentón')

    # Dermatitis perioral: eritema en zona perioral directa (más específico que proxy mentón)
    # Ref: Fonacier et al. 2021, JEADV — el halo perioral es el signo patognomónico
    e_perioral = eritema.get('zona_perioral', 0)
    if e_perioral >= ERYTHEMA_PERIORAL_DIRECT and e_mejillas_media < ERYTHEMA_PERIORAL_MAX_MEJILLAS:
        _boost('perioral-dermatitis', BOOST_PERIORAL_DIRECT, 'eritema en zona perioral directa')

    # Acné excoriado: eritema difuso en mejillas sin comedones marcados
    if e_mejillas_media >= ERYTHEMA_MIN_EXCORIATED and c_mejillas_media < ERYTHEMA_THRESHOLD_MILD:
        _boost('acne-excoriated', BOOST_ACNE_EXCORIATED_ZONA, 'eritema difuso sin comedones marcados')

    # Piel sana: eritema global bajo en todas las zonas
    if all(v < ERYTHEMA_MIN_HEALTHY for v in eritema.values()):
        _boost('healthy-skin', BOOST_HEALTHY_SKIN, 'eritema global bajo')

    # Renormalizar a suma = 1
    total = sum(probs.values())
    if total > 0:
        probs = {k: round(v / total, 6) for k, v in probs.items()}

    return probs