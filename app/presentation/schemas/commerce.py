from datetime import datetime
import uuid

from pydantic import BaseModel, Field

from app.presentation.schemas.base import BaseResponseSchema


class ProductSchema(BaseModel):
    id: uuid.UUID
    sku: str
    name: str
    description: str = ""
    image_urls: list[str] = Field(default_factory=list)
    kind: str
    unit_price: int
    currency: str
    is_active: bool


class ProductsResponse(BaseResponseSchema[list[ProductSchema]]):
    pass


class CartItemSchema(BaseModel):
    product_id: uuid.UUID
    sku: str
    name: str
    unit_price: int
    currency: str
    quantity: int
    amount: int


class CartSchema(BaseModel):
    id: uuid.UUID
    items: list[CartItemSchema]
    total_amount: int
    currency: str = "RUB"


class CartResponse(BaseResponseSchema[CartSchema]):
    pass


class AddCartItemRequest(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    quantity: int = Field(default=1, ge=1, le=100)


class UpdateCartItemRequest(BaseModel):
    quantity: int = Field(ge=1, le=100)


class CheckoutRequest(BaseModel):
    promo_code: str | None = Field(default=None, max_length=20)


class OrderItemSchema(BaseModel):
    product_id: uuid.UUID
    quantity: int
    unit_price: int
    amount: int


class OrderSchema(BaseModel):
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
    order_id: uuid.UUID
    confirmation_url: str | None = None
    amount: int
    currency: str
    discount_percent: int | None = None
    amount_before_discount: int | None = None


class CheckoutResponse(BaseResponseSchema[CheckoutResultSchema]):
    pass


class OrderResponse(BaseResponseSchema[OrderSchema]):
    pass


class OrdersPageSchema(BaseModel):
    items: list[OrderSchema]
    total: int
    page: int
    page_size: int


class OrdersResponse(BaseResponseSchema[OrdersPageSchema]):
    pass


class PromoCodeSchema(BaseModel):
    id: uuid.UUID
    code: str
    discount_percent: int
    expires_at: datetime
    usage_count: int
    is_active: bool
    created_at: datetime


class CreatePromoCodeRequest(BaseModel):
    code: str = Field(min_length=4, max_length=20)
    discount_percent: int = Field(ge=5, le=100)
    expires_at: datetime


class PromoCodesResponse(BaseResponseSchema[list[PromoCodeSchema]]):
    pass


class PromoCodeResponse(BaseResponseSchema[PromoCodeSchema]):
    pass


class CreateProductRequest(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=128)
    description: str = Field(default="", max_length=2000)
    unit_price: int = Field(ge=0, description="Price in kopecks")
    kind: str = Field(default="credit", max_length=32)
    currency: str = Field(default="RUB", min_length=3, max_length=8)
    is_active: bool = True
    image_urls: list[str] = Field(default_factory=list, max_length=5)


class UpdateProductRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = Field(default=None, max_length=2000)
    unit_price: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
    image_urls: list[str] | None = Field(default=None, max_length=5)


class ProductResponse(BaseResponseSchema[ProductSchema]):
    pass


class BalanceSchema(BaseModel):
    product_id: uuid.UUID
    sku: str
    name: str
    balance: int


class BalancesResponse(BaseResponseSchema[list[BalanceSchema]]):
    pass


class BalanceLogSchema(BaseModel):
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
    items: list[BalanceLogSchema]
    total: int
    page: int
    page_size: int


class BalanceLogsResponse(BaseResponseSchema[BalanceLogsPageSchema]):
    pass


class SyncPendingOrdersSchema(BaseModel):
    synced: int


class SyncPendingOrdersResponse(BaseResponseSchema[SyncPendingOrdersSchema]):
    pass
