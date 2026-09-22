from app.application.dto.designs import BoxDesignWithRating
from app.domain.aggregates.boxes import Box
from app.domain.entities.box_designs import BoxDesign
from app.domain.entities.box_items import BoxItem
from app.domain.entities.media_files import MediaFile
from app.presentation.schemas.boxes import (
    BoxItemSchema,
    BoxSchema,
    MediaFileSchema,
    PublicBoxSchema,
)
from app.presentation.schemas.designs import AdminBoxDesignSchema, BoxDesignSchema


def box_item_to_response(item: BoxItem) -> BoxItemSchema:
    return BoxItemSchema(
        id=item.id,
        media_file_id=item.media_file_id,
        item_type=item.item_type.value,
        sort_order=item.sort_order.value,
        caption=item.caption.value if item.caption is not None else None,
        metadata=dict(item.metadata),
    )


def box_to_response(box: Box) -> BoxSchema:
    return BoxSchema(
        id=box.id,
        owner_id=box.owner_id,
        design_id=box.design_id,
        public_slug=box.public_slug.value,
        title=box.title.value,
        recipient_name=box.recipient_name.value,
        recipient_email=(
            box.recipient_email.value if box.recipient_email is not None else None
        ),
        unlock_password=(
            box.unlock_password.value if box.unlock_password is not None else None
        ),
        activates_at=box.activates_at.value,
        status=box.status.value,
        timezone=box.timezone,
        message=box.message.value if box.message is not None else None,
        preview_title=box.preview_title.value if box.preview_title is not None else None,
        preview_image_url=(
            box.preview_image_url.value if box.preview_image_url is not None else None
        ),
        published_at=box.published_at,
        first_opened_at=box.first_opened_at,
        items=[box_item_to_response(item) for item in box.items],
    )


def public_box_to_response(
    box: Box,
    *,
    content_unlocked: bool,
    design: BoxDesign | None = None,
) -> PublicBoxSchema:
    return PublicBoxSchema(
        public_slug=box.public_slug.value,
        title=box.title.value,
        recipient_name=box.recipient_name.value,
        activates_at=box.activates_at.value,
        status=box.status.value,
        timezone=box.timezone,
        preview_title=box.preview_title.value if box.preview_title is not None else None,
        preview_image_url=(
            box.preview_image_url.value if box.preview_image_url is not None else None
        ),
        content_unlocked=content_unlocked,
        password_required=box.unlock_password is not None,
        message=(
            box.message.value
            if content_unlocked and box.message is not None
            else None
        ),
        design_code=design.code if design is not None else None,
        theme_config=dict(design.theme_config) if design is not None else {},
        items=(
            [box_item_to_response(item) for item in box.items] if content_unlocked else []
        ),
    )


def box_design_to_response(
    design: BoxDesign,
    *,
    rating_avg: float = 0.0,
    rating_count: int = 0,
    my_rating: int | None = None,
) -> BoxDesignSchema:
    return BoxDesignSchema(
        id=design.id,
        code=design.code,
        name=design.name.value,
        preview_image_url=design.preview_image_url.value,
        sort_order=design.sort_order.value,
        description=(
            design.description.value if design.description is not None else None
        ),
        theme_config=dict(design.theme_config),
        rating_avg=rating_avg,
        rating_count=rating_count,
        my_rating=my_rating,
    )


def box_design_with_rating_to_response(
    item: BoxDesignWithRating,
) -> BoxDesignSchema:
    return box_design_to_response(
        item.design,
        rating_avg=item.rating_avg,
        rating_count=item.rating_count,
        my_rating=item.my_rating,
    )


def admin_box_design_to_response(design: BoxDesign) -> AdminBoxDesignSchema:
    return AdminBoxDesignSchema(
        id=design.id,
        code=design.code,
        name=design.name.value,
        preview_image_url=design.preview_image_url.value,
        sort_order=design.sort_order.value,
        description=(
            design.description.value if design.description is not None else None
        ),
        theme_config=dict(design.theme_config),
        is_active=design.is_active,
        preview_asset_id=design.preview_asset_id,
        preview_asset_id_light=design.preview_asset_id_light,
        rating_avg=0.0,
        rating_count=0,
        my_rating=None,
    )


def media_to_response(media: MediaFile) -> MediaFileSchema:
    return MediaFileSchema(
        id=media.id,
        owner_id=media.owner_id,
        storage_key=media.storage_key,
        mime_type=media.mime_type,
        media_kind=media.media_kind.value,
        size_bytes=media.size_bytes,
        original_filename=media.original_filename,
    )
