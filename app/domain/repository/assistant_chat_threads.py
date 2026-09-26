from abc import ABC, abstractmethod
import uuid

from app.domain.entities.assistant_chat_threads import AssistantChatThread


class BaseAssistantChatThreadsRepository(ABC):
    @abstractmethod
    async def add(self, entity: AssistantChatThread) -> None: ...

    @abstractmethod
    async def get_by_id(self, thread_id: uuid.UUID) -> AssistantChatThread | None: ...

    @abstractmethod
    async def get_by_box_id(self, box_id: uuid.UUID) -> AssistantChatThread | None: ...

    @abstractmethod
    async def bind_box(
        self,
        *,
        thread_id: uuid.UUID,
        user_id: uuid.UUID,
        box_id: uuid.UUID,
    ) -> AssistantChatThread | None:
        """Attach an unbound thread to a box. Returns updated thread or None."""
