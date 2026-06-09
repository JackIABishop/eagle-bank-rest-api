from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.account import BankAccount
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import CreateTransactionRequest, ListTransactionsResponse, TransactionResponse

DEPOSIT_TRANSACTION_TYPE = "deposit"
WITHDRAWAL_TRANSACTION_TYPE = "withdrawal"
MAX_ACCOUNT_BALANCE = Decimal("10000.00")


def _generate_transaction_id() -> str:
    return f"tan-{uuid4().hex[:8]}"


def _to_decimal(amount: float) -> Decimal:
    # Currency values should be normalised to a fixed two-decimal representation
    # before balance arithmetic, otherwise float rounding can drift over time.
    return Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def create_transaction(
    db: Session,
    account: BankAccount,
    current_user: User,
    payload: CreateTransactionRequest,
) -> Transaction:
    amount = _to_decimal(payload.amount)

    if payload.type == WITHDRAWAL_TRANSACTION_TYPE and account.balance < amount:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Insufficient funds to process transaction",
        )

    if payload.type == DEPOSIT_TRANSACTION_TYPE:
        # The supplied OpenAPI contract caps the exposed account balance at
        # 10,000.00, so deposits must be rejected before they push the account
        # beyond the documented maximum.
        if account.balance + amount > MAX_ACCOUNT_BALANCE:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Account balance cannot exceed 10000.00",
            )
        account.balance += amount
    else:
        account.balance -= amount

    transaction = Transaction(
        id=_generate_transaction_id(),
        account_number=account.account_number,
        user_id=current_user.id,
        amount=amount,
        currency=payload.currency,
        transaction_type=payload.type,
        reference=payload.reference,
    )

    db.add(transaction)
    db.add(account)
    db.commit()
    db.refresh(transaction)
    db.refresh(account)
    return transaction


def serialise_transaction(transaction: Transaction) -> TransactionResponse:
    return TransactionResponse(
        id=transaction.id,
        amount=float(transaction.amount),
        currency=transaction.currency,
        type=transaction.transaction_type,
        reference=transaction.reference,
        userId=transaction.user_id,
        createdTimestamp=transaction.created_timestamp,
    )


def list_transactions_for_account(db: Session, account: BankAccount) -> list[Transaction]:
    return (
        db.query(Transaction)
        .filter(Transaction.account_number == account.account_number)
        .order_by(Transaction.created_timestamp.asc(), Transaction.id.asc())
        .all()
    )


def get_transaction_for_account(db: Session, account: BankAccount, transaction_id: str) -> Transaction | None:
    return (
        db.query(Transaction)
        .filter(
            Transaction.account_number == account.account_number,
            Transaction.id == transaction_id,
        )
        .first()
    )


def serialise_transaction_list(transactions: list[Transaction]) -> ListTransactionsResponse:
    return ListTransactionsResponse(
        transactions=[serialise_transaction(transaction) for transaction in transactions]
    )
