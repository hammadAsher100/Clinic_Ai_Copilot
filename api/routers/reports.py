"""
Reports router — PDF report generation and download.

POST /api/v1/cases/{case_id}/generate-report
GET  /api/v1/cases/{case_id}/report/download
"""
from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.db.models import Case, ModelPrediction, HITLDecision, Report, CaseStatus
from api.schemas.report import ReportGenerateResponse, ReportStatusResponse
from api.schemas.common import ErrorResponse
from api.services import pdf_service

router = APIRouter(prefix="/api/v1/cases", tags=["reports"])
logger = logging.getLogger("api")


@router.post(
    "/{case_id}/generate-report",
    response_model=ReportGenerateResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def generate_report(
    case_id: int,
    db: Session = Depends(get_db),
) -> ReportGenerateResponse:
    """Generate the final clinical report PDF after HITL review."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    # Fetch predictions
    predictions = db.query(ModelPrediction).filter(
        ModelPrediction.case_id == case_id
    ).all()

    if not predictions:
        raise HTTPException(
            status_code=400,
            detail="No predictions found — run predictions before generating report",
        )

    # Fetch decisions
    decisions = db.query(HITLDecision).filter(
        HITLDecision.case_id == case_id
    ).all()

    # Build data for PDF
    patient_info = None
    if case.patient:
        patient_info = {
            "name": case.patient.name,
            "age": case.patient.age,
            "sex": case.patient.sex,
        }

    pred_list = [
        {
            "modality": p.modality.value,
            "prediction": p.prediction,
            "confidence": p.confidence,
        }
        for p in predictions
    ]

    dec_list = [
        {
            "modality": d.modality.value,
            "clinician_action": d.clinician_action.value,
            "edited_value": d.edited_value,
            "reviewer": d.reviewer,
        }
        for d in decisions
    ]

    # Find explainability artifacts
    gradcam_path = None
    shap_chart_path = None
    for p in predictions:
        if p.modality.value == "image" and p.explainability_ref:
            gradcam_path = p.explainability_ref
        elif p.modality.value == "tabular" and p.explainability_ref:
            shap_chart_path = p.explainability_ref

    try:
        filepath = pdf_service.generate_report(
            case_id=case_id,
            patient_info=patient_info,
            predictions=pred_list,
            decisions=dec_list,
            llm_narrative=case.llm_narrative,
            gradcam_path=gradcam_path,
            shap_chart_path=shap_chart_path,
        )

        # Persist report record
        report = Report(case_id=case_id, file_path=filepath)
        db.add(report)

        case.status = CaseStatus.COMPLETED
        db.commit()
        db.refresh(report)

        logger.info("Report generated for case %d: %s", case_id, filepath)

        return ReportGenerateResponse(
            case_id=case_id,
            status="completed",
            message="Report generated successfully",
            report_id=report.id,
        )

    except Exception as e:
        logger.error("Report generation failed for case %d: %s", case_id, e)
        raise HTTPException(status_code=500, detail=f"Report generation failed: {e}")


@router.get(
    "/{case_id}/report/download",
    responses={404: {"model": ErrorResponse}},
)
async def download_report(
    case_id: int,
    db: Session = Depends(get_db),
) -> FileResponse:
    """Download the generated report PDF."""
    report = db.query(Report).filter(
        Report.case_id == case_id
    ).order_by(Report.generated_at.desc()).first()

    if report is None:
        raise HTTPException(status_code=404, detail="No report found — generate one first")

    filepath = Path(report.file_path)
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Report file not found on disk")

    return FileResponse(
        path=str(filepath),
        media_type="application/pdf",
        filename=filepath.name,
    )


@router.get(
    "/{case_id}/report/status",
    response_model=ReportStatusResponse,
)
async def report_status(
    case_id: int,
    db: Session = Depends(get_db),
) -> ReportStatusResponse:
    """Check if a report exists for download."""
    report = db.query(Report).filter(
        Report.case_id == case_id
    ).order_by(Report.generated_at.desc()).first()

    if report is None:
        return ReportStatusResponse(case_id=case_id, ready=False)

    return ReportStatusResponse(
        case_id=case_id,
        ready=True,
        download_url=f"/api/v1/cases/{case_id}/report/download",
        generated_at=report.generated_at,
    )
