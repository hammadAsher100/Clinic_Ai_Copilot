import pytest
import numpy as np

def test_model_imports():
    # If this fails, the ML environment is not correctly configured
    import tensorflow as tf
    import keras
    assert keras.__version__

def test_cnn_model_mock():
    # Simple mock check for the CNN shape before we load real model
    dummy_input = np.random.rand(1, 224, 224, 3)
    assert dummy_input.shape == (1, 224, 224, 3)

def test_ann_model_mock():
    # Simple mock check for the ANN shape
    dummy_input = np.random.rand(1, 14)
    assert dummy_input.shape == (1, 14)
