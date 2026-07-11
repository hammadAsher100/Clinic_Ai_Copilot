"""Pydantic schemas for HITL (Human-in-the-Loop) decisions."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class HITLDecisionRequest(BaseModel):
    """Clinician decision on a single modality's prediction."""
    modality: str = Field(description="image, tabular, or text")
    action: str = Field(description="approve, reject, or edit")
    edited_value: Optional[str] = Field(
        None, description="New value if action is 'edit'"
    )


class HITLDecisionResponse(BaseModel):
    """Confirmation of a recorded HITL decision."""
    id: int
    case_id: int
    modality: str
    clinician_action: str
    original_value: Optional[str] = None
    edited_value: Optional[str] = None
    reviewer: Optional[str] = None
    timestamp: datetime

    model_config = {"from_attributes": True}


class CaseReviewResponse(BaseModel):
    """Full review data for the HITL dashboard."""
    case_id: int
    status: str
    predictions: list[dict] = []
    decisions: list[dict] = []
    llm_narrative: Optional[str] = None
