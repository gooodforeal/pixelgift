"""Товар каталога (например, пакет кредитов на создание боксов)."""

from dataclasses import dataclass, field
from enum import StrEnum

from app.domain.entities.base import BaseEntity
from app.domain.exceptions.commerce import ProductValidationError

PRODUCT_MAX_IMAGES = 5


class ProductKind(StrEnum):
    """Тип товара в каталоге."""

    CREDIT = "credit"


@dataclass(frozen=False, kw_only=True)
class Product(BaseEntity):
    """Описание SKU с ценой в копейках, медиа и флагом активности."""

    sku: str
    name: str
    kind: ProductKind
    unit_price: int
    currency: str = "RUB"
    description: str = ""
    image_urls: list[str] = field(default_factory=list)
    is_active: bool = True

    @staticmethod
    def validate_image_urls(urls: list[str] | None) -> list[str]:
        """Нормализует список URL изображений и проверяет лимит PRODUCT_MAX_IMAGES."""
        if urls is None:
            return []
        cleaned: list[str] = []
        for raw in urls:
            url = (raw or "").strip()
            if not url:
                continue
            cleaned.append(url)
        if len(cleaned) > PRODUCT_MAX_IMAGES:
            raise ProductValidationError(
                f"Product may have at most {PRODUCT_MAX_IMAGES} images"
            )
        return cleaned
