from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import BadRequestErrorResponse, ErrorResponse
from app.schemas.user import CreateUserRequest, UserResponse
from app.services.user import create_user, serialise_user

router = APIRouter(prefix="/v1/users", tags=["user"])
UserIdPath = Annotated[str, Path(pattern=r"^usr-[A-Za-z0-9]+$")]


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": BadRequestErrorResponse, "description": "Invalid details supplied"},
        500: {"model": ErrorResponse, "description": "An unexpected error occurred"},
    },
)
def create_user_route(payload: CreateUserRequest, db: Session = Depends(get_db)) -> UserResponse:
    """Create a new user record."""

    # Email is the credential used for login, so it must be unique.
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with that email already exists",
        )

    user = create_user(db, payload)
    return serialise_user(user)

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    responses={
        400: {"model": BadRequestErrorResponse, "description": "The request didn't supply all the necessary data"},
        401: {"model": ErrorResponse, "description": "Access token is missing or invalid"},
        403: {"model": ErrorResponse, "description": "The user is not allowed to access the user details"},
        404: {"model": ErrorResponse, "description": "User was not found"},
        500: {"model": ErrorResponse, "description": "An unexpected error occurred"},
    },
)
def fetch_user_by_id(
    user_id: UserIdPath,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Fetch the currently authenticated user's details."""

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User was not found",
        )

    # This endpoint only allows a user to fetch their own record.
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user is not allowed to access the user details",
        )

    return serialise_user(user)
