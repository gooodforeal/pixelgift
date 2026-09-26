from dataclasses import dataclass
from datetime import datetime, timezone as dt_timezone
import uuid

from app.domain.entities.base import BaseEntity
from app.domain.exceptions.commerce import (
    PromoCodeExpiredError,
    PromoCodeFormatError,
    PromoCodeInactiveError,
    PromoCodeInvalidDiscountError,
)


@dataclass(frozen=False, kw_only=True)
class PromoCode(BaseEntity):
    code: str
    discount_percent: int
    expires_at: datetime
    usage_count: int = 0
    is_active: bool = True
    created_by_user_id: uuid.UUID | None = None

    @staticmethod
    def normalize_code(raw: str) -> str:
        return raw.strip().upper()

    @classmethod
    def validate_code(cls, raw: str) -> str:
        code = cls.normalize_code(raw)
        if not (4 <= len(code) <= 20):
            raise PromoCodeFormatError(code)
        if not code.isalnum():
            raise PromoCodeFormatError(code)
        if code != code.upper():
            raise PromoCodeFormatError(code)
        return code

    @staticmethod
    def validate_discount_percent(value: int) -> int:
        if value < 5 or value > 100 or value % 5 != 0:
            raise PromoCodeInvalidDiscountError(value)
        return value

    def assert_usable(self, *, now: datetime | None = None) -> None:
        if not self.is_active:
            raise PromoCodeInactiveError(self.code)
        moment = now or datetime.now(dt_timezone.utc)
        expires = self.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=dt_timezone.utc)
        if expires <= moment:
            raise PromoCodeExpiredError(self.code)

    def discounted_amount(self, amount_kopecks: int) -> int:
        if amount_kopecks <= 0:
            return 0
        # Round to nearest kopeck downward for customer benefit consistency.
        discounted = amount_kopecks * (100 - self.discount_percent) // 100
        return max(0, discounted)

    def register_purchase(self) -> None:
        self.usage_count += 1
        self.updated_at = datetime.now(dt_timezone.utc)
