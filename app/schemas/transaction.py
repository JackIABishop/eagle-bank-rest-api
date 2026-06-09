from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

TRANSACTION_TYPE_PATTERN = r"^(deposit|withdrawal)$"
TRANSACTION_ID_PATTERN = r"^tan-[A-Za-z0-9]+$"


class CreateTransactionRequest(BaseModel):
    # The supplied OpenAPI contract caps individual transaction amounts at 10,000,
    # so the validation is mirrored here rather than invented locally.
    amount: float = Field(ge=0.0, le=10000.0)
    currency: str = Field(pattern=r"^GBP$")
    type: str = Field(pattern=TRANSACTION_TYPE_PATTERN)
    reference: str | None = None


class TransactionResponse(BaseModel):
    id: str = Field(pattern=TRANSACTION_ID_PATTERN)
    amount: float
    currency: str
    type: str
    reference: str | None = None
    userId: str
    createdTimestamp: datetime


class ListTransactionsResponse(BaseModel):
    transactions: list[TransactionResponse]
