from __future__ import annotations

import json
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import CreateUserRequest, UserResponse
from app.services.auth import hash_password


def _generate_user_id() -> str:
    return f"usr-{uuid4().hex[:12]}"


def create_user(db: Session, payload: CreateUserRequest) -> User:
    # The API accepts a structured address object, but the current database
    # stores it as JSON text to keep the first slice simple.
    user = User(
        id=_generate_user_id(),
        name=payload.name,
        address=json.dumps(payload.address.model_dump()),
        phone_number=payload.phoneNumber,
        email=payload.email,
        # Passwords are never stored in plaintext.
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def serialise_user(user: User) -> UserResponse:
    # Convert the stored JSON address string back into the response shape
    # defined by the API contract.
    return UserResponse(
        id=user.id,
        name=user.name,
        address=json.loads(user.address),
        phoneNumber=user.phone_number,
        email=user.email,
        createdTimestamp=user.created_timestamp,
        updatedTimestamp=user.updated_timestamp,
    )
