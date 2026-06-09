from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
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
    get_owned_account_or_raise,
    list_accounts_for_user,
    serialise_account,
    serialise_account_list,
    update_account,
)

router = APIRouter(prefix="/v1/accounts", tags=["account"])
# Mirror the OpenAPI contract so invalid account numbers fail validation
# before the route logic attempts a lookup.
AccountNumberPath = Annotated[str, Path(pattern=r"^01\d{6}$")]


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
    account_number: AccountNumberPath,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BankAccountResponse:
    """Fetch a single bank account owned by the authenticated user."""

    account = get_owned_account_or_raise(
        db,
        account_number,
        current_user,
        forbidden_detail="The user is not allowed to access the bank account details",
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
    account_number: AccountNumberPath,
    payload: UpdateBankAccountRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BankAccountResponse:
    """Update a bank account owned by the authenticated user."""

    account = get_owned_account_or_raise(
        db,
        account_number,
        current_user,
        forbidden_detail="The user is not allowed to update the bank account details",
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
    account_number: AccountNumberPath,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    """Delete a bank account owned by the authenticated user."""

    account = get_owned_account_or_raise(
        db,
        account_number,
        current_user,
        forbidden_detail="The user is not allowed to delete the bank account details",
    )

    # TODO: Once transactions exist, revisit whether this should return 409
    # instead of hard-deleting the account to preserve transaction history.
    delete_account(db, account)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
