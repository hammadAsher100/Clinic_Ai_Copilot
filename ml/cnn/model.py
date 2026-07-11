"""
CNN model definition for chest X-ray pneumonia detection.

Uses MobileNetV2 (pretrained on ImageNet) as the backbone with a frozen
base and a custom classification head.  Transfer learning is the highest-
leverage shortcut for hitting good accuracy quickly given hackathon time
constraints.

Architecture:
  MobileNetV2 (frozen) → GlobalAveragePooling2D → Dense(128, relu) →
  Dropout(0.5) → Dense(1, sigmoid)
"""
from __future__ import annotations

import keras
from keras import layers, Model
from keras.applications import MobileNetV2


def build_cnn(
    input_shape: tuple[int, int, int] = (224, 224, 3),
    learning_rate: float = 1e-4,
    fine_tune_from: int | None = None,
) -> Model:
    """Build and compile the pneumonia detection CNN.

    Parameters
    ----------
    input_shape : tuple
        Image dimensions (H, W, C).
    learning_rate : float
        Adam optimizer learning rate.
    fine_tune_from : int, optional
        If set, unfreeze base layers starting from this layer index
        for fine-tuning.  Use after initial training with frozen base.

    Returns
    -------
    Compiled Keras Model.
    """
    # ── Base model ───────────────────────────────────────────────────────
    base_model = MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False  # Freeze base initially

    if fine_tune_from is not None:
        base_model.trainable = True
        for layer in base_model.layers[:fine_tune_from]:
            layer.trainable = False

    # ── Classification head ──────────────────────────────────────────────
    inputs = keras.Input(shape=input_shape)
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(128, activation="relu", name="head_dense")(x)
    x = layers.Dropout(0.5)(x)
    outputs = layers.Dense(1, activation="sigmoid", name="output")(x)

    model = Model(inputs, outputs, name="pneumonia_cnn")

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )

    return model
