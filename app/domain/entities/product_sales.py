"""Скидка на конкретный товар каталога."""

from dataclasses import dataclass
import uuid

from app.domain.entities.base import BaseEntity
from app.domain.exceptions.commerce import ProductValidationError


@dataclass(frozen=False, kw_only=True)
class ProductSale(BaseEntity):
    """Процент скидки на product_id с возможностью отключения."""

    product_id: uuid.UUID
    discount_percent: int
    is_active: bool = True

    @staticmethod
    def validate_discount_percent(value: int) -> int:
        """Проверяет скидку: от 5 до 100 % с шагом 5."""
        if value < 5 or value > 100 or value % 5 != 0:
            raise ProductValidationError(
                "Sale discount must be 5–100% in steps of 5"
            )
        return value

    def apply(self, unit_price: int) -> int:
        """Возвращает цену после скидки (целые копейки, округление вниз)."""
        if not self.is_active or unit_price <= 0:
            return max(0, unit_price)
        return max(0, unit_price * (100 - self.discount_percent) // 100)
