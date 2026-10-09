"""Зависимости каталога, корзины, заказов и промокодов."""

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
    """Use case публичного каталога активных товаров."""
    return ListProductsUseCase(SqlAlchemyUnitOfWork())


def get_get_cart_uc() -> GetCartUseCase:
    """Use case текущей корзины пользователя."""
    return GetCartUseCase(SqlAlchemyUnitOfWork())


def get_add_cart_item_uc() -> AddCartItemUseCase:
    """Use case добавления позиции в корзину."""
    return AddCartItemUseCase(SqlAlchemyUnitOfWork())


def get_update_cart_item_uc() -> UpdateCartItemUseCase:
    """Use case изменения количества в корзине."""
    return UpdateCartItemUseCase(SqlAlchemyUnitOfWork())


def get_remove_cart_item_uc() -> RemoveCartItemUseCase:
    """Use case удаления позиции из корзины."""
    return RemoveCartItemUseCase(SqlAlchemyUnitOfWork())


def get_checkout_cart_uc(
    settings: Settings = Depends(get_settings),
) -> CheckoutCartUseCase:
    """Use case оформления заказа и создания платежа YooKassa."""
    return CheckoutCartUseCase(
        SqlAlchemyUnitOfWork(),
        YooKassaPaymentProvider(settings),
        settings,
    )


def get_get_order_uc() -> GetOrderUseCase:
    """Use case одного заказа пользователя."""
    return GetOrderUseCase(SqlAlchemyUnitOfWork())


def get_list_balances_uc() -> ListUserBalancesUseCase:
    """Use case балансов кредитов по продуктам."""
    return ListUserBalancesUseCase(SqlAlchemyUnitOfWork())


def get_list_balance_logs_uc() -> ListUserBalanceLogsUseCase:
    """Use case журнала изменений баланса."""
    return ListUserBalanceLogsUseCase(SqlAlchemyUnitOfWork())


def get_list_orders_uc() -> ListUserOrdersUseCase:
    """Use case списка заказов пользователя."""
    return ListUserOrdersUseCase(SqlAlchemyUnitOfWork())


def get_yookassa_webhook_uc(
    settings: Settings = Depends(get_settings),
) -> HandleYookassaWebhookUseCase:
    """Use case обработки webhook YooKassa."""
    return HandleYookassaWebhookUseCase(
        SqlAlchemyUnitOfWork(),
        YooKassaPaymentProvider(settings),
    )


def get_sync_pending_orders_uc(
    settings: Settings = Depends(get_settings),
) -> SyncPendingOrdersUseCase:
    """Use case синхронизации статусов ожидающих заказов с YooKassa."""
    return SyncPendingOrdersUseCase(
        SqlAlchemyUnitOfWork(),
        YooKassaPaymentProvider(settings),
    )


def get_list_promo_codes_uc() -> ListPromoCodesUseCase:
    """Use case списка промокодов (админ)."""
    return ListPromoCodesUseCase(SqlAlchemyUnitOfWork())


def get_create_promo_code_uc() -> CreatePromoCodeUseCase:
    """Use case создания промокода."""
    return CreatePromoCodeUseCase(SqlAlchemyUnitOfWork())


def get_set_promo_code_active_uc() -> SetPromoCodeActiveUseCase:
    """Use case включения/выключения промокода."""
    return SetPromoCodeActiveUseCase(SqlAlchemyUnitOfWork())


def get_list_all_products_uc() -> ListAllProductsUseCase:
    """Use case всех товаров для админки."""
    return ListAllProductsUseCase(SqlAlchemyUnitOfWork())


def get_create_product_uc() -> CreateProductUseCase:
    """Use case создания товара."""
    return CreateProductUseCase(SqlAlchemyUnitOfWork())


def get_update_product_uc() -> UpdateProductUseCase:
    """Use case частичного обновления товара."""
    return UpdateProductUseCase(SqlAlchemyUnitOfWork())
