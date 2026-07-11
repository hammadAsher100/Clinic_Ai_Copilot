"""
Preprocessing pipeline for the Symptom2Disease text classification dataset.

Tokenizes symptom descriptions, pads sequences, and encodes disease labels.
Saves tokenizer and label encoder artifacts for inference reuse.

Expected CSV format:
  label,text
  "Psoriasis","I have been experiencing flaky skin and redness..."
  ...
  (24 disease classes, ~1200 rows)
"""
from __future__ import annotations

import os
import pickle
import re
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from keras.preprocessing.text import Tokenizer
from keras.utils import pad_sequences

MAX_WORDS: int = 5000
MAX_SEQUENCE_LENGTH: int = 100

RAW_DATA_PATH = os.getenv("TEXT_RAW_DATA", "data/raw/text/Symptom2Disease.csv")
REGISTRY_DIR = Path(os.getenv("MODEL_REGISTRY_PATH", "ml/registry"))


def load_raw_data(path: str = RAW_DATA_PATH) -> pd.DataFrame:
    """Load the Symptom2Disease CSV."""
    df = pd.read_csv(path)

    # Normalise column names — dataset may have 'label'/'text' or other variants
    col_map = {}
    for col in df.columns:
        if col.lower() in ("label", "disease", "prognosis"):
            col_map[col] = "label"
        elif col.lower() in ("text", "symptoms", "symptom", "description"):
            col_map[col] = "text"
    df = df.rename(columns=col_map)

    if "label" not in df.columns or "text" not in df.columns:
        raise ValueError(
            f"Expected 'label' and 'text' columns, got: {list(df.columns)}"
        )

    return df[["label", "text"]].dropna()


def clean_text(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def preprocess_and_split(
    df: pd.DataFrame,
    test_size: float = 0.2,
    random_state: int = 42,
    save_artifacts: bool = True,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, list[str]]:
    """Tokenize texts, encode labels, split train/test.

    Returns
    -------
    X_train, X_test, y_train, y_test, num_classes, class_names
    """
    # Clean text
    df = df.copy()
    df["text"] = df["text"].apply(clean_text)

    # Encode labels
    class_names = sorted(df["label"].unique().tolist())
    label_to_idx = {label: idx for idx, label in enumerate(class_names)}
    num_classes = len(class_names)

    y = df["label"].map(label_to_idx).values

    # Tokenize
    tokenizer = Tokenizer(num_words=MAX_WORDS, oov_token="<OOV>")
    tokenizer.fit_on_texts(df["text"].values)

    sequences = tokenizer.texts_to_sequences(df["text"].values)
    X = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH, padding="post", truncating="post")

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    print(f"[TEXT] Vocabulary size: {min(len(tokenizer.word_index) + 1, MAX_WORDS)}")
    print(f"[TEXT] Sequence length: {MAX_SEQUENCE_LENGTH}")
    print(f"[TEXT] Classes ({num_classes}): {class_names}")

    if save_artifacts:
        REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
        with open(REGISTRY_DIR / "tokenizer.pkl", "wb") as f:
            pickle.dump(tokenizer, f)
        with open(REGISTRY_DIR / "text_label_encoder.pkl", "wb") as f:
            pickle.dump({"class_names": class_names, "label_to_idx": label_to_idx}, f)

    return X_train, X_test, y_train, y_test, num_classes, class_names


def preprocess_single_text(text: str) -> np.ndarray:
    """Preprocess a single symptom text for inference.

    Returns
    -------
    np.ndarray of shape (1, MAX_SEQUENCE_LENGTH).
    """
    with open(REGISTRY_DIR / "tokenizer.pkl", "rb") as f:
        tokenizer: Tokenizer = pickle.load(f)

    cleaned = clean_text(text)
    seq = tokenizer.texts_to_sequences([cleaned])
    padded = pad_sequences(seq, maxlen=MAX_SEQUENCE_LENGTH, padding="post", truncating="post")
    return padded


def get_class_names() -> list[str]:
    """Load saved class names from registry."""
    with open(REGISTRY_DIR / "text_label_encoder.pkl", "rb") as f:
        data = pickle.load(f)
    return data["class_names"]
