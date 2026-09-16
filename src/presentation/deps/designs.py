from __future__ import annotations

from fastapi import Depends

from src.application.use_cases.designs import (
    CreateBoxDesignUseCase,
    GetBoxDesignUseCase,
    GetDesignAssetContentUseCase,
    ListAllBoxDesignsUseCase,
    ListBoxDesignsUseCase,
    RateDesignUseCase,
    UpdateBoxDesignUseCase,
    UploadDesignAssetUseCase,
)
from src.infrastructure.storage.s3_storage import S3ObjectStorage
from src.infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork
from src.presentation.deps.common import get_settings, get_storage
from src.settings import Settings


def get_list_designs_uc() -> ListBoxDesignsUseCase:
    return ListBoxDesignsUseCase(SqlAlchemyUnitOfWork())


def get_rate_design_uc() -> RateDesignUseCase:
    return RateDesignUseCase(SqlAlchemyUnitOfWork())


def get_list_all_designs_uc() -> ListAllBoxDesignsUseCase:
    return ListAllBoxDesignsUseCase(SqlAlchemyUnitOfWork())


def get_get_design_uc() -> GetBoxDesignUseCase:
    return GetBoxDesignUseCase(SqlAlchemyUnitOfWork())


def get_create_design_uc() -> CreateBoxDesignUseCase:
    return CreateBoxDesignUseCase(SqlAlchemyUnitOfWork())


def get_update_design_uc() -> UpdateBoxDesignUseCase:
    return UpdateBoxDesignUseCase(SqlAlchemyUnitOfWork())


def get_upload_design_asset_uc(
    storage: S3ObjectStorage = Depends(get_storage),
    cfg: Settings = Depends(get_settings),
) -> UploadDesignAssetUseCase:
    return UploadDesignAssetUseCase(
        SqlAlchemyUnitOfWork(),
        storage,
        api_base_url=cfg.api_base_url,
    )


def get_design_asset_content_uc(
    storage: S3ObjectStorage = Depends(get_storage),
) -> GetDesignAssetContentUseCase:
    return GetDesignAssetContentUseCase(SqlAlchemyUnitOfWork(), storage)
