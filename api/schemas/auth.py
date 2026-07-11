"""Pydantic schemas for authentication."""
from __future__ import annotations

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Login credentials."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Current user info."""
    username: str
    full_name: str
    role: str
