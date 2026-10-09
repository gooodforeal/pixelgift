"""Промокод со скидкой на заказ и лимитом использований."""

from dataclasses import dataclass
from datetime import datetime, timezone as dt_timezone
from typing import Literal
import uuid

from app.domain.entities.base import BaseEntity
from app.domain.exceptions.commerce import (
    PromoCodeExhaustedError,
    PromoCodeExpiredError,
    PromoCodeFormatError,
    PromoCodeInactiveError,
    PromoCodeInvalidDiscountError,
    PromoCodeInvalidMaxUsagesError,
)

PromoCodeStatus = Literal["active", "inactive", "expired", "exhausted"]


@dataclass(frozen=False, kw_only=True)
class PromoCode(BaseEntity):
    """Код скидки, сроком действия, счётчиком применений и флагом активности."""

    code: str
    discount_percent: int
    expires_at: datetime
    usage_count: int = 0
    max_usages: int | None = None
    is_active: bool = True
    created_by_user_id: uuid.UUID | None = None

    @staticmethod
    def normalize_code(raw: str) -> str:
        """Приводит ввод к trim + upper case без проверки формата."""
        return raw.strip().upper()

    @classmethod
    def validate_code(cls, raw: str) -> str:
        """Нормализует и проверяет длину и символы промокода."""
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
        """Проверяет процент скидки: 5–100 с шагом 5."""
        if value < 5 or value > 100 or value % 5 != 0:
            raise PromoCodeInvalidDiscountError(value)
        return value

    @staticmethod
    def validate_max_usages(value: int | None) -> int | None:
        """Допускает None (без лимита) или положительное целое."""
        if value is None:
            return None
        if value < 1:
            raise PromoCodeInvalidMaxUsagesError(value)
        return value

    def _expires_at_utc(self) -> datetime:
        expires = self.expires_at
        if expires.tzinfo is None:
            return expires.replace(tzinfo=dt_timezone.utc)
        return expires

    def is_expired(self, *, now: datetime | None = None) -> bool:
        """True, если expires_at уже наступил (UTC)."""
        moment = now or datetime.now(dt_timezone.utc)
        return self._expires_at_utc() <= moment

    def is_exhausted(self) -> bool:
        """True, если достигнут max_usages."""
        return self.max_usages is not None and self.usage_count >= self.max_usages

    def resolve_status(self, *, now: datetime | None = None) -> PromoCodeStatus:
        """Вычисляет отображаемый статус с учётом активности, срока и лимита."""
        if not self.is_active:
            return "inactive"
        if self.is_expired(now=now):
            return "expired"
        if self.is_exhausted():
            return "exhausted"
        return "active"

    def assert_usable(self, *, now: datetime | None = None) -> None:
        """Бросает доменное исключение, если код нельзя применить к заказу."""
        if not self.is_active:
            raise PromoCodeInactiveError(self.code)
        if self.is_expired(now=now):
            raise PromoCodeExpiredError(self.code)
        if self.is_exhausted():
            raise PromoCodeExhaustedError(self.code)

    def discounted_amount(self, amount_kopecks: int) -> int:
        """Сумма в копейках после скидки (целочисленное деление)."""
        if amount_kopecks <= 0:
            return 0
        # Round to nearest kopeck downward for customer benefit consistency.
        discounted = amount_kopecks * (100 - self.discount_percent) // 100
        return max(0, discounted)

    def register_purchase(self) -> None:
        """Увеличивает usage_count после успешной оплаты с промокодом."""
        self.usage_count += 1
        self.updated_at = datetime.now(dt_timezone.utc)

    def set_active(self, active: bool) -> None:
        """Включает или отключает промокод."""
        self.is_active = active
        self.updated_at = datetime.now(dt_timezone.utc)
