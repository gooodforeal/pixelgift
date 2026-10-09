"""Маппинг AssistantChatThread ↔ ORM."""

from app.domain.entities.assistant_chat_threads import AssistantChatThread
from app.infrastructure.models.assistant_chat_threads import AssistantChatThreadModel


def assistant_chat_thread_to_model(
    entity: AssistantChatThread,
) -> AssistantChatThreadModel:
    return AssistantChatThreadModel(
        id=entity.id,
        user_id=entity.user_id,
        box_id=entity.box_id,
        created_at=entity.created_at,
    )


def assistant_chat_thread_to_entity(
    model: AssistantChatThreadModel,
) -> AssistantChatThread:
    return AssistantChatThread(
        id=model.id,
        user_id=model.user_id,
        box_id=model.box_id,
        created_at=model.created_at,
        updated_at=model.created_at,
    )
