from typing import Any
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from src.application.use_cases.designs import (
    CreateBoxDesignUseCase,
    GetBoxDesignUseCase,
    ListAllBoxDesignsUseCase,
    UpdateBoxDesignUseCase,
    UploadDesignAssetUseCase,
)
from src.domain.entities.users import User
from src.domain.exceptions.box_designs import (
    BoxDesignCodeConflictError,
    BoxDesignDescriptionError,
    BoxDesignNameError,
    BoxDesignNotFoundError,
)
from src.domain.exceptions.media_files import UnsupportedMediaTypeError
from src.domain.exceptions.sort_order import SortOrderError
from src.domain.exceptions.url import UrlError
from src.presentation.deps import (
    get_create_design_uc,
    get_get_design_uc,
    get_list_all_designs_uc,
    get_update_design_uc,
    get_upload_design_asset_uc,
    require_admin,
)
from src.presentation.schemas.designs import (
    AdminBoxDesignResponse,
    CreateBoxDesignRequest,
    DesignAssetUploadResponse,
    PatchBoxDesignRequest,
    UpdateBoxDesignRequest,
)
from src.presentation.schemas.mappers import admin_box_design_to_response

router = APIRouter(prefix="/admin/designs", tags=["admin-designs"])


def _theme_config_dict(value: BaseModel | dict[str, Any]) -> dict[str, Any]:
    if isinstance(value, BaseModel):
        return value.model_dump(exclude_none=False)
    return dict(value)


@router.get("", response_model=list[AdminBoxDesignResponse])
async def list_all_designs(
    _: User = Depends(require_admin),
    uc: ListAllBoxDesignsUseCase = Depends(get_list_all_designs_uc),
) -> list[AdminBoxDesignResponse]:
    designs = await uc.execute()
    return [admin_box_design_to_response(design) for design in designs]


@router.post(
    "/upload",
    response_model=DesignAssetUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_design_asset(
    file: UploadFile = File(...),
    _: User = Depends(require_admin),
    uc: UploadDesignAssetUseCase = Depends(get_upload_design_asset_uc),
) -> DesignAssetUploadResponse:
    data = await file.read()
    if not data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Empty file")

    content_type = file.content_type or "application/octet-stream"
    try:
        asset, url = await uc.execute(
            data=data,
            content_type=content_type,
            original_filename=file.filename,
        )
    except UnsupportedMediaTypeError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            detail=f"Upload failed: {exc}",
        ) from exc

    return DesignAssetUploadResponse(
        id=asset.id,
        url=url,
        mime_type=asset.mime_type,
        size_bytes=asset.size_bytes,
    )


@router.post("", response_model=AdminBoxDesignResponse, status_code=status.HTTP_201_CREATED)
async def create_design(
    body: CreateBoxDesignRequest,
    _: User = Depends(require_admin),
    uc: CreateBoxDesignUseCase = Depends(get_create_design_uc),
) -> AdminBoxDesignResponse:
    try:
        design = await uc.execute(
            code=body.code,
            name=body.name,
            preview_image_url=body.preview_image_url,
            description=body.description,
            theme_config=_theme_config_dict(body.theme_config),
            is_active=body.is_active,
            sort_order=body.sort_order,
        )
    except BoxDesignCodeConflictError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except (
        BoxDesignNameError,
        BoxDesignDescriptionError,
        UrlError,
        SortOrderError,
        ValueError,
    ) as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return admin_box_design_to_response(design)


@router.get("/{design_id}", response_model=AdminBoxDesignResponse)
async def get_design(
    design_id: uuid.UUID,
    _: User = Depends(require_admin),
    uc: GetBoxDesignUseCase = Depends(get_get_design_uc),
) -> AdminBoxDesignResponse:
    try:
        design = await uc.execute(design_id=design_id)
    except BoxDesignNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return admin_box_design_to_response(design)


@router.put("/{design_id}", response_model=AdminBoxDesignResponse)
async def update_design(
    design_id: uuid.UUID,
    body: UpdateBoxDesignRequest,
    _: User = Depends(require_admin),
    uc: UpdateBoxDesignUseCase = Depends(get_update_design_uc),
) -> AdminBoxDesignResponse:
    try:
        design = await uc.execute(
            design_id=design_id,
            code=body.code,
            name=body.name,
            preview_image_url=body.preview_image_url,
            description=body.description,
            theme_config=_theme_config_dict(body.theme_config),
            is_active=body.is_active,
            sort_order=body.sort_order,
        )
    except BoxDesignNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except BoxDesignCodeConflictError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except (
        BoxDesignNameError,
        BoxDesignDescriptionError,
        UrlError,
        SortOrderError,
        ValueError,
    ) as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return admin_box_design_to_response(design)


@router.patch("/{design_id}", response_model=AdminBoxDesignResponse)
async def patch_design(
    design_id: uuid.UUID,
    body: PatchBoxDesignRequest,
    _: User = Depends(require_admin),
    uc: UpdateBoxDesignUseCase = Depends(get_update_design_uc),
) -> AdminBoxDesignResponse:
    payload = body.model_dump(exclude_unset=True)
    theme_config = payload.pop("theme_config", None)
    if theme_config is not None and body.theme_config is not None:
        theme_config = _theme_config_dict(body.theme_config)

    description_set = "description" in body.model_fields_set
    try:
        design = await uc.execute(
            design_id=design_id,
            code=payload.get("code"),
            name=payload.get("name"),
            preview_image_url=payload.get("preview_image_url"),
            description=payload.get("description") if description_set else ...,
            theme_config=theme_config,
            is_active=payload.get("is_active"),
            sort_order=payload.get("sort_order"),
        )
    except BoxDesignNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except BoxDesignCodeConflictError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except (
        BoxDesignNameError,
        BoxDesignDescriptionError,
        UrlError,
        SortOrderError,
        ValueError,
    ) as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return admin_box_design_to_response(design)
