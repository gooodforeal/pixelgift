from src.domain.aggregates.boxes import Box, BoxStatus
from src.domain.entities.box_items import BoxItem, BoxItemType
from src.domain.values.activates_at import ActivatesAt
from src.domain.values.box_item_caption import BoxItemCaption
from src.domain.values.box_message import BoxMessage
from src.domain.values.box_preview_title import BoxPreviewTitle
from src.domain.values.box_recipient_email import BoxRecipientEmail
from src.domain.values.box_recipient_name import BoxRecipientName
from src.domain.values.box_title import BoxTitle
from src.domain.values.public_slug import PublicSlug
from src.domain.values.sort_order import SortOrder
from src.domain.values.url import Url
from src.infrastructure.models.box_items import BoxItemModel
from src.infrastructure.models.boxes import BoxModel


def box_item_to_model(entity: BoxItem) -> BoxItemModel:
    return BoxItemModel(
        id=entity.id,
        box_id=entity.box_id,
        media_file_id=entity.media_file_id,
        item_type=entity.item_type.value,
        sort_order=entity.sort_order.value,
        caption=entity.caption.value if entity.caption is not None else None,
        item_metadata=dict(entity.metadata),
        created_at=entity.created_at,
    )


def box_item_to_entity(model: BoxItemModel) -> BoxItem:
    return BoxItem(
        id=model.id,
        box_id=model.box_id,
        media_file_id=model.media_file_id,
        item_type=BoxItemType(model.item_type),
        sort_order=SortOrder(model.sort_order),
        caption=(
            BoxItemCaption(model.caption) if model.caption is not None else None
        ),
        metadata=dict(model.item_metadata or {}),
        created_at=model.created_at,
        updated_at=model.created_at,
    )


def apply_box_item(entity: BoxItem, model: BoxItemModel) -> None:
    model.box_id = entity.box_id
    model.media_file_id = entity.media_file_id
    model.item_type = entity.item_type.value
    model.sort_order = entity.sort_order.value
    model.caption = entity.caption.value if entity.caption is not None else None
    model.item_metadata = dict(entity.metadata)


def box_to_model(entity: Box) -> BoxModel:
    model = BoxModel(
        id=entity.id,
        owner_id=entity.owner_id,
        design_id=entity.design_id,
        public_slug=entity.public_slug.value,
        title=entity.title.value,
        recipient_name=entity.recipient_name.value,
        recipient_email=(
            entity.recipient_email.value if entity.recipient_email is not None else None
        ),
        message=entity.message.value if entity.message is not None else None,
        preview_title=(
            entity.preview_title.value if entity.preview_title is not None else None
        ),
        preview_image_url=(
            entity.preview_image_url.value
            if entity.preview_image_url is not None
            else None
        ),
        activates_at=entity.activates_at.value,
        timezone=entity.timezone,
        status=entity.status.value,
        published_at=entity.published_at,
        first_opened_at=entity.first_opened_at,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )
    model.items = [box_item_to_model(item) for item in entity.items]
    return model


def box_to_entity(model: BoxModel) -> Box:
    items = sorted(
        (box_item_to_entity(item) for item in model.items),
        key=lambda item: item.sort_order.value,
    )
    return Box(
        id=model.id,
        owner_id=model.owner_id,
        design_id=model.design_id,
        public_slug=PublicSlug(model.public_slug),
        title=BoxTitle(model.title),
        recipient_name=BoxRecipientName(model.recipient_name),
        recipient_email=(
            BoxRecipientEmail(model.recipient_email)
            if model.recipient_email is not None
            else None
        ),
        activates_at=ActivatesAt.reconstitute(model.activates_at),
        status=BoxStatus(model.status),
        timezone=model.timezone,
        message=BoxMessage(model.message) if model.message is not None else None,
        preview_title=(
            BoxPreviewTitle(model.preview_title)
            if model.preview_title is not None
            else None
        ),
        preview_image_url=(
            Url(model.preview_image_url)
            if model.preview_image_url is not None
            else None
        ),
        published_at=model.published_at,
        first_opened_at=model.first_opened_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
        items=items,
    )


def apply_box(entity: Box, model: BoxModel) -> None:
    model.owner_id = entity.owner_id
    model.design_id = entity.design_id
    model.public_slug = entity.public_slug.value
    model.title = entity.title.value
    model.recipient_name = entity.recipient_name.value
    model.recipient_email = (
        entity.recipient_email.value if entity.recipient_email is not None else None
    )
    model.message = entity.message.value if entity.message is not None else None
    model.preview_title = (
        entity.preview_title.value if entity.preview_title is not None else None
    )
    model.preview_image_url = (
        entity.preview_image_url.value
        if entity.preview_image_url is not None
        else None
    )
    model.activates_at = entity.activates_at.value
    model.timezone = entity.timezone
    model.status = entity.status.value
    model.published_at = entity.published_at
    model.first_opened_at = entity.first_opened_at
    model.updated_at = entity.updated_at
