"""Pydantic schemas for report generation."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReportGenerateResponse(BaseModel):
    """Response after triggering report generation."""
    case_id: int
    status: str
    message: str
    report_id: Optional[int] = None


class ReportStatusResponse(BaseModel):
    """Response for report download status check."""
    case_id: int
    ready: bool
    download_url: Optional[str] = None
    generated_at: Optional[datetime] = None
