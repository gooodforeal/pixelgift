from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
import uuid

from app.domain.entities.base import BaseEntity


class AssistantMessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


@dataclass(frozen=False, kw_only=True)
class AssistantChatMessage(BaseEntity):
    thread_id: uuid.UUID
    role: AssistantMessageRole
    content: str
    step: str | None = None
    hidden_at: datetime | None = None
