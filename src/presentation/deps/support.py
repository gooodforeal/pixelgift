from fastapi import Depends

from src.application.use_cases.support import (
    CreateSupportTicketUseCase,
    GetSupportTicketAttachmentContentUseCase,
    GetSupportTicketUseCase,
    ListSupportTicketsUseCase,
    UpdateSupportTicketStatusUseCase,
)
from src.infrastructure.storage.s3_storage import S3ObjectStorage
from src.infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork
from src.presentation.deps.common import get_storage


def get_create_support_ticket_uc(
    storage: S3ObjectStorage = Depends(get_storage),
) -> CreateSupportTicketUseCase:
    return CreateSupportTicketUseCase(SqlAlchemyUnitOfWork(), storage)


def get_list_support_tickets_uc() -> ListSupportTicketsUseCase:
    return ListSupportTicketsUseCase(SqlAlchemyUnitOfWork())


def get_get_support_ticket_uc() -> GetSupportTicketUseCase:
    return GetSupportTicketUseCase(SqlAlchemyUnitOfWork())


def get_update_support_ticket_status_uc() -> UpdateSupportTicketStatusUseCase:
    return UpdateSupportTicketStatusUseCase(SqlAlchemyUnitOfWork())


def get_support_attachment_content_uc(
    storage: S3ObjectStorage = Depends(get_storage),
) -> GetSupportTicketAttachmentContentUseCase:
    return GetSupportTicketAttachmentContentUseCase(SqlAlchemyUnitOfWork(), storage)
