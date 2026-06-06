from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.schemas.auth import AuthTokenResponse, LoginRequest
from app.services.auth import authenticate_user, create_access_token

router = APIRouter(prefix="/v1/auth", tags=["auth"])


@router.post("/login", response_model=AuthTokenResponse)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthTokenResponse:
    """Authenticate a user with email and password and issue a JWT."""

    user = authenticate_user(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password is incorrect",
        )

    access_token = create_access_token(user.id)
    return AuthTokenResponse(
        accessToken=access_token,
        tokenType="Bearer",
        expiresIn=settings.jwt_expiry_seconds,
    )
