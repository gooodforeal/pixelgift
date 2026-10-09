"""Маппинг AssistantChatMessage ↔ ORM."""

from app.domain.entities.assistant_chat_messages import (
    AssistantChatMessage,
    AssistantMessageRole,
)
from app.infrastructure.models.assistant_chat_messages import AssistantChatMessageModel


def assistant_chat_message_to_model(
    entity: AssistantChatMessage,
) -> AssistantChatMessageModel:
    return AssistantChatMessageModel(
        id=entity.id,
        thread_id=entity.thread_id,
        role=entity.role.value,
        content=entity.content,
        step=entity.step,
        hidden_at=entity.hidden_at,
        created_at=entity.created_at,
    )


def assistant_chat_message_to_entity(
    model: AssistantChatMessageModel,
) -> AssistantChatMessage:
    return AssistantChatMessage(
        id=model.id,
        thread_id=model.thread_id,
        role=AssistantMessageRole(model.role),
        content=model.content,
        step=model.step,
        hidden_at=model.hidden_at,
        created_at=model.created_at,
        updated_at=model.created_at,
    )
