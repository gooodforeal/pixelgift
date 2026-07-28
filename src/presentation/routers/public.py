from fastapi import APIRouter, Depends, HTTPException, status

from src.application.use_cases.queries import GetPublicBoxUseCase
from src.domain.exceptions.boxes import BoxNotFoundBySlugError, PublicSlugFormatError
from src.presentation.deps import get_public_box_uc
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
    return public_box_to_response(view.box, content_unlocked=view.content_unlocked)
