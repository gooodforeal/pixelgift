from __future__ import annotations

from app.application.dto.commerce_views import (
    BalanceLogView,
    BalanceView,
    CartView,
    ProductView,
)
from app.domain.entities.orders import Order
from app.domain.entities.products import Product
from app.domain.entities.product_sales import ProductSale
from app.presentation.schemas.commerce import (
    BalanceLogSchema,
    BalanceLogsPageSchema,
    BalanceSchema,
    CartItemSchema,
    CartSchema,
    OrderItemSchema,
    OrderSchema,
    OrdersPageSchema,
    ProductSchema,
)


def _active_sale(sale: ProductSale | None) -> ProductSale | None:
    if sale is None or not sale.is_active:
        return None
    return sale


def product_to_schema(
    product: Product,
    sale: ProductSale | None = None,
) -> ProductSchema:
    active = _active_sale(sale)
    return ProductSchema(
        id=product.id,
        sku=product.sku,
        name=product.name,
        description=product.description,
        image_urls=list(product.image_urls),
        kind=product.kind.value,
        unit_price=product.unit_price,
        currency=product.currency,
        is_active=product.is_active,
        sale_discount_percent=active.discount_percent if active else None,
        sale_unit_price=active.apply(product.unit_price) if active else None,
    )


def product_view_to_schema(view: ProductView) -> ProductSchema:
    return product_to_schema(view.product, view.sale)


def cart_view_to_schema(view: CartView) -> CartSchema:
    sales = view.sales_by_product_id or {}
    items: list[CartItemSchema] = []
    total = 0
    currency = "RUB"
    for item in view.cart.items:
        product = view.products_by_id.get(item.product_id)
        if product is None:
            continue
        sale = _active_sale(sales.get(product.id))
        unit_price = sale.apply(product.unit_price) if sale else product.unit_price
        amount = unit_price * item.quantity
        total += amount
        currency = product.currency
        items.append(
            CartItemSchema(
                product_id=product.id,
                sku=product.sku,
                name=product.name,
                unit_price=unit_price,
                currency=product.currency,
                quantity=item.quantity,
                amount=amount,
                compare_at_price=product.unit_price if sale else None,
                sale_discount_percent=sale.discount_percent if sale else None,
            )
        )
    return CartSchema(
        id=view.cart.id,
        items=items,
        total_amount=total,
        currency=currency,
    )


def order_to_schema(order: Order) -> OrderSchema:
    return OrderSchema(
        id=order.id,
        status=order.status.value,
        amount=order.amount,
        currency=order.currency,
        confirmation_url=order.confirmation_url,
        paid_at=order.paid_at,
        discount_percent=order.discount_percent,
        amount_before_discount=order.amount_before_discount,
        items=[
            OrderItemSchema(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                amount=item.amount,
            )
            for item in order.items
        ],
        created_at=order.created_at,
    )


def balance_view_to_schema(view: BalanceView) -> BalanceSchema:
    return BalanceSchema(
        product_id=view.product.id,
        sku=view.product.sku,
        name=view.product.name,
        balance=view.balance.balance,
    )


def balance_log_view_to_schema(view: BalanceLogView) -> BalanceLogSchema:
    return BalanceLogSchema(
        id=view.log.id,
        product_id=view.product.id,
        sku=view.product.sku,
        name=view.product.name,
        delta=view.log.delta,
        balance_after=view.log.balance_after,
        reason=view.log.reason.value,
        reference_type=view.log.reference_type,
        reference_id=view.log.reference_id,
        created_at=view.log.created_at,
    )


def balance_logs_page_to_schema(
    *,
    items: list[BalanceLogView],
    total: int,
    page: int,
    page_size: int,
) -> BalanceLogsPageSchema:
    return BalanceLogsPageSchema(
        items=[balance_log_view_to_schema(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


def orders_page_to_schema(
    *,
    items: list[Order],
    total: int,
    page: int,
    page_size: int,
) -> OrdersPageSchema:
    return OrdersPageSchema(
        items=[order_to_schema(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )
