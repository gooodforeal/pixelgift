"""Схемы LLM-ассистента редактора бокса."""

from typing import Any, Literal
import uuid

from pydantic import BaseModel, Field

from app.presentation.schemas.base import BaseResponseSchema


class BoxEditorFormSnapshotSchema(BaseModel):
    """Снимок формы редактора для контекста LLM."""
    design_id: str | None = None
    title: str | None = None
    recipient_name: str | None = None
    recipient_email: str | None = None
    unlock_password_set: bool | None = None
    activates_at: str | None = None
    timezone: str | None = None
    message: str | None = None
    preview_title: str | None = None


class ChatBoxAssistantRequest(BaseModel):
    """Запрос сообщения ассистенту."""
    message: str = Field(min_length=1, max_length=2000)
    step: Literal["design", "details", "content", "publish", "certificate"]
    thread_id: uuid.UUID | None = None
    box_id: uuid.UUID | None = None
    form: BoxEditorFormSnapshotSchema | None = None


class ChatBoxAssistantSchema(BaseModel):
    """Ответ ассистента и thread_id."""
    reply: str
    thread_id: uuid.UUID
    context: dict[str, Any] = Field(default_factory=dict)


class ChatBoxAssistantResponse(BaseResponseSchema[ChatBoxAssistantSchema]):
    """Ответ POST /assistant/box-editor."""
    pass


class AssistantHistoryMessageSchema(BaseModel):
    """Сообщение в истории диалога."""
    role: Literal["user", "assistant"]
    content: str


class BoxAssistantHistorySchema(BaseModel):
    """История thread ассистента."""
    thread_id: uuid.UUID
    messages: list[AssistantHistoryMessageSchema] = Field(default_factory=list)


class BoxAssistantHistoryResponse(BaseResponseSchema[BoxAssistantHistorySchema]):
    """Ответ GET /assistant/box-editor/history."""
    pass
