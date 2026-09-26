from datetime import datetime
from collections.abc import Sequence
from typing import Optional
import uuid

from app.application.ports.llm.base import BaseLlmClient, LlmMessage
from app.application.uow.base import BaseUnitOfWork
from app.domain.aggregates.boxes import Box, BoxStatus
from app.domain.entities.box_designs import BoxDesign
from app.domain.entities.design_assets import DesignAsset
from app.domain.entities.design_ratings import DesignRating
from app.domain.entities.media_files import MediaFile
from app.domain.entities.notification_jobs import (
    NotificationJob,
    NotificationJobStatus,
    NotificationTemplate,
)
from app.domain.entities.support_tickets import SupportTicket, SupportTicketStatus
from app.domain.entities.telegram_login_challenges import TelegramLoginChallenge
from app.domain.entities.user_sessions import UserSession
from app.domain.entities.assistant_chat_messages import AssistantChatMessage
from app.domain.entities.assistant_chat_threads import AssistantChatThread
from app.domain.entities.carts import Cart
from app.domain.entities.orders import Order
from app.domain.entities.products import Product, ProductKind
from app.domain.entities.product_sales import ProductSale
from app.domain.entities.promo_codes import PromoCode
from app.domain.entities.user_balance_logs import UserBalanceLog
from app.domain.entities.user_balances import UserBalance
from app.domain.entities.users import User
from app.domain.exceptions.commerce import BOX_CREDIT_SKU
from app.domain.repository.assistant_chat_messages import (
    BaseAssistantChatMessagesRepository,
)
from app.domain.repository.assistant_chat_threads import (
    BaseAssistantChatThreadsRepository,
)
from app.domain.repository.box_designs import BaseBoxDesignsRepository
from app.domain.repository.boxes import BaseBoxesRepository
from app.domain.repository.carts import BaseCartsRepository
from app.domain.repository.design_assets import BaseDesignAssetsRepository
from app.domain.repository.design_ratings import (
    BaseDesignRatingsRepository,
    DesignRatingAggregate,
)
from app.domain.repository.media_files import BaseMediaFilesRepository
from app.domain.repository.notification_jobs import BaseNotificationJobsRepository
from app.domain.repository.orders import BaseOrdersRepository
from app.domain.repository.products import BaseProductsRepository
from app.domain.repository.product_sales import BaseProductSalesRepository
from app.domain.repository.promo_codes import BasePromoCodesRepository
from app.domain.repository.support_tickets import BaseSupportTicketsRepository
from app.domain.repository.telegram_login_challenges import (
    BaseTelegramLoginChallengesRepository,
)
from app.domain.repository.user_balance_logs import BaseUserBalanceLogsRepository
from app.domain.repository.user_balances import BaseUserBalancesRepository
from app.domain.repository.user_sessions import BaseUserSessionsRepository
from app.domain.repository.users import BaseUsersRepository
from app.domain.values.public_slug import PublicSlug

BOX_CREDIT_PRODUCT_ID = uuid.UUID("a1b2c3d4-e5f6-4789-a012-3456789abcde")


def seed_box_credit_product(uow: "InMemoryUnitOfWork") -> Product:
    existing = uow.products.items.get(BOX_CREDIT_PRODUCT_ID)
    if existing is not None:
        return existing
    product = Product(
        id=BOX_CREDIT_PRODUCT_ID,
        sku=BOX_CREDIT_SKU,
        name="Бокс",
        description=(
            "Кредит на создание одного виртуального бокса-подарка. "
            "После оплаты кредит появится на балансе и спишется при создании бокса."
        ),
        image_urls=[],
        kind=ProductKind.CREDIT,
        unit_price=9900,
        currency="RUB",
        is_active=True,
    )
    uow.products.items[product.id] = product
    return product


async def grant_box_credits(
    uow: "InMemoryUnitOfWork", *, user_id: uuid.UUID, quantity: int = 10
) -> UserBalance:
    product = seed_box_credit_product(uow)
    balance = await uow.user_balances.get_by_user_and_product(
        user_id=user_id, product_id=product.id
    )
    if balance is None:
        balance = UserBalance(user_id=user_id, product_id=product.id, balance=quantity)
        await uow.user_balances.add(balance)
    else:
        balance.balance = quantity
        await uow.user_balances.update(balance)
    return balance


class FakeLlmClient(BaseLlmClient):
    def __init__(self, reply: str = "ok") -> None:
        self.reply = reply
        self.calls: list[dict[str, object]] = []
        self.error: Exception | None = None

    async def complete(
        self,
        *,
        messages: Sequence[LlmMessage],
        system: str,
    ) -> str:
        self.calls.append({"messages": list(messages), "system": system})
        if self.error is not None:
            raise self.error
        return self.reply


class InMemoryBoxesRepository(BaseBoxesRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, Box] = {}

    async def add(self, entity: Box) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[Box]:
        return self.items.get(id_)

    async def update(self, entity: Box) -> Box:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)

    async def get_by_public_slug(self, public_slug: PublicSlug) -> Box | None:
        for box in self.items.values():
            if box.public_slug == public_slug:
                return box
        return None

    async def list_by_owner_id(
        self,
        owner_id: uuid.UUID,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Box]:
        boxes = [box for box in self.items.values() if box.owner_id == owner_id]
        boxes.sort(key=lambda box: box.created_at, reverse=True)
        if offset:
            boxes = boxes[offset:]
        if limit is not None:
            boxes = boxes[:limit]
        return boxes

    async def count_by_owner_id(self, owner_id: uuid.UUID) -> int:
        return sum(1 for box in self.items.values() if box.owner_id == owner_id)

    async def count_statuses_by_owner_id(
        self,
        owner_id: uuid.UUID,
    ) -> dict[str, int]:
        counts: dict[str, int] = {}
        for box in self.items.values():
            if box.owner_id != owner_id:
                continue
            key = box.status.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    async def count_opened_between(
        self,
        *,
        start: datetime,
        end: datetime,
    ) -> int:
        return sum(
            1
            for box in self.items.values()
            if box.first_opened_at is not None
            and start <= box.first_opened_at < end
        )

    async def claim_due_to_activate(
        self,
        now: datetime,
        *,
        limit: int = 50,
    ) -> list[Box]:
        due = [
            box
            for box in self.items.values()
            if box.status == BoxStatus.SCHEDULED and box.activates_at.value <= now
        ]
        due.sort(key=lambda box: box.activates_at.value)
        return due[:limit]


class InMemoryBoxDesignsRepository(BaseBoxDesignsRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, BoxDesign] = {}

    async def add(self, entity: BoxDesign) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[BoxDesign]:
        return self.items.get(id_)

    async def update(self, entity: BoxDesign) -> BoxDesign:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)

    async def get_by_code(self, code: str) -> Optional[BoxDesign]:
        for design in self.items.values():
            if design.code == code:
                return design
        return None

    async def list_active(self) -> list[BoxDesign]:
        designs = [design for design in self.items.values() if design.is_active]
        return sorted(designs, key=lambda design: (design.sort_order.value, design.name.value))

    async def list_all(self) -> list[BoxDesign]:
        return sorted(
            self.items.values(),
            key=lambda design: (design.sort_order.value, design.name.value),
        )


class InMemoryDesignAssetsRepository(BaseDesignAssetsRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, DesignAsset] = {}

    async def add(self, entity: DesignAsset) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[DesignAsset]:
        return self.items.get(id_)

    async def update(self, entity: DesignAsset) -> DesignAsset:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)


class InMemoryDesignRatingsRepository(BaseDesignRatingsRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, DesignRating] = {}

    async def add(self, entity: DesignRating) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[DesignRating]:
        return self.items.get(id_)

    async def update(self, entity: DesignRating) -> DesignRating:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)

    async def get_by_user_and_design(
        self,
        *,
        user_id: uuid.UUID,
        design_id: uuid.UUID,
    ) -> Optional[DesignRating]:
        for rating in self.items.values():
            if rating.user_id == user_id and rating.design_id == design_id:
                return rating
        return None

    async def list_aggregates_by_design_ids(
        self,
        design_ids: list[uuid.UUID],
    ) -> list[DesignRatingAggregate]:
        by_design: dict[uuid.UUID, list[int]] = {design_id: [] for design_id in design_ids}
        for rating in self.items.values():
            if rating.design_id in by_design:
                by_design[rating.design_id].append(rating.stars.value)

        aggregates: list[DesignRatingAggregate] = []
        for design_id, stars in by_design.items():
            if not stars:
                continue
            aggregates.append(
                DesignRatingAggregate(
                    design_id=design_id,
                    average=sum(stars) / len(stars),
                    count=len(stars),
                )
            )
        return aggregates

    async def list_user_ratings_for_designs(
        self,
        *,
        user_id: uuid.UUID,
        design_ids: list[uuid.UUID],
    ) -> list[DesignRating]:
        design_id_set = set(design_ids)
        return [
            rating
            for rating in self.items.values()
            if rating.user_id == user_id and rating.design_id in design_id_set
        ]


class InMemoryMediaFilesRepository(BaseMediaFilesRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, MediaFile] = {}

    async def add(self, entity: MediaFile) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[MediaFile]:
        return self.items.get(id_)

    async def update(self, entity: MediaFile) -> MediaFile:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)

    async def list_by_owner_id(self, owner_id: uuid.UUID) -> list[MediaFile]:
        return [
            media for media in self.items.values() if media.owner_id == owner_id
        ]


class InMemoryUsersRepository(BaseUsersRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, User] = {}

    async def add(self, entity: User) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[User]:
        return self.items.get(id_)

    async def update(self, entity: User) -> User:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        for user in self.items.values():
            if int(user.telegram_id.value) == telegram_id:
                return user
        return None


class InMemoryTelegramLoginChallengesRepository(
    BaseTelegramLoginChallengesRepository
):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, TelegramLoginChallenge] = {}

    async def add(self, entity: TelegramLoginChallenge) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[TelegramLoginChallenge]:
        return self.items.get(id_)

    async def update(self, entity: TelegramLoginChallenge) -> TelegramLoginChallenge:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)

    async def get_by_code(
        self, code: str, *, for_update: bool = False
    ) -> Optional[TelegramLoginChallenge]:
        del for_update  # in-memory store has no row locks
        for challenge in self.items.values():
            if challenge.code == code:
                return challenge
        return None


class InMemoryUserSessionsRepository(BaseUserSessionsRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, UserSession] = {}

    async def add(self, entity: UserSession) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[UserSession]:
        return self.items.get(id_)

    async def update(self, entity: UserSession) -> UserSession:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)

    async def get_by_refresh_token_hash(
        self, refresh_token_hash: str
    ) -> UserSession | None:
        for session in self.items.values():
            if session.refresh_token_hash == refresh_token_hash:
                return session
        return None

    async def list_by_user_id(self, user_id: uuid.UUID) -> list[UserSession]:
        return [
            session for session in self.items.values() if session.user_id == user_id
        ]


class InMemoryNotificationJobsRepository(BaseNotificationJobsRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, NotificationJob] = {}

    async def add(self, entity: NotificationJob) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[NotificationJob]:
        return self.items.get(id_)

    async def update(self, entity: NotificationJob) -> NotificationJob:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)

    async def get_by_box_and_template(
        self,
        box_id: uuid.UUID,
        template: NotificationTemplate,
    ) -> NotificationJob | None:
        for job in self.items.values():
            if job.box_id == box_id and job.template == template:
                return job
        return None

    async def claim_due(
        self,
        now: datetime,
        *,
        limit: int = 20,
        stale_before: datetime | None = None,
    ) -> list[NotificationJob]:
        due = []
        for job in self.items.values():
            if job.status == NotificationJobStatus.SCHEDULED and job.next_run_at <= now:
                due.append(job)
            elif (
                stale_before is not None
                and job.status == NotificationJobStatus.PROCESSING
                and job.updated_at <= stale_before
            ):
                due.append(job)
        due.sort(key=lambda job: job.next_run_at)
        claimed: list[NotificationJob] = []
        for job in due[:limit]:
            job.mark_processing()
            claimed.append(job)
        return claimed


class InMemorySupportTicketsRepository(BaseSupportTicketsRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, SupportTicket] = {}

    async def add(self, entity: SupportTicket) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> SupportTicket | None:
        return self.items.get(id_)

    async def update(self, entity: SupportTicket) -> SupportTicket:
        self.items[entity.id] = entity
        return entity

    async def list_all(
        self,
        *,
        status: SupportTicketStatus | None = None,
        sort_asc: bool = False,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[SupportTicket]:
        tickets = list(self.items.values())
        if status is not None:
            tickets = [ticket for ticket in tickets if ticket.status == status]
        tickets.sort(key=lambda ticket: ticket.created_at, reverse=not sort_asc)
        if offset:
            tickets = tickets[offset:]
        if limit is not None:
            tickets = tickets[:limit]
        return tickets

    async def count_all(
        self,
        *,
        status: SupportTicketStatus | None = None,
    ) -> int:
        tickets = list(self.items.values())
        if status is not None:
            tickets = [ticket for ticket in tickets if ticket.status == status]
        return len(tickets)


class InMemoryAssistantChatThreadsRepository(BaseAssistantChatThreadsRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, AssistantChatThread] = {}

    async def add(self, entity: AssistantChatThread) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, thread_id: uuid.UUID) -> AssistantChatThread | None:
        return self.items.get(thread_id)

    async def get_by_box_id(self, box_id: uuid.UUID) -> AssistantChatThread | None:
        for item in self.items.values():
            if item.box_id == box_id:
                return item
        return None

    async def bind_box(
        self,
        *,
        thread_id: uuid.UUID,
        user_id: uuid.UUID,
        box_id: uuid.UUID,
    ) -> AssistantChatThread | None:
        thread = self.items.get(thread_id)
        if thread is None or thread.user_id != user_id or thread.box_id is not None:
            return thread
        thread.box_id = box_id
        return thread


class InMemoryAssistantChatMessagesRepository(BaseAssistantChatMessagesRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, AssistantChatMessage] = {}

    def _thread_messages(
        self,
        *,
        thread_id: uuid.UUID,
        include_hidden: bool = False,
    ) -> list[AssistantChatMessage]:
        messages = [
            item
            for item in self.items.values()
            if item.thread_id == thread_id
            and (include_hidden or item.hidden_at is None)
        ]
        messages.sort(key=lambda item: item.created_at)
        return messages

    async def add(self, entity: AssistantChatMessage) -> None:
        self.items[entity.id] = entity

    async def list_for_thread(
        self,
        *,
        thread_id: uuid.UUID,
        limit: int,
    ) -> list[AssistantChatMessage]:
        if limit <= 0:
            return []
        messages = self._thread_messages(thread_id=thread_id)
        if len(messages) > limit:
            messages = messages[-limit:]
        return messages

    async def count_for_thread(self, *, thread_id: uuid.UUID) -> int:
        return len(self._thread_messages(thread_id=thread_id))

    async def hide_oldest_beyond(
        self,
        *,
        thread_id: uuid.UUID,
        keep: int,
    ) -> int:
        from datetime import datetime, timezone

        messages = self._thread_messages(thread_id=thread_id)
        excess = len(messages) - max(keep, 0)
        if excess <= 0:
            return 0
        now = datetime.now(timezone.utc)
        for item in messages[:excess]:
            item.hidden_at = now
        return excess


class InMemoryProductsRepository(BaseProductsRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, Product] = {}

    async def add(self, entity: Product) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[Product]:
        return self.items.get(id_)

    async def update(self, entity: Product) -> Product:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)

    async def get_by_sku(self, sku: str) -> Product | None:
        for product in self.items.values():
            if product.sku == sku:
                return product
        return None

    async def list_active(self) -> list[Product]:
        return sorted(
            [p for p in self.items.values() if p.is_active],
            key=lambda p: p.name,
        )

    async def list_all(self) -> list[Product]:
        return sorted(
            self.items.values(),
            key=lambda p: p.created_at,
            reverse=True,
        )

    async def list_by_ids(self, ids: list[uuid.UUID]) -> list[Product]:
        return [self.items[i] for i in ids if i in self.items]


class InMemoryProductSalesRepository(BaseProductSalesRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, ProductSale] = {}

    async def add(self, entity: ProductSale) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[ProductSale]:
        return self.items.get(id_)

    async def update(self, entity: ProductSale) -> ProductSale:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)

    async def get_by_product_id(self, product_id: uuid.UUID) -> ProductSale | None:
        for sale in self.items.values():
            if sale.product_id == product_id:
                return sale
        return None

    async def list_by_product_ids(
        self, product_ids: list[uuid.UUID]
    ) -> list[ProductSale]:
        ids = set(product_ids)
        return [sale for sale in self.items.values() if sale.product_id in ids]

    async def list_active_by_product_ids(
        self, product_ids: list[uuid.UUID]
    ) -> list[ProductSale]:
        ids = set(product_ids)
        return [
            sale
            for sale in self.items.values()
            if sale.product_id in ids and sale.is_active
        ]


class InMemoryPromoCodesRepository(BasePromoCodesRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, PromoCode] = {}

    async def add(self, entity: PromoCode) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[PromoCode]:
        return self.items.get(id_)

    async def update(self, entity: PromoCode) -> PromoCode:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)

    async def get_by_code(self, code: str) -> PromoCode | None:
        for promo in self.items.values():
            if promo.code == code:
                return promo
        return None

    async def list_all(self) -> list[PromoCode]:
        return sorted(
            self.items.values(),
            key=lambda p: p.created_at,
            reverse=True,
        )


class InMemoryCartsRepository(BaseCartsRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, Cart] = {}

    async def add(self, entity: Cart) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[Cart]:
        return self.items.get(id_)

    async def update(self, entity: Cart) -> Cart:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)

    async def get_by_user_id(self, user_id: uuid.UUID) -> Cart | None:
        for cart in self.items.values():
            if cart.user_id == user_id:
                return cart
        return None


class InMemoryOrdersRepository(BaseOrdersRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, Order] = {}

    async def add(self, entity: Order) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[Order]:
        return self.items.get(id_)

    async def update(self, entity: Order) -> Order:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)

    async def get_by_provider_payment_id(
        self, provider_payment_id: str
    ) -> Order | None:
        for order in self.items.values():
            if order.provider_payment_id == provider_payment_id:
                return order
        return None

    async def get_by_idempotency_key(self, idempotency_key: str) -> Order | None:
        for order in self.items.values():
            if order.idempotency_key == idempotency_key:
                return order
        return None

    async def list_pending_by_user_id(
        self, user_id: uuid.UUID, *, limit: int = 20
    ) -> list[Order]:
        from app.domain.entities.orders import OrderStatus

        orders = [
            order
            for order in self.items.values()
            if order.user_id == user_id and order.status == OrderStatus.PENDING
        ]
        orders.sort(key=lambda o: o.created_at, reverse=True)
        return orders[:limit]

    async def list_by_user_id(
        self,
        user_id: uuid.UUID,
        *,
        limit: int,
        offset: int = 0,
    ) -> list[Order]:
        orders = [order for order in self.items.values() if order.user_id == user_id]
        orders.sort(key=lambda o: o.created_at, reverse=True)
        return orders[offset : offset + limit]

    async def count_by_user_id(self, user_id: uuid.UUID) -> int:
        return sum(1 for order in self.items.values() if order.user_id == user_id)


class InMemoryUserBalancesRepository(BaseUserBalancesRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, UserBalance] = {}

    async def add(self, entity: UserBalance) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[UserBalance]:
        return self.items.get(id_)

    async def update(self, entity: UserBalance) -> UserBalance:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)

    async def get_by_user_and_product(
        self, *, user_id: uuid.UUID, product_id: uuid.UUID
    ) -> UserBalance | None:
        for balance in self.items.values():
            if balance.user_id == user_id and balance.product_id == product_id:
                return balance
        return None

    async def list_by_user_id(self, user_id: uuid.UUID) -> list[UserBalance]:
        return [b for b in self.items.values() if b.user_id == user_id]


class InMemoryUserBalanceLogsRepository(BaseUserBalanceLogsRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, UserBalanceLog] = {}

    async def add(self, entity: UserBalanceLog) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[UserBalanceLog]:
        return self.items.get(id_)

    async def update(self, entity: UserBalanceLog) -> UserBalanceLog:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)

    async def get_by_reason_reference(
        self,
        *,
        reason: str,
        reference_type: str,
        reference_id: uuid.UUID,
    ) -> UserBalanceLog | None:
        for log in self.items.values():
            if (
                log.reason.value == reason
                and log.reference_type == reference_type
                and log.reference_id == reference_id
            ):
                return log
        return None

    async def list_by_user_id(
        self,
        user_id: uuid.UUID,
        *,
        limit: int,
        offset: int = 0,
    ) -> list[UserBalanceLog]:
        logs = [log for log in self.items.values() if log.user_id == user_id]
        logs.sort(key=lambda log: log.created_at, reverse=True)
        return logs[offset : offset + limit]

    async def count_by_user_id(self, user_id: uuid.UUID) -> int:
        return sum(1 for log in self.items.values() if log.user_id == user_id)


class InMemoryUnitOfWork(BaseUnitOfWork):
    def __init__(self) -> None:
        self.boxes = InMemoryBoxesRepository()
        self.box_designs = InMemoryBoxDesignsRepository()
        self.design_assets = InMemoryDesignAssetsRepository()
        self.design_ratings = InMemoryDesignRatingsRepository()
        self.media_files = InMemoryMediaFilesRepository()
        self.notification_jobs = InMemoryNotificationJobsRepository()
        self.support_tickets = InMemorySupportTicketsRepository()
        self.assistant_chat_threads = InMemoryAssistantChatThreadsRepository()
        self.assistant_chat_messages = InMemoryAssistantChatMessagesRepository()
        self.users = InMemoryUsersRepository()
        self.telegram_login_challenges = InMemoryTelegramLoginChallengesRepository()
        self.user_sessions = InMemoryUserSessionsRepository()
        self.products = InMemoryProductsRepository()
        self.product_sales = InMemoryProductSalesRepository()
        self.promo_codes = InMemoryPromoCodesRepository()
        self.carts = InMemoryCartsRepository()
        self.orders = InMemoryOrdersRepository()
        self.user_balances = InMemoryUserBalancesRepository()
        self.user_balance_logs = InMemoryUserBalanceLogsRepository()
        self.committed = False
        self.rolled_back = False
        seed_box_credit_product(self)

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True
