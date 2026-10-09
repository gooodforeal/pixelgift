"""Диалог пользователя с AI-ассистентом."""

from dataclasses import dataclass
import uuid

from app.domain.entities.base import BaseEntity


@dataclass(frozen=False, kw_only=True)
class AssistantChatThread(BaseEntity):
    """Нить чата; опционально связана с боксом при создании подарка."""

    user_id: uuid.UUID
    box_id: uuid.UUID | None = None
