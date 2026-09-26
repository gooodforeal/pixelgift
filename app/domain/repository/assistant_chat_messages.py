from abc import ABC, abstractmethod
import uuid

from app.domain.entities.assistant_chat_messages import AssistantChatMessage


class BaseAssistantChatMessagesRepository(ABC):
    @abstractmethod
    async def add(self, entity: AssistantChatMessage) -> None: ...

    @abstractmethod
    async def list_for_thread(
        self,
        *,
        thread_id: uuid.UUID,
        limit: int,
    ) -> list[AssistantChatMessage]:
        """Active (non-hidden) messages for a thread, oldest first."""

    @abstractmethod
    async def count_for_thread(self, *, thread_id: uuid.UUID) -> int: ...

    @abstractmethod
    async def hide_oldest_beyond(
        self,
        *,
        thread_id: uuid.UUID,
        keep: int,
    ) -> int: ...
