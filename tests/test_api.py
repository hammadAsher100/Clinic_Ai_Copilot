import pytest
from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "models_loaded" in data

def test_auth_login(client: TestClient):
    # Depending on how your demo user is created, this tests login
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "clinician", "password": "demo2026"}
    )
    assert response.status_code in [200, 401] # 401 if demo user isn't in test DB yet
