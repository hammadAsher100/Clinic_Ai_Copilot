"""
PDF service — handles both input-side document parsing and output-side
report generation.

Input:  Extract text/structured fields from uploaded clinical PDFs using pdfplumber.
Output: Assemble final downloadable report (findings + charts + LLM narrative +
        clinician sign-off) using reportlab.
"""
from __future__ import annotations

import io
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pdfplumber
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage,
    PageBreak, HRFlowable,
)

logger = logging.getLogger("api")

REPORTS_DIR = Path(os.getenv("REPORTS_DIR", "data/reports"))


# ═══════════════════════════════════════════════════════════════════════
# INPUT SIDE — PDF text extraction
# ═══════════════════════════════════════════════════════════════════════

def extract_pdf_text(file_bytes: bytes) -> dict:
    """Extract text and attempt structured field parsing from a PDF.

    Returns
    -------
    dict with keys: raw_text, pages, extracted_fields
    """
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages_text = []
            for page in pdf.pages:
                text = page.extract_text() or ""
                pages_text.append(text)

            full_text = "\n\n".join(pages_text)

            # Attempt basic field extraction
            extracted = _extract_fields(full_text)

            return {
                "raw_text": full_text,
                "num_pages": len(pages_text),
                "pages": pages_text,
                "extracted_fields": extracted,
            }

    except Exception as e:
        logger.error("PDF extraction failed: %s", e)
        return {
            "raw_text": "",
            "num_pages": 0,
            "pages": [],
            "extracted_fields": {},
            "error": str(e),
        }


def _extract_fields(text: str) -> dict:
    """Attempt to extract common clinical fields from raw text.

    This is a simple keyword-based extraction — sufficient for
    hackathon demo with synthetic PDFs.  Not a production NER system.
    """
    import re

    fields = {}
    text_lower = text.lower()

    # Patient name
    name_match = re.search(r"(?:patient\s*(?:name)?|name)\s*[:\-]\s*(.+)", text_lower)
    if name_match:
        fields["patient_name"] = name_match.group(1).strip().title()

    # Age
    age_match = re.search(r"age\s*[:\-]\s*(\d+)", text_lower)
    if age_match:
        fields["age"] = int(age_match.group(1))

    # Sex/Gender
    sex_match = re.search(r"(?:sex|gender)\s*[:\-]\s*(male|female|m|f)", text_lower)
    if sex_match:
        val = sex_match.group(1)
        fields["sex"] = "Male" if val in ("male", "m") else "Female"

    # Blood pressure
    bp_match = re.search(r"(?:bp|blood\s*pressure)\s*[:\-]\s*(\d+/\d+)", text_lower)
    if bp_match:
        fields["blood_pressure"] = bp_match.group(1)

    # Heart rate
    hr_match = re.search(r"(?:heart\s*rate|hr|pulse)\s*[:\-]\s*(\d+)", text_lower)
    if hr_match:
        fields["heart_rate"] = int(hr_match.group(1))

    # Diagnosis
    diag_match = re.search(r"(?:diagnosis|impression)\s*[:\-]\s*(.+)", text_lower)
    if diag_match:
        fields["diagnosis"] = diag_match.group(1).strip().capitalize()

    return fields


# ═══════════════════════════════════════════════════════════════════════
# OUTPUT SIDE — Report PDF generation
# ═══════════════════════════════════════════════════════════════════════

def generate_report(
    case_id: int,
    patient_info: Optional[dict] = None,
    predictions: Optional[list[dict]] = None,
    decisions: Optional[list[dict]] = None,
    llm_narrative: Optional[str] = None,
    gradcam_path: Optional[str] = None,
    shap_chart_path: Optional[str] = None,
) -> str:
    """Generate the final clinical report PDF.

    Returns
    -------
    str — file path to the generated PDF.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"clinical_report_case_{case_id}_{timestamp}.pdf"
    filepath = REPORTS_DIR / filename

    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontSize=18,
        spaceAfter=12,
        textColor=colors.HexColor("#0a0e27"),
    ))
    styles.add(ParagraphStyle(
        name="SectionHeader",
        parent=styles["Heading2"],
        fontSize=13,
        spaceAfter=6,
        textColor=colors.HexColor("#00a884"),
    ))
    styles.add(ParagraphStyle(
        name="NarrativeText",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        spaceAfter=8,
    ))

    elements = []

    # ── Title ────────────────────────────────────────────────────────────
    elements.append(Paragraph("Clinical AI Co-Pilot — Consolidated Report", styles["ReportTitle"]))
    elements.append(Paragraph(
        f"Case ID: {case_id} | Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        styles["Normal"],
    ))
    elements.append(Spacer(1, 8 * mm))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#00d4aa")))
    elements.append(Spacer(1, 4 * mm))

    # ── Patient Info ─────────────────────────────────────────────────────
    if patient_info:
        elements.append(Paragraph("Patient Information", styles["SectionHeader"]))
        info_data = [
            ["Name", patient_info.get("name", "Anonymous")],
            ["Age", str(patient_info.get("age", "N/A"))],
            ["Sex", patient_info.get("sex", "N/A")],
        ]
        info_table = Table(info_data, colWidths=[40 * mm, 120 * mm])
        info_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f0f0")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 6 * mm))

    # ── Model Predictions ────────────────────────────────────────────────
    if predictions:
        elements.append(Paragraph("Model Predictions", styles["SectionHeader"]))
        pred_data = [["Modality", "Prediction", "Confidence"]]
        for pred in predictions:
            pred_data.append([
                pred.get("modality", "").upper(),
                pred.get("prediction", "N/A"),
                f"{pred.get('confidence', 0):.1%}",
            ])
        pred_table = Table(pred_data, colWidths=[40 * mm, 60 * mm, 40 * mm])
        pred_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a0e27")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f8f8")]),
        ]))
        elements.append(pred_table)
        elements.append(Spacer(1, 6 * mm))

    # ── Explainability Images ────────────────────────────────────────────
    if gradcam_path and Path(gradcam_path).exists():
        elements.append(Paragraph("Chest X-Ray — Grad-CAM Heatmap", styles["SectionHeader"]))
        try:
            elements.append(RLImage(gradcam_path, width=80 * mm, height=80 * mm))
        except Exception:
            elements.append(Paragraph("[Grad-CAM image could not be embedded]", styles["Normal"]))
        elements.append(Spacer(1, 4 * mm))

    if shap_chart_path and Path(shap_chart_path).exists():
        elements.append(Paragraph("Heart Disease Risk — SHAP Feature Contributions", styles["SectionHeader"]))
        try:
            elements.append(RLImage(shap_chart_path, width=140 * mm, height=80 * mm))
        except Exception:
            elements.append(Paragraph("[SHAP chart could not be embedded]", styles["Normal"]))
        elements.append(Spacer(1, 4 * mm))

    # ── LLM Narrative ────────────────────────────────────────────────────
    if llm_narrative:
        elements.append(Paragraph("AI-Generated Clinical Narrative", styles["SectionHeader"]))
        elements.append(Paragraph(
            "<i>(Generated by LLM — reasoning/summarization only, not a diagnostic engine)</i>",
            styles["Normal"],
        ))
        elements.append(Spacer(1, 2 * mm))
        # Split narrative into paragraphs for proper formatting
        for para in llm_narrative.split("\n"):
            para = para.strip()
            if para:
                elements.append(Paragraph(para, styles["NarrativeText"]))
        elements.append(Spacer(1, 4 * mm))

    # ── Clinician Decisions ──────────────────────────────────────────────
    if decisions:
        elements.append(Paragraph("Clinician Review Decisions", styles["SectionHeader"]))
        dec_data = [["Modality", "Action", "Edited Value", "Reviewer"]]
        for dec in decisions:
            dec_data.append([
                dec.get("modality", "").upper(),
                dec.get("clinician_action", "N/A").upper(),
                dec.get("edited_value", "—") or "—",
                dec.get("reviewer", "—") or "—",
            ])
        dec_table = Table(dec_data, colWidths=[35 * mm, 30 * mm, 50 * mm, 40 * mm])
        dec_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a0e27")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(dec_table)
        elements.append(Spacer(1, 8 * mm))

    # ── Sign-off ─────────────────────────────────────────────────────────
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#00d4aa")))
    elements.append(Spacer(1, 4 * mm))
    elements.append(Paragraph(
        "This report was generated by the Clinical AI Co-Pilot system. "
        "All predictions were produced by dedicated deep-learning models (CNN, ANN, BiLSTM) "
        "and reviewed by a clinician through the Human-in-the-Loop workflow. "
        "The LLM-generated narrative is for summarization purposes only.",
        ParagraphStyle("Disclaimer", parent=styles["Normal"], fontSize=8, textColor=colors.grey),
    ))

    # Build PDF
    doc.build(elements)
    logger.info("Report generated: %s", filepath)

    return str(filepath)
