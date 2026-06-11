from __future__ import annotations

import json
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.account import BankAccount
from app.models.user import User
from app.schemas.user import CreateUserRequest, UpdateUserRequest, UserResponse
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


def update_user(db: Session, user: User, payload: UpdateUserRequest) -> User:
    updates = payload.model_dump(exclude_unset=True)

    if "email" in updates and updates["email"] != user.email:
        existing_user = db.query(User).filter(User.email == updates["email"]).first()
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with that email already exists",
            )

    if "name" in updates:
        user.name = updates["name"]
    if "address" in updates:
        user.address = json.dumps(updates["address"])
    if "phoneNumber" in updates:
        user.phone_number = updates["phoneNumber"]
    if "email" in updates:
        user.email = updates["email"]
    if "password" in updates:
        user.password_hash = hash_password(updates["password"])

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    has_accounts = db.query(BankAccount.account_number).filter(BankAccount.user_id == user.id).first() is not None
    if has_accounts:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User cannot be deleted while bank accounts exist",
        )

    db.delete(user)
    db.commit()


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
