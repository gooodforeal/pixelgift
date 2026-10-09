"""Зависимости use case'ов дизайнов боксов и ассетов."""

from __future__ import annotations

from fastapi import Depends

from app.application.use_cases.designs import (
    CreateBoxDesignUseCase,
    GetBoxDesignUseCase,
    GetDesignAssetContentUseCase,
    ListAllBoxDesignsUseCase,
    ListBoxDesignsUseCase,
    RateDesignUseCase,
    UpdateBoxDesignUseCase,
    UploadDesignAssetUseCase,
)
from app.infrastructure.storage.s3_storage import S3ObjectStorage
from app.infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork
from app.presentation.deps.common import get_settings, get_storage
from app.settings import Settings


def get_list_designs_uc() -> ListBoxDesignsUseCase:
    """Use case списка активных дизайнов для каталога."""
    return ListBoxDesignsUseCase(SqlAlchemyUnitOfWork())


def get_rate_design_uc() -> RateDesignUseCase:
    """Use case выставления оценки дизайну."""
    return RateDesignUseCase(SqlAlchemyUnitOfWork())


def get_list_all_designs_uc() -> ListAllBoxDesignsUseCase:
    """Use case списка всех дизайнов для админки."""
    return ListAllBoxDesignsUseCase(SqlAlchemyUnitOfWork())


def get_get_design_uc() -> GetBoxDesignUseCase:
    """Use case получения одного дизайна по id."""
    return GetBoxDesignUseCase(SqlAlchemyUnitOfWork())


def get_create_design_uc() -> CreateBoxDesignUseCase:
    """Use case создания дизайна."""
    return CreateBoxDesignUseCase(SqlAlchemyUnitOfWork())


def get_update_design_uc() -> UpdateBoxDesignUseCase:
    """Use case обновления дизайна."""
    return UpdateBoxDesignUseCase(SqlAlchemyUnitOfWork())


def get_upload_design_asset_uc(
    storage: S3ObjectStorage = Depends(get_storage),
    cfg: Settings = Depends(get_settings),
) -> UploadDesignAssetUseCase:
    """Use case загрузки файла ассета дизайна в S3."""
    return UploadDesignAssetUseCase(
        SqlAlchemyUnitOfWork(),
        storage,
        api_base_url=cfg.api_base_url,
    )


def get_design_asset_content_uc(
    storage: S3ObjectStorage = Depends(get_storage),
) -> GetDesignAssetContentUseCase:
    """Use case выдачи байтов ассета дизайна."""
    return GetDesignAssetContentUseCase(SqlAlchemyUnitOfWork(), storage)
