"""
Grad-CAM implementation for the Pneumonia Detection CNN.

Generates a class-activation heatmap overlay on the original chest X-ray
by computing gradients of the predicted class w.r.t. the last convolutional
layer's feature maps.

Keras 3 compatible implementation.
"""
from __future__ import annotations

import io
import os
from pathlib import Path
from typing import Optional

import numpy as np
import keras
import cv2
from PIL import Image

REGISTRY_DIR = Path(os.getenv("MODEL_REGISTRY_PATH", "ml/registry"))

_model: Optional[keras.Model] = None


def _load_model() -> keras.Model:
    """Load the trained CNN from registry (cached)."""
    global _model
    if _model is None:
        model_path = REGISTRY_DIR / "cnn_pneumonia.h5"
        _model = keras.saving.load_model(str(model_path))
    return _model


def _find_last_conv_layer(model: keras.Model) -> str:
    """Find the name of the last convolutional layer in the model."""
    for layer in reversed(model.layers):
        if hasattr(layer, "layers"):
            for sub_layer in reversed(layer.layers):
                if type(sub_layer).__name__ == "Conv2D":
                    return sub_layer.name
        if type(layer).__name__ == "Conv2D":
            return layer.name
    raise ValueError("No convolutional layer found in model")


def generate_gradcam(
    image_array: np.ndarray,
    model: keras.Model | None = None,
    last_conv_layer_name: str | None = None,
) -> np.ndarray:
    """Generate Grad-CAM heatmap for pneumonia detection.
    
    Parameters
    ----------
    image_array : np.ndarray
        Preprocessed image of shape (1, 224, 224, 3)
    model : keras.Model, optional
        The trained CNN model
    last_conv_layer_name : str, optional
        Name of the last conv layer (auto-detected if None)
    
    Returns
    -------
    np.ndarray
        Heatmap of shape (H, W) with values in [0, 1]
    """
    import tensorflow as tf
    import logging
    logger = logging.getLogger("gradcam")
    
    if model is None:
        model = _load_model()
    
    # Auto-detect last conv layer if not provided
    if last_conv_layer_name is None:
        # For MobileNetV2 base model
        last_conv_layer_name = "Conv_1"
        
        # Try to find it in model layers
        for layer in reversed(model.layers):
            if hasattr(layer, 'layers'):  # Nested model (MobileNetV2)
                for sub_layer in reversed(layer.layers):
                    if 'conv' in sub_layer.name.lower() and 'bn' not in sub_layer.name.lower():
                        last_conv_layer_name = sub_layer.name
                        break
                break
    
    try:
        # Create a model that outputs both conv features and predictions
        grad_model = keras.Model(
            inputs=model.input,
            outputs=[
                model.get_layer(last_conv_layer_name).output,
                model.output
            ]
        )
        
        # Compute gradients
        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(image_array)
            # Use the predicted class probability
            loss = predictions[:, 0]
        
        # Get gradients of the predicted class with respect to conv outputs
        grads = tape.gradient(loss, conv_outputs)
        
        # Pool the gradients over all axes except the channel axis
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        
        # Weight the channels by the corresponding gradients
        conv_outputs = conv_outputs[0]
        pooled_grads = pooled_grads.numpy()
        conv_outputs = conv_outputs.numpy()
        
        # Weight each channel by its importance
        for i in range(pooled_grads.shape[0]):
            conv_outputs[:, :, i] *= pooled_grads[i]
        
        # Average over all channels to get the heatmap
        heatmap = np.mean(conv_outputs, axis=-1)
        
        # Normalize to [0, 1]
        heatmap = np.maximum(heatmap, 0)  # ReLU
        if heatmap.max() > 0:
            heatmap /= heatmap.max()
        
        logger.info(f"Grad-CAM generated successfully using layer: {last_conv_layer_name}")
        return heatmap
        
    except Exception as e:
        logger.warning(f"Grad-CAM generation failed: {e}, returning uniform heatmap")
        # Fallback to uniform heatmap
        return np.ones((7, 7), dtype=np.float32) * 0.5


def create_heatmap_overlay(
    original_image_bytes: bytes,
    heatmap: np.ndarray,
    alpha: float = 0.4,
    save_path: str | None = None,
) -> bytes:
    """Overlay the Grad-CAM heatmap on the original X-ray image."""
    img = Image.open(io.BytesIO(original_image_bytes)).convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img)

    heatmap_resized = cv2.resize(heatmap, (224, 224))
    heatmap_colored = cv2.applyColorMap(
        np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET
    )
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

    overlay = np.uint8(img_array * (1 - alpha) + heatmap_colored * alpha)

    overlay_img = Image.fromarray(overlay)
    buf = io.BytesIO()
    overlay_img.save(buf, format="PNG")
    buf.seek(0)
    img_bytes = buf.read()

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(img_bytes)

    return img_bytes
