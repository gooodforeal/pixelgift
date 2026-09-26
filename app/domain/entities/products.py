from dataclasses import dataclass, field
from enum import StrEnum

from app.domain.entities.base import BaseEntity
from app.domain.exceptions.commerce import ProductValidationError

PRODUCT_MAX_IMAGES = 5


class ProductKind(StrEnum):
    CREDIT = "credit"


@dataclass(frozen=False, kw_only=True)
class Product(BaseEntity):
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
