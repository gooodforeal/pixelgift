from __future__ import annotations

from datetime import datetime, timezone as dt_timezone
import uuid

from app.application.dto.commerce import (
    AddCartItemCommand,
    CheckoutCartCommand,
    CreateProductCommand,
    CreatePromoCodeCommand,
    GetOrderCommand,
    HandleYookassaWebhookCommand,
    ListBalanceLogsCommand,
    ListOrdersCommand,
    RemoveCartItemCommand,
    UpdateCartItemCommand,
    UpdateProductCommand,
)
from app.application.dto.commerce_views import (
    BalanceLogView,
    BalanceLogsPage,
    BalanceView,
    CartView,
    CheckoutResult,
    OrdersPage,
)
from app.application.ports.payments.base import BasePaymentProvider
from app.application.uow.base import BaseUnitOfWork
from app.domain.entities.carts import Cart
from app.domain.entities.orders import Order, OrderItem, OrderStatus
from app.domain.entities.products import Product, ProductKind
from app.domain.entities.promo_codes import PromoCode
from app.domain.entities.user_balance_logs import BalanceLogReason
from app.domain.entities.user_balances import UserBalance
from app.domain.exceptions.commerce import (
    CartItemNotFoundError,
    EmptyCartError,
    OrderAccessDeniedError,
    OrderNotFoundError,
    ProductAlreadyExistsError,
    ProductNotAvailableError,
    ProductNotFoundError,
    ProductValidationError,
    PromoCodeAlreadyExistsError,
    PromoCodeExpiredError,
    PromoCodeNotFoundError,
)
from app.settings import Settings


async def _products_map(
    uow: BaseUnitOfWork, product_ids: list[uuid.UUID]
) -> dict[uuid.UUID, Product]:
    products = await uow.products.list_by_ids(product_ids)
    return {p.id: p for p in products}


async def _credit_balance(
    uow: BaseUnitOfWork,
    *,
    user_id: uuid.UUID,
    product_id: uuid.UUID,
    quantity: int,
    reference_id: uuid.UUID,
) -> None:
    existing_log = await uow.user_balance_logs.get_by_reason_reference(
        reason=BalanceLogReason.PURCHASE.value,
        reference_type="order_item",
        reference_id=reference_id,
    )
    if existing_log is not None:
        return

    balance = await uow.user_balances.get_by_user_and_product(
        user_id=user_id, product_id=product_id
    )
    created = False
    if balance is None:
        balance = UserBalance(user_id=user_id, product_id=product_id, balance=0)
        created = True

    log = balance.credit(
        delta=quantity,
        reason=BalanceLogReason.PURCHASE,
        reference_type="order_item",
        reference_id=reference_id,
    )
    if created:
        await uow.user_balances.add(balance)
    else:
        await uow.user_balances.update(balance)
    await uow.user_balance_logs.add(log)


async def _fulfill_succeeded_order(
    uow: BaseUnitOfWork,
    order: Order,
    *,
    payment_status: str,
    payment_paid: bool,
) -> bool:
    """Apply YooKassa result to a pending order. Returns True if state changed."""
    if payment_status == "canceled" and order.status == OrderStatus.PENDING:
        order.mark_canceled()
        await uow.orders.update(order)
        return True

    if payment_status != "succeeded" or not payment_paid:
        return False
    if order.status != OrderStatus.PENDING:
        return False

    await _credit_order_items(uow, order)

    if order.promo_code_id is not None:
        promo = await uow.promo_codes.get_by_id(order.promo_code_id)
        if promo is not None:
            promo.register_purchase()
            await uow.promo_codes.update(promo)

    order.mark_succeeded()
    await uow.orders.update(order)
    return True


async def _resolve_promo(
    uow: BaseUnitOfWork, raw_code: str | None
) -> PromoCode | None:
    if raw_code is None or not raw_code.strip():
        return None
    code = PromoCode.normalize_code(raw_code)
    promo = await uow.promo_codes.get_by_code(code)
    if promo is None:
        raise PromoCodeNotFoundError(code)
    promo.assert_usable()
    return promo


async def _credit_order_items(uow: BaseUnitOfWork, order: Order) -> None:
    products = await _products_map(uow, [item.product_id for item in order.items])
    for item in order.items:
        product = products.get(item.product_id)
        if product is None or product.kind != ProductKind.CREDIT:
            continue
        await _credit_balance(
            uow,
            user_id=order.user_id,
            product_id=item.product_id,
            quantity=item.quantity,
            reference_id=item.id,
        )


class ListProductsUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self) -> list[Product]:
        async with self._uow as uow:
            return await uow.products.list_active()


class GetCartUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, actor_id: uuid.UUID) -> CartView:
        async with self._uow as uow:
            cart = await uow.carts.get_by_user_id(actor_id)
            if cart is None:
                cart = Cart(user_id=actor_id)
                await uow.carts.add(cart)
                await uow.commit()
            products = await _products_map(
                uow, [item.product_id for item in cart.items]
            )
            return CartView(cart=cart, products_by_id=products)


class AddCartItemUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: AddCartItemCommand) -> CartView:
        async with self._uow as uow:
            product = await uow.products.get_by_sku(command.sku)
            if product is None:
                raise ProductNotFoundError(sku=command.sku)
            if not product.is_active:
                raise ProductNotAvailableError(command.sku)

            cart = await uow.carts.get_by_user_id(command.actor_id)
            is_new = cart is None
            if is_new:
                cart = Cart(user_id=command.actor_id)
            assert cart is not None
            cart.add_item(product_id=product.id, quantity=command.quantity)
            if is_new:
                await uow.carts.add(cart)
            else:
                await uow.carts.update(cart)
            await uow.commit()
            products = await _products_map(
                uow, [item.product_id for item in cart.items]
            )
            return CartView(cart=cart, products_by_id=products)


class UpdateCartItemUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: UpdateCartItemCommand) -> CartView:
        async with self._uow as uow:
            cart = await uow.carts.get_by_user_id(command.actor_id)
            if cart is None:
                raise CartItemNotFoundError(command.product_id)
            cart.set_quantity(
                product_id=command.product_id, quantity=command.quantity
            )
            await uow.carts.update(cart)
            await uow.commit()
            products = await _products_map(
                uow, [item.product_id for item in cart.items]
            )
            return CartView(cart=cart, products_by_id=products)


class RemoveCartItemUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: RemoveCartItemCommand) -> CartView:
        async with self._uow as uow:
            cart = await uow.carts.get_by_user_id(command.actor_id)
            if cart is None:
                raise CartItemNotFoundError(command.product_id)
            cart.remove_item(product_id=command.product_id)
            await uow.carts.update(cart)
            await uow.commit()
            products = await _products_map(
                uow, [item.product_id for item in cart.items]
            )
            return CartView(cart=cart, products_by_id=products)


class CheckoutCartUseCase:
    def __init__(
        self,
        uow: BaseUnitOfWork,
        payments: BasePaymentProvider,
        settings: Settings,
    ) -> None:
        self._uow = uow
        self._payments = payments
        self._settings = settings

    async def execute(self, command: CheckoutCartCommand) -> CheckoutResult:
        async with self._uow as uow:
            cart = await uow.carts.get_by_user_id(command.actor_id)
            if cart is None or not cart.items:
                raise EmptyCartError()

            products = await _products_map(
                uow, [item.product_id for item in cart.items]
            )
            promo = await _resolve_promo(uow, command.promo_code)

            order = Order(
                user_id=command.actor_id,
                status=OrderStatus.PENDING,
                amount=0,
                currency="RUB",
                idempotency_key=str(uuid.uuid4()),
            )
            total = 0
            order_items: list[OrderItem] = []
            for cart_item in cart.items:
                product = products.get(cart_item.product_id)
                if product is None or not product.is_active:
                    sku = product.sku if product else str(cart_item.product_id)
                    raise ProductNotAvailableError(sku)
                order.currency = product.currency
                line_amount = product.unit_price * cart_item.quantity
                total += line_amount
                order_items.append(
                    OrderItem(
                        order_id=order.id,
                        product_id=product.id,
                        quantity=cart_item.quantity,
                        unit_price=product.unit_price,
                        amount=line_amount,
                    )
                )

            payable = total
            if promo is not None:
                payable = promo.discounted_amount(total)
                order.promo_code_id = promo.id
                order.discount_percent = promo.discount_percent
                order.amount_before_discount = total
            order.amount = payable
            order.items = order_items

            description = "PixelGift: " + ", ".join(
                f"{products[i.product_id].name}×{i.quantity}" for i in order_items
            )

            if payable == 0:
                await _credit_order_items(uow, order)
                if promo is not None:
                    promo.register_purchase()
                    await uow.promo_codes.update(promo)
                order.mark_succeeded()
                await uow.orders.add(order)
                cart.clear()
                await uow.carts.update(cart)
                await uow.commit()
                return CheckoutResult(order=order, confirmation_url=None)

            payment = await self._payments.create_payment(
                amount_kopecks=payable,
                currency=order.currency,
                description=description,
                return_url=self._settings.yookassa_return_url,
                idempotency_key=order.idempotency_key,
                metadata={
                    "order_id": str(order.id),
                    "user_id": str(command.actor_id),
                },
            )
            order.provider_payment_id = payment.provider_payment_id
            order.confirmation_url = payment.confirmation_url

            await uow.orders.add(order)
            cart.clear()
            await uow.carts.update(cart)
            await uow.commit()

            return CheckoutResult(
                order=order, confirmation_url=payment.confirmation_url
            )


class CreatePromoCodeUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: CreatePromoCodeCommand) -> PromoCode:
        code = PromoCode.validate_code(command.code)
        discount = PromoCode.validate_discount_percent(command.discount_percent)
        expires_at = command.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=dt_timezone.utc)
        now = datetime.now(dt_timezone.utc)
        if expires_at <= now:
            raise PromoCodeExpiredError(code)

        async with self._uow as uow:
            existing = await uow.promo_codes.get_by_code(code)
            if existing is not None:
                raise PromoCodeAlreadyExistsError(code)

            promo = PromoCode(
                code=code,
                discount_percent=discount,
                expires_at=expires_at,
                created_by_user_id=command.actor_id,
            )
            await uow.promo_codes.add(promo)
            await uow.commit()
            return promo


class ListPromoCodesUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self) -> list[PromoCode]:
        async with self._uow as uow:
            return await uow.promo_codes.list_all()


class ListAllProductsUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self) -> list[Product]:
        async with self._uow as uow:
            return await uow.products.list_all()


class CreateProductUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: CreateProductCommand) -> Product:
        sku = command.sku.strip().lower()
        name = command.name.strip()
        description = command.description.strip()
        if not (1 <= len(sku) <= 64) or not all(
            ch.isalnum() or ch in "_-" for ch in sku
        ):
            raise ProductValidationError(
                "SKU must be 1–64 chars: letters, digits, _ or -"
            )
        if not name:
            raise ProductValidationError("Product name is required")
        if command.unit_price < 0:
            raise ProductValidationError("Price must be >= 0")
        try:
            kind = ProductKind(command.kind)
        except ValueError as exc:
            raise ProductValidationError(f"Unknown product kind: {command.kind}") from exc

        async with self._uow as uow:
            existing = await uow.products.get_by_sku(sku)
            if existing is not None:
                raise ProductAlreadyExistsError(sku)
            product = Product(
                sku=sku,
                name=name,
                description=description,
                image_urls=Product.validate_image_urls(command.image_urls),
                kind=kind,
                unit_price=command.unit_price,
                currency=command.currency.strip().upper() or "RUB",
                is_active=command.is_active,
            )
            await uow.products.add(product)
            await uow.commit()
            return product


class UpdateProductUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: UpdateProductCommand) -> Product:
        async with self._uow as uow:
            product = await uow.products.get_by_id(command.product_id)
            if product is None:
                raise ProductNotFoundError(product_id=command.product_id)
            if command.name is not None:
                name = command.name.strip()
                if not name:
                    raise ProductValidationError("Product name is required")
                product.name = name
            if command.description is not None:
                product.description = command.description.strip()
            if command.unit_price is not None:
                if command.unit_price < 0:
                    raise ProductValidationError("Price must be >= 0")
                product.unit_price = command.unit_price
            if command.is_active is not None:
                product.is_active = command.is_active
            if command.image_urls is not None:
                product.image_urls = Product.validate_image_urls(command.image_urls)
            product.updated_at = datetime.now(dt_timezone.utc)
            await uow.products.update(product)
            await uow.commit()
            return product


class GetOrderUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: GetOrderCommand) -> Order:
        async with self._uow as uow:
            order = await uow.orders.get_by_id(command.order_id)
            if order is None:
                raise OrderNotFoundError(command.order_id)
            if order.user_id != command.actor_id:
                raise OrderAccessDeniedError(command.order_id, command.actor_id)
            return order


class ListUserBalancesUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, actor_id: uuid.UUID) -> list[BalanceView]:
        async with self._uow as uow:
            balances = await uow.user_balances.list_by_user_id(actor_id)
            if not balances:
                return []
            products = await _products_map(uow, [b.product_id for b in balances])
            views = [
                BalanceView(balance=balance, product=products[balance.product_id])
                for balance in balances
                if balance.product_id in products
            ]
            views.sort(key=lambda v: v.product.name)
            return views


class ListUserBalanceLogsUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: ListBalanceLogsCommand) -> BalanceLogsPage:
        page = max(1, command.page)
        page_size = min(100, max(1, command.page_size))
        offset = (page - 1) * page_size
        async with self._uow as uow:
            total = await uow.user_balance_logs.count_by_user_id(command.actor_id)
            logs = await uow.user_balance_logs.list_by_user_id(
                command.actor_id, limit=page_size, offset=offset
            )
            products = await _products_map(uow, [log.product_id for log in logs])
            items = [
                BalanceLogView(log=log, product=products[log.product_id])
                for log in logs
                if log.product_id in products
            ]
            return BalanceLogsPage(
                items=items, total=total, page=page, page_size=page_size
            )


class ListUserOrdersUseCase:
    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, command: ListOrdersCommand) -> OrdersPage:
        page = max(1, command.page)
        page_size = min(100, max(1, command.page_size))
        offset = (page - 1) * page_size
        async with self._uow as uow:
            total = await uow.orders.count_by_user_id(command.actor_id)
            items = await uow.orders.list_by_user_id(
                command.actor_id, limit=page_size, offset=offset
            )
            return OrdersPage(
                items=items, total=total, page=page, page_size=page_size
            )


class HandleYookassaWebhookUseCase:
    def __init__(
        self,
        uow: BaseUnitOfWork,
        payments: BasePaymentProvider,
    ) -> None:
        self._uow = uow
        self._payments = payments

    async def execute(self, command: HandleYookassaWebhookCommand) -> None:
        obj = command.object_payload
        provider_payment_id = str(obj.get("id") or "")
        if not provider_payment_id:
            return

        payment = await self._payments.get_payment(provider_payment_id)

        async with self._uow as uow:
            order = await uow.orders.get_by_provider_payment_id(provider_payment_id)
            if order is None:
                meta_order_id = payment.metadata.get("order_id")
                if meta_order_id:
                    try:
                        order = await uow.orders.get_by_id(uuid.UUID(meta_order_id))
                    except ValueError:
                        order = None
            if order is None:
                return

            changed = await _fulfill_succeeded_order(
                uow,
                order,
                payment_status=payment.status,
                payment_paid=payment.paid,
            )
            if changed:
                await uow.commit()


class SyncPendingOrdersUseCase:
    """Poll YooKassa for the user's pending orders (fallback when webhook is delayed)."""

    def __init__(
        self,
        uow: BaseUnitOfWork,
        payments: BasePaymentProvider,
    ) -> None:
        self._uow = uow
        self._payments = payments

    async def execute(self, actor_id: uuid.UUID) -> int:
        async with self._uow as uow:
            pending = await uow.orders.list_pending_by_user_id(actor_id, limit=20)

        synced = 0
        for order in pending:
            if not order.provider_payment_id:
                continue
            payment = await self._payments.get_payment(order.provider_payment_id)
            async with self._uow as uow:
                fresh = await uow.orders.get_by_id(order.id)
                if fresh is None or fresh.status != OrderStatus.PENDING:
                    continue
                changed = await _fulfill_succeeded_order(
                    uow,
                    fresh,
                    payment_status=payment.status,
                    payment_paid=payment.paid,
                )
                if changed:
                    await uow.commit()
                    synced += 1
        return synced
