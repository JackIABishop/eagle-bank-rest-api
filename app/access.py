from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.account import BankAccount
from app.models.user import User
from app.services.account import get_account_by_number


def get_owned_account_or_raise(
    db: Session,
    account_number: str,
    current_user: User,
    *,
    forbidden_detail: str,
) -> BankAccount:
    """Fetch an account and enforce that it belongs to the authenticated user."""

    account = get_account_by_number(db, account_number)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bank account was not found")

    if account.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=forbidden_detail)

    return account
