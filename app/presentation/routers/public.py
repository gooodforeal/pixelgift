import uuid

from fastapi import APIRouter, Depends, Query, Response

from app.application.use_cases.queries import (
    GetPublicBoxItemContentUseCase,
    GetPublicBoxUseCase,
    UnlockPublicBoxUseCase,
)
from app.presentation.deps.boxes import (
    get_public_box_item_content_uc,
    get_public_box_uc,
    get_unlock_public_box_uc,
)
from app.presentation.schemas.boxes import (
    PublicBoxResponse,
    UnlockPublicBoxRequest,
    UnlockPublicBoxResponse,
    UnlockPublicBoxSchema,
)
from app.presentation.schemas.mappers import public_box_to_response

router = APIRouter(tags=["public"])


@router.get("/b/{public_slug}", response_model=PublicBoxResponse)
async def get_public_box(
    public_slug: str,
    unlock_token: str | None = Query(default=None),
    uc: GetPublicBoxUseCase = Depends(get_public_box_uc),
) -> PublicBoxResponse:
    view = await uc.execute(public_slug=public_slug, unlock_token=unlock_token)
    return PublicBoxResponse(
        message="Success",
        result=public_box_to_response(
            view.box,
            content_unlocked=view.content_unlocked,
            design=view.design,
        ),
    )


@router.post(
    "/b/{public_slug}/unlock",
    response_model=UnlockPublicBoxResponse,
)
async def unlock_public_box(
    public_slug: str,
    body: UnlockPublicBoxRequest,
    uc: UnlockPublicBoxUseCase = Depends(get_unlock_public_box_uc),
) -> UnlockPublicBoxResponse:
    view = await uc.execute(public_slug=public_slug, password=body.password)
    return UnlockPublicBoxResponse(
        message="Success",
        result=UnlockPublicBoxSchema(
            unlock_token=view.unlock_token,
            box=public_box_to_response(
                view.box,
                content_unlocked=view.content_unlocked,
                design=view.design,
            ),
        ),
    )


@router.get("/b/{public_slug}/items/{item_id}/content")
async def get_public_box_item_content(
    public_slug: str,
    item_id: uuid.UUID,
    unlock_token: str | None = Query(default=None),
    uc: GetPublicBoxItemContentUseCase = Depends(get_public_box_item_content_uc),
) -> Response:
    content = await uc.execute(
        public_slug=public_slug,
        item_id=item_id,
        unlock_token=unlock_token,
    )
    return Response(
        content=content.data,
        media_type=content.mime_type,
        headers={"Cache-Control": "public, max-age=3600"},
    )
