import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status

from src.application.use_cases.designs import (
    GetDesignAssetContentUseCase,
    ListBoxDesignsUseCase,
)
from src.domain.exceptions.box_designs import DesignAssetNotFoundError
from src.presentation.deps import get_design_asset_content_uc, get_list_designs_uc
from src.presentation.schemas.designs import BoxDesignResponse
from src.presentation.schemas.mappers import box_design_to_response

router = APIRouter(prefix="/designs", tags=["designs"])


@router.get("", response_model=list[BoxDesignResponse])
async def list_designs(
    uc: ListBoxDesignsUseCase = Depends(get_list_designs_uc),
) -> list[BoxDesignResponse]:
    designs = await uc.execute()
    return [box_design_to_response(design) for design in designs]


@router.get("/assets/{asset_id}")
async def get_design_asset(
    asset_id: uuid.UUID,
    uc: GetDesignAssetContentUseCase = Depends(get_design_asset_content_uc),
) -> Response:
    try:
        content = await uc.execute(asset_id=asset_id)
    except DesignAssetNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return Response(
        content=content.data,
        media_type=content.mime_type,
        headers={"Cache-Control": "public, max-age=86400"},
    )
