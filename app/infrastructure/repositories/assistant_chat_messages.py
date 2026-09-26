import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.assistant_chat_messages import AssistantChatMessage
from app.domain.repository.assistant_chat_messages import (
    BaseAssistantChatMessagesRepository,
)
from app.infrastructure.mappers.assistant_chat_messages import (
    assistant_chat_message_to_entity,
    assistant_chat_message_to_model,
)
from app.infrastructure.models.assistant_chat_messages import AssistantChatMessageModel


class SqlAlchemyAssistantChatMessagesRepository(BaseAssistantChatMessagesRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, entity: AssistantChatMessage) -> None:
        self._session.add(assistant_chat_message_to_model(entity))

    async def list_for_thread(
        self,
        *,
        thread_id: uuid.UUID,
        limit: int,
    ) -> list[AssistantChatMessage]:
        if limit <= 0:
            return []

        subquery = (
            select(AssistantChatMessageModel.id)
            .where(
                AssistantChatMessageModel.thread_id == thread_id,
                AssistantChatMessageModel.hidden_at.is_(None),
            )
            .order_by(AssistantChatMessageModel.created_at.desc())
            .limit(limit)
            .subquery()
        )
        result = await self._session.execute(
            select(AssistantChatMessageModel)
            .where(AssistantChatMessageModel.id.in_(select(subquery.c.id)))
            .order_by(AssistantChatMessageModel.created_at.asc())
        )
        return [
            assistant_chat_message_to_entity(model) for model in result.scalars().all()
        ]

    async def count_for_thread(self, *, thread_id: uuid.UUID) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(AssistantChatMessageModel)
            .where(
                AssistantChatMessageModel.thread_id == thread_id,
                AssistantChatMessageModel.hidden_at.is_(None),
            )
        )
        return int(result.scalar_one())

    async def hide_oldest_beyond(
        self,
        *,
        thread_id: uuid.UUID,
        keep: int,
    ) -> int:
        if keep < 0:
            keep = 0
        total = await self.count_for_thread(thread_id=thread_id)
        excess = total - keep
        if excess <= 0:
            return 0

        oldest_ids = (
            select(AssistantChatMessageModel.id)
            .where(
                AssistantChatMessageModel.thread_id == thread_id,
                AssistantChatMessageModel.hidden_at.is_(None),
            )
            .order_by(AssistantChatMessageModel.created_at.asc())
            .limit(excess)
        )
        result = await self._session.execute(
            update(AssistantChatMessageModel)
            .where(AssistantChatMessageModel.id.in_(oldest_ids))
            .values(hidden_at=datetime.now(timezone.utc))
        )
        return int(result.rowcount or 0)
