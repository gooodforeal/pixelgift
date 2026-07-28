import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from src.application.use_cases.media import UploadMediaUseCase
from src.presentation.deps import get_current_user_id, get_upload_media_uc
from src.presentation.schemas.boxes import MediaFileResponse
from src.presentation.schemas.mappers import media_to_response

router = APIRouter(prefix="/media", tags=["media"])


@router.post("", response_model=MediaFileResponse, status_code=status.HTTP_201_CREATED)
async def upload_media(
    file: UploadFile = File(...),
    user_id: uuid.UUID = Depends(get_current_user_id),
    uc: UploadMediaUseCase = Depends(get_upload_media_uc),
) -> MediaFileResponse:
    data = await file.read()
    if not data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Empty file")

    content_type = file.content_type or "application/octet-stream"
    try:
        media = await uc.execute(
            owner_id=user_id,
            data=data,
            content_type=content_type,
            original_filename=file.filename,
        )
    except Exception as exc:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            detail=f"Upload failed: {exc}",
        ) from exc
    return media_to_response(media)
