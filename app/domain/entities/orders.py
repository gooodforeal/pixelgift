from dataclasses import dataclass, field
from datetime import datetime, timezone as dt_timezone
from enum import StrEnum
import uuid

from app.domain.entities.base import BaseEntity
from app.domain.exceptions.commerce import OrderNotPayableError


class OrderStatus(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    CANCELED = "canceled"


@dataclass(frozen=False, kw_only=True)
class OrderItem(BaseEntity):
    order_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    unit_price: int
    amount: int


@dataclass(frozen=False, kw_only=True)
class Order(BaseEntity):
    user_id: uuid.UUID
    status: OrderStatus
    amount: int
    currency: str = "RUB"
    provider: str = "yookassa"
    provider_payment_id: str | None = None
    idempotency_key: str = ""
    confirmation_url: str | None = None
    paid_at: datetime | None = None
    promo_code_id: uuid.UUID | None = None
    discount_percent: int | None = None
    amount_before_discount: int | None = None
    items: list[OrderItem] = field(default_factory=list)

    def mark_succeeded(self, *, paid_at: datetime | None = None) -> None:
        if self.status != OrderStatus.PENDING:
            raise OrderNotPayableError(self.id, self.status.value)
        self.status = OrderStatus.SUCCEEDED
        self.paid_at = paid_at or datetime.now(dt_timezone.utc)
        self._touch()

    def mark_canceled(self) -> None:
        if self.status != OrderStatus.PENDING:
            raise OrderNotPayableError(self.id, self.status.value)
        self.status = OrderStatus.CANCELED
        self._touch()

    def _touch(self) -> None:
        self.updated_at = datetime.now(dt_timezone.utc)
