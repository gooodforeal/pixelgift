from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass(frozen=True, kw_only=True)
class AddCartItemCommand:
    actor_id: uuid.UUID
    sku: str
    quantity: int


@dataclass(frozen=True, kw_only=True)
class UpdateCartItemCommand:
    actor_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int


@dataclass(frozen=True, kw_only=True)
class RemoveCartItemCommand:
    actor_id: uuid.UUID
    product_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class CheckoutCartCommand:
    actor_id: uuid.UUID
    promo_code: str | None = None


@dataclass(frozen=True, kw_only=True)
class CreatePromoCodeCommand:
    actor_id: uuid.UUID
    code: str
    discount_percent: int
    expires_at: datetime


@dataclass(frozen=True, kw_only=True)
class CreateProductCommand:
    actor_id: uuid.UUID
    sku: str
    name: str
    description: str
    unit_price: int
    kind: str = "credit"
    currency: str = "RUB"
    is_active: bool = True
    image_urls: list[str] | None = None
    sale_discount_percent: int | None = None


@dataclass(frozen=True, kw_only=True)
class UpdateProductCommand:
    actor_id: uuid.UUID
    product_id: uuid.UUID
    name: str | None = None
    description: str | None = None
    unit_price: int | None = None
    is_active: bool | None = None
    image_urls: list[str] | None = None
    sale_discount_percent: int | None = None
    update_sale: bool = False


@dataclass(frozen=True, kw_only=True)
class GetOrderCommand:
    actor_id: uuid.UUID
    order_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class ListBalanceLogsCommand:
    actor_id: uuid.UUID
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True, kw_only=True)
class ListOrdersCommand:
    actor_id: uuid.UUID
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True, kw_only=True)
class HandleYookassaWebhookCommand:
    event: str
    object_payload: dict
