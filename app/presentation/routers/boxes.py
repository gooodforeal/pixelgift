import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response

from app.application.dto.boxes import (
    AddBoxItemCommand,
    ArchiveBoxCommand,
    CreateBoxCommand,
    PublishBoxCommand,
    RemoveBoxItemCommand,
    ReorderBoxItemsCommand,
    UnarchiveBoxCommand,
    UpdateBoxCommand,
    UpdateBoxItemCommand,
)
from app.application.use_cases.boxes import (
    AddBoxItemUseCase,
    ArchiveBoxUseCase,
    CreateBoxUseCase,
    PublishBoxUseCase,
    RemoveBoxItemUseCase,
    ReorderBoxItemsUseCase,
    UnarchiveBoxUseCase,
    UpdateBoxItemUseCase,
    UpdateBoxUseCase,
)
from app.application.use_cases.queries import GetBoxUseCase, ListBoxesUseCase
from app.domain.exceptions.boxes import (
    BoxAccessDeniedError,
    BoxAlreadyArchivedError,
    BoxAlreadyOpenedError,
    BoxDesignNotAvailableError,
    BoxItemNotFoundError,
    BoxItemReorderError,
    BoxItemsLimitExceededError,
    BoxNotArchivedError,
    BoxNotEditableError,
    BoxNotFoundError,
    BoxCertificateNotAvailableError,
    BoxNotPublishableError,
    BoxWithoutItemsError,
    PublicSlugAlreadyTakenError,
)
from app.domain.exceptions.box_items import BoxItemInvalidError
from app.domain.exceptions.media_files import (
    MediaFileAccessDeniedError,
    MediaFileNotFoundError,
)
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
from app.presentation.deps.auth import get_current_user_id
from app.presentation.deps.boxes import (
    get_add_box_item_uc,
    get_archive_box_uc,
    get_create_box_uc,
    get_get_box_uc,
    get_gift_certificate_uc,
    get_list_boxes_uc,
    get_publish_box_uc,
    get_remove_box_item_uc,
    get_reorder_box_items_uc,
    get_unarchive_box_uc,
    get_update_box_item_uc,
    get_update_box_uc,
)
from app.presentation.deps.common import PaginationParams, pagination_dep
from app.application.use_cases.certificates import GenerateGiftCertificateUseCase
from app.presentation.schemas.boxes import (
    AddBoxItemRequest,
    BoxResponse,
    CreateBoxRequest,
    PaginatedBoxesResponse,
    ReorderBoxItemsRequest,
    UpdateBoxItemRequest,
    UpdateBoxRequest,
)
from app.presentation.schemas.mappers import box_to_response

router = APIRouter(prefix="/boxes", tags=["boxes"])


def _http_error(exc: Exception) -> HTTPException:
    mapping: list[tuple[type[Exception], int]] = [
        (BoxNotFoundError, status.HTTP_404_NOT_FOUND),
        (BoxItemNotFoundError, status.HTTP_404_NOT_FOUND),
        (MediaFileNotFoundError, status.HTTP_404_NOT_FOUND),
        (BoxAccessDeniedError, status.HTTP_403_FORBIDDEN),
        (MediaFileAccessDeniedError, status.HTTP_403_FORBIDDEN),
        (BoxNotEditableError, status.HTTP_409_CONFLICT),
        (BoxNotPublishableError, status.HTTP_409_CONFLICT),
        (BoxCertificateNotAvailableError, status.HTTP_409_CONFLICT),
        (BoxAlreadyArchivedError, status.HTTP_409_CONFLICT),
        (BoxNotArchivedError, status.HTTP_409_CONFLICT),
        (BoxAlreadyOpenedError, status.HTTP_409_CONFLICT),
        (BoxItemsLimitExceededError, status.HTTP_409_CONFLICT),
        (BoxWithoutItemsError, status.HTTP_400_BAD_REQUEST),
        (BoxDesignNotAvailableError, status.HTTP_400_BAD_REQUEST),
        (BoxItemInvalidError, status.HTTP_400_BAD_REQUEST),
        (PublicSlugAlreadyTakenError, status.HTTP_409_CONFLICT),
        (BoxItemReorderError, status.HTTP_400_BAD_REQUEST),
    ]
    for exc_type, code in mapping:
        if isinstance(exc, exc_type):
            return HTTPException(code, detail=str(exc))
    return HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("", response_model=BoxResponse, status_code=status.HTTP_201_CREATED)
async def create_box(
    body: CreateBoxRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    uc: CreateBoxUseCase = Depends(get_create_box_uc),
) -> BoxResponse:
    try:
        box = await uc.execute(
            CreateBoxCommand(
                owner_id=user_id,
                design_id=body.design_id,
                title=BoxTitle(body.title),
                recipient_name=BoxRecipientName(body.recipient_name),
                recipient_email=BoxRecipientEmail(body.recipient_email),
                unlock_password=BoxUnlockPassword(body.unlock_password),
                activates_at=ActivatesAt(body.activates_at),
                timezone=body.timezone,
                public_slug=PublicSlug(body.public_slug) if body.public_slug else None,
                message=BoxMessage(body.message) if body.message else None,
                preview_title=(
                    BoxPreviewTitle(body.preview_title) if body.preview_title else None
                ),
                preview_image_url=(
                    Url(body.preview_image_url) if body.preview_image_url else None
                ),
            )
        )
    except Exception as exc:
        raise _http_error(exc) from exc
    return box_to_response(box)


@router.get("", response_model=PaginatedBoxesResponse)
async def list_boxes(
    user_id: uuid.UUID = Depends(get_current_user_id),
    pagination: PaginationParams = Depends(pagination_dep),
    uc: ListBoxesUseCase = Depends(get_list_boxes_uc),
) -> PaginatedBoxesResponse:
    page = await uc.execute(
        owner_id=user_id,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return PaginatedBoxesResponse(
        items=[box_to_response(box) for box in page.items],
        total=page.total,
        page=page.page,
        page_size=page.page_size,
        status_counts=page.status_counts,
    )


@router.get("/{box_id}", response_model=BoxResponse)
async def get_box(
    box_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    uc: GetBoxUseCase = Depends(get_get_box_uc),
) -> BoxResponse:
    try:
        box = await uc.execute(box_id=box_id, actor_id=user_id)
    except Exception as exc:
        raise _http_error(exc) from exc
    return box_to_response(box)


@router.get("/{box_id}/certificate.pdf")
async def download_gift_certificate(
    box_id: uuid.UUID,
    theme: str = Query(default="dark", pattern="^(dark|light)$"),
    user_id: uuid.UUID = Depends(get_current_user_id),
    uc: GenerateGiftCertificateUseCase = Depends(get_gift_certificate_uc),
) -> Response:
    try:
        certificate = await uc.execute(
            box_id=box_id,
            actor_id=user_id,
            theme=theme,  # type: ignore[arg-type]
        )
    except Exception as exc:
        raise _http_error(exc) from exc
    return Response(
        content=certificate.data,
        media_type=certificate.media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{certificate.filename}"',
            "Cache-Control": "private, no-store",
        },
    )


@router.put("/{box_id}", response_model=BoxResponse)
async def update_box(
    box_id: uuid.UUID,
    body: UpdateBoxRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    uc: UpdateBoxUseCase = Depends(get_update_box_uc),
) -> BoxResponse:
    try:
        box = await uc.execute(
            UpdateBoxCommand(
                box_id=box_id,
                actor_id=user_id,
                design_id=body.design_id,
                title=BoxTitle(body.title),
                recipient_name=BoxRecipientName(body.recipient_name),
                recipient_email=BoxRecipientEmail(body.recipient_email),
                unlock_password=BoxUnlockPassword(body.unlock_password),
                activates_at=ActivatesAt(body.activates_at),
                timezone=body.timezone,
                message=BoxMessage(body.message) if body.message else None,
                preview_title=(
                    BoxPreviewTitle(body.preview_title) if body.preview_title else None
                ),
                preview_image_url=(
                    Url(body.preview_image_url) if body.preview_image_url else None
                ),
            )
        )
    except Exception as exc:
        raise _http_error(exc) from exc
    return box_to_response(box)


@router.post("/{box_id}/publish", response_model=BoxResponse)
async def publish_box(
    box_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    uc: PublishBoxUseCase = Depends(get_publish_box_uc),
) -> BoxResponse:
    try:
        box = await uc.execute(PublishBoxCommand(box_id=box_id, actor_id=user_id))
    except Exception as exc:
        raise _http_error(exc) from exc
    return box_to_response(box)


@router.post("/{box_id}/archive", response_model=BoxResponse)
async def archive_box(
    box_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    uc: ArchiveBoxUseCase = Depends(get_archive_box_uc),
) -> BoxResponse:
    try:
        box = await uc.execute(ArchiveBoxCommand(box_id=box_id, actor_id=user_id))
    except Exception as exc:
        raise _http_error(exc) from exc
    return box_to_response(box)


@router.post("/{box_id}/unarchive", response_model=BoxResponse)
async def unarchive_box(
    box_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    uc: UnarchiveBoxUseCase = Depends(get_unarchive_box_uc),
) -> BoxResponse:
    try:
        box = await uc.execute(UnarchiveBoxCommand(box_id=box_id, actor_id=user_id))
    except Exception as exc:
        raise _http_error(exc) from exc
    return box_to_response(box)


@router.post("/{box_id}/items", response_model=BoxResponse)
async def add_box_item(
    box_id: uuid.UUID,
    body: AddBoxItemRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    uc: AddBoxItemUseCase = Depends(get_add_box_item_uc),
) -> BoxResponse:
    try:
        box = await uc.execute(
            AddBoxItemCommand(
                box_id=box_id,
                actor_id=user_id,
                media_file_id=body.media_file_id,
                item_type=body.item_type,
                caption=BoxItemCaption(body.caption) if body.caption else None,
                sort_order=SortOrder(body.sort_order) if body.sort_order else None,
                metadata=body.metadata,
            )
        )
    except Exception as exc:
        raise _http_error(exc) from exc
    return box_to_response(box)


@router.patch("/{box_id}/items/{item_id}", response_model=BoxResponse)
async def update_box_item(
    box_id: uuid.UUID,
    item_id: uuid.UUID,
    body: UpdateBoxItemRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    uc: UpdateBoxItemUseCase = Depends(get_update_box_item_uc),
) -> BoxResponse:
    try:
        box = await uc.execute(
            UpdateBoxItemCommand(
                box_id=box_id,
                actor_id=user_id,
                item_id=item_id,
                caption=BoxItemCaption(body.caption) if body.caption else None,
                metadata=body.metadata,
            )
        )
    except Exception as exc:
        raise _http_error(exc) from exc
    return box_to_response(box)


@router.delete("/{box_id}/items/{item_id}", response_model=BoxResponse)
async def remove_box_item(
    box_id: uuid.UUID,
    item_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    uc: RemoveBoxItemUseCase = Depends(get_remove_box_item_uc),
) -> BoxResponse:
    try:
        box = await uc.execute(
            RemoveBoxItemCommand(box_id=box_id, actor_id=user_id, item_id=item_id)
        )
    except Exception as exc:
        raise _http_error(exc) from exc
    return box_to_response(box)


@router.put("/{box_id}/items/reorder", response_model=BoxResponse)
async def reorder_box_items(
    box_id: uuid.UUID,
    body: ReorderBoxItemsRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    uc: ReorderBoxItemsUseCase = Depends(get_reorder_box_items_uc),
) -> BoxResponse:
    try:
        box = await uc.execute(
            ReorderBoxItemsCommand(
                box_id=box_id,
                actor_id=user_id,
                item_ids=tuple(body.item_ids),
            )
        )
    except Exception as exc:
        raise _http_error(exc) from exc
    return box_to_response(box)
