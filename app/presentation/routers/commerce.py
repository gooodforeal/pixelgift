"""Каталог, корзина, заказы, балансы и webhook YooKassa."""

from __future__ import annotations

from typing import Any
import uuid

from fastapi import APIRouter, Depends, Query, Request

from app.application.dto.commerce import (
    AddCartItemCommand,
    CheckoutCartCommand,
    GetOrderCommand,
    HandleYookassaWebhookCommand,
    ListBalanceLogsCommand,
    ListOrdersCommand,
    RemoveCartItemCommand,
    UpdateCartItemCommand,
)
from app.application.use_cases.commerce import (
    AddCartItemUseCase,
    CheckoutCartUseCase,
    GetCartUseCase,
    GetOrderUseCase,
    HandleYookassaWebhookUseCase,
    ListProductsUseCase,
    ListUserBalanceLogsUseCase,
    ListUserBalancesUseCase,
    ListUserOrdersUseCase,
    RemoveCartItemUseCase,
    SyncPendingOrdersUseCase,
    UpdateCartItemUseCase,
)
from app.presentation.deps.commerce import (
    get_add_cart_item_uc,
    get_checkout_cart_uc,
    get_get_cart_uc,
    get_get_order_uc,
    get_list_balance_logs_uc,
    get_list_balances_uc,
    get_list_orders_uc,
    get_list_products_uc,
    get_remove_cart_item_uc,
    get_sync_pending_orders_uc,
    get_update_cart_item_uc,
    get_yookassa_webhook_uc,
)
from app.presentation.deps.users import get_current_user_id
from app.presentation.schemas.commerce import (
    AddCartItemRequest,
    BalanceLogsResponse,
    BalancesResponse,
    CartResponse,
    CheckoutRequest,
    CheckoutResponse,
    CheckoutResultSchema,
    OrderResponse,
    OrdersResponse,
    ProductsResponse,
    SyncPendingOrdersResponse,
    SyncPendingOrdersSchema,
    UpdateCartItemRequest,
)
from app.presentation.schemas.commerce_mappers import (
    balance_logs_page_to_schema,
    balance_view_to_schema,
    cart_view_to_schema,
    order_to_schema,
    orders_page_to_schema,
    product_view_to_schema,
)

router = APIRouter(tags=["commerce"])


@router.get("/products", response_model=ProductsResponse)
async def list_products(
    uc: ListProductsUseCase = Depends(get_list_products_uc),
) -> ProductsResponse:
    """GET /products — активные товары."""
    views = await uc.execute()
    return ProductsResponse(
        message="ok",
        result=[product_view_to_schema(v) for v in views],
    )


@router.get("/cart", response_model=CartResponse)
async def get_cart(
    actor_id: uuid.UUID = Depends(get_current_user_id),
    uc: GetCartUseCase = Depends(get_get_cart_uc),
) -> CartResponse:
    """GET /cart — корзина текущего пользователя."""
    view = await uc.execute(actor_id)
    return CartResponse(message="ok", result=cart_view_to_schema(view))


@router.post("/cart/items", response_model=CartResponse)
async def add_cart_item(
    body: AddCartItemRequest,
    actor_id: uuid.UUID = Depends(get_current_user_id),
    uc: AddCartItemUseCase = Depends(get_add_cart_item_uc),
) -> CartResponse:
    """POST /cart/items — добавить SKU в корзину."""
    view = await uc.execute(
        AddCartItemCommand(
            actor_id=actor_id, sku=body.sku, quantity=body.quantity
        )
    )
    return CartResponse(message="ok", result=cart_view_to_schema(view))


@router.patch("/cart/items/{product_id}", response_model=CartResponse)
async def update_cart_item(
    product_id: uuid.UUID,
    body: UpdateCartItemRequest,
    actor_id: uuid.UUID = Depends(get_current_user_id),
    uc: UpdateCartItemUseCase = Depends(get_update_cart_item_uc),
) -> CartResponse:
    """PATCH /cart/items/{product_id} — изменить количество."""
    view = await uc.execute(
        UpdateCartItemCommand(
            actor_id=actor_id, product_id=product_id, quantity=body.quantity
        )
    )
    return CartResponse(message="ok", result=cart_view_to_schema(view))


@router.delete("/cart/items/{product_id}", response_model=CartResponse)
async def remove_cart_item(
    product_id: uuid.UUID,
    actor_id: uuid.UUID = Depends(get_current_user_id),
    uc: RemoveCartItemUseCase = Depends(get_remove_cart_item_uc),
) -> CartResponse:
    """DELETE /cart/items/{product_id} — удалить позицию."""
    view = await uc.execute(
        RemoveCartItemCommand(actor_id=actor_id, product_id=product_id)
    )
    return CartResponse(message="ok", result=cart_view_to_schema(view))


@router.post("/cart/checkout", response_model=CheckoutResponse)
async def checkout_cart(
    body: CheckoutRequest = CheckoutRequest(),
    actor_id: uuid.UUID = Depends(get_current_user_id),
    uc: CheckoutCartUseCase = Depends(get_checkout_cart_uc),
) -> CheckoutResponse:
    """POST /cart/checkout — создать заказ и платёж."""
    result = await uc.execute(
        CheckoutCartCommand(
            actor_id=actor_id,
            promo_code=body.promo_code,
        )
    )
    return CheckoutResponse(
        message="ok",
        result=CheckoutResultSchema(
            order_id=result.order.id,
            confirmation_url=result.confirmation_url,
            amount=result.order.amount,
            currency=result.order.currency,
            discount_percent=result.order.discount_percent,
            amount_before_discount=result.order.amount_before_discount,
        ),
    )


@router.post("/orders/sync", response_model=SyncPendingOrdersResponse)
async def sync_pending_orders(
    actor_id: uuid.UUID = Depends(get_current_user_id),
    uc: SyncPendingOrdersUseCase = Depends(get_sync_pending_orders_uc),
) -> SyncPendingOrdersResponse:
    """POST /orders/sync — синхронизация pending с YooKassa."""
    synced = await uc.execute(actor_id)
    return SyncPendingOrdersResponse(
        message="ok",
        result=SyncPendingOrdersSchema(synced=synced),
    )


@router.get("/orders", response_model=OrdersResponse)
async def list_orders(
    actor_id: uuid.UUID = Depends(get_current_user_id),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    uc: ListUserOrdersUseCase = Depends(get_list_orders_uc),
) -> OrdersResponse:
    """GET /orders — заказы пользователя."""
    result = await uc.execute(
        ListOrdersCommand(actor_id=actor_id, page=page, page_size=page_size)
    )
    return OrdersResponse(
        message="ok",
        result=orders_page_to_schema(
            items=result.items,
            total=result.total,
            page=result.page,
            page_size=result.page_size,
        ),
    )


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: uuid.UUID,
    actor_id: uuid.UUID = Depends(get_current_user_id),
    uc: GetOrderUseCase = Depends(get_get_order_uc),
) -> OrderResponse:
    """GET /orders/{order_id} — один заказ."""
    order = await uc.execute(GetOrderCommand(actor_id=actor_id, order_id=order_id))
    return OrderResponse(message="ok", result=order_to_schema(order))


@router.get("/balances", response_model=BalancesResponse)
async def list_balances(
    actor_id: uuid.UUID = Depends(get_current_user_id),
    uc: ListUserBalancesUseCase = Depends(get_list_balances_uc),
) -> BalancesResponse:
    """GET /balances — балансы кредитов."""
    views = await uc.execute(actor_id)
    return BalancesResponse(
        message="ok",
        result=[balance_view_to_schema(v) for v in views],
    )


@router.get("/balance-logs", response_model=BalanceLogsResponse)
async def list_balance_logs(
    actor_id: uuid.UUID = Depends(get_current_user_id),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    uc: ListUserBalanceLogsUseCase = Depends(get_list_balance_logs_uc),
) -> BalanceLogsResponse:
    """GET /balance-logs — журнал баланса."""
    result = await uc.execute(
        ListBalanceLogsCommand(actor_id=actor_id, page=page, page_size=page_size)
    )
    return BalanceLogsResponse(
        message="ok",
        result=balance_logs_page_to_schema(
            items=result.items,
            total=result.total,
            page=result.page,
            page_size=result.page_size,
        ),
    )


@router.post("/payments/yookassa/webhook")
async def yookassa_webhook(
    request: Request,
    uc: HandleYookassaWebhookUseCase = Depends(get_yookassa_webhook_uc),
) -> dict[str, str]:
    """POST /payments/yookassa/webhook — уведомления платёжки."""
    payload: dict[str, Any] = await request.json()
    event = str(payload.get("event") or "")
    obj = payload.get("object")
    if not isinstance(obj, dict):
        obj = {}
    await uc.execute(
        HandleYookassaWebhookCommand(event=event, object_payload=obj)
    )
    return {"status": "ok"}
