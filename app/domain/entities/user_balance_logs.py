from dataclasses import dataclass
from enum import StrEnum
import uuid

from app.domain.entities.base import BaseEntity


class BalanceLogReason(StrEnum):
    PURCHASE = "purchase"
    CONSUME = "consume"
    REFUND = "refund"
    ADMIN = "admin"


@dataclass(frozen=False, kw_only=True)
class UserBalanceLog(BaseEntity):
    user_id: uuid.UUID
    product_id: uuid.UUID
    delta: int
    balance_after: int
    reason: BalanceLogReason
    reference_type: str
    reference_id: uuid.UUID
