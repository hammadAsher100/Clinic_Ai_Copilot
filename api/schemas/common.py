"""Common response schemas used across all routers."""
from __future__ import annotations

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Consistent error response schema for all endpoints."""
    error: str
    detail: str
