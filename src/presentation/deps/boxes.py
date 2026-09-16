from __future__ import annotations

from fastapi import Depends

from src.application.use_cases.boxes import (
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
from src.application.use_cases.queries import (
    GetBoxUseCase,
    GetPublicBoxItemContentUseCase,
    GetPublicBoxUseCase,
    ListBoxesUseCase,
)
from src.infrastructure.storage.s3_storage import S3ObjectStorage
from src.infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork
from src.infrastructure.worker.task_queue import TaskiqTaskQueue
from src.presentation.deps.common import get_storage, get_task_queue


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


def get_public_box_uc(
    storage: S3ObjectStorage = Depends(get_storage),
    task_queue: TaskiqTaskQueue = Depends(get_task_queue),
) -> GetPublicBoxUseCase:
    return GetPublicBoxUseCase(SqlAlchemyUnitOfWork(), storage, task_queue)


def get_public_box_item_content_uc(
    storage: S3ObjectStorage = Depends(get_storage),
) -> GetPublicBoxItemContentUseCase:
    return GetPublicBoxItemContentUseCase(SqlAlchemyUnitOfWork(), storage)
