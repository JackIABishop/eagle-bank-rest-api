from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import BadRequestErrorResponse, ErrorResponse
from app.schemas.transaction import (
    CreateTransactionRequest,
    ListTransactionsResponse,
    TRANSACTION_ID_PATTERN,
    TransactionResponse,
)
from app.services.account import get_owned_account_or_raise
from app.services.transaction import (
    create_transaction,
    get_transaction_for_account,
    list_transactions_for_account,
    serialise_transaction,
    serialise_transaction_list,
)

router = APIRouter(prefix="/v1/accounts", tags=["transaction"])
AccountNumberPath = Annotated[str, Path(pattern=r"^01\d{6}$")]
TransactionIdPath = Annotated[str, Path(pattern=TRANSACTION_ID_PATTERN)]


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
    account_number: AccountNumberPath,
    payload: CreateTransactionRequest = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TransactionResponse:
    """Create a deposit or withdrawal on an owned bank account."""

    account = get_owned_account_or_raise(
        db,
        account_number,
        current_user,
        forbidden_detail="The user is not allowed to delete the bank account details",
    )

    transaction = create_transaction(db, account, current_user, payload)
    return serialise_transaction(transaction)


@router.get(
    "/{account_number}/transactions",
    response_model=ListTransactionsResponse,
    responses={
        400: {"model": BadRequestErrorResponse, "description": "The request didn't supply all the necessary data"},
        401: {"model": ErrorResponse, "description": "Access token is missing or invalid"},
        403: {"model": ErrorResponse, "description": "The user is not allowed to access the transactions"},
        404: {"model": ErrorResponse, "description": "Bank account was not found"},
        500: {"model": ErrorResponse, "description": "An unexpected error occurred"},
    },
)
def list_transactions_route(
    account_number: AccountNumberPath,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ListTransactionsResponse:
    """List transactions for an owned bank account."""

    account = get_owned_account_or_raise(
        db,
        account_number,
        current_user,
        forbidden_detail="The user is not allowed to access the transactions",
    )

    transactions = list_transactions_for_account(db, account)
    return serialise_transaction_list(transactions)


@router.get(
    "/{account_number}/transactions/{transaction_id}",
    response_model=TransactionResponse,
    responses={
        400: {"model": BadRequestErrorResponse, "description": "The request didn't supply all the necessary data"},
        401: {"model": ErrorResponse, "description": "Access token is missing or invalid"},
        403: {"model": ErrorResponse, "description": "The user is not allowed to access the transaction"},
        404: {"model": ErrorResponse, "description": "Bank account was not found"},
        500: {"model": ErrorResponse, "description": "An unexpected error occurred"},
    },
)
def fetch_transaction_by_id_route(
    account_number: AccountNumberPath,
    transaction_id: TransactionIdPath,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TransactionResponse:
    """Fetch a specific transaction for an owned bank account."""

    account = get_owned_account_or_raise(
        db,
        account_number,
        current_user,
        forbidden_detail="The user is not allowed to access the transaction",
    )

    transaction = get_transaction_for_account(db, account, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction was not found")

    return serialise_transaction(transaction)
