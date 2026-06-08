from __future__ import annotations

import random
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.account import BankAccount
from app.models.user import User
from app.schemas.account import (
    BankAccountResponse,
    CreateBankAccountRequest,
    ListBankAccountsResponse,
    UpdateBankAccountRequest,
)

DEFAULT_SORT_CODE = "10-10-10"
DEFAULT_CURRENCY = "GBP"


def _generate_account_number(db: Session) -> str:
    while True:
        account_number = f"01{random.randint(0, 999999):06d}"
        existing_account = db.query(BankAccount).filter(BankAccount.account_number == account_number).first()
        if existing_account is None:
            return account_number


def create_account(db: Session, current_user: User, payload: CreateBankAccountRequest) -> BankAccount:
    account = BankAccount(
        account_number=_generate_account_number(db),
        user_id=current_user.id,
        sort_code=DEFAULT_SORT_CODE,
        name=payload.name,
        account_type=payload.accountType,
        balance=Decimal("0.00"),
        currency=DEFAULT_CURRENCY,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def get_account_by_number(db: Session, account_number: str) -> BankAccount | None:
    return db.query(BankAccount).filter(BankAccount.account_number == account_number).first()


def list_accounts_for_user(db: Session, current_user: User) -> list[BankAccount]:
    return (
        db.query(BankAccount)
        .filter(BankAccount.user_id == current_user.id)
        .order_by(BankAccount.created_timestamp.asc(), BankAccount.account_number.asc())
        .all()
    )


def update_account(db: Session, account: BankAccount, payload: UpdateBankAccountRequest) -> BankAccount:
    updates = payload.model_dump(exclude_unset=True)
    if "name" in updates:
        account.name = updates["name"]
    if "accountType" in updates:
        account.account_type = updates["accountType"]

    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def delete_account(db: Session, account: BankAccount) -> None:
    # TODO: Need to check the bank account is empty before deleting?
    db.delete(account)
    db.commit()


def serialise_account(account: BankAccount) -> BankAccountResponse:
    return BankAccountResponse(
        accountNumber=account.account_number,
        sortCode=account.sort_code,
        name=account.name,
        accountType=account.account_type,
        balance=float(account.balance),
        currency=account.currency,
        createdTimestamp=account.created_timestamp,
        updatedTimestamp=account.updated_timestamp,
    )


def serialise_account_list(accounts: list[BankAccount]) -> ListBankAccountsResponse:
    return ListBankAccountsResponse(accounts=[serialise_account(account) for account in accounts])
