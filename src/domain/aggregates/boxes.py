from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone as dt_timezone
from enum import StrEnum
from typing import Any
import uuid

from src.domain.entities.base import BaseEntity
from src.domain.entities.box_items import BoxItem, BoxItemType, TOY_CODES
from src.domain.exceptions.box_items import BoxItemInvalidError

from src.domain.exceptions.boxes import (
    BoxAlreadyArchivedError,
    BoxAlreadyOpenedError,
    BoxItemDuplicateSortOrderError,
    BoxItemNotFoundError,
    BoxItemReorderError,
    BoxItemsLimitExceededError,
    BoxNotArchivedError,
    BoxNotPublishableError,
    BoxWithoutItemsError,
)
from src.domain.values.activates_at import ActivatesAt
from src.domain.values.box_item_caption import BoxItemCaption
from src.domain.values.box_message import BoxMessage
from src.domain.values.box_preview_title import BoxPreviewTitle
from src.domain.values.box_recipient_name import BoxRecipientName
from src.domain.values.box_title import BoxTitle
from src.domain.values.public_slug import PublicSlug
from src.domain.values.sort_order import SortOrder
from src.domain.values.url import Url


MAX_BOX_ITEMS = 12


class BoxStatus(StrEnum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    ARCHIVED = "archived"


@dataclass(frozen=False, kw_only=True)
class Box(BaseEntity):
    owner_id: uuid.UUID
    design_id: uuid.UUID
    public_slug: PublicSlug
    title: BoxTitle
    recipient_name: BoxRecipientName
    activates_at: ActivatesAt
    status: BoxStatus
    timezone: str = "UTC"
    message: BoxMessage | None = None
    preview_title: BoxPreviewTitle | None = None
    preview_image_url: Url | None = None
    published_at: datetime | None = None
    first_opened_at: datetime | None = None
    items: list[BoxItem] = field(default_factory=list)

    def add_item(
        self,
        *,
        media_file_id: uuid.UUID | None = None,
        item_type: BoxItemType,
        sort_order: SortOrder | None = None,
        caption: BoxItemCaption | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> BoxItem:
        if item_type == BoxItemType.TEXT:
            if media_file_id is not None:
                raise BoxItemInvalidError("Text item must not reference a media file")
            if caption is None:
                raise BoxItemInvalidError("Text item requires non-empty text")
        elif item_type == BoxItemType.TOY:
            if media_file_id is not None:
                raise BoxItemInvalidError("Toy item must not reference a media file")
            toy_code = (metadata or {}).get("toy_code")
            if not isinstance(toy_code, str) or toy_code not in TOY_CODES:
                raise BoxItemInvalidError(
                    f"Toy item requires a valid toy_code ({', '.join(sorted(TOY_CODES))})"
                )
        elif media_file_id is None:
            raise BoxItemInvalidError("Media item requires a media file")

        if len(self.items) >= MAX_BOX_ITEMS:
            raise BoxItemsLimitExceededError(MAX_BOX_ITEMS)

        order = sort_order or SortOrder(len(self.items) + 1)
        if any(item.sort_order == order for item in self.items):
            raise BoxItemDuplicateSortOrderError(order.value)

        item = BoxItem(
            box_id=self.id,
            media_file_id=media_file_id,
            item_type=item_type,
            sort_order=order,
            caption=caption,
            metadata=metadata if metadata is not None else {},
        )
        self.items.append(item)
        self.items.sort(key=lambda i: i.sort_order.value)
        self._touch()
        return item

    def remove_item(self, item_id: uuid.UUID) -> None:
        for index, item in enumerate(self.items):
            if item.id == item_id:
                del self.items[index]
                self._reindex_sort_orders()
                self._touch()
                return
        raise BoxItemNotFoundError(item_id)

    def update_item(
        self,
        item_id: uuid.UUID,
        *,
        caption: BoxItemCaption | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> BoxItem:
        for item in self.items:
            if item.id == item_id:
                item.caption = caption
                if metadata is not None:
                    item.metadata = metadata
                self._touch()
                return item
        raise BoxItemNotFoundError(item_id)

    def reorder_items(self, item_ids: Sequence[uuid.UUID]) -> None:
        current_ids = {item.id for item in self.items}
        if len(item_ids) != len(self.items) or set(item_ids) != current_ids:
            raise BoxItemReorderError()

        by_id = {item.id: item for item in self.items}
        reordered: list[BoxItem] = []
        for order, item_id in enumerate(item_ids, start=1):
            item = by_id[item_id]
            item.sort_order = SortOrder(order)
            reordered.append(item)
        self.items = reordered
        self._touch()

    def update_details(
        self,
        *,
        design_id: uuid.UUID,
        title: BoxTitle,
        recipient_name: BoxRecipientName,
        activates_at: ActivatesAt,
        timezone: str = "UTC",
        message: BoxMessage | None = None,
        preview_title: BoxPreviewTitle | None = None,
        preview_image_url: Url | None = None,
    ) -> None:
        self.design_id = design_id
        self.title = title
        self.recipient_name = recipient_name
        self.activates_at = activates_at
        self.timezone = timezone
        self.message = message
        self.preview_title = preview_title
        self.preview_image_url = preview_image_url
        self._touch()

    def publish(self, *, now: datetime | None = None) -> None:
        if self.status != BoxStatus.DRAFT:
            raise BoxNotPublishableError(self.id, self.status.value)
        if not self.items:
            raise BoxWithoutItemsError(self.id)

        self.status = BoxStatus.SCHEDULED
        self.published_at = now or datetime.now(dt_timezone.utc)
        self._touch()

    def archive(self) -> None:
        if self.status == BoxStatus.ARCHIVED:
            raise BoxAlreadyArchivedError(self.id)

        self.status = BoxStatus.ARCHIVED
        self._touch()

    def unarchive(self) -> None:
        if self.status != BoxStatus.ARCHIVED:
            raise BoxNotArchivedError(self.id)
        if self.first_opened_at is not None:
            raise BoxAlreadyOpenedError(self.id)

        # ACTIVE ставится только при первом открытии — без first_opened_at
        # бокс был draft или scheduled.
        self.status = (
            BoxStatus.SCHEDULED if self.published_at is not None else BoxStatus.DRAFT
        )
        self._touch()

    def _reindex_sort_orders(self) -> None:
        self.items.sort(key=lambda i: i.sort_order.value)
        for order, item in enumerate(self.items, start=1):
            item.sort_order = SortOrder(order)

    def _touch(self) -> None:
        self.updated_at = datetime.now(dt_timezone.utc)
