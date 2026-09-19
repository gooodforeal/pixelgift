import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.support_tickets import SupportTicket, SupportTicketStatus
from src.domain.repository.support_tickets import BaseSupportTicketsRepository
from src.infrastructure.mappers.support_tickets import (
    apply_support_ticket,
    support_ticket_to_entity,
    support_ticket_to_model,
)
from src.infrastructure.models.support_tickets import SupportTicketModel


class SqlAlchemySupportTicketsRepository(BaseSupportTicketsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, entity: SupportTicket) -> None:
        self._session.add(support_ticket_to_model(entity))

    async def get_by_id(self, id_: uuid.UUID) -> SupportTicket | None:
        result = await self._session.execute(
            select(SupportTicketModel)
            .where(SupportTicketModel.id == id_)
            .options(selectinload(SupportTicketModel.attachments))
        )
        model = result.scalar_one_or_none()
        return support_ticket_to_entity(model) if model is not None else None

    async def update(self, entity: SupportTicket) -> SupportTicket:
        model = await self._session.get(SupportTicketModel, entity.id)
        if model is None:
            raise ValueError(f"Support ticket not found: {entity.id}")
        apply_support_ticket(entity, model)
        await self._session.flush()
        return entity

    async def count_all(
        self,
        *,
        status: SupportTicketStatus | None = None,
    ) -> int:
        query = select(func.count()).select_from(SupportTicketModel)
        if status is not None:
            query = query.where(SupportTicketModel.status == status.value)
        result = await self._session.execute(query)
        return int(result.scalar_one())

    async def list_all(
        self,
        *,
        status: SupportTicketStatus | None = None,
        sort_asc: bool = False,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[SupportTicket]:
        order = (
            SupportTicketModel.created_at.asc()
            if sort_asc
            else SupportTicketModel.created_at.desc()
        )
        query = (
            select(SupportTicketModel)
            .options(selectinload(SupportTicketModel.attachments))
            .order_by(order)
            .offset(offset)
        )
        if status is not None:
            query = query.where(SupportTicketModel.status == status.value)
        if limit is not None:
            query = query.limit(limit)
        result = await self._session.execute(query)
        return [support_ticket_to_entity(model) for model in result.scalars().all()]
