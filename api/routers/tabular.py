"""
Tabular prediction router — heart disease risk via ANN.

POST /api/v1/predict/tabular
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.db.models import Case, ModelPrediction, Modality, Patient, CaseStatus
from api.schemas.prediction import TabularPredictionRequest, TabularPredictionResponse
from api.schemas.common import ErrorResponse
from api.services import inference_service

router = APIRouter(prefix="/api/v1/predict", tags=["predictions"])
logger = logging.getLogger("prediction")


@router.post(
    "/tabular",
    response_model=TabularPredictionResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def predict_tabular(
    request: TabularPredictionRequest,
    db: Session = Depends(get_db),
) -> TabularPredictionResponse:
    """Assess heart disease risk from clinical features using the ANN model."""
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

        # Build features dict
        features = request.model_dump(exclude={"case_id"})

        # Run inference
        result = inference_service.predict_tabular(features)

        # Persist prediction
        from pathlib import Path
        shap_url = None
        if result.get("shap_chart_path"):
            shap_url = f"/static/uploads/{Path(result['shap_chart_path']).name}"

        prediction = ModelPrediction(
            case_id=case_id,
            modality=Modality.TABULAR,
            prediction=result["prediction"],
            confidence=result["confidence"],
            raw_output_json=result,
            explainability_ref=result.get("shap_chart_path"),
        )
        db.add(prediction)
        db.commit()

        logger.info(
            "TABULAR | case=%d | prediction=%s | confidence=%.3f",
            case_id, result["prediction"], result["confidence"],
        )

        return TabularPredictionResponse(
            case_id=case_id,
            prediction=result["prediction"],
            confidence=result["confidence"],
            shap_values=result.get("shap_values"),
            shap_chart_url=shap_url,
        )

    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error("Tabular prediction failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
