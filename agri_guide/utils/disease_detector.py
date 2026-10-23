"""Classical Computer Vision & Machine Learning Plant Disease Detector for CropPulse.

Extracts statistical color moments, HSV distribution, and texture descriptors
from leaf photos and predicts disease classifications using an ExtraTreesClassifier.
Runs efficiently on serverless environments (Vercel) without PyTorch or TensorFlow.
"""

from __future__ import annotations
import base64
import io
import json
import os
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from PIL import Image
import scipy.stats as stats
import scipy.ndimage as ndimage

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / "final_model" / "disease_model.pkl"
CLASSES_PATH = BASE_DIR / "final_model" / "disease_classes.json"

_disease_model: Any = None
_disease_classes: Optional[Dict[str, Any]] = None


def load_disease_assets() -> Tuple[Any, Dict[str, Any]]:
    """Lazy-load the trained disease classifier and metadata catalog."""
    global _disease_model, _disease_classes

    if _disease_model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Disease model not found at {MODEL_PATH}")
        with open(MODEL_PATH, "rb") as f:
            _disease_model = pickle.load(f)

    if _disease_classes is None:
        if not CLASSES_PATH.exists():
            raise FileNotFoundError(f"Disease classes catalog not found at {CLASSES_PATH}")
        with open(CLASSES_PATH, "r", encoding="utf-8") as f:
            _disease_classes = json.load(f)

    return _disease_model, _disease_classes


def extract_leaf_features(img_input: Union[Image.Image, bytes, str, io.BytesIO]) -> np.ndarray:
    """
    Extract a compact 45-dimensional feature descriptor from a leaf image:
    1. Color moments (mean, std, skewness) across R, G, B and H, S, V (18 features).
    2. Normalized HSV color distribution histograms (20 features).
    3. Laplacian & Sobel spatial texture energy descriptors (4 features).
    4. Chlorosis (yellow), necrosis (brown), and healthy green chromatic ratios (3 features).
    """
    if isinstance(img_input, (bytes, bytearray)):
        img = Image.open(io.BytesIO(img_input)).convert("RGB")
    elif isinstance(img_input, io.BytesIO):
        img = Image.open(img_input).convert("RGB")
    elif isinstance(img_input, str):
        if img_input.startswith("data:image"):
            header, encoded = img_input.split(",", 1)
            raw = base64.b64decode(encoded)
            img = Image.open(io.BytesIO(raw)).convert("RGB")
        elif os.path.exists(img_input):
            img = Image.open(img_input).convert("RGB")
        else:
            raw = base64.b64decode(img_input)
            img = Image.open(io.BytesIO(raw)).convert("RGB")
    elif isinstance(img_input, Image.Image):
        img = img_input.convert("RGB")
    else:
        raise ValueError(f"Unsupported image input type: {type(img_input)}")

    # Standardize scale
    img = img.resize((128, 128))
    arr = np.array(img, dtype=np.float32)

    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    hsv = np.array(img.convert("HSV"), dtype=np.float32)
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]

    feats: List[float] = []

    # 1. Color moments across R, G, B, H, S, V (18 features)
    for ch in [r, g, b, h, s, v]:
        m = float(np.mean(ch))
        std_val = float(np.std(ch))
        skew_val = float(stats.skew(ch.ravel())) if std_val > 1e-4 else 0.0
        feats.extend([m, std_val, skew_val])

    # 2. Histograms (20 features)
    h_hist, _ = np.histogram(h, bins=10, range=(0, 256), density=True)
    s_hist, _ = np.histogram(s, bins=5, range=(0, 256), density=True)
    v_hist, _ = np.histogram(v, bins=5, range=(0, 256), density=True)
    feats.extend(h_hist.tolist())
    feats.extend(s_hist.tolist())
    feats.extend(v_hist.tolist())

    # 3. Spatial texture via grayscale Laplacian (2 features)
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    lap = ndimage.laplace(gray)
    feats.append(float(np.var(lap)))
    feats.append(float(np.mean(np.abs(lap))))

    # 4. Sobel gradients (2 features)
    sx = ndimage.sobel(gray, axis=1)
    sy = ndimage.sobel(gray, axis=0)
    mag = np.hypot(sx, sy)
    feats.append(float(np.mean(mag)))
    feats.append(float(np.std(mag)))

    # 5. Biological pigment / lesion ratios (3 features)
    total_px = 128.0 * 128.0
    green_mask = (g > r) & (g > b) & (g > 50)
    brown_mask = (r > g) & (g > b) & (r > 60)
    yellow_mask = (r > 100) & (g > 100) & (b < 90)
    feats.append(float(np.sum(green_mask) / total_px))
    feats.append(float(np.sum(brown_mask) / total_px))
    feats.append(float(np.sum(yellow_mask) / total_px))

    return np.array(feats, dtype=np.float32).reshape(1, -1)


def predict_disease(img_input: Union[Image.Image, bytes, str, io.BytesIO]) -> Dict[str, Any]:
    """
    Run leaf feature extraction and predict crop disease diagnosis.
    Returns disease classification, confidence score, pathogen type, and remedial recommendations.
    """
    model, classes = load_disease_assets()

    features = extract_leaf_features(img_input)

    pred_idx = int(model.predict(features)[0])
    probabilities = model.predict_proba(features)[0]
    confidence = float(probabilities[pred_idx] * 100.0)

    meta = classes.get(str(pred_idx), {})

    # Top 3 alternative predictions for clinical transparency
    top_indices = np.argsort(probabilities)[::-1][:3]
    top_candidates = []
    for idx in top_indices:
        item = classes.get(str(idx), {})
        top_candidates.append({
            "id": int(idx),
            "disease_name": item.get("disease_name", "Unknown"),
            "confidence": round(float(probabilities[idx] * 100.0), 2)
        })

    return {
        "class_id": pred_idx,
        "disease_name": meta.get("disease_name", "Unknown"),
        "crop": meta.get("crop", "Unknown"),
        "status": meta.get("status", "Diseased"),
        "severity": meta.get("severity", "Moderate"),
        "confidence": round(confidence, 2),
        "pathogen_type": meta.get("pathogen_type", "Fungal / Physiological"),
        "description": meta.get("description", "No description available."),
        "organic_treatment": meta.get("organic_treatment", "Apply organic copper spray or compost tea."),
        "chemical_treatment": meta.get("chemical_treatment", "Consult local agricultural extension."),
        "prevention": meta.get("prevention", "Maintain balanced irrigation and good canopy ventilation."),
        "top_candidates": top_candidates
    }
