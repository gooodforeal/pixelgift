"""Представления для ответов API магазина (агрегаты сущностей)."""

from dataclasses import dataclass
from datetime import datetime
import uuid

from app.domain.entities.carts import Cart
from app.domain.entities.orders import Order
from app.domain.entities.products import Product
from app.domain.entities.product_sales import ProductSale
from app.domain.entities.promo_codes import PromoCode
from app.domain.entities.user_balance_logs import UserBalanceLog
from app.domain.entities.user_balances import UserBalance


@dataclass(frozen=True, kw_only=True)
class CartView:
    """Корзина с подгруженными товарами и активными скидками."""

    cart: Cart
    products_by_id: dict[uuid.UUID, Product]
    sales_by_product_id: dict[uuid.UUID, ProductSale] | None = None


@dataclass(frozen=True, kw_only=True)
class ProductView:
    """Товар с опциональной активной распродажей."""

    product: Product
    sale: ProductSale | None = None


@dataclass(frozen=True, kw_only=True)
class BalanceView:
    """Остаток кредита по конкретному товару."""

    balance: UserBalance
    product: Product


@dataclass(frozen=True, kw_only=True)
class BalanceLogView:
    """Запись журнала баланса с названием товара."""

    log: UserBalanceLog
    product: Product


@dataclass(frozen=True, kw_only=True)
class BalanceLogsPage:
    """Страница журнала баланса."""

    items: list[BalanceLogView]
    total: int
    page: int
    page_size: int


@dataclass(frozen=True, kw_only=True)
class OrdersPage:
    """Страница списка заказов."""

    items: list[Order]
    total: int
    page: int
    page_size: int


@dataclass(frozen=True, kw_only=True)
class PromoCodesPage:
    """Страница списка промокодов."""

    items: list[PromoCode]
    total: int
    page: int
    page_size: int


@dataclass(frozen=True, kw_only=True)
class CheckoutResult:
    """Итог checkout: заказ и ссылка на оплату (``None`` при нулевой сумме)."""

    order: Order
    confirmation_url: str | None
