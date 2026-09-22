import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status

from app.application.use_cases.media import (
    GetOwnMediaContentUseCase,
    UploadMediaUseCase,
)
from app.domain.entities.media_files import MediaKind
from app.presentation.deps.auth import get_current_user_id
from app.presentation.deps.media import (
    get_own_media_content_uc,
    get_upload_media_uc,
)
from app.presentation.schemas.boxes import MediaFileResponse
from app.presentation.schemas.mappers import media_to_response

router = APIRouter(prefix="/media", tags=["media"])

_KIND_VALUES = {kind.value for kind in MediaKind}


@router.post(
    "",
    response_model=MediaFileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_media(
    file: UploadFile = File(...),
    kind: str | None = Form(default=None),
    user_id: uuid.UUID = Depends(get_current_user_id),
    uc: UploadMediaUseCase = Depends(get_upload_media_uc),
) -> MediaFileResponse:
    data = await file.read()
    if not data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Empty file")

    preferred_kind: MediaKind | None = None
    if kind is not None:
        if kind not in _KIND_VALUES:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown media kind: {kind!r}",
            )
        preferred_kind = MediaKind(kind)

    content_type = file.content_type or "application/octet-stream"
    media = await uc.execute(
        owner_id=user_id,
        data=data,
        content_type=content_type,
        original_filename=file.filename,
        preferred_kind=preferred_kind,
    )
    return MediaFileResponse(message="Success", result=media_to_response(media))


@router.get("/{media_id}/content")
async def get_media_content(
    media_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    uc: GetOwnMediaContentUseCase = Depends(get_own_media_content_uc),
) -> Response:
    content = await uc.execute(media_id=media_id, actor_id=user_id)
    return Response(
        content=content.data,
        media_type=content.mime_type,
        headers={"Cache-Control": "private, max-age=300"},
    )
