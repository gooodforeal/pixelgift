import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.application.dto.commerce import (
    AddCartItemCommand,
    CheckoutCartCommand,
    CreateProductCommand,
    CreatePromoCodeCommand,
    HandleYookassaWebhookCommand,
    ListBalanceLogsCommand,
    ListPromoCodesCommand,
    SetPromoCodeActiveCommand,
    UpdateProductCommand,
)
from app.application.ports.payments.base import (
    BasePaymentProvider,
    CreatedPayment,
    PaymentInfo,
)
from app.application.use_cases.commerce import (
    AddCartItemUseCase,
    CheckoutCartUseCase,
    CreateProductUseCase,
    CreatePromoCodeUseCase,
    HandleYookassaWebhookUseCase,
    ListAllProductsUseCase,
    ListProductsUseCase,
    ListPromoCodesUseCase,
    ListUserBalanceLogsUseCase,
    ListUserBalancesUseCase,
    SetPromoCodeActiveUseCase,
    UpdateProductUseCase,
)
from app.domain.entities.orders import OrderStatus
from app.domain.entities.promo_codes import PromoCode
from app.domain.exceptions.commerce import (
    BOX_CREDIT_SKU,
    EmptyCartError,
    ProductAlreadyExistsError,
    ProductValidationError,
    PromoCodeAlreadyExistsError,
    PromoCodeExhaustedError,
    PromoCodeExpiredError,
    PromoCodeFormatError,
    PromoCodeInactiveError,
    PromoCodeInvalidDiscountError,
    PromoCodeInvalidMaxUsagesError,
    PromoCodeNotFoundError,
)
from app.settings import Settings
from tests.application.fakes import InMemoryUnitOfWork


class FakePaymentProvider(BasePaymentProvider):
    def __init__(self) -> None:
        self.payments: dict[str, PaymentInfo] = {}
        self.created: list[CreatedPayment] = []

    async def create_payment(
        self,
        *,
        amount_kopecks: int,
        currency: str,
        description: str,
        return_url: str,
        idempotency_key: str,
        metadata: dict[str, str],
    ) -> CreatedPayment:
        payment_id = f"yk_{uuid.uuid4().hex[:12]}"
        created = CreatedPayment(
            provider_payment_id=payment_id,
            confirmation_url=f"https://yookassa.test/pay/{payment_id}",
            status="pending",
        )
        self.created.append(created)
        self.payments[payment_id] = PaymentInfo(
            provider_payment_id=payment_id,
            status="pending",
            paid=False,
            amount_value=f"{amount_kopecks / 100:.2f}",
            currency=currency,
            metadata=metadata,
        )
        return created

    async def get_payment(self, provider_payment_id: str) -> PaymentInfo:
        return self.payments[provider_payment_id]

    def mark_succeeded(self, provider_payment_id: str) -> None:
        current = self.payments[provider_payment_id]
        self.payments[provider_payment_id] = PaymentInfo(
            provider_payment_id=current.provider_payment_id,
            status="succeeded",
            paid=True,
            amount_value=current.amount_value,
            currency=current.currency,
            metadata=current.metadata,
        )


def _future_expiry(*, days: int = 30) -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=days)


async def _seed_promo(
    uow: InMemoryUnitOfWork,
    *,
    code: str = "SALE20",
    discount_percent: int = 20,
    max_usages: int | None = None,
    usage_count: int = 0,
    is_active: bool = True,
    expires_at: datetime | None = None,
) -> PromoCode:
    promo = PromoCode(
        code=code,
        discount_percent=discount_percent,
        expires_at=expires_at or _future_expiry(),
        max_usages=max_usages,
        usage_count=usage_count,
        is_active=is_active,
    )
    await uow.promo_codes.add(promo)
    return promo


class TestCommerceUseCases:
    async def test_lists_seeded_box_credit_product(self):
        uow = InMemoryUnitOfWork()
        products = await ListProductsUseCase(uow).execute()
        assert any(p.sku == BOX_CREDIT_SKU for p in products)

    async def test_cart_checkout_and_webhook_credits_balance(self):
        uow = InMemoryUnitOfWork()
        user_id = uuid.uuid4()
        payments = FakePaymentProvider()
        settings = Settings(yookassa_return_url="http://localhost/profile")

        cart = await AddCartItemUseCase(uow).execute(
            AddCartItemCommand(actor_id=user_id, sku=BOX_CREDIT_SKU, quantity=3)
        )
        assert len(cart.cart.items) == 1
        assert cart.cart.items[0].quantity == 3

        result = await CheckoutCartUseCase(uow, payments, settings).execute(
            CheckoutCartCommand(actor_id=user_id)
        )
        assert result.order.status == OrderStatus.PENDING
        assert result.order.amount == 9900 * 3
        assert result.confirmation_url
        emptied = await uow.carts.get_by_user_id(user_id)
        assert emptied is not None
        assert emptied.items == []

        payments.mark_succeeded(result.order.provider_payment_id or "")
        await HandleYookassaWebhookUseCase(uow, payments).execute(
            HandleYookassaWebhookCommand(
                event="payment.succeeded",
                object_payload={"id": result.order.provider_payment_id},
            )
        )

        balances = await ListUserBalancesUseCase(uow).execute(user_id)
        assert len(balances) == 1
        assert balances[0].balance.balance == 3
        assert balances[0].product.sku == BOX_CREDIT_SKU

        logs = await ListUserBalanceLogsUseCase(uow).execute(
            ListBalanceLogsCommand(actor_id=user_id, page=1, page_size=10)
        )
        assert logs.total == 1
        assert logs.items[0].log.delta == 3

        # idempotent webhook
        await HandleYookassaWebhookUseCase(uow, payments).execute(
            HandleYookassaWebhookCommand(
                event="payment.succeeded",
                object_payload={"id": result.order.provider_payment_id},
            )
        )
        balances = await ListUserBalancesUseCase(uow).execute(user_id)
        assert balances[0].balance.balance == 3

    async def test_sync_pending_orders_credits_balance(self):
        uow = InMemoryUnitOfWork()
        user_id = uuid.uuid4()
        payments = FakePaymentProvider()
        settings = Settings(yookassa_return_url="http://localhost/profile")

        await AddCartItemUseCase(uow).execute(
            AddCartItemCommand(actor_id=user_id, sku=BOX_CREDIT_SKU, quantity=2)
        )
        result = await CheckoutCartUseCase(uow, payments, settings).execute(
            CheckoutCartCommand(actor_id=user_id)
        )
        payments.mark_succeeded(result.order.provider_payment_id or "")

        from app.application.use_cases.commerce import SyncPendingOrdersUseCase

        synced = await SyncPendingOrdersUseCase(uow, payments).execute(user_id)
        assert synced == 1
        balances = await ListUserBalancesUseCase(uow).execute(user_id)
        assert balances[0].balance.balance == 2

    async def test_checkout_empty_cart_fails(self):
        uow = InMemoryUnitOfWork()
        payments = FakePaymentProvider()
        settings = Settings()
        with pytest.raises(EmptyCartError):
            await CheckoutCartUseCase(uow, payments, settings).execute(
                CheckoutCartCommand(actor_id=uuid.uuid4())
            )

    async def test_checkout_with_promo_discount(self):
        uow = InMemoryUnitOfWork()
        user_id = uuid.uuid4()
        payments = FakePaymentProvider()
        settings = Settings(yookassa_return_url="http://localhost/profile")
        promo = await _seed_promo(uow, code="SALE20", discount_percent=20)

        await AddCartItemUseCase(uow).execute(
            AddCartItemCommand(actor_id=user_id, sku=BOX_CREDIT_SKU, quantity=1)
        )
        result = await CheckoutCartUseCase(uow, payments, settings).execute(
            CheckoutCartCommand(actor_id=user_id, promo_code="sale20")
        )
        assert result.order.amount == 7920
        assert result.order.amount_before_discount == 9900
        assert result.order.discount_percent == 20
        assert result.order.promo_code_id == promo.id
        assert payments.created[0]
        assert result.confirmation_url

        payments.mark_succeeded(result.order.provider_payment_id or "")
        await HandleYookassaWebhookUseCase(uow, payments).execute(
            HandleYookassaWebhookCommand(
                event="payment.succeeded",
                object_payload={"id": result.order.provider_payment_id},
            )
        )
        updated = await uow.promo_codes.get_by_id(promo.id)
        assert updated is not None
        assert updated.usage_count == 1

    async def test_checkout_with_100_percent_promo_is_free(self):
        uow = InMemoryUnitOfWork()
        user_id = uuid.uuid4()
        payments = FakePaymentProvider()
        settings = Settings(yookassa_return_url="http://localhost/profile")
        promo = await _seed_promo(uow, code="FREE100", discount_percent=100)

        await AddCartItemUseCase(uow).execute(
            AddCartItemCommand(actor_id=user_id, sku=BOX_CREDIT_SKU, quantity=2)
        )
        result = await CheckoutCartUseCase(uow, payments, settings).execute(
            CheckoutCartCommand(actor_id=user_id, promo_code="FREE100")
        )
        assert result.order.status == OrderStatus.SUCCEEDED
        assert result.order.amount == 0
        assert result.confirmation_url is None
        assert payments.created == []

        balances = await ListUserBalancesUseCase(uow).execute(user_id)
        assert balances[0].balance.balance == 2
        updated = await uow.promo_codes.get_by_id(promo.id)
        assert updated is not None
        assert updated.usage_count == 1

    async def test_checkout_unknown_promo_fails(self):
        uow = InMemoryUnitOfWork()
        user_id = uuid.uuid4()
        payments = FakePaymentProvider()
        settings = Settings()
        await AddCartItemUseCase(uow).execute(
            AddCartItemCommand(actor_id=user_id, sku=BOX_CREDIT_SKU, quantity=1)
        )
        with pytest.raises(PromoCodeNotFoundError):
            await CheckoutCartUseCase(uow, payments, settings).execute(
                CheckoutCartCommand(actor_id=user_id, promo_code="NOPE")
            )

    async def test_checkout_inactive_promo_fails(self):
        uow = InMemoryUnitOfWork()
        user_id = uuid.uuid4()
        payments = FakePaymentProvider()
        settings = Settings(yookassa_return_url="http://localhost/profile")
        await _seed_promo(uow, code="OFF1", is_active=False)
        await AddCartItemUseCase(uow).execute(
            AddCartItemCommand(actor_id=user_id, sku=BOX_CREDIT_SKU, quantity=1)
        )
        with pytest.raises(PromoCodeInactiveError):
            await CheckoutCartUseCase(uow, payments, settings).execute(
                CheckoutCartCommand(actor_id=user_id, promo_code="OFF1")
            )

    async def test_checkout_exhausted_promo_fails(self):
        uow = InMemoryUnitOfWork()
        user_id = uuid.uuid4()
        payments = FakePaymentProvider()
        settings = Settings(yookassa_return_url="http://localhost/profile")
        await _seed_promo(uow, code="LIMIT1", max_usages=2, usage_count=2)
        await AddCartItemUseCase(uow).execute(
            AddCartItemCommand(actor_id=user_id, sku=BOX_CREDIT_SKU, quantity=1)
        )
        with pytest.raises(PromoCodeExhaustedError):
            await CheckoutCartUseCase(uow, payments, settings).execute(
                CheckoutCartCommand(actor_id=user_id, promo_code="LIMIT1")
            )

    async def test_checkout_expired_promo_fails(self):
        uow = InMemoryUnitOfWork()
        user_id = uuid.uuid4()
        payments = FakePaymentProvider()
        settings = Settings(yookassa_return_url="http://localhost/profile")
        await _seed_promo(
            uow,
            code="OLD1",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        await AddCartItemUseCase(uow).execute(
            AddCartItemCommand(actor_id=user_id, sku=BOX_CREDIT_SKU, quantity=1)
        )
        with pytest.raises(PromoCodeExpiredError):
            await CheckoutCartUseCase(uow, payments, settings).execute(
                CheckoutCartCommand(actor_id=user_id, promo_code="OLD1")
            )

    async def test_create_and_list_promo_codes(self):
        uow = InMemoryUnitOfWork()
        admin_id = uuid.uuid4()
        promo = await CreatePromoCodeUseCase(uow).execute(
            CreatePromoCodeCommand(
                actor_id=admin_id,
                code="spring",
                discount_percent=15,
                expires_at=_future_expiry(),
                max_usages=50,
            )
        )
        assert promo.code == "SPRING"
        assert promo.discount_percent == 15
        assert promo.max_usages == 50
        assert promo.resolve_status() == "active"
        listed = await ListPromoCodesUseCase(uow).execute(
            ListPromoCodesCommand(page=1, page_size=10)
        )
        assert listed.total == 1
        assert listed.items[0].id == promo.id

        with pytest.raises(PromoCodeAlreadyExistsError):
            await CreatePromoCodeUseCase(uow).execute(
                CreatePromoCodeCommand(
                    actor_id=admin_id,
                    code="SPRING",
                    discount_percent=10,
                    expires_at=_future_expiry(),
                )
            )

    async def test_deactivate_and_reactivate_promo_code(self):
        uow = InMemoryUnitOfWork()
        admin_id = uuid.uuid4()
        promo = await CreatePromoCodeUseCase(uow).execute(
            CreatePromoCodeCommand(
                actor_id=admin_id,
                code="TOGGLE",
                discount_percent=10,
                expires_at=_future_expiry(),
            )
        )
        off = await SetPromoCodeActiveUseCase(uow).execute(
            SetPromoCodeActiveCommand(
                actor_id=admin_id,
                promo_id=promo.id,
                is_active=False,
            )
        )
        assert off.is_active is False
        assert off.resolve_status() == "inactive"

        on = await SetPromoCodeActiveUseCase(uow).execute(
            SetPromoCodeActiveCommand(
                actor_id=admin_id,
                promo_id=promo.id,
                is_active=True,
            )
        )
        assert on.is_active is True
        assert on.resolve_status() == "active"

    async def test_create_promo_rejects_bad_input(self):
        uow = InMemoryUnitOfWork()
        admin_id = uuid.uuid4()
        with pytest.raises(PromoCodeFormatError):
            await CreatePromoCodeUseCase(uow).execute(
                CreatePromoCodeCommand(
                    actor_id=admin_id,
                    code="AB",
                    discount_percent=10,
                    expires_at=_future_expiry(),
                )
            )
        with pytest.raises(PromoCodeInvalidDiscountError):
            await CreatePromoCodeUseCase(uow).execute(
                CreatePromoCodeCommand(
                    actor_id=admin_id,
                    code="GOOD1",
                    discount_percent=12,
                    expires_at=_future_expiry(),
                )
            )
        with pytest.raises(PromoCodeExpiredError):
            await CreatePromoCodeUseCase(uow).execute(
                CreatePromoCodeCommand(
                    actor_id=admin_id,
                    code="OLDIE",
                    discount_percent=10,
                    expires_at=datetime.now(timezone.utc) - timedelta(days=1),
                )
            )
        with pytest.raises(PromoCodeInvalidMaxUsagesError):
            await CreatePromoCodeUseCase(uow).execute(
                CreatePromoCodeCommand(
                    actor_id=admin_id,
                    code="ZERO1",
                    discount_percent=10,
                    expires_at=_future_expiry(),
                    max_usages=0,
                )
            )

    async def test_create_and_update_product(self):
        uow = InMemoryUnitOfWork()
        admin_id = uuid.uuid4()
        product = await CreateProductUseCase(uow).execute(
            CreateProductCommand(
                actor_id=admin_id,
                sku="Extra_Box",
                name="Доп. бокс",
                description="Ещё один кредит",
                unit_price=14900,
            )
        )
        assert product.sku == "extra_box"
        assert product.description == "Ещё один кредит"
        listed = await ListAllProductsUseCase(uow).execute()
        assert any(p.id == product.id for p in listed)

        updated = await UpdateProductUseCase(uow).execute(
            UpdateProductCommand(
                actor_id=admin_id,
                product_id=product.id,
                name="Доп. бокс Pro",
                description="Обновлённое описание",
                unit_price=19900,
                is_active=False,
            )
        )
        assert updated.name == "Доп. бокс Pro"
        assert updated.unit_price == 19900
        assert updated.is_active is False
        active = await ListProductsUseCase(uow).execute()
        assert all(p.id != product.id for p in active)

        with pytest.raises(ProductAlreadyExistsError):
            await CreateProductUseCase(uow).execute(
                CreateProductCommand(
                    actor_id=admin_id,
                    sku="extra_box",
                    name="Dup",
                    description="",
                    unit_price=100,
                )
            )

        with pytest.raises(ProductValidationError):
            await CreateProductUseCase(uow).execute(
                CreateProductCommand(
                    actor_id=admin_id,
                    sku="bad sku!",
                    name="X",
                    description="",
                    unit_price=100,
                )
            )
