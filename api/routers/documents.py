"""
Document router — PDF upload, text extraction, and case attachment.

POST /api/v1/documents/extract
"""
from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.db.models import Case, Patient, CaseStatus
from api.services.pdf_service import extract_pdf_text

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
logger = logging.getLogger("api")


@router.post("/extract")
async def extract_document(
    file: UploadFile = File(..., description="Clinical PDF document"),
    case_id: int | None = Form(None),
    patient_name: str = Form("Anonymous"),
    db: Session = Depends(get_db),
) -> dict:
    """Upload a PDF, extract text and structured fields, attach to case."""
    if file.content_type and file.content_type not in (
        "application/pdf",
        "application/octet-stream",
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Please upload a PDF.",
        )

    try:
        pdf_bytes = await file.read()
        if len(pdf_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")

        # Save uploaded PDF
        upload_dir = Path(os.getenv("UPLOAD_DIR", "data/uploads"))
        upload_dir.mkdir(parents=True, exist_ok=True)
        fname = f"doc_{uuid.uuid4().hex[:8]}_{file.filename}"
        upload_path = upload_dir / fname
        with open(upload_path, "wb") as f:
            f.write(pdf_bytes)

        # Extract text
        extraction = extract_pdf_text(pdf_bytes)

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

        db.commit()

        logger.info(
            "DOCUMENT | case=%d | pages=%d | fields=%s",
            case_id,
            extraction.get("num_pages", 0),
            list(extraction.get("extracted_fields", {}).keys()),
        )

        return {
            "case_id": case_id,
            "filename": file.filename,
            "num_pages": extraction.get("num_pages", 0),
            "raw_text": extraction.get("raw_text", "")[:2000],  # Trim for response
            "extracted_fields": extraction.get("extracted_fields", {}),
            "message": "Document extracted and attached to case successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Document extraction failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Extraction failed: {e}")
