"""Pydantic schemas for prediction request/response bodies."""
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional


# ── Image (CNN — Pneumonia) ──────────────────────────────────────────────

class ImagePredictionResponse(BaseModel):
    """Response from the chest X-ray pneumonia prediction endpoint."""
    case_id: int
    prediction: str = Field(description="PNEUMONIA or NORMAL")
    confidence: float = Field(ge=0, le=1)
    gradcam_url: Optional[str] = Field(None, description="URL to Grad-CAM heatmap overlay")


# ── Tabular (ANN — Heart Disease) ────────────────────────────────────────

class TabularPredictionRequest(BaseModel):
    """Input features for heart disease risk prediction.

    All 13 features from the UCI Heart Disease dataset.
    """
    case_id: Optional[int] = None
    age: float
    sex: float = Field(description="0=female, 1=male")
    cp: float = Field(description="chest pain type (0-3)")
    trestbps: float = Field(description="resting blood pressure (mm Hg)")
    chol: float = Field(description="serum cholesterol (mg/dl)")
    fbs: float = Field(description="fasting blood sugar > 120 mg/dl (0/1)")
    restecg: float = Field(description="resting ECG results (0-2)")
    thalach: float = Field(description="max heart rate achieved")
    exang: float = Field(description="exercise induced angina (0/1)")
    oldpeak: float = Field(description="ST depression induced by exercise")
    slope: float = Field(description="slope of peak exercise ST segment (0-2)")
    ca: float = Field(description="number of major vessels coloured by fluoroscopy (0-3)")
    thal: float = Field(description="thalassemia (1=normal, 2=fixed defect, 3=reversible defect)")


class TabularPredictionResponse(BaseModel):
    """Response from the heart disease risk prediction endpoint."""
    case_id: int
    prediction: str = Field(description="HIGH_RISK or LOW_RISK")
    confidence: float = Field(ge=0, le=1)
    shap_values: Optional[dict[str, float]] = None
    shap_chart_url: Optional[str] = None


# ── Text (BiLSTM — Symptom Classification) ───────────────────────────────

class TextPredictionRequest(BaseModel):
    """Input for symptom-to-condition classification."""
    case_id: Optional[int] = None
    symptoms: str = Field(min_length=5, description="Free-text symptom description")


class TextPredictionResponse(BaseModel):
    """Response from the symptom classification endpoint."""
    case_id: int
    condition: str
    confidence: float = Field(ge=0, le=1)
    top_3: Optional[list[dict[str, float]]] = Field(
        None, description="Top 3 predicted conditions with confidence scores"
    )
