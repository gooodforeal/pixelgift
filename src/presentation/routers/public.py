import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status

from src.application.use_cases.queries import (
    GetPublicBoxItemContentUseCase,
    GetPublicBoxUseCase,
)
from src.domain.exceptions.boxes import (
    BoxContentLockedError,
    BoxItemNotFoundError,
    BoxNotFoundBySlugError,
    PublicSlugFormatError,
)
from src.domain.exceptions.media_files import MediaFileNotFoundError
from src.presentation.deps.boxes import get_public_box_item_content_uc, get_public_box_uc
from src.presentation.schemas.boxes import PublicBoxResponse
from src.presentation.schemas.mappers import public_box_to_response

router = APIRouter(tags=["public"])


@router.get("/b/{public_slug}", response_model=PublicBoxResponse)
async def get_public_box(
    public_slug: str,
    uc: GetPublicBoxUseCase = Depends(get_public_box_uc),
) -> PublicBoxResponse:
    try:
        view = await uc.execute(public_slug=public_slug)
    except BoxNotFoundBySlugError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PublicSlugFormatError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return public_box_to_response(
        view.box,
        content_unlocked=view.content_unlocked,
        design=view.design,
    )


@router.get("/b/{public_slug}/items/{item_id}/content")
async def get_public_box_item_content(
    public_slug: str,
    item_id: uuid.UUID,
    uc: GetPublicBoxItemContentUseCase = Depends(get_public_box_item_content_uc),
) -> Response:
    try:
        content = await uc.execute(public_slug=public_slug, item_id=item_id)
    except (BoxNotFoundBySlugError, BoxItemNotFoundError, MediaFileNotFoundError) as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except BoxContentLockedError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except PublicSlugFormatError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return Response(
        content=content.data,
        media_type=content.mime_type,
        headers={"Cache-Control": "public, max-age=3600"},
    )
