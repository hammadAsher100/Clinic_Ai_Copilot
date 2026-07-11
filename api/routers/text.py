"""
Text prediction router — symptom-to-condition classification via BiLSTM.

POST /api/v1/predict/text
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.db.models import Case, ModelPrediction, Modality, Patient, CaseStatus
from api.schemas.prediction import TextPredictionRequest, TextPredictionResponse
from api.schemas.common import ErrorResponse
from api.services import inference_service

router = APIRouter(prefix="/api/v1/predict", tags=["predictions"])
logger = logging.getLogger("prediction")


@router.post(
    "/text",
    response_model=TextPredictionResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def predict_text(
    request: TextPredictionRequest,
    db: Session = Depends(get_db),
) -> TextPredictionResponse:
    """Classify likely condition from symptom description using the BiLSTM model."""
    try:
        # Create or fetch case
        case_id = request.case_id
        if case_id is None:
            patient = Patient(name="Anonymous")
            db.add(patient)
            db.flush()
            case = Case(patient_id=patient.id, status=CaseStatus.PENDING)
            db.add(case)
            db.flush()
            case_id = case.id
        else:
            case = db.query(Case).filter(Case.id == case_id).first()
            if case is None:
                raise HTTPException(status_code=400, detail=f"Case {case_id} not found")

        # Run inference
        result = inference_service.predict_text(request.symptoms)

        # Persist prediction
        prediction = ModelPrediction(
            case_id=case_id,
            modality=Modality.TEXT,
            prediction=result["condition"],
            confidence=result["confidence"],
            raw_output_json=result,
        )
        db.add(prediction)
        db.commit()

        logger.info(
            "TEXT | case=%d | condition=%s | confidence=%.3f",
            case_id, result["condition"], result["confidence"],
        )

        return TextPredictionResponse(
            case_id=case_id,
            condition=result["condition"],
            confidence=result["confidence"],
            top_3=result.get("top_3"),
        )

    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error("Text prediction failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
