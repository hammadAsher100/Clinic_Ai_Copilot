"""
HITL (Human-in-the-Loop) router — clinician review and decision recording.

GET  /api/v1/cases/{case_id}/review  — fetch all findings for review
POST /api/v1/cases/{case_id}/decision — record approve/reject/edit
GET  /api/v1/cases — list all cases
POST /api/v1/cases — create a new case
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.db.models import (
    Case, ModelPrediction, HITLDecision, Patient,
    CaseStatus, Modality, ClinicianAction,
)
from api.schemas.case import CaseCreate, CaseResponse, CaseDetailResponse, PredictionSummary
from api.schemas.hitl import HITLDecisionRequest, HITLDecisionResponse
from api.schemas.common import ErrorResponse

router = APIRouter(prefix="/api/v1/cases", tags=["hitl"])
logger = logging.getLogger("hitl")


@router.post(
    "",
    response_model=CaseResponse,
    status_code=201,
)
async def create_case(
    request: CaseCreate,
    db: Session = Depends(get_db),
) -> CaseResponse:
    """Create a new clinical case."""
    patient = Patient(
        name=request.patient_name,
        age=request.patient_age,
        sex=request.patient_sex,
    )
    db.add(patient)
    db.flush()

    case = Case(patient_id=patient.id, status=CaseStatus.PENDING)
    db.add(case)
    db.commit()
    db.refresh(case)

    logger.info("Case created: id=%d, patient=%s", case.id, request.patient_name)
    return CaseResponse(
        id=case.id,
        patient_id=patient.id,
        status=case.status.value,
        created_at=case.created_at,
    )


@router.get("", response_model=list[CaseResponse])
async def list_cases(db: Session = Depends(get_db)) -> list[CaseResponse]:
    """List all clinical cases."""
    cases = db.query(Case).order_by(Case.created_at.desc()).all()
    return [
        CaseResponse(
            id=c.id,
            patient_id=c.patient_id,
            status=c.status.value,
            created_at=c.created_at,
        )
        for c in cases
    ]


@router.get(
    "/{case_id}/review",
    response_model=CaseDetailResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_case_review(
    case_id: int,
    db: Session = Depends(get_db),
) -> CaseDetailResponse:
    """Get all findings for a case — used by the HITL review dashboard."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    # Fetch predictions
    predictions = db.query(ModelPrediction).filter(
        ModelPrediction.case_id == case_id
    ).all()

    pred_summaries = []
    for p in predictions:
        explainability_url = None
        if p.explainability_ref:
            from pathlib import Path
            explainability_url = f"/static/uploads/{Path(p.explainability_ref).name}"

        pred_summaries.append(PredictionSummary(
            modality=p.modality.value,
            prediction=p.prediction,
            confidence=p.confidence,
            explainability_ref=explainability_url,
            raw_output=p.raw_output_json,
        ))

    # Fetch existing decisions
    decisions = db.query(HITLDecision).filter(
        HITLDecision.case_id == case_id
    ).all()

    dec_list = [
        {
            "modality": d.modality.value,
            "clinician_action": d.clinician_action.value,
            "original_value": d.original_value,
            "edited_value": d.edited_value,
            "reviewer": d.reviewer,
            "timestamp": d.timestamp.isoformat() if d.timestamp else None,
        }
        for d in decisions
    ]

    # Patient info
    patient_name = case.patient.name if case.patient else None
    patient_age = case.patient.age if case.patient else None
    patient_sex = case.patient.sex if case.patient else None

    return CaseDetailResponse(
        id=case.id,
        status=case.status.value,
        patient_name=patient_name,
        patient_age=patient_age,
        patient_sex=patient_sex,
        predictions=pred_summaries,
        llm_narrative=case.llm_narrative,
        decisions=dec_list,
        created_at=case.created_at,
    )


@router.post(
    "/{case_id}/decision",
    response_model=HITLDecisionResponse,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def record_decision(
    case_id: int,
    request: HITLDecisionRequest,
    db: Session = Depends(get_db),
) -> HITLDecisionResponse:
    """Record a clinician's approve/reject/edit decision for a modality."""
    # Validate case exists
    case = db.query(Case).filter(Case.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    # Validate modality
    try:
        modality = Modality(request.modality)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid modality '{request.modality}'. Must be: image, tabular, text",
        )

    # Validate action
    try:
        action = ClinicianAction(request.action)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action '{request.action}'. Must be: approve, reject, edit",
        )

    # Get original prediction value
    pred = db.query(ModelPrediction).filter(
        ModelPrediction.case_id == case_id,
        ModelPrediction.modality == modality,
    ).first()

    original_value = pred.prediction if pred else None

    # Require edited_value for edit actions
    if action == ClinicianAction.EDIT and not request.edited_value:
        raise HTTPException(status_code=400, detail="edited_value required for 'edit' action")

    # Record decision
    decision = HITLDecision(
        case_id=case_id,
        modality=modality,
        clinician_action=action,
        original_value=original_value,
        edited_value=request.edited_value,
        reviewer="clinician",  # From JWT in production
    )
    db.add(decision)

    # Update case status
    case.status = CaseStatus.IN_REVIEW
    db.commit()
    db.refresh(decision)

    logger.info(
        "HITL | case=%d | modality=%s | action=%s | original=%s | edited=%s",
        case_id, modality.value, action.value, original_value, request.edited_value,
    )

    return HITLDecisionResponse(
        id=decision.id,
        case_id=case_id,
        modality=decision.modality.value,
        clinician_action=decision.clinician_action.value,
        original_value=decision.original_value,
        edited_value=decision.edited_value,
        reviewer=decision.reviewer,
        timestamp=decision.timestamp,
    )
