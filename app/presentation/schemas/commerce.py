"""Схемы каталога, корзины, заказов и балансов."""

from datetime import datetime
import uuid

from pydantic import BaseModel, Field, field_validator

from app.presentation.schemas.base import BaseResponseSchema


class ProductSchema(BaseModel):
    """Товар каталога."""
    id: uuid.UUID
    sku: str
    name: str
    description: str = ""
    image_urls: list[str] = Field(default_factory=list)
    kind: str
    unit_price: int
    currency: str
    is_active: bool
    sale_discount_percent: int | None = None
    sale_unit_price: int | None = None


class ProductsResponse(BaseResponseSchema[list[ProductSchema]]):
    """Список товаров."""
    pass


class CartItemSchema(BaseModel):
    """Позиция корзины."""
    product_id: uuid.UUID
    sku: str
    name: str
    image_urls: list[str] = Field(default_factory=list)
    unit_price: int
    currency: str
    quantity: int
    amount: int
    compare_at_price: int | None = None
    sale_discount_percent: int | None = None


class CartSchema(BaseModel):
    """Корзина пользователя."""
    id: uuid.UUID
    items: list[CartItemSchema]
    total_amount: int
    currency: str = "RUB"


class CartResponse(BaseResponseSchema[CartSchema]):
    """Ответ операций с корзиной."""
    pass


class AddCartItemRequest(BaseModel):
    """Добавление позиции по SKU."""
    sku: str = Field(min_length=1, max_length=64)
    quantity: int = Field(default=1, ge=1, le=100)


class UpdateCartItemRequest(BaseModel):
    """Изменение количества."""
    quantity: int = Field(ge=1, le=100)


class CheckoutRequest(BaseModel):
    """Оформление заказа с опциональным промокодом."""
    promo_code: str | None = Field(default=None, max_length=20)


class OrderItemSchema(BaseModel):
    """Строка заказа."""
    product_id: uuid.UUID
    quantity: int
    unit_price: int
    amount: int


class OrderSchema(BaseModel):
    """Заказ пользователя."""
    id: uuid.UUID
    status: str
    amount: int
    currency: str
    confirmation_url: str | None = None
    paid_at: datetime | None = None
    discount_percent: int | None = None
    amount_before_discount: int | None = None
    items: list[OrderItemSchema]
    created_at: datetime


class CheckoutResultSchema(BaseModel):
    """Результат checkout с URL оплаты."""
    order_id: uuid.UUID
    confirmation_url: str | None = None
    amount: int
    currency: str
    discount_percent: int | None = None
    amount_before_discount: int | None = None


class CheckoutResponse(BaseResponseSchema[CheckoutResultSchema]):
    """Ответ POST /cart/checkout."""
    pass


class OrderResponse(BaseResponseSchema[OrderSchema]):
    """Ответ с одним заказом."""
    pass


class OrdersPageSchema(BaseModel):
    """Страница заказов."""
    items: list[OrderSchema]
    total: int
    page: int
    page_size: int


class OrdersResponse(BaseResponseSchema[OrdersPageSchema]):
    """Ответ GET /orders."""
    pass


class PromoCodeSchema(BaseModel):
    """Промокод."""
    id: uuid.UUID
    code: str
    discount_percent: int
    expires_at: datetime
    usage_count: int
    max_usages: int | None = None
    is_active: bool
    status: str
    created_at: datetime


class CreatePromoCodeRequest(BaseModel):
    """Создание промокода (админ)."""
    code: str = Field(min_length=4, max_length=20)
    discount_percent: int = Field(ge=5, le=100)
    expires_at: datetime
    max_usages: int | None = Field(default=None, ge=1)


class SetPromoCodeActiveRequest(BaseModel):
    """Включение/выключение промокода."""
    is_active: bool


class PromoCodesPageSchema(BaseModel):
    """Страница промокодов."""
    items: list[PromoCodeSchema]
    total: int
    page: int
    page_size: int


class PromoCodesResponse(BaseResponseSchema[PromoCodesPageSchema]):
    """Список промокодов (админ)."""
    pass


class PromoCodeResponse(BaseResponseSchema[PromoCodeSchema]):
    """Ответ с одним промокодом."""
    pass


class CreateProductRequest(BaseModel):
    """Создание товара (админ)."""
    sku: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=128)
    description: str = Field(default="", max_length=2000)
    unit_price: int = Field(ge=0, description="Price in kopecks")
    kind: str = Field(default="credit", max_length=32)
    currency: str = Field(default="RUB", min_length=3, max_length=8)
    is_active: bool = True
    image_urls: list[str] = Field(default_factory=list, max_length=5)
    sale_discount_percent: int | None = None

    @field_validator("sale_discount_percent")
    @classmethod
    def validate_sale_discount(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value < 5 or value > 100 or value % 5 != 0:
            raise ValueError("Sale discount must be 5–100 in steps of 5")
        return value


class UpdateProductRequest(BaseModel):
    """Обновление товара (админ)."""
    name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = Field(default=None, max_length=2000)
    unit_price: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
    image_urls: list[str] | None = Field(default=None, max_length=5)
    sale_discount_percent: int | None = None

    @field_validator("sale_discount_percent")
    @classmethod
    def validate_sale_discount(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value < 5 or value > 100 or value % 5 != 0:
            raise ValueError("Sale discount must be 5–100 in steps of 5")
        return value


class ProductResponse(BaseResponseSchema[ProductSchema]):
    """Ответ с одним товаром."""
    pass


class BalanceSchema(BaseModel):
    """Баланс кредитов по продукту."""
    product_id: uuid.UUID
    sku: str
    name: str
    balance: int


class BalancesResponse(BaseResponseSchema[list[BalanceSchema]]):
    """Список балансов."""
    pass


class BalanceLogSchema(BaseModel):
    """Запись журнала баланса."""
    id: uuid.UUID
    product_id: uuid.UUID
    sku: str
    name: str
    delta: int
    balance_after: int
    reason: str
    reference_type: str
    reference_id: uuid.UUID
    created_at: datetime


class BalanceLogsPageSchema(BaseModel):
    """Страница журнала баланса."""
    items: list[BalanceLogSchema]
    total: int
    page: int
    page_size: int


class BalanceLogsResponse(BaseResponseSchema[BalanceLogsPageSchema]):
    """Ответ GET /balance-logs."""
    pass


class SyncPendingOrdersSchema(BaseModel):
    """Число синхронизированных заказов."""
    synced: int


class SyncPendingOrdersResponse(BaseResponseSchema[SyncPendingOrdersSchema]):
    """Ответ POST /orders/sync."""
    pass
