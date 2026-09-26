from dataclasses import dataclass
from datetime import datetime, timezone as dt_timezone
import uuid

from app.domain.entities.base import BaseEntity
from app.domain.entities.user_balance_logs import BalanceLogReason, UserBalanceLog
from app.domain.exceptions.commerce import InsufficientBalanceError


@dataclass(frozen=False, kw_only=True)
class UserBalance(BaseEntity):
    user_id: uuid.UUID
    product_id: uuid.UUID
    balance: int = 0

    def credit(
        self,
        *,
        delta: int,
        reason: BalanceLogReason,
        reference_type: str,
        reference_id: uuid.UUID,
        sku: str | None = None,
    ) -> UserBalanceLog:
        if delta <= 0:
            raise ValueError("credit delta must be positive")
        self.balance += delta
        self._touch()
        return UserBalanceLog(
            user_id=self.user_id,
            product_id=self.product_id,
            delta=delta,
            balance_after=self.balance,
            reason=reason,
            reference_type=reference_type,
            reference_id=reference_id,
        )

    def debit(
        self,
        *,
        delta: int,
        reason: BalanceLogReason,
        reference_type: str,
        reference_id: uuid.UUID,
        sku: str = "credit",
    ) -> UserBalanceLog:
        if delta <= 0:
            raise ValueError("debit delta must be positive")
        if self.balance < delta:
            raise InsufficientBalanceError(
                sku=sku, required=delta, available=self.balance
            )
        self.balance -= delta
        self._touch()
        return UserBalanceLog(
            user_id=self.user_id,
            product_id=self.product_id,
            delta=-delta,
            balance_after=self.balance,
            reason=reason,
            reference_type=reference_type,
            reference_id=reference_id,
        )

    def _touch(self) -> None:
        self.updated_at = datetime.now(dt_timezone.utc)
