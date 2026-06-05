"""
ai_runner.py
Wrapper del modelo EfficientNet-B3 para análisis dermatológico.
Carga el modelo una sola vez (singleton) y lo reutiliza en cada tarea Celery.
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

logger = logging.getLogger(__name__)

MODEL_DIR     = Path(os.getenv("AI_MODEL_DIR", "/app/models"))
MODEL_FILE    = "SkinAI_opcionA.pth"
LABELS_FILE   = "labels_opcionA.json"
MODEL_VERSION = "efficientnet_b3_v1"

IMG_SIZE      = 300
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]

_model:  Optional[nn.Module] = None
_clases: Optional[list]      = None
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

    modelo = timm.create_model("efficientnet_b3", pretrained=False, num_classes=0)
    n_feat = modelo.num_features
    modelo.classifier = nn.Sequential(
        nn.BatchNorm1d(n_feat),
        nn.Dropout(p=0.3),
        nn.Linear(n_feat, 256),
        nn.ReLU(),
        nn.Dropout(p=0.2),
        nn.Linear(256, n_clases),
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


def run_inference(image_path: str, n_aug: int = 5) -> Dict[str, Any]:
    """
    Ejecuta EfficientNet-B3 con TTA sobre la imagen dada.
    Devuelve un dict con puntuaciones de todas las clases y metadatos.
    """
    modelo, clases, device = _load_model()

    val_t = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])
    tta_t = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=10),
        transforms.RandomResizedCrop(IMG_SIZE, scale=(0.93, 1.0)),
        transforms.ColorJitter(brightness=0.10),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])

    img = PILImage.open(image_path).convert("RGB")

    with torch.no_grad():
        probs = torch.softmax(
            modelo(val_t(img).unsqueeze(0).to(device)), dim=1
        ).cpu().numpy()[0]

    for _ in range(n_aug):
        with torch.no_grad():
            probs += torch.softmax(
                modelo(tta_t(img).unsqueeze(0).to(device)), dim=1
            ).cpu().numpy()[0]

    probs /= (n_aug + 1)

    top_idx        = int(np.argmax(probs))
    top1_label     = clases[top_idx]
    top1_confidence = float(probs[top_idx])
    all_scores     = {clases[i]: round(float(probs[i]), 6) for i in range(len(clases))}

    return {
        "top1_label":      top1_label,
        "top1_confidence": round(top1_confidence, 6),
        "all_scores":      all_scores,
        "tta_passes":      n_aug,
        "compute":         str(device),
        "model_version":   MODEL_VERSION,
    }
