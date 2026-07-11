"""
Generate synthetic clinical PDF samples for demo/testing.

Creates 3 sample documents:
1. Discharge summary
2. Lab report
3. Clinical note

These are used for the PDF upload/extraction feature demo.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "pdf_samples"


def create_discharge_summary() -> None:
    """Generate a synthetic discharge summary PDF."""
    filepath = OUTPUT_DIR / "sample_discharge_summary.pdf"
    doc = SimpleDocTemplate(str(filepath), pagesize=A4)
    styles = getSampleStyleSheet()

    elements = [
        Paragraph("DISCHARGE SUMMARY", styles["Title"]),
        Spacer(1, 6 * mm),
        Paragraph("Patient Name: John Smith", styles["Normal"]),
        Paragraph("Age: 62", styles["Normal"]),
        Paragraph("Sex: Male", styles["Normal"]),
        Paragraph(f"Date of Discharge: {datetime.now().strftime('%Y-%m-%d')}", styles["Normal"]),
        Spacer(1, 6 * mm),
        Paragraph("Diagnosis: Community-acquired pneumonia, right lower lobe", styles["Heading2"]),
        Spacer(1, 4 * mm),
        Paragraph(
            "The patient was admitted with a 5-day history of productive cough, fever (38.7°C), "
            "and progressive shortness of breath. Chest X-ray on admission revealed consolidation "
            "in the right lower lobe consistent with pneumonia. Blood cultures were negative. "
            "The patient was treated with IV ceftriaxone and azithromycin for 5 days, "
            "then transitioned to oral amoxicillin-clavulanate.",
            styles["Normal"],
        ),
        Spacer(1, 4 * mm),
        Paragraph("Vitals on Discharge:", styles["Heading3"]),
        Paragraph("Blood Pressure: 128/78 mmHg", styles["Normal"]),
        Paragraph("Heart Rate: 76 bpm", styles["Normal"]),
        Paragraph("Temperature: 36.8°C", styles["Normal"]),
        Paragraph("SpO2: 97% on room air", styles["Normal"]),
        Spacer(1, 4 * mm),
        Paragraph("Medications on Discharge:", styles["Heading3"]),
        Paragraph("1. Amoxicillin-clavulanate 875/125 mg PO BID x 5 days", styles["Normal"]),
        Paragraph("2. Acetaminophen 500 mg PRN for pain/fever", styles["Normal"]),
        Paragraph("3. Continue home medications (atorvastatin 40 mg daily, lisinopril 10 mg daily)", styles["Normal"]),
        Spacer(1, 4 * mm),
        Paragraph("Follow-up: Pulmonology clinic in 2 weeks. Repeat chest X-ray in 6 weeks.", styles["Normal"]),
    ]

    doc.build(elements)
    print(f"  [OK] Created: {filepath.name}")


def create_lab_report() -> None:
    """Generate a synthetic lab report PDF."""
    filepath = OUTPUT_DIR / "sample_lab_report.pdf"
    doc = SimpleDocTemplate(str(filepath), pagesize=A4)
    styles = getSampleStyleSheet()

    lab_data = [
        ["Test", "Result", "Reference Range", "Flag"],
        ["WBC", "12.4 x10³/µL", "4.5-11.0", "HIGH"],
        ["RBC", "4.8 x10⁶/µL", "4.5-5.5", ""],
        ["Hemoglobin", "14.2 g/dL", "13.5-17.5", ""],
        ["Hematocrit", "42%", "38-50", ""],
        ["Platelets", "245 x10³/µL", "150-400", ""],
        ["Glucose (fasting)", "142 mg/dL", "70-100", "HIGH"],
        ["Total Cholesterol", "268 mg/dL", "<200", "HIGH"],
        ["LDL", "165 mg/dL", "<100", "HIGH"],
        ["HDL", "42 mg/dL", ">40", ""],
        ["Triglycerides", "198 mg/dL", "<150", "HIGH"],
        ["Creatinine", "1.1 mg/dL", "0.7-1.3", ""],
        ["BUN", "18 mg/dL", "7-20", ""],
    ]

    lab_table = Table(lab_data, colWidths=[50 * mm, 35 * mm, 40 * mm, 20 * mm])
    lab_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
        ("TEXTCOLOR", (3, 1), (3, -1), colors.red),
    ]))

    elements = [
        Paragraph("LABORATORY REPORT", styles["Title"]),
        Spacer(1, 4 * mm),
        Paragraph("Patient Name: Sarah Johnson", styles["Normal"]),
        Paragraph("Age: 55", styles["Normal"]),
        Paragraph("Sex: Female", styles["Normal"]),
        Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", styles["Normal"]),
        Paragraph("Ordering Physician: Dr. Martinez", styles["Normal"]),
        Spacer(1, 8 * mm),
        Paragraph("Complete Blood Count & Metabolic Panel", styles["Heading2"]),
        Spacer(1, 4 * mm),
        lab_table,
        Spacer(1, 6 * mm),
        Paragraph(
            "Impression: Elevated WBC suggesting possible infection. Elevated glucose and lipid "
            "panel suggest metabolic syndrome. Recommend fasting glucose retest and HbA1c. "
            "Consider statin therapy adjustment.",
            styles["Normal"],
        ),
    ]

    doc.build(elements)
    print(f"  [OK] Created: {filepath.name}")


def create_clinical_note() -> None:
    """Generate a synthetic clinical note PDF."""
    filepath = OUTPUT_DIR / "sample_clinical_note.pdf"
    doc = SimpleDocTemplate(str(filepath), pagesize=A4)
    styles = getSampleStyleSheet()

    elements = [
        Paragraph("CLINICAL NOTE", styles["Title"]),
        Spacer(1, 6 * mm),
        Paragraph("Patient Name: Maria Garcia", styles["Normal"]),
        Paragraph("Age: 45", styles["Normal"]),
        Paragraph("Sex: Female", styles["Normal"]),
        Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", styles["Normal"]),
        Spacer(1, 6 * mm),
        Paragraph("Chief Complaint:", styles["Heading2"]),
        Paragraph(
            "Recurrent headaches, blurred vision, and intermittent dizziness for the past 3 weeks.",
            styles["Normal"],
        ),
        Spacer(1, 4 * mm),
        Paragraph("History of Present Illness:", styles["Heading2"]),
        Paragraph(
            "The patient reports bilateral temporal headaches occurring daily, rated 6/10 in severity. "
            "Associated symptoms include episodic blurred vision lasting 10-15 minutes and postural "
            "dizziness. No nausea, vomiting, or photophobia. No recent head trauma. She has a "
            "history of hypertension controlled with amlodipine 5 mg daily. Family history significant "
            "for stroke (father, age 68) and type 2 diabetes (mother).",
            styles["Normal"],
        ),
        Spacer(1, 4 * mm),
        Paragraph("Vital Signs:", styles["Heading2"]),
        Paragraph("Blood Pressure: 158/95 mmHg", styles["Normal"]),
        Paragraph("Heart Rate: 82 bpm", styles["Normal"]),
        Paragraph("Temperature: 36.9°C", styles["Normal"]),
        Paragraph("SpO2: 98%", styles["Normal"]),
        Spacer(1, 4 * mm),
        Paragraph("Assessment & Plan:", styles["Heading2"]),
        Paragraph(
            "1. Hypertensive urgency — increase amlodipine to 10 mg daily, add hydrochlorothiazide 25 mg.\n"
            "2. Headaches — likely secondary to uncontrolled hypertension. MRI brain if no improvement in 2 weeks.\n"
            "3. Lab work: CBC, CMP, lipid panel, HbA1c.\n"
            "4. Follow-up in 1 week for BP recheck.",
            styles["Normal"],
        ),
    ]

    doc.build(elements)
    print(f"  [OK] Created: {filepath.name}")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Generating synthetic clinical PDF samples...")
    create_discharge_summary()
    create_lab_report()
    create_clinical_note()
    print(f"\n[OK] All samples generated in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
