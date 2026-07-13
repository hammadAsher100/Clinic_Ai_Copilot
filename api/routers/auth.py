"""
Authentication router — minimal JWT-based auth for clinician login.

POST /api/v1/auth/login
GET  /api/v1/auth/me
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends

from api.core.security import (
    authenticate_user, create_access_token, get_current_user,
)
from api.schemas.auth import LoginRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest) -> TokenResponse:
    """Authenticate clinician and return JWT token."""
    # Debug logging
    import logging
    logger = logging.getLogger("api")
    logger.info(f"Login attempt - username: '{request.username}', password length: {len(request.password)}")
    
    user = authenticate_user(request.username, request.password)
    if user is None:
        logger.warning(f"Authentication failed for username: '{request.username}'")
        raise HTTPException(status_code=401, detail="Invalid username or password")

    logger.info(f"Authentication successful for user: '{request.username}'")
    token = create_access_token(data={"sub": user["username"]})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)) -> UserResponse:
    """Return the current authenticated user's info."""
    return UserResponse(
        username=user["username"],
        full_name=user["full_name"],
        role=user["role"],
    )
