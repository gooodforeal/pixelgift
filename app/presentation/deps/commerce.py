from __future__ import annotations

from fastapi import Depends

from app.application.use_cases.commerce import (
    AddCartItemUseCase,
    CheckoutCartUseCase,
    CreateProductUseCase,
    CreatePromoCodeUseCase,
    GetCartUseCase,
    GetOrderUseCase,
    HandleYookassaWebhookUseCase,
    ListAllProductsUseCase,
    ListProductsUseCase,
    ListPromoCodesUseCase,
    ListUserBalanceLogsUseCase,
    ListUserBalancesUseCase,
    ListUserOrdersUseCase,
    RemoveCartItemUseCase,
    SetPromoCodeActiveUseCase,
    SyncPendingOrdersUseCase,
    UpdateCartItemUseCase,
    UpdateProductUseCase,
)
from app.infrastructure.payments.yookassa import YooKassaPaymentProvider
from app.infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork
from app.presentation.deps.common import get_settings
from app.settings import Settings


def get_list_products_uc() -> ListProductsUseCase:
    return ListProductsUseCase(SqlAlchemyUnitOfWork())


def get_get_cart_uc() -> GetCartUseCase:
    return GetCartUseCase(SqlAlchemyUnitOfWork())


def get_add_cart_item_uc() -> AddCartItemUseCase:
    return AddCartItemUseCase(SqlAlchemyUnitOfWork())


def get_update_cart_item_uc() -> UpdateCartItemUseCase:
    return UpdateCartItemUseCase(SqlAlchemyUnitOfWork())


def get_remove_cart_item_uc() -> RemoveCartItemUseCase:
    return RemoveCartItemUseCase(SqlAlchemyUnitOfWork())


def get_checkout_cart_uc(
    settings: Settings = Depends(get_settings),
) -> CheckoutCartUseCase:
    return CheckoutCartUseCase(
        SqlAlchemyUnitOfWork(),
        YooKassaPaymentProvider(settings),
        settings,
    )


def get_get_order_uc() -> GetOrderUseCase:
    return GetOrderUseCase(SqlAlchemyUnitOfWork())


def get_list_balances_uc() -> ListUserBalancesUseCase:
    return ListUserBalancesUseCase(SqlAlchemyUnitOfWork())


def get_list_balance_logs_uc() -> ListUserBalanceLogsUseCase:
    return ListUserBalanceLogsUseCase(SqlAlchemyUnitOfWork())


def get_list_orders_uc() -> ListUserOrdersUseCase:
    return ListUserOrdersUseCase(SqlAlchemyUnitOfWork())


def get_yookassa_webhook_uc(
    settings: Settings = Depends(get_settings),
) -> HandleYookassaWebhookUseCase:
    return HandleYookassaWebhookUseCase(
        SqlAlchemyUnitOfWork(),
        YooKassaPaymentProvider(settings),
    )


def get_sync_pending_orders_uc(
    settings: Settings = Depends(get_settings),
) -> SyncPendingOrdersUseCase:
    return SyncPendingOrdersUseCase(
        SqlAlchemyUnitOfWork(),
        YooKassaPaymentProvider(settings),
    )


def get_list_promo_codes_uc() -> ListPromoCodesUseCase:
    return ListPromoCodesUseCase(SqlAlchemyUnitOfWork())


def get_create_promo_code_uc() -> CreatePromoCodeUseCase:
    return CreatePromoCodeUseCase(SqlAlchemyUnitOfWork())


def get_set_promo_code_active_uc() -> SetPromoCodeActiveUseCase:
    return SetPromoCodeActiveUseCase(SqlAlchemyUnitOfWork())


def get_list_all_products_uc() -> ListAllProductsUseCase:
    return ListAllProductsUseCase(SqlAlchemyUnitOfWork())


def get_create_product_uc() -> CreateProductUseCase:
    return CreateProductUseCase(SqlAlchemyUnitOfWork())


def get_update_product_uc() -> UpdateProductUseCase:
    return UpdateProductUseCase(SqlAlchemyUnitOfWork())
