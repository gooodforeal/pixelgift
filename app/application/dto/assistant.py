from dataclasses import dataclass, field
from typing import Any, Literal
import uuid


BoxWizardStep = Literal[
    "design",
    "details",
    "content",
    "publish",
    "certificate",
]

AssistantHistoryRole = Literal["user", "assistant"]


@dataclass(frozen=True, kw_only=True)
class AssistantHistoryMessage:
    role: AssistantHistoryRole
    content: str


@dataclass(frozen=True, kw_only=True)
class BoxEditorFormSnapshot:
    design_id: str | None = None
    title: str | None = None
    recipient_name: str | None = None
    recipient_email: str | None = None
    unlock_password_set: bool | None = None
    activates_at: str | None = None
    timezone: str | None = None
    message: str | None = None
    preview_title: str | None = None


@dataclass(frozen=True, kw_only=True)
class ChatBoxAssistantCommand:
    user_id: uuid.UUID
    message: str
    step: BoxWizardStep
    thread_id: uuid.UUID | None = None
    box_id: uuid.UUID | None = None
    form: BoxEditorFormSnapshot | None = None


@dataclass(frozen=True, kw_only=True)
class ChatBoxAssistantResult:
    reply: str
    thread_id: uuid.UUID
    context: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class ListBoxAssistantHistoryCommand:
    user_id: uuid.UUID
    thread_id: uuid.UUID | None = None
    box_id: uuid.UUID | None = None


@dataclass(frozen=True, kw_only=True)
class ListBoxAssistantHistoryResult:
    thread_id: uuid.UUID
    messages: tuple[AssistantHistoryMessage, ...]
