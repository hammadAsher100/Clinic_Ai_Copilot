"""Pydantic schemas for case management."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CaseCreate(BaseModel):
    """Request body to create a new clinical case."""
    patient_name: str = Field(default="Anonymous")
    patient_age: Optional[int] = None
    patient_sex: Optional[str] = None


class CaseResponse(BaseModel):
    """Basic case info returned on creation."""
    id: int
    patient_id: Optional[int] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PredictionSummary(BaseModel):
    """Summary of a single model prediction for the review page."""
    modality: str
    prediction: str
    confidence: float
    explainability_ref: Optional[str] = None
    raw_output: Optional[dict] = None


class CaseDetailResponse(BaseModel):
    """Full case details for the HITL review page."""
    id: int
    status: str
    patient_name: Optional[str] = None
    patient_age: Optional[int] = None
    patient_sex: Optional[str] = None
    predictions: list[PredictionSummary] = []
    llm_narrative: Optional[str] = None
    decisions: list[dict] = []
    created_at: datetime

    model_config = {"from_attributes": True}
