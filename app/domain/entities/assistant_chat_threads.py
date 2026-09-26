from dataclasses import dataclass
import uuid

from app.domain.entities.base import BaseEntity


@dataclass(frozen=False, kw_only=True)
class AssistantChatThread(BaseEntity):
    user_id: uuid.UUID
    box_id: uuid.UUID | None = None
