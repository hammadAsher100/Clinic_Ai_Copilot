"""
Training script for the Symptom Classification BiLSTM.

Loads Symptom2Disease CSV, tokenizes/pads, trains the BiLSTM with early
stopping, evaluates, and logs everything to MLflow.
"""
from __future__ import annotations

import os
import sys
import json
from pathlib import Path

import numpy as np
import mlflow
import mlflow.keras
from sklearn.metrics import (
    accuracy_score, f1_score, classification_report, confusion_matrix,
)
from dotenv import load_dotenv
import keras

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from ml.text_model.preprocess import (
    load_raw_data, preprocess_and_split, MAX_WORDS, MAX_SEQUENCE_LENGTH,
)
from ml.text_model.model import build_text_model

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MLFLOW_EXPERIMENT = os.getenv("MLFLOW_EXPERIMENT_NAME", "clinical-copilot")
REGISTRY_DIR = Path(os.getenv("MODEL_REGISTRY_PATH", "ml/registry"))
RAW_DATA_PATH = os.getenv("TEXT_RAW_DATA", "data/raw/text/Symptom2Disease.csv")


def train(
    epochs: int = 30,
    batch_size: int = 32,
    learning_rate: float = 1e-3,
    patience: int = 7,
) -> dict:
    """Train the BiLSTM, log to MLflow, save best model.

    Returns
    -------
    dict with evaluation metrics.
    """
    # ── Load and preprocess ──────────────────────────────────────────────
    df = load_raw_data(RAW_DATA_PATH)
    X_train, X_test, y_train, y_test, num_classes, class_names = preprocess_and_split(
        df, save_artifacts=True
    )

    print(f"[TEXT] Training data: {X_train.shape}, Test data: {X_test.shape}")
    print(f"[TEXT] Number of classes: {num_classes}")

    # ── Build model ──────────────────────────────────────────────────────
    model = build_text_model(
        vocab_size=MAX_WORDS,
        max_sequence_length=MAX_SEQUENCE_LENGTH,
        num_classes=num_classes,
        learning_rate=learning_rate,
    )
    model.summary()

    # ── MLflow ───────────────────────────────────────────────────────────
    try:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    except Exception:
        mlflow.set_tracking_uri("mlruns")

    mlflow.set_experiment(MLFLOW_EXPERIMENT)

    with mlflow.start_run(run_name="bilstm_symptom_classifier"):
        mlflow.log_params({
            "model_type": "BiLSTM",
            "vocab_size": MAX_WORDS,
            "max_seq_length": MAX_SEQUENCE_LENGTH,
            "embedding_dim": 128,
            "lstm_units": 64,
            "num_classes": num_classes,
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "patience": patience,
        })

        # ── Train ────────────────────────────────────────────────────────
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor="val_loss", patience=patience, restore_best_weights=True
            ),
        ]

        history = model.fit(
            X_train, y_train,
            validation_split=0.15,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1,
        )

        # ── Evaluate ─────────────────────────────────────────────────────
        y_proba = model.predict(X_test)
        y_pred = np.argmax(y_proba, axis=1)

        metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "f1_macro": float(f1_score(y_test, y_pred, average="macro")),
            "f1_weighted": float(f1_score(y_test, y_pred, average="weighted")),
        }

        report = classification_report(
            y_test, y_pred, target_names=class_names, zero_division=0
        )
        print(f"\n[TEXT] Evaluation metrics: {json.dumps(metrics, indent=2)}")
        print(f"\n[TEXT] Classification report:\n{report}")

        mlflow.log_metrics(metrics)
        mlflow.log_text(report, "classification_report.txt")

        # ── Save model ──────────────────────────────────────────────────
        REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
        model_path = REGISTRY_DIR / "text_triage.h5"
        model.save(str(model_path))
        mlflow.log_artifact(str(model_path))
        mlflow.keras.log_model(model, "text_model")
        print(f"[TEXT] Model saved to {model_path}")

    return metrics


if __name__ == "__main__":
    train()
