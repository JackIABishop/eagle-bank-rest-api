from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import BadRequestErrorResponse, ErrorResponse
from app.schemas.transaction import CreateTransactionRequest, TransactionResponse
from app.services.account import get_account_by_number
from app.services.transaction import create_transaction, serialise_transaction

router = APIRouter(prefix="/v1/accounts", tags=["transaction"])
AccountNumberPath = str


@router.post(
    "/{account_number}/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": BadRequestErrorResponse, "description": "Invalid details supplied"},
        401: {"model": ErrorResponse, "description": "Access token is missing or invalid"},
        403: {"model": ErrorResponse, "description": "The user is not allowed to delete the bank account details"},
        404: {"model": ErrorResponse, "description": "Bank account was not found"},
        422: {"model": ErrorResponse, "description": "Insufficient funds to process transaction"},
        500: {"model": ErrorResponse, "description": "An unexpected error occurred"},
    },
)
def create_transaction_route(
    account_number: AccountNumberPath = Path(pattern=r"^01\d{6}$"),
    payload: CreateTransactionRequest = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TransactionResponse:
    """Create a deposit or withdrawal on an owned bank account."""

    account = get_account_by_number(db, account_number)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bank account was not found")

    if account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user is not allowed to delete the bank account details",
        )

    transaction = create_transaction(db, account, current_user, payload)
    return serialise_transaction(transaction)
