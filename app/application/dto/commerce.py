"""Команды use case'ов магазина: корзина, заказы, товары, промокоды."""

from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass(frozen=True, kw_only=True)
class AddCartItemCommand:
    """Добавление позиции в корзину по SKU."""

    actor_id: uuid.UUID
    sku: str
    quantity: int


@dataclass(frozen=True, kw_only=True)
class UpdateCartItemCommand:
    """Изменение количества товара в корзине."""

    actor_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int


@dataclass(frozen=True, kw_only=True)
class RemoveCartItemCommand:
    """Удаление позиции из корзины."""

    actor_id: uuid.UUID
    product_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class CheckoutCartCommand:
    """Оформление заказа из текущей корзины."""

    actor_id: uuid.UUID
    promo_code: str | None = None


@dataclass(frozen=True, kw_only=True)
class CreatePromoCodeCommand:
    """Создание промокода (админ)."""

    actor_id: uuid.UUID
    code: str
    discount_percent: int
    expires_at: datetime
    max_usages: int | None = None


@dataclass(frozen=True, kw_only=True)
class SetPromoCodeActiveCommand:
    """Включение или отключение промокода."""

    actor_id: uuid.UUID
    promo_id: uuid.UUID
    is_active: bool


@dataclass(frozen=True, kw_only=True)
class CreateProductCommand:
    """Создание товара каталога."""

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
    """Частичное обновление товара; ``update_sale`` управляет блоком скидки."""

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
    """Запрос одного заказа владельцем."""

    actor_id: uuid.UUID
    order_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class ListBalanceLogsCommand:
    """Постраничный журнал операций с балансом пользователя."""

    actor_id: uuid.UUID
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True, kw_only=True)
class ListOrdersCommand:
    """Постраничный список заказов пользователя."""

    actor_id: uuid.UUID
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True, kw_only=True)
class ListPromoCodesCommand:
    """Постраничный список всех промокодов."""

    page: int = 1
    page_size: int = 10


@dataclass(frozen=True, kw_only=True)
class HandleYookassaWebhookCommand:
    """Тело webhook YooKassa: тип события и объект payment."""

    event: str
    object_payload: dict
