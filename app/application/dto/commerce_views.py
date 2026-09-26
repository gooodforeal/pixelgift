from dataclasses import dataclass
from datetime import datetime
import uuid

from app.domain.entities.carts import Cart
from app.domain.entities.orders import Order
from app.domain.entities.products import Product
from app.domain.entities.product_sales import ProductSale
from app.domain.entities.user_balance_logs import UserBalanceLog
from app.domain.entities.user_balances import UserBalance


@dataclass(frozen=True, kw_only=True)
class CartView:
    cart: Cart
    products_by_id: dict[uuid.UUID, Product]
    sales_by_product_id: dict[uuid.UUID, ProductSale] | None = None


@dataclass(frozen=True, kw_only=True)
class ProductView:
    product: Product
    sale: ProductSale | None = None


@dataclass(frozen=True, kw_only=True)
class BalanceView:
    balance: UserBalance
    product: Product


@dataclass(frozen=True, kw_only=True)
class BalanceLogView:
    log: UserBalanceLog
    product: Product


@dataclass(frozen=True, kw_only=True)
class BalanceLogsPage:
    items: list[BalanceLogView]
    total: int
    page: int
    page_size: int


@dataclass(frozen=True, kw_only=True)
class OrdersPage:
    items: list[Order]
    total: int
    page: int
    page_size: int


@dataclass(frozen=True, kw_only=True)
class CheckoutResult:
    order: Order
    confirmation_url: str | None
