"""
Shared test fixtures for the Clinical AI Co-Pilot test suite.

Provides:
- In-memory SQLite test database
- FastAPI TestClient with mocked model loading
- Mock prediction results
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Set test environment BEFORE importing app modules
os.environ["DATABASE_URL"] = "sqlite:///./test_clinical.db"
os.environ["GROQ_API_KEY"] = ""
os.environ["MODEL_REGISTRY_PATH"] = "ml/registry"


@pytest.fixture(scope="session")
def test_engine():
    """Create an in-memory SQLite engine for tests."""
    engine = create_engine("sqlite:///./test_clinical.db", connect_args={"check_same_thread": False})
    from api.db.models import Base
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    # Cleanup test db file
    try:
        os.remove("test_clinical.db")
    except OSError:
        pass


@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    """Session factory bound to the test database."""
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture()
def db_session(test_session_factory):
    """Yield a fresh DB session per test, rolled back after."""
    session = test_session_factory()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="session")
def mock_models():
    """Mock all ML model loading so tests don't require real .h5 files."""
    mock_result_image = {
        "prediction": "PNEUMONIA",
        "confidence": 0.92,
        "gradcam_path": None,
    }
    mock_result_tabular = {
        "prediction": "HIGH_RISK",
        "confidence": 0.85,
        "shap_values": {"age": 0.15, "chol": 0.12, "thalach": -0.08},
        "shap_chart_path": None,
    }
    mock_result_text = {
        "condition": "Migraine",
        "confidence": 0.78,
        "top_3": [
            {"condition": "Migraine", "confidence": 0.78},
            {"condition": "Hypertension", "confidence": 0.12},
            {"condition": "Anxiety", "confidence": 0.05},
        ],
    }

    return {
        "image": mock_result_image,
        "tabular": mock_result_tabular,
        "text": mock_result_text,
    }


@pytest.fixture(scope="session")
def client(test_engine, mock_models):
    """FastAPI TestClient with mocked model loading and test DB."""
    from api.db.models import Base
    from api.db.session import get_db

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Patch model loading and inference
    with patch("api.services.inference_service.load_all_models"):
        with patch("api.services.inference_service._models_loaded", True):
            with patch("api.services.inference_service.predict_image", return_value=mock_models["image"]):
                with patch("api.services.inference_service.predict_tabular", return_value=mock_models["tabular"]):
                    with patch("api.services.inference_service.predict_text", return_value=mock_models["text"]):
                        from api.main import app
                        app.dependency_overrides[get_db] = override_get_db

                        with TestClient(app) as c:
                            yield c

                        app.dependency_overrides.clear()


@pytest.fixture()
def auth_token(client) -> str:
    """Get a valid JWT token for authenticated requests."""
    response = client.post("/api/v1/auth/login", json={
        "username": "clinician",
        "password": "demo2026",
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture()
def auth_headers(auth_token) -> dict:
    """Authorization headers with Bearer token."""
    return {"Authorization": f"Bearer {auth_token}"}
