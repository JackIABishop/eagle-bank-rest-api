from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Transaction(Base):
    """Database model for account transactions."""

    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    account_number: Mapped[str] = mapped_column(ForeignKey("bank_accounts.account_number"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(32), nullable=False)
    reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
