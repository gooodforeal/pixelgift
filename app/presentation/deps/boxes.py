from __future__ import annotations

from fastapi import Depends

from app.application.use_cases.certificates import GenerateGiftCertificateUseCase
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
from app.application.use_cases.queries import (
    GetBoxUseCase,
    GetOpenedThisMonthStatsUseCase,
    GetPublicBoxItemContentUseCase,
    GetPublicBoxUseCase,
    ListBoxesUseCase,
    UnlockPublicBoxUseCase,
)
from app.infrastructure.certificates.gift_certificate_pdf import (
    ReportLabGiftCertificateRenderer,
)
from app.infrastructure.storage.s3_storage import S3ObjectStorage
from app.infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork
from app.infrastructure.worker.task_queue import TaskiqTaskQueue
from app.presentation.deps.common import (
    get_jwt_service,
    get_settings,
    get_storage,
    get_task_queue,
)
from app.application.services.jwt import JwtService
from app.settings import Settings


def get_create_box_uc() -> CreateBoxUseCase:
    return CreateBoxUseCase(SqlAlchemyUnitOfWork())


def get_update_box_uc() -> UpdateBoxUseCase:
    return UpdateBoxUseCase(SqlAlchemyUnitOfWork())


def get_add_box_item_uc() -> AddBoxItemUseCase:
    return AddBoxItemUseCase(SqlAlchemyUnitOfWork())


def get_update_box_item_uc() -> UpdateBoxItemUseCase:
    return UpdateBoxItemUseCase(SqlAlchemyUnitOfWork())


def get_remove_box_item_uc() -> RemoveBoxItemUseCase:
    return RemoveBoxItemUseCase(SqlAlchemyUnitOfWork())


def get_reorder_box_items_uc() -> ReorderBoxItemsUseCase:
    return ReorderBoxItemsUseCase(SqlAlchemyUnitOfWork())


def get_publish_box_uc() -> PublishBoxUseCase:
    return PublishBoxUseCase(SqlAlchemyUnitOfWork(), TaskiqTaskQueue())


def get_archive_box_uc() -> ArchiveBoxUseCase:
    return ArchiveBoxUseCase(SqlAlchemyUnitOfWork(), TaskiqTaskQueue())


def get_unarchive_box_uc() -> UnarchiveBoxUseCase:
    return UnarchiveBoxUseCase(SqlAlchemyUnitOfWork(), TaskiqTaskQueue())


def get_list_boxes_uc() -> ListBoxesUseCase:
    return ListBoxesUseCase(SqlAlchemyUnitOfWork())


def get_get_box_uc() -> GetBoxUseCase:
    return GetBoxUseCase(SqlAlchemyUnitOfWork())


def get_gift_certificate_uc(
    settings: Settings = Depends(get_settings),
) -> GenerateGiftCertificateUseCase:
    return GenerateGiftCertificateUseCase(
        SqlAlchemyUnitOfWork(),
        ReportLabGiftCertificateRenderer(),
        public_web_url=settings.public_web_url,
    )


def get_public_box_uc(
    storage: S3ObjectStorage = Depends(get_storage),
    task_queue: TaskiqTaskQueue = Depends(get_task_queue),
    jwt_service: JwtService = Depends(get_jwt_service),
) -> GetPublicBoxUseCase:
    return GetPublicBoxUseCase(
        SqlAlchemyUnitOfWork(), storage, task_queue, jwt_service
    )


def get_unlock_public_box_uc(
    task_queue: TaskiqTaskQueue = Depends(get_task_queue),
    jwt_service: JwtService = Depends(get_jwt_service),
) -> UnlockPublicBoxUseCase:
    return UnlockPublicBoxUseCase(SqlAlchemyUnitOfWork(), jwt_service, task_queue)


def get_public_box_item_content_uc(
    storage: S3ObjectStorage = Depends(get_storage),
    jwt_service: JwtService = Depends(get_jwt_service),
) -> GetPublicBoxItemContentUseCase:
    return GetPublicBoxItemContentUseCase(
        SqlAlchemyUnitOfWork(), storage, jwt_service
    )


def get_opened_this_month_stats_uc() -> GetOpenedThisMonthStatsUseCase:
    return GetOpenedThisMonthStatsUseCase(SqlAlchemyUnitOfWork())
