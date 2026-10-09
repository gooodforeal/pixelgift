"""Команды изменения подарочного бокса в редакторе."""

from dataclasses import dataclass, field
from typing import Any
import uuid

from app.domain.values.activates_at import ActivatesAt
from app.domain.values.box_item_caption import BoxItemCaption
from app.domain.values.box_message import BoxMessage
from app.domain.values.box_preview_title import BoxPreviewTitle
from app.domain.values.box_recipient_email import BoxRecipientEmail
from app.domain.values.box_recipient_name import BoxRecipientName
from app.domain.values.box_title import BoxTitle
from app.domain.values.box_unlock_password import BoxUnlockPassword
from app.domain.values.public_slug import PublicSlug
from app.domain.values.sort_order import SortOrder
from app.domain.values.url import Url


@dataclass(frozen=True, kw_only=True)
class CreateBoxCommand:
    """Создание черновика бокса; списывается один кредит «бокс»."""

    owner_id: uuid.UUID
    design_id: uuid.UUID
    title: BoxTitle
    recipient_name: BoxRecipientName
    activates_at: ActivatesAt
    unlock_password: BoxUnlockPassword
    timezone: str = "UTC"
    recipient_email: BoxRecipientEmail | None = None
    public_slug: PublicSlug | None = None
    message: BoxMessage | None = None
    preview_title: BoxPreviewTitle | None = None
    preview_image_url: Url | None = None
    assistant_thread_id: uuid.UUID | None = None


@dataclass(frozen=True, kw_only=True)
class UpdateBoxCommand:
    """Обновление полей бокса в статусе черновик/запланирован."""

    box_id: uuid.UUID
    actor_id: uuid.UUID
    design_id: uuid.UUID
    title: BoxTitle
    recipient_name: BoxRecipientName
    activates_at: ActivatesAt
    unlock_password: BoxUnlockPassword
    timezone: str = "UTC"
    recipient_email: BoxRecipientEmail | None = None
    message: BoxMessage | None = None
    preview_title: BoxPreviewTitle | None = None
    preview_image_url: Url | None = None


@dataclass(frozen=True, kw_only=True)
class AddBoxItemCommand:
    """Добавление карточки; тип задаётся ``item_type`` или выводится из медиа."""

    box_id: uuid.UUID
    actor_id: uuid.UUID
    media_file_id: uuid.UUID | None = None
    item_type: str | None = None
    caption: BoxItemCaption | None = None
    sort_order: SortOrder | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class UpdateBoxItemCommand:
    """Изменение подписи и metadata карточки."""

    box_id: uuid.UUID
    actor_id: uuid.UUID
    item_id: uuid.UUID
    caption: BoxItemCaption | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True, kw_only=True)
class RemoveBoxItemCommand:
    """Удаление карточки из бокса."""

    box_id: uuid.UUID
    actor_id: uuid.UUID
    item_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class ReorderBoxItemsCommand:
    """Новый порядок карточек списком id."""

    box_id: uuid.UUID
    actor_id: uuid.UUID
    item_ids: tuple[uuid.UUID, ...]


@dataclass(frozen=True, kw_only=True)
class PublishBoxCommand:
    """Публикация бокса: ссылка становится доступна получателю."""

    box_id: uuid.UUID
    actor_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class ArchiveBoxCommand:
    """Архивация: публичная ссылка перестаёт открывать подарок."""

    box_id: uuid.UUID
    actor_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class UnarchiveBoxCommand:
    """Восстановление бокса из архива."""

    box_id: uuid.UUID
    actor_id: uuid.UUID
