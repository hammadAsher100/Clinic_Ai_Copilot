"""
ML model unit tests — validates model definitions build correctly
and produce outputs of expected shape.

These tests do NOT require trained model artifacts (.h5 files).
They test the model architecture definitions only.
"""
from __future__ import annotations

import numpy as np
import pytest


class TestANNModel:
    """ANN (heart disease) model architecture tests."""

    def test_build_ann(self):
        from ml.ann.model import build_ann
        model = build_ann(input_dim=20)
        assert model is not None
        assert model.name == "heart_disease_ann"

    def test_ann_output_shape(self):
        from ml.ann.model import build_ann
        model = build_ann(input_dim=20)
        dummy_input = np.random.randn(1, 20).astype(np.float32)
        output = model.predict(dummy_input, verbose=0)
        assert output.shape == (1, 1)
        assert 0 <= output[0][0] <= 1  # Sigmoid output

    def test_ann_batch_prediction(self):
        from ml.ann.model import build_ann
        model = build_ann(input_dim=15)
        batch = np.random.randn(8, 15).astype(np.float32)
        output = model.predict(batch, verbose=0)
        assert output.shape == (8, 1)


class TestCNNModel:
    """CNN (pneumonia) model architecture tests."""

    def test_build_cnn(self):
        from ml.cnn.model import build_cnn
        model = build_cnn(input_shape=(224, 224, 3))
        assert model is not None
        assert model.name == "pneumonia_cnn"

    def test_cnn_output_shape(self):
        from ml.cnn.model import build_cnn
        model = build_cnn(input_shape=(224, 224, 3))
        dummy_img = np.random.rand(1, 224, 224, 3).astype(np.float32)
        output = model.predict(dummy_img, verbose=0)
        assert output.shape == (1, 1)
        assert 0 <= output[0][0] <= 1

    def test_cnn_with_fine_tuning(self):
        from ml.cnn.model import build_cnn
        model = build_cnn(input_shape=(224, 224, 3), fine_tune_from=100)
        assert model is not None
        # At least some layers should be trainable
        trainable_count = sum(1 for layer in model.layers if layer.trainable)
        assert trainable_count > 0


class TestTextModel:
    """BiLSTM (symptom classification) model architecture tests."""

    def test_build_text_model(self):
        from ml.text_model.model import build_text_model
        model = build_text_model(vocab_size=1000, num_classes=24)
        assert model is not None
        assert model.name == "symptom_bilstm"

    def test_text_model_output_shape(self):
        from ml.text_model.model import build_text_model
        model = build_text_model(vocab_size=1000, max_sequence_length=50, num_classes=24)
        dummy_seq = np.random.randint(0, 999, size=(1, 50))
        output = model.predict(dummy_seq, verbose=0)
        assert output.shape == (1, 24)
        # Softmax outputs should sum to ~1
        assert abs(output[0].sum() - 1.0) < 1e-5

    def test_text_model_different_classes(self):
        from ml.text_model.model import build_text_model
        model = build_text_model(vocab_size=500, num_classes=10)
        dummy_seq = np.random.randint(0, 499, size=(4, 100))
        output = model.predict(dummy_seq, verbose=0)
        assert output.shape == (4, 10)


class TestPreprocessing:
    """Preprocessing utility tests (no data files required)."""

    def test_text_clean(self):
        from ml.text_model.preprocess import clean_text
        assert clean_text("  HELLO World!  ") == "hello world"
        assert clean_text("Pain in chest #123") == "pain in chest 123"
        assert clean_text("Multiple   spaces") == "multiple spaces"

    def test_cnn_preprocess_single_image(self):
        """Test that a synthetic image can be preprocessed."""
        from PIL import Image
        import io
        from ml.cnn.preprocess import preprocess_single_image

        # Create a synthetic 100x100 RGB image
        img = Image.new("RGB", (100, 100), color=(128, 128, 128))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        img_bytes = buf.getvalue()

        result = preprocess_single_image(img_bytes)
        assert result.shape == (1, 224, 224, 3)
        assert result.min() >= 0
        assert result.max() <= 1
