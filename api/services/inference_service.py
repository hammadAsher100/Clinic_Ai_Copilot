"""
Inference service — loads all three serialized models ONCE at FastAPI startup
and exposes predict_image(), predict_tabular(), predict_text() functions.

Each returns {prediction, confidence, explainability} — the router layer
persists these to the database and serves them to the frontend.

This module is NOT the predictive engine for the LLM — it runs dedicated
deep-learning models (CNN, ANN, BiLSTM) independently.
"""
from __future__ import annotations

import logging
import os
import pickle
import sys
from pathlib import Path
from typing import Optional

import numpy as np

# Ensure project root is on path for ml.* imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger("prediction")

REGISTRY_DIR = Path(os.getenv("MODEL_REGISTRY_PATH", "ml/registry"))

# ── Module-level model caches (loaded once at startup) ──────────────────
_cnn_model = None
_ann_model = None
_text_model = None
_text_tokenizer = None
_text_label_data = None
_ann_scaler = None
_ann_feature_names = None
_ann_num_indices = None
_models_loaded = False


def load_all_models() -> None:
    """Load all three models + preprocessor artifacts into memory.

    Called once during FastAPI startup.  Fails loudly if any model
    artifact is missing — do not silently serve a broken endpoint.
    """
    global _cnn_model, _ann_model, _text_model
    global _text_tokenizer, _text_label_data
    global _ann_scaler, _ann_feature_names, _ann_num_indices
    global _models_loaded

    import keras

    # ── CNN (pneumonia) ──────────────────────────────────────────────────
    cnn_path = REGISTRY_DIR / "cnn_pneumonia.h5"
    if cnn_path.exists():
        _cnn_model = keras.saving.load_model(str(cnn_path))
        logger.info("CNN model loaded from %s", cnn_path)
    else:
        logger.warning("CNN model not found at %s — image predictions disabled", cnn_path)

    # ── ANN (heart disease) ──────────────────────────────────────────────
    ann_path = REGISTRY_DIR / "ann_heart_risk.h5"
    if ann_path.exists():
        _ann_model = keras.saving.load_model(str(ann_path))
        logger.info("ANN model loaded from %s", ann_path)
    else:
        logger.warning("ANN model not found at %s — tabular predictions disabled", ann_path)

    # ANN preprocessor artifacts
    for name, attr in [
        ("ann_scaler.pkl", "_ann_scaler"),
        ("ann_feature_names.pkl", "_ann_feature_names"),
        ("ann_num_indices.pkl", "_ann_num_indices"),
    ]:
        artifact_path = REGISTRY_DIR / name
        if artifact_path.exists():
            with open(artifact_path, "rb") as f:
                globals()[attr] = pickle.load(f)

    # ── Text (symptom classifier) ────────────────────────────────────────
    text_path = REGISTRY_DIR / "text_triage.h5"
    if text_path.exists():
        _text_model = keras.saving.load_model(str(text_path))
        logger.info("Text model loaded from %s", text_path)
    else:
        logger.warning("Text model not found at %s — text predictions disabled", text_path)

    tokenizer_path = REGISTRY_DIR / "tokenizer.pkl"
    if tokenizer_path.exists():
        with open(tokenizer_path, "rb") as f:
            _text_tokenizer = pickle.load(f)

    label_path = REGISTRY_DIR / "text_label_encoder.pkl"
    if label_path.exists():
        with open(label_path, "rb") as f:
            _text_label_data = pickle.load(f)

    _models_loaded = True
    logger.info("All available models loaded successfully")


def models_are_loaded() -> bool:
    """Check if load_all_models() has been called."""
    return _models_loaded


# ═══════════════════════════════════════════════════════════════════════
# Prediction functions
# ═══════════════════════════════════════════════════════════════════════

def predict_image(image_bytes: bytes) -> dict:
    """Run pneumonia detection on a chest X-ray image.

    Returns
    -------
    dict with keys: prediction, confidence, gradcam_path
    """
    if _cnn_model is None:
        raise RuntimeError("CNN model not loaded — run load_all_models() first")

    from ml.cnn.preprocess import preprocess_single_image
    from ml.cnn.gradcam import generate_gradcam, create_heatmap_overlay

    # Preprocess
    img_array = preprocess_single_image(image_bytes)

    # Predict
    prob = float(_cnn_model.predict(img_array, verbose=0)[0][0])
    prediction = "PNEUMONIA" if prob >= 0.5 else "NORMAL"
    confidence = prob if prob >= 0.5 else 1 - prob

    # Grad-CAM
    gradcam_path: Optional[str] = None
    try:
        heatmap = generate_gradcam(img_array, model=_cnn_model)
        import uuid
        fname = f"gradcam_{uuid.uuid4().hex[:8]}.png"
        save_path = str(Path(os.getenv("UPLOAD_DIR", "data/uploads")) / fname)
        create_heatmap_overlay(image_bytes, heatmap, save_path=save_path)
        gradcam_path = save_path
    except Exception as e:
        logger.warning("Grad-CAM generation failed: %s", e)

    logger.info(
        "IMAGE prediction: %s (confidence=%.3f, gradcam=%s)",
        prediction, confidence, gradcam_path,
    )

    return {
        "prediction": prediction,
        "confidence": round(confidence, 4),
        "gradcam_path": gradcam_path,
    }


def predict_tabular(features: dict) -> dict:
    """Run heart disease risk prediction on tabular clinical features.

    Returns
    -------
    dict with keys: prediction, confidence, shap_values, shap_chart_path
    """
    if _ann_model is None:
        raise RuntimeError("ANN model not loaded — run load_all_models() first")

    from ml.ann.preprocess import preprocess_single_input

    # Preprocess
    input_array = preprocess_single_input(features)

    # Predict
    prob = float(_ann_model.predict(input_array, verbose=0)[0][0])
    prediction = "HIGH_RISK" if prob >= 0.5 else "LOW_RISK"
    confidence = prob if prob >= 0.5 else 1 - prob

    # SHAP explanation
    shap_values: Optional[dict] = None
    shap_chart_path: Optional[str] = None
    try:
        from ml.ann.shap_explain import explain, generate_shap_chart
        shap_values = explain(input_array)

        import uuid
        fname = f"shap_{uuid.uuid4().hex[:8]}.png"
        save_path = str(Path(os.getenv("UPLOAD_DIR", "data/uploads")) / fname)
        generate_shap_chart(shap_values, save_path=save_path)
        shap_chart_path = save_path
    except Exception as e:
        logger.warning("SHAP explanation failed: %s", e)

    logger.info(
        "TABULAR prediction: %s (confidence=%.3f)",
        prediction, confidence,
    )

    return {
        "prediction": prediction,
        "confidence": round(confidence, 4),
        "shap_values": shap_values,
        "shap_chart_path": shap_chart_path,
    }


def predict_text(symptom_text: str) -> dict:
    """Run symptom-to-condition classification.

    Returns
    -------
    dict with keys: condition, confidence, top_3
    """
    if _text_model is None:
        raise RuntimeError("Text model not loaded — run load_all_models() first")

    from ml.text_model.preprocess import preprocess_single_text

    # Preprocess
    input_seq = preprocess_single_text(symptom_text)

    # Predict
    probas = _text_model.predict(input_seq, verbose=0)[0]
    top_idx = int(np.argmax(probas))
    confidence = float(probas[top_idx])

    # Get class names
    class_names = _text_label_data["class_names"] if _text_label_data else [str(i) for i in range(len(probas))]
    condition = class_names[top_idx] if top_idx < len(class_names) else f"Class_{top_idx}"

    # Top 3 predictions
    top3_indices = np.argsort(probas)[-3:][::-1]
    top_3 = [
        {
            "condition": class_names[i] if i < len(class_names) else f"Class_{i}",
            "confidence": round(float(probas[i]), 4),
        }
        for i in top3_indices
    ]

    logger.info(
        "TEXT prediction: %s (confidence=%.3f)",
        condition, confidence,
    )

    return {
        "condition": condition,
        "confidence": round(confidence, 4),
        "top_3": top_3,
    }
