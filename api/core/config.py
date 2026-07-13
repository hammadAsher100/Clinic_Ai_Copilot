"""
Centralised application configuration via Pydantic BaseSettings.

All config is loaded from environment variables / .env file.
Import the singleton ``settings`` object throughout the app.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings — loaded from .env automatically."""
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
        "protected_namespaces": ()  # Allow "model_" prefix in field names
    }

    # ── Database ─────────────────────────────────────────────────────────
    database_url: str = "sqlite:///./clinical_copilot.db"

    # ── MLflow ───────────────────────────────────────────────────────────
    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_experiment_name: str = "clinical-copilot"

    # ── Model registry paths ─────────────────────────────────────────────
    cnn_model_path: str = "ml/registry/cnn_pneumonia.h5"
    ann_model_path: str = "ml/registry/ann_heart_risk.h5"
    text_model_path: str = "ml/registry/text_triage.h5"
    text_tokenizer_path: str = "ml/registry/tokenizer.pkl"
    model_registry_path: str = "ml/registry"

    # ── LLM API (Groq — reasoning/summarization only) ───────────────────
    groq_api_key: str = ""
    groq_api_base_url: str = "https://api.groq.com/openai/v1"
    groq_model: str = "llama-3.3-70b-versatile"

    # ── Auth ─────────────────────────────────────────────────────────────
    jwt_secret_key: str = "changeme-generate-a-real-random-secret"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 480  # 8 hours

    # ── API ──────────────────────────────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # ── File paths ───────────────────────────────────────────────────────
    upload_dir: str = "data/uploads"
    reports_dir: str = "data/reports"


@lru_cache()
def get_settings() -> Settings:
    """Return the singleton Settings instance."""
    return Settings()


settings = get_settings()
