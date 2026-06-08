from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

ACCOUNT_NUMBER_PATTERN = r"^01\d{6}$"
# The current contract only allows personal accounts, but this is a clear
# extension point if the API is later expanded to support business accounts.
# i.e. ACCOUNT_TYPE_PATTERN = r"^(personal|business|joint)$"
ACCOUNT_TYPE_PATTERN = r"^personal$"


class CreateBankAccountRequest(BaseModel):
    name: str
    accountType: str = Field(pattern=ACCOUNT_TYPE_PATTERN)


class UpdateBankAccountRequest(BaseModel):
    name: str | None = None
    accountType: str | None = Field(default=None, pattern=ACCOUNT_TYPE_PATTERN)


class BankAccountResponse(BaseModel):
    accountNumber: str = Field(pattern=ACCOUNT_NUMBER_PATTERN)
    sortCode: str
    name: str
    accountType: str
    balance: float
    currency: str
    createdTimestamp: datetime
    updatedTimestamp: datetime


class ListBankAccountsResponse(BaseModel):
    accounts: list[BankAccountResponse]
