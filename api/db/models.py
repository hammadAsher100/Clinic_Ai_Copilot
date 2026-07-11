"""
SQLAlchemy ORM models for the Clinical AI Co-Pilot.

Tables:
  - patients: basic patient demographics
  - cases: a clinical case aggregating predictions across modalities
  - model_predictions: raw output from each ML model (per modality)
  - hitl_decisions: clinician approve/reject/edit actions per modality
  - reports: generated PDF/DOCX report metadata
"""
from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, Enum, ForeignKey, JSON,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


# ── Enums ────────────────────────────────────────────────────────────────

class CaseStatus(str, enum.Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"


class Modality(str, enum.Enum):
    IMAGE = "image"
    TABULAR = "tabular"
    TEXT = "text"


class ClinicianAction(str, enum.Enum):
    APPROVE = "approve"
    REJECT = "reject"
    EDIT = "edit"


# ── ORM Models ──────────────────────────────────────────────────────────

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, default="Anonymous")
    age = Column(Integer, nullable=True)
    sex = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    cases = relationship("Case", back_populates="patient")


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    status = Column(Enum(CaseStatus), default=CaseStatus.PENDING)
    llm_narrative = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    patient = relationship("Patient", back_populates="cases")
    predictions = relationship("ModelPrediction", back_populates="case")
    decisions = relationship("HITLDecision", back_populates="case")
    reports = relationship("Report", back_populates="case")


class ModelPrediction(Base):
    __tablename__ = "model_predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    modality = Column(Enum(Modality), nullable=False)
    prediction = Column(String(255), nullable=False)
    confidence = Column(Float, nullable=False)
    raw_output_json = Column(JSON, nullable=True)
    explainability_ref = Column(String(500), nullable=True)  # Path to heatmap/chart
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    case = relationship("Case", back_populates="predictions")


class HITLDecision(Base):
    __tablename__ = "hitl_decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    modality = Column(Enum(Modality), nullable=False)
    clinician_action = Column(Enum(ClinicianAction), nullable=False)
    original_value = Column(String(255), nullable=True)
    edited_value = Column(String(255), nullable=True)
    reviewer = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    case = relationship("Case", back_populates="decisions")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    case = relationship("Case", back_populates="reports")
