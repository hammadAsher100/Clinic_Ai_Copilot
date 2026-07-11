"""
BiLSTM model definition for symptom-to-condition classification.

Architecture (anti-overfit):
  Embedding(vocab, 64) → SpatialDropout1D(0.4) →
  Bidirectional(LSTM(32)) → BatchNorm → Dense(32, relu) →
  Dropout(0.5) → Dense(num_classes, softmax)

24-class classification over disease labels from symptom descriptions.
"""
from __future__ import annotations

import keras
from keras import layers, Model, regularizers


def build_text_model(
    vocab_size: int = 5000,
    max_sequence_length: int = 100,
    embedding_dim: int = 64,
    num_classes: int = 24,
    learning_rate: float = 1e-3,
) -> Model:
    """Build and compile the symptom classification BiLSTM.

    Parameters
    ----------
    vocab_size : int
        Size of the vocabulary (from tokenizer).
    max_sequence_length : int
        Fixed length of padded input sequences.
    embedding_dim : int
        Dimensionality of the embedding layer.
    num_classes : int
        Number of disease classes.
    learning_rate : float
        Adam optimizer learning rate.

    Returns
    -------
    Compiled Keras Model.
    """
    model = keras.Sequential([
        layers.Input(shape=(max_sequence_length,)),
        layers.Embedding(
            input_dim=vocab_size,
            output_dim=embedding_dim,
            name="embedding",
        ),
        layers.SpatialDropout1D(0.4),
        layers.Bidirectional(
            layers.LSTM(
                32,
                kernel_regularizer=regularizers.l2(1e-4),
                recurrent_regularizer=regularizers.l2(1e-4),
                name="lstm",
            ),
            name="bilstm",
        ),
        layers.BatchNormalization(),
        layers.Dense(
            32,
            activation="relu",
            kernel_regularizer=regularizers.l2(1e-4),
            name="dense_1",
        ),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation="softmax", name="output"),
    ], name="symptom_bilstm")

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    return model
