"""
API router tests — validates endpoints with mocked model outputs.

Tests cover: health check, auth, predictions (all 3 modalities),
HITL decision flow, and report generation.
"""
from __future__ import annotations

import io
import pytest


class TestHealthCheck:
    """Health check endpoint tests."""

    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestAuth:
    """Authentication endpoint tests."""

    def test_login_success(self, client):
        response = client.post("/api/v1/auth/login", json={
            "username": "clinician",
            "password": "demo2026",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        response = client.post("/api/v1/auth/login", json={
            "username": "clinician",
            "password": "wrong",
        })
        assert response.status_code == 401

    def test_login_unknown_user(self, client):
        response = client.post("/api/v1/auth/login", json={
            "username": "nobody",
            "password": "test",
        })
        assert response.status_code == 401

    def test_get_me_authenticated(self, client, auth_headers):
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "clinician"
        assert data["role"] == "clinician"

    def test_get_me_unauthenticated(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401


class TestCases:
    """Case management endpoint tests."""

    def test_create_case(self, client, auth_headers):
        response = client.post("/api/v1/cases", json={
            "patient_name": "Test Patient",
            "patient_age": 55,
            "patient_sex": "Male",
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["id"] > 0
        assert data["status"] == "pending"

    def test_list_cases(self, client, auth_headers):
        # Create a case first
        client.post("/api/v1/cases", json={"patient_name": "List Test"}, headers=auth_headers)
        response = client.get("/api/v1/cases", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0


class TestPredictions:
    """Prediction endpoint tests with mocked models."""

    def test_predict_tabular(self, client, auth_headers):
        response = client.post("/api/v1/predict/tabular", json={
            "age": 55, "sex": 1, "cp": 2, "trestbps": 130, "chol": 250,
            "fbs": 0, "restecg": 0, "thalach": 150, "exang": 0,
            "oldpeak": 1.5, "slope": 1, "ca": 0, "thal": 2,
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["prediction"] in ("HIGH_RISK", "LOW_RISK")
        assert 0 <= data["confidence"] <= 1
        assert data["case_id"] > 0

    def test_predict_text(self, client, auth_headers):
        response = client.post("/api/v1/predict/text", json={
            "symptoms": "I have been experiencing severe headaches and blurred vision for two weeks",
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "condition" in data
        assert 0 <= data["confidence"] <= 1
        assert data["case_id"] > 0

    def test_predict_text_too_short(self, client, auth_headers):
        response = client.post("/api/v1/predict/text", json={
            "symptoms": "hi",
        }, headers=auth_headers)
        assert response.status_code == 422  # Pydantic validation

    def test_predict_image(self, client, auth_headers):
        # Create a minimal PNG-like bytes (1x1 white pixel PNG)
        png_bytes = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00'
            b'\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00'
            b'\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        response = client.post(
            "/api/v1/predict/image",
            files={"file": ("test.png", io.BytesIO(png_bytes), "image/png")},
            data={"patient_name": "Test"},
            headers={"Authorization": auth_headers["Authorization"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["prediction"] in ("PNEUMONIA", "NORMAL")
        assert 0 <= data["confidence"] <= 1


class TestHITL:
    """Human-in-the-Loop decision flow tests."""

    def _create_case_with_prediction(self, client, auth_headers) -> int:
        """Helper: create a case and add a tabular prediction."""
        response = client.post("/api/v1/predict/tabular", json={
            "age": 55, "sex": 1, "cp": 2, "trestbps": 130, "chol": 250,
            "fbs": 0, "restecg": 0, "thalach": 150, "exang": 0,
            "oldpeak": 1.5, "slope": 1, "ca": 0, "thal": 2,
        }, headers=auth_headers)
        return response.json()["case_id"]

    def test_get_case_review(self, client, auth_headers):
        case_id = self._create_case_with_prediction(client, auth_headers)
        response = client.get(f"/api/v1/cases/{case_id}/review", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == case_id
        assert len(data["predictions"]) > 0

    def test_approve_decision(self, client, auth_headers):
        case_id = self._create_case_with_prediction(client, auth_headers)
        response = client.post(f"/api/v1/cases/{case_id}/decision", json={
            "modality": "tabular",
            "action": "approve",
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["clinician_action"] == "approve"

    def test_edit_decision(self, client, auth_headers):
        case_id = self._create_case_with_prediction(client, auth_headers)
        response = client.post(f"/api/v1/cases/{case_id}/decision", json={
            "modality": "tabular",
            "action": "edit",
            "edited_value": "LOW_RISK",
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["clinician_action"] == "edit"
        assert data["edited_value"] == "LOW_RISK"

    def test_edit_without_value_fails(self, client, auth_headers):
        case_id = self._create_case_with_prediction(client, auth_headers)
        response = client.post(f"/api/v1/cases/{case_id}/decision", json={
            "modality": "tabular",
            "action": "edit",
        }, headers=auth_headers)
        assert response.status_code == 400

    def test_invalid_modality_fails(self, client, auth_headers):
        case_id = self._create_case_with_prediction(client, auth_headers)
        response = client.post(f"/api/v1/cases/{case_id}/decision", json={
            "modality": "invalid",
            "action": "approve",
        }, headers=auth_headers)
        assert response.status_code == 400

    def test_case_not_found(self, client, auth_headers):
        response = client.get("/api/v1/cases/99999/review", headers=auth_headers)
        assert response.status_code == 404


class TestReports:
    """Report generation and download tests."""

    def test_report_status_not_ready(self, client, auth_headers):
        # Create case
        resp = client.post("/api/v1/cases", json={"patient_name": "Report Test"}, headers=auth_headers)
        case_id = resp.json()["id"]

        response = client.get(f"/api/v1/cases/{case_id}/report/status", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is False

    def test_generate_report_no_predictions(self, client, auth_headers):
        resp = client.post("/api/v1/cases", json={"patient_name": "Empty"}, headers=auth_headers)
        case_id = resp.json()["id"]

        response = client.post(f"/api/v1/cases/{case_id}/generate-report", headers=auth_headers)
        assert response.status_code == 400

    def test_generate_and_download_report(self, client, auth_headers):
        # Create case with prediction
        pred_resp = client.post("/api/v1/predict/tabular", json={
            "age": 55, "sex": 1, "cp": 2, "trestbps": 130, "chol": 250,
            "fbs": 0, "restecg": 0, "thalach": 150, "exang": 0,
            "oldpeak": 1.5, "slope": 1, "ca": 0, "thal": 2,
        }, headers=auth_headers)
        case_id = pred_resp.json()["case_id"]

        # Generate report
        gen_resp = client.post(f"/api/v1/cases/{case_id}/generate-report", headers=auth_headers)
        assert gen_resp.status_code == 200
        assert gen_resp.json()["status"] == "completed"

        # Check status
        status_resp = client.get(f"/api/v1/cases/{case_id}/report/status", headers=auth_headers)
        assert status_resp.json()["ready"] is True

        # Download
        dl_resp = client.get(f"/api/v1/cases/{case_id}/report/download", headers=auth_headers)
        assert dl_resp.status_code == 200
        assert dl_resp.headers["content-type"] == "application/pdf"
