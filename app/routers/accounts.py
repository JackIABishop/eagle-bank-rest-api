from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.account import (
    BankAccountResponse,
    CreateBankAccountRequest,
    ListBankAccountsResponse,
    UpdateBankAccountRequest,
)
from app.schemas.common import BadRequestErrorResponse, ErrorResponse
from app.services.account import (
    create_account,
    delete_account,
    get_account_by_number,
    list_accounts_for_user,
    serialise_account,
    serialise_account_list,
    update_account,
)

router = APIRouter(prefix="/v1/accounts", tags=["account"])


@router.post(
    "",
    response_model=BankAccountResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": BadRequestErrorResponse, "description": "Invalid details supplied"},
        401: {"model": ErrorResponse, "description": "Access token is missing or invalid"},
        403: {"model": ErrorResponse, "description": "The user is not allowed to access the transaction"},
        500: {"model": ErrorResponse, "description": "An unexpected error occurred"},
    },
)
def create_account_route(
    payload: CreateBankAccountRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BankAccountResponse:
    """Create a bank account for the authenticated user."""

    account = create_account(db, current_user, payload)
    return serialise_account(account)


@router.get(
    "",
    response_model=ListBankAccountsResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Access token is missing or invalid"},
        500: {"model": ErrorResponse, "description": "An unexpected error occurred"},
    },
)
def list_accounts_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ListBankAccountsResponse:
    """List the authenticated user's bank accounts."""

    accounts = list_accounts_for_user(db, current_user)
    return serialise_account_list(accounts)


@router.get(
    "/{account_number}",
    response_model=BankAccountResponse,
    responses={
        400: {"model": BadRequestErrorResponse, "description": "The request didn't supply all the necessary data"},
        401: {"model": ErrorResponse, "description": "The user was not authenticated"},
        403: {"model": ErrorResponse, "description": "The user is not allowed to access the bank account details"},
        404: {"model": ErrorResponse, "description": "Bank account was not found"},
        500: {"model": ErrorResponse, "description": "An unexpected error occurred"},
    },
)
def fetch_account_by_number(
    account_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BankAccountResponse:
    """Fetch a single bank account owned by the authenticated user."""

    account = get_account_by_number(db, account_number)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bank account was not found")

    # Ownership is checked after lookup so a valid token cannot read another customer's account.
    if account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user is not allowed to access the bank account details",
        )

    return serialise_account(account)


@router.patch(
    "/{account_number}",
    response_model=BankAccountResponse,
    responses={
        400: {"model": BadRequestErrorResponse, "description": "The request didn't supply all the necessary data"},
        401: {"model": ErrorResponse, "description": "Access token is missing or invalid"},
        403: {"model": ErrorResponse, "description": "The user is not allowed to update the bank account details"},
        404: {"model": ErrorResponse, "description": "Bank account was not found"},
        500: {"model": ErrorResponse, "description": "An unexpected error occurred"},
    },
)
def update_account_by_number(
    account_number: str,
    payload: UpdateBankAccountRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BankAccountResponse:
    """Update a bank account owned by the authenticated user."""

    account = get_account_by_number(db, account_number)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bank account was not found")

    if account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user is not allowed to update the bank account details",
        )

    updated_account = update_account(db, account, payload)
    return serialise_account(updated_account)


@router.delete(
    "/{account_number}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        400: {"model": BadRequestErrorResponse, "description": "The request didn't supply all the necessary data"},
        401: {"model": ErrorResponse, "description": "Access token is missing or invalid"},
        403: {"model": ErrorResponse, "description": "The user is not allowed to delete the bank account details"},
        404: {"model": ErrorResponse, "description": "Bank account was not found"},
        500: {"model": ErrorResponse, "description": "An unexpected error occurred"},
    },
)
def delete_account_by_number(
    account_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    """Delete a bank account owned by the authenticated user."""

    account = get_account_by_number(db, account_number)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bank account was not found")

    if account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user is not allowed to delete the bank account details",
        )

    # TODO: Once transactions exist, revisit whether this should return 409
    # instead of hard-deleting the account to preserve transaction history.
    delete_account(db, account)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
