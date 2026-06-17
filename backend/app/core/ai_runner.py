"""
ai_runner.py
Pipeline completo de inferencia dermatológica.

  1. Carga EfficientNet-B3 (singleton por proceso, reutilizado en cada tarea Celery).
  2. Predice con TTA×N sobre la imagen censurada (seeds fijas → reproducible).
  3. Ajusta probabilidades por perfil clínico y métricas zonales.
  4. Construye el resultado completo que se guarda en la BD.
  5. Calcula el delta respecto al análisis anterior (si existe).
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image as PILImage

from app.core.skinai_config import (
    IMG_SIZE, IMAGENET_MEAN, IMAGENET_STD,
    MODEL_ARCH, MODEL_HIDDEN_SIZE, MODEL_DROPOUT_1, MODEL_DROPOUT_2,
    TTA_FLIP_PROB, TTA_ROTATION_DEGREES, TTA_CROP_SCALE_MIN, TTA_CROP_SCALE_MAX,
    TTA_BRIGHTNESS_JITTER, TTA_SEED_MULTIPLIER,
)
from app.core.face_censor_v3 import ajustar_por_zona
from app.core.skinai_analizar_v3 import (
    ajustar_por_perfil,
    construir_resultado_completo,
    calcular_delta,
)

logger = logging.getLogger(__name__)

MODEL_DIR     = Path(os.getenv("AI_MODEL_DIR", "/app/models"))
MODEL_FILE    = "SkinAI_opcionA-v3.pth"
LABELS_FILE   = "labels_opcionA-v3.json"
MODEL_VERSION = "efficientnet_b3_v3"

_model:  Optional[nn.Module]    = None
_clases: Optional[list]         = None
_device: Optional[torch.device] = None


def _load_model():
    global _model, _clases, _device
    if _model is not None:
        return _model, _clases, _device

    try:
        import timm
    except ImportError:
        raise RuntimeError("timm no instalado. Agrega 'timm' al Dockerfile.")

    model_path  = MODEL_DIR / MODEL_FILE
    labels_path = MODEL_DIR / LABELS_FILE

    if not model_path.exists():
        raise FileNotFoundError(f"Modelo no encontrado: {model_path}")
    if not labels_path.exists():
        raise FileNotFoundError(f"Labels no encontrado: {labels_path}")

    with open(labels_path, "r") as f:
        labels_dict = json.load(f)
    clases   = [k for k, v in sorted(labels_dict.items(), key=lambda x: x[1])]
    n_clases = len(clases)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

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
        torch.load(model_path, map_location=device, weights_only=True)
    )
    modelo = modelo.to(device)
    modelo.eval()

    _model  = modelo
    _clases = clases
    _device = device

    logger.info(f"Modelo cargado: {MODEL_FILE} — {n_clases} clases — {device}")
    return _model, _clases, _device


def run_inference(
    image_path: str,
    analisis_zonal: Optional[Dict] = None,
    perfil: Optional[Dict] = None,
    result_anterior: Optional[Dict] = None,
    n_aug: int = 5,
) -> Dict[str, Any]:
    """
    Pipeline completo de inferencia dermatológica.

    Parámetros
    ----------
    image_path      : ruta de la imagen censurada
    analisis_zonal  : métricas zonales producidas por FaceCensor, o None
    perfil          : {edad, sexo, fototipo, tipo_piel, historial, exposicion_ac}, o None
    result_anterior : campo result del análisis previo del usuario, o None
    n_aug           : pasadas TTA adicionales (total = n_aug + 1)

    Retorna
    -------
    Dict con el resultado completo listo para guardar en analyses.result.
    Incluye la clave 'delta' si se proporcionó result_anterior.
    """
    modelo, clases, device = _load_model()

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

    img = PILImage.open(image_path).convert("RGB")

    with torch.no_grad():
        probs = torch.softmax(
            modelo(val_t(img).unsqueeze(0).to(device)), dim=1
        ).cpu().numpy()[0]

    for seed in range(n_aug):
        torch.manual_seed(seed * TTA_SEED_MULTIPLIER)
        with torch.no_grad():
            probs += torch.softmax(
                modelo(tta_t(img).unsqueeze(0).to(device)), dim=1
            ).cpu().numpy()[0]

    probs /= (n_aug + 1)

    class_indices = {c: i for i, c in enumerate(clases)}

    if perfil or result_anterior:
        probs = ajustar_por_perfil(
            probs, perfil or {}, class_indices, result_anterior=result_anterior
        )

    if analisis_zonal:
        probs_dict = {clases[i]: float(probs[i]) for i in range(len(clases))}
        probs_dict = ajustar_por_zona(probs_dict, analisis_zonal)
        probs      = np.array([probs_dict.get(c, 0.0) for c in clases])

    result = construir_resultado_completo(
        probs, clases, analisis_zonal, perfil, result_anterior, n_aug=n_aug
    )

    if result_anterior:
        result["delta"] = calcular_delta(result_anterior, result)

    result["model_version"] = MODEL_VERSION

    logger.info(
        f"Inferencia completada: {result['condition']} "
        f"({result['confidence']*100:.1f}%) — severity {result['severity_score']:.3f}"
    )
    return result
