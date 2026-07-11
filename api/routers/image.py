"""
Image prediction router — chest X-ray pneumonia detection via CNN.

POST /api/v1/predict/image
"""
from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.db.models import Case, ModelPrediction, Modality, Patient, CaseStatus
from api.schemas.prediction import ImagePredictionResponse
from api.schemas.common import ErrorResponse
from api.services import inference_service

router = APIRouter(prefix="/api/v1/predict", tags=["predictions"])
logger = logging.getLogger("prediction")


@router.post(
    "/image",
    response_model=ImagePredictionResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def predict_image(
    file: UploadFile = File(..., description="Chest X-ray image (jpg/png)"),
    case_id: int | None = Form(None, description="Existing case ID, or create new"),
    patient_name: str = Form("Anonymous"),
    db: Session = Depends(get_db),
) -> ImagePredictionResponse:
    """Classify a chest X-ray as PNEUMONIA or NORMAL using the CNN model."""
    # Validate file type
    if file.content_type and file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(status_code=400, detail=f"Unsupported image type: {file.content_type}")

    try:
        image_bytes = await file.read()
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")

        # Save uploaded file
        upload_dir = Path(os.getenv("UPLOAD_DIR", "data/uploads"))
        upload_dir.mkdir(parents=True, exist_ok=True)
        fname = f"xray_{uuid.uuid4().hex[:8]}_{file.filename}"
        upload_path = upload_dir / fname
        with open(upload_path, "wb") as f:
            f.write(image_bytes)

        # Create or fetch case
        if case_id is None:
            patient = Patient(name=patient_name)
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
        result = inference_service.predict_image(image_bytes)

        # Persist prediction
        gradcam_url = None
        if result.get("gradcam_path"):
            gradcam_url = f"/static/uploads/{Path(result['gradcam_path']).name}"

        prediction = ModelPrediction(
            case_id=case_id,
            modality=Modality.IMAGE,
            prediction=result["prediction"],
            confidence=result["confidence"],
            raw_output_json=result,
            explainability_ref=result.get("gradcam_path"),
        )
        db.add(prediction)
        db.commit()

        logger.info(
            "IMAGE | case=%d | prediction=%s | confidence=%.3f",
            case_id, result["prediction"], result["confidence"],
        )

        return ImagePredictionResponse(
            case_id=case_id,
            prediction=result["prediction"],
            confidence=result["confidence"],
            gradcam_url=gradcam_url,
        )

    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error("Image prediction failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
