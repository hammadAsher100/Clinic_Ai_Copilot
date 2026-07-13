"""
JWT-based authentication for clinician access.

Minimal single-role auth — no RBAC needed for hackathon scope.
Seeded demo user: clinician / demo2026
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from api.core.config import settings

# ── Password hashing ────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── OAuth2 scheme ────────────────────────────────────────────────────────
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

# ── Demo users (in production, these would be in the database) ──────────
# Using simple password verification to avoid bcrypt compatibility issues
DEMO_USERS: dict[str, dict] = {
    "clinician": {
        "username": "clinician",
        "full_name": "Dr. Demo Clinician",
        "password": "demo2026",  # In production, this would be hashed in DB
        "role": "clinician",
    },
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "password": "admin2026",  # In production, this would be hashed in DB
        "role": "admin",
    },
}


def verify_password(plain_password: str, stored_password: str) -> bool:
    """Check a plaintext password against stored password.
    
    For demo purposes, we use simple comparison. In production, use proper hashing.
    """
    return plain_password == stored_password


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate a user by username and password.

    Returns the user dict if valid, None otherwise.
    """
    user = DEMO_USERS.get(username)
    if user is None:
        return None
    if not verify_password(password, user["password"]):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt_expiration_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


async def get_current_user(token: str | None = Depends(oauth2_scheme)) -> dict:
    """FastAPI dependency: extract and validate the current user from JWT.

    Returns user dict or raises 401.
    """
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        username: str = payload.get("sub", "")
        if not username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = DEMO_USERS.get(username)
    if user is None:
        raise credentials_exception

    return user


async def get_optional_user(token: str | None = Depends(oauth2_scheme)) -> dict | None:
    """Like get_current_user but returns None instead of raising 401."""
    if token is None:
        return None
    try:
        return await get_current_user(token)
    except HTTPException:
        return None
