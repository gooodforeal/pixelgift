"""SQLAlchemy-репозиторий тредов чата ассистента."""
import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.assistant_chat_threads import AssistantChatThread
from app.domain.repository.assistant_chat_threads import (
    BaseAssistantChatThreadsRepository,
)
from app.infrastructure.mappers.assistant_chat_threads import (
    assistant_chat_thread_to_entity,
    assistant_chat_thread_to_model,
)
from app.infrastructure.models.assistant_chat_threads import AssistantChatThreadModel


class SqlAlchemyAssistantChatThreadsRepository(BaseAssistantChatThreadsRepository):
    """SQLAlchemy-репозиторий тредов; bind_box — условный UPDATE по user_id."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, entity: AssistantChatThread) -> None:
        self._session.add(assistant_chat_thread_to_model(entity))

    async def get_by_id(self, thread_id: uuid.UUID) -> AssistantChatThread | None:
        model = await self._session.get(AssistantChatThreadModel, thread_id)
        if model is None:
            return None
        return assistant_chat_thread_to_entity(model)

    async def get_by_box_id(self, box_id: uuid.UUID) -> AssistantChatThread | None:
        result = await self._session.execute(
            select(AssistantChatThreadModel).where(
                AssistantChatThreadModel.box_id == box_id
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return assistant_chat_thread_to_entity(model)

    async def bind_box(
        self,
        *,
        thread_id: uuid.UUID,
        user_id: uuid.UUID,
        box_id: uuid.UUID,
    ) -> AssistantChatThread | None:
        result = await self._session.execute(
            update(AssistantChatThreadModel)
            .where(
                AssistantChatThreadModel.id == thread_id,
                AssistantChatThreadModel.user_id == user_id,
                AssistantChatThreadModel.box_id.is_(None),
            )
            .values(box_id=box_id)
            .returning(AssistantChatThreadModel)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return await self.get_by_id(thread_id)
        return assistant_chat_thread_to_entity(model)
