"""
LLM Co-Pilot router — generates clinical narrative from structured model outputs.

POST /api/v1/copilot/summarize

╔══════════════════════════════════════════════════════════════════════╗
║  This endpoint performs REASONING / SUMMARIZATION ONLY.             ║
║  It receives already-computed predictions from the CNN, ANN, and    ║
║  BiLSTM models and asks the LLM to generate a plain-language       ║
║  clinical narrative.  The LLM is NEVER the diagnostic engine.      ║
╚══════════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.db.models import Case, ModelPrediction, CaseStatus
from api.schemas.common import ErrorResponse
from api.services import llm_service

router = APIRouter(prefix="/api/v1/copilot", tags=["llm-copilot"])
logger = logging.getLogger("api")


class SummarizeRequest(BaseModel):
    """Request body: just the case ID — predictions are fetched from DB."""
    case_id: int


class SummarizeResponse(BaseModel):
    """The LLM-generated clinical narrative."""
    case_id: int
    narrative: str


@router.post(
    "/summarize",
    response_model=SummarizeResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def summarize_case(
    request: SummarizeRequest,
    db: Session = Depends(get_db),
) -> SummarizeResponse:
    """Generate a plain-language clinical narrative for a case.

    Fetches the three structured prediction outputs from the database
    and sends them (NOT raw patient data) to the LLM for summarization.
    """
    case = db.query(Case).filter(Case.id == request.case_id).first()
    if case is None:
        raise HTTPException(status_code=400, detail=f"Case {request.case_id} not found")

    predictions = db.query(ModelPrediction).filter(
        ModelPrediction.case_id == request.case_id
    ).all()

    if not predictions:
        raise HTTPException(
            status_code=400,
            detail="No predictions found for this case — run predictions first",
        )

    # Build structured results from DB records
    image_result = None
    tabular_result = None
    text_result = None

    for pred in predictions:
        raw = pred.raw_output_json or {}
        if pred.modality.value == "image":
            image_result = raw
        elif pred.modality.value == "tabular":
            tabular_result = raw
        elif pred.modality.value == "text":
            text_result = raw

    # Get patient info
    patient_info = None
    if case.patient:
        patient_info = {
            "name": case.patient.name,
            "age": case.patient.age,
            "sex": case.patient.sex,
        }

    try:
        # Call LLM for narrative generation (reasoning/summarization only)
        narrative = await llm_service.generate_narrative(
            image_result=image_result,
            tabular_result=tabular_result,
            text_result=text_result,
            patient_info=patient_info,
        )

        # Persist narrative to case
        case.llm_narrative = narrative
        case.status = CaseStatus.IN_REVIEW
        db.commit()

        logger.info("LLM narrative generated for case %d (%d chars)", request.case_id, len(narrative))

        return SummarizeResponse(
            case_id=request.case_id,
            narrative=narrative,
        )

    except Exception as e:
        logger.error("LLM summarization failed for case %d: %s", request.case_id, e)
        raise HTTPException(status_code=500, detail=f"Narrative generation failed: {e}")
