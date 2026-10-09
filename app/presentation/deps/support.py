"""Зависимости тикетов поддержки."""

from fastapi import Depends

from app.application.use_cases.support import (
    CreateSupportTicketUseCase,
    GetSupportTicketAttachmentContentUseCase,
    GetSupportTicketUseCase,
    ListSupportTicketsUseCase,
    UpdateSupportTicketStatusUseCase,
)
from app.infrastructure.storage.s3_storage import S3ObjectStorage
from app.infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork
from app.presentation.deps.common import get_storage


def get_create_support_ticket_uc(
    storage: S3ObjectStorage = Depends(get_storage),
) -> CreateSupportTicketUseCase:
    """Use case создания тикета с вложениями в S3."""
    return CreateSupportTicketUseCase(SqlAlchemyUnitOfWork(), storage)


def get_list_support_tickets_uc() -> ListSupportTicketsUseCase:
    """Use case списка тикетов для админки."""
    return ListSupportTicketsUseCase(SqlAlchemyUnitOfWork())


def get_get_support_ticket_uc() -> GetSupportTicketUseCase:
    """Use case одного тикета по id."""
    return GetSupportTicketUseCase(SqlAlchemyUnitOfWork())


def get_update_support_ticket_status_uc() -> UpdateSupportTicketStatusUseCase:
    """Use case смены статуса тикета."""
    return UpdateSupportTicketStatusUseCase(SqlAlchemyUnitOfWork())


def get_support_attachment_content_uc(
    storage: S3ObjectStorage = Depends(get_storage),
) -> GetSupportTicketAttachmentContentUseCase:
    """Use case выдачи файла вложения тикета."""
    return GetSupportTicketAttachmentContentUseCase(SqlAlchemyUnitOfWork(), storage)
