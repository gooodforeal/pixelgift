"""Обращения в поддержку: создание с вложениями и админские операции."""

from dataclasses import dataclass
from pathlib import Path
import uuid

from app.application.dto.media import MediaContent
from app.application.dto.support import (
    CreateSupportTicketCommand,
    UpdateSupportTicketStatusCommand,
)
from app.application.ports.storage.base import BaseObjectStorage
from app.application.uow.base import BaseUnitOfWork
from app.domain.entities.support_tickets import (
    SupportTicket,
    SupportTicketAttachment,
    SupportTicketStatus,
)
from app.domain.exceptions.support import (
    SupportTicketAttachmentNotFoundError,
    SupportTicketNotFoundError,
    SupportTicketValidationError,
)

MAX_CONTACT_LENGTH = 254
MAX_SUBJECT_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 4096
MAX_ATTACHMENTS = 5
MAX_TOTAL_BYTES = 4 * 1024 * 1024
ALLOWED_IMAGE_MIME = frozenset(
    {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
    }
)


def _validate_text_fields(*, contact: str, subject: str, description: str) -> tuple[str, str, str]:
    contact = contact.strip()
    subject = subject.strip()
    description = description.strip()

    if not contact:
        raise SupportTicketValidationError("Contact is required")
    if len(contact) > MAX_CONTACT_LENGTH:
        raise SupportTicketValidationError("Contact is too long")
    if not subject:
        raise SupportTicketValidationError("Subject is required")
    if len(subject) > MAX_SUBJECT_LENGTH:
        raise SupportTicketValidationError("Subject is too long")
    if not description:
        raise SupportTicketValidationError("Description is required")
    if len(description) > MAX_DESCRIPTION_LENGTH:
        raise SupportTicketValidationError("Description is too long")
    return contact, subject, description


class CreateSupportTicketUseCase:
    """Принимает обращение, валидирует текст и загружает изображения в storage."""

    def __init__(self, uow: BaseUnitOfWork, storage: BaseObjectStorage) -> None:
        self._uow = uow
        self._storage = storage

    async def execute(self, command: CreateSupportTicketCommand) -> SupportTicket:
        contact, subject, description = _validate_text_fields(
            contact=command.contact,
            subject=command.subject,
            description=command.description,
        )

        if len(command.files) > MAX_ATTACHMENTS:
            raise SupportTicketValidationError(
                f"At most {MAX_ATTACHMENTS} images are allowed"
            )

        total_size = sum(len(item.data) for item in command.files)
        if total_size > MAX_TOTAL_BYTES:
            raise SupportTicketValidationError(
                "Total attachments size must be at most 4 MB"
            )

        for item in command.files:
            if item.mime_type not in ALLOWED_IMAGE_MIME:
                raise SupportTicketValidationError(
                    f"Unsupported image type: {item.mime_type}"
                )
            if not item.data:
                raise SupportTicketValidationError("Empty attachment is not allowed")

        ticket = SupportTicket(
            contact=contact,
            subject=subject,
            description=description,
        )

        for item in command.files:
            attachment_id = uuid.uuid4()
            ext = Path(item.original_filename or "").suffix.lower() or {
                "image/jpeg": ".jpg",
                "image/png": ".png",
                "image/webp": ".webp",
                "image/gif": ".gif",
            }.get(item.mime_type, ".bin")
            storage_key = f"support/{ticket.id}/{attachment_id}{ext}"
            await self._storage.upload(
                storage_key,
                item.data,
                content_type=item.mime_type,
            )
            ticket.attachments.append(
                SupportTicketAttachment(
                    id=attachment_id,
                    ticket_id=ticket.id,
                    storage_key=storage_key,
                    mime_type=item.mime_type,
                    size_bytes=len(item.data),
                    original_filename=item.original_filename,
                )
            )

        async with self._uow as uow:
            await uow.support_tickets.add(ticket)
            await uow.commit()
            return ticket


@dataclass(frozen=True, kw_only=True)
class SupportTicketsPage:
    """Постраничный список тикетов для админки."""

    items: list[SupportTicket]
    total: int
    page: int
    page_size: int


class ListSupportTicketsUseCase:
    """Фильтруемый список тикетов поддержки."""

    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        status: SupportTicketStatus | None = None,
        sort_asc: bool = False,
        page: int = 1,
        page_size: int = 10,
    ) -> SupportTicketsPage:
        offset = (page - 1) * page_size
        async with self._uow as uow:
            items = await uow.support_tickets.list_all(
                status=status,
                sort_asc=sort_asc,
                limit=page_size,
                offset=offset,
            )
            total = await uow.support_tickets.count_all(status=status)
            return SupportTicketsPage(
                items=items,
                total=total,
                page=page,
                page_size=page_size,
            )


class GetSupportTicketUseCase:
    """Возвращает тикет с вложениями по id."""

    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, *, ticket_id: uuid.UUID) -> SupportTicket:
        async with self._uow as uow:
            ticket = await uow.support_tickets.get_by_id(ticket_id)
            if ticket is None:
                raise SupportTicketNotFoundError(ticket_id)
            return ticket


class UpdateSupportTicketStatusUseCase:
    """Меняет статус обработки тикета."""

    def __init__(self, uow: BaseUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self, command: UpdateSupportTicketStatusCommand
    ) -> SupportTicket:
        async with self._uow as uow:
            ticket = await uow.support_tickets.get_by_id(command.ticket_id)
            if ticket is None:
                raise SupportTicketNotFoundError(command.ticket_id)
            ticket.set_status(command.status)
            updated = await uow.support_tickets.update(ticket)
            await uow.commit()
            return updated


class GetSupportTicketAttachmentContentUseCase:
    """Скачивает вложение тикета из storage для просмотра админом."""

    def __init__(self, uow: BaseUnitOfWork, storage: BaseObjectStorage) -> None:
        self._uow = uow
        self._storage = storage

    async def execute(
        self,
        *,
        ticket_id: uuid.UUID,
        attachment_id: uuid.UUID,
    ) -> MediaContent:
        async with self._uow as uow:
            ticket = await uow.support_tickets.get_by_id(ticket_id)
            if ticket is None:
                raise SupportTicketNotFoundError(ticket_id)
            attachment = next(
                (item for item in ticket.attachments if item.id == attachment_id),
                None,
            )
            if attachment is None:
                raise SupportTicketAttachmentNotFoundError(attachment_id)

        data = await self._storage.download(attachment.storage_key)
        return MediaContent(
            data=data,
            mime_type=attachment.mime_type,
            filename=attachment.original_filename,
        )
