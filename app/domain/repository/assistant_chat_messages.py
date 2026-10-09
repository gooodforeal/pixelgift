"""Контракт персистентности сообщений ассистента."""

from abc import ABC, abstractmethod
import uuid

from app.domain.entities.assistant_chat_messages import AssistantChatMessage


class BaseAssistantChatMessagesRepository(ABC):
    """Добавление сообщений, лимит видимой истории и soft-hide старых."""

    @abstractmethod
    async def add(self, entity: AssistantChatMessage) -> None: ...

    @abstractmethod
    async def list_for_thread(
        self,
        *,
        thread_id: uuid.UUID,
        limit: int,
    ) -> list[AssistantChatMessage]:
        """Видимые сообщения треда от старых к новым."""

    @abstractmethod
    async def count_for_thread(self, *, thread_id: uuid.UUID) -> int: ...

    @abstractmethod
    async def hide_oldest_beyond(
        self,
        *,
        thread_id: uuid.UUID,
        keep: int,
    ) -> int: ...
