"""
ai_runner.py  —  SkinAI  (orquestador de inferencia)
====================================================
Punto de entrada que invocan las tareas Celery. Responsabilidades:

  1. Cargar el modelo UNA sola vez por proceso (singleton).
     Modelo v12 → EfficientNetB2, 7 clases.
  2. Ejecutar TTA (Test-Time Augmentation): 1 pasada limpia + N aumentadas.
  3. Llamar a la lógica clínica de skinai_analizar_v3 (librería):
        ajustar_por_perfil → ajustar_por_zona → construir_resultado_completo → calcular_delta
  4. Devolver el dict listo para guardar en la base de datos.

──────────────────────────────────────────────────────────────────────────────
PUNTOS A AJUSTAR A TU REPO (marcados con  # >>> AJUSTAR):
  - Los imports: si usas paquete (app.core.*), antepón la ruta del paquete.
  - MODELS_DIR: dónde viven el .pth y el .json (en tu repo: backend/models/).
  - Cómo recibe la imagen FaceCensor y qué firma usa process_image en tu proyecto.
──────────────────────────────────────────────────────────────────────────────
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime

import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image as PILImage

# >>> AJUSTAR imports a tu paquete si aplica, p.ej.:
#     from app.core.face_censor import FaceCensor, ajustar_por_zona
#     from app.core.skinai_analizar_v3 import (...)
from .face_censor import FaceCensor, ajustar_por_zona
from .skinai_analizar_v3 import (
    ajustar_por_perfil,
    construir_resultado_completo,
    calcular_delta,
)
from .skinai_config import (
    MODEL_ARCH,                       # 'efficientnet_b2'  (v12)
    MODEL_HIDDEN_SIZE, MODEL_DROPOUT_1, MODEL_DROPOUT_2,
    IMG_SIZE, IMAGENET_MEAN, IMAGENET_STD,
    TTA_SEED_MULTIPLIER, TTA_ROTATION_DEGREES,
    TTA_CROP_SCALE_MIN, TTA_CROP_SCALE_MAX,
    TTA_BRIGHTNESS_JITTER, TTA_FLIP_PROB,
)

# ── Rutas de artefactos del modelo ────────────────────────────────────────────

MODELS_DIR = Path(__file__).resolve().parents[2] / 'models'
MODEL_PATH  = MODELS_DIR / 'SkinAI_opcionA-v12.pth'
LABELS_PATH = MODELS_DIR / 'labels_opcionA-v12.json'

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Número de pasadas de TTA. En v12, TTA aporta +1.34pp (positivo) → se mantiene.
TTA_PASSES = 5

# ── Singleton del modelo ──────────────────────────────────────────────────────
_modelo_cache: torch.nn.Module | None = None
_clases_cache: list[str] | None = None


# =============================================================================
# CARGA DEL MODELO  (una sola vez por proceso)
# =============================================================================

def _cargar_modelo_desde_disco() -> tuple[torch.nn.Module, list[str]]:
    """Instancia el modelo (MODEL_ARCH = EfficientNetB2 en v12), carga pesos y labels."""
    try:
        import timm
    except ImportError as e:
        raise RuntimeError('timm no instalado: pip install timm') from e

    for ruta, nombre in [(MODEL_PATH, 'Modelo'), (LABELS_PATH, 'Labels')]:
        if not ruta.exists():
            raise FileNotFoundError(f'{nombre} no encontrado: {ruta}')

    with open(LABELS_PATH, 'r', encoding='utf-8') as f:
        labels_dict = json.load(f)
    clases_lista = [k for k, _ in sorted(labels_dict.items(), key=lambda x: x[1])]
    n_clases = len(clases_lista)

    modelo = timm.create_model(MODEL_ARCH, pretrained=False, num_classes=0)
    n_feat = modelo.num_features  # type: ignore[union-attr]  # B2 → 1408
    modelo.classifier = nn.Sequential(  # type: ignore[union-attr]
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
    return modelo, clases_lista


def get_modelo() -> tuple[torch.nn.Module, list[str]]:
    """Devuelve (modelo, clases). Carga desde disco solo la primera vez."""
    global _modelo_cache, _clases_cache
    if _modelo_cache is None or _clases_cache is None:
        _modelo_cache, _clases_cache = _cargar_modelo_desde_disco()
    return _modelo_cache, _clases_cache


# =============================================================================
# TTA  (Test-Time Augmentation)
# =============================================================================

def predecir_con_tta(modelo: torch.nn.Module, ruta_imagen: str,
                     n_aug: int = TTA_PASSES) -> np.ndarray:
    """
    Promedia N+1 inferencias con variaciones leves.
    Pasada 1: imagen original sin augmentation (reproducible).
    Pasadas 2…N+1: variaciones con seeds fijas → resultados reproducibles.
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
            modelo(val_t(img).unsqueeze(0).to(DEVICE)), dim=1  # type: ignore[operator]
        ).cpu().numpy()[0]

    for seed in range(n_aug):
        torch.manual_seed(seed * TTA_SEED_MULTIPLIER)
        with torch.no_grad():
            probs += torch.softmax(
                modelo(tta_t(img).unsqueeze(0).to(DEVICE)), dim=1  # type: ignore[operator]
            ).cpu().numpy()[0]

    return probs / (n_aug + 1)


# =============================================================================
# ENTRADA PRINCIPAL  (la que invoca la tarea Celery)
# =============================================================================

def run_inference(image_path: str,
                  analisis_zonal: dict | None = None,
                  perfil: dict | None = None,
                  result_anterior: dict | None = None,
                  n_aug: int = TTA_PASSES) -> dict:
    """
    Pipeline de inferencia sobre imagen ya censurada.
    La censura y la extracción de analisis_zonal se hacen en la tarea Celery
    antes de llamar aquí.
    """
    modelo, clases_lista = get_modelo()
    class_indices = {c: i for i, c in enumerate(clases_lista)}

    probs = predecir_con_tta(modelo, image_path, n_aug=n_aug)

    if perfil or result_anterior:
        probs = ajustar_por_perfil(
            probs, perfil or {}, class_indices,
            result_anterior=result_anterior,
        )

    if analisis_zonal:
        probs_dict = {clases_lista[i]: float(probs[i]) for i in range(len(clases_lista))}
        probs_dict = ajustar_por_zona(probs_dict, analisis_zonal, verbose=False)
        probs = np.array([probs_dict.get(c, 0.0) for c in clases_lista])

    return construir_resultado_completo(
        probs, clases_lista, analisis_zonal, perfil,
        result_anterior=result_anterior,
        tta_passes=n_aug,
    )


def run_analysis(input_path: str,
                 output_path: str | None = None,
                 perfil: dict | None = None,
                 result_anterior: dict | None = None) -> dict:
    """
    Pipeline completo de inferencia.

    Parámetros
    ----------
    input_path      : ruta de la imagen original subida por el usuario.
    output_path     : ruta donde guardar la imagen censurada. Si es None,
                      FaceCensor genera una junto a la original.
    perfil          : dict del perfil clínico del usuario (o None).
    result_anterior : dict 'result' del análisis previo (o None).

    Retorna
    -------
    dict con la forma {'result': {...}} y, si hay análisis previo, {'delta': {...}}.
    Es lo que la capa de persistencia guarda en analyses.result.
    """
    # ── 1. Censura + métricas zonales ─────────────────────────────────────────
    censor = FaceCensor(mode='blur')
    # >>> AJUSTAR: adapta esta llamada a la firma real de process_image en tu repo.
    censor.process_image(input_path, output_path)
    analisis_zonal = censor.ultimo_analisis_zonal  # dict o None si no detectó rostro

    # ── 2. Modelo (singleton) + TTA ───────────────────────────────────────────
    modelo, clases_lista = get_modelo()
    class_indices = {c: i for i, c in enumerate(clases_lista)}

    # Se predice sobre la imagen censurada (ojos difuminados) si existe.
    ruta_pred = output_path or input_path
    probs = predecir_con_tta(modelo, ruta_pred, n_aug=TTA_PASSES)

    # ── 3. Ajuste por perfil + continuidad diagnóstica ────────────────────────
    if perfil or result_anterior:
        probs = ajustar_por_perfil(
            probs, perfil or {}, class_indices,
            result_anterior=result_anterior,
        )

    # ── 4. Ajuste por métricas zonales ────────────────────────────────────────
    if analisis_zonal:
        probs_dict = {clases_lista[i]: float(probs[i]) for i in range(len(clases_lista))}
        probs_dict = ajustar_por_zona(probs_dict, analisis_zonal, verbose=False)
        probs = np.array([probs_dict.get(c, 0.0) for c in clases_lista])

    # ── 5. Construir resultado ────────────────────────────────────────────────
    result = construir_resultado_completo(
        probs, clases_lista, analisis_zonal, perfil,
        result_anterior=result_anterior,
        tta_passes=TTA_PASSES,
    )

    # ── 6. Delta vs análisis anterior ─────────────────────────────────────────
    output: dict = {'result': result}
    if result_anterior:
        output['delta'] = calcular_delta(result_anterior, result)

    return output
