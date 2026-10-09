"""Преобразование сущностей поддержки в API-схемы."""

from app.domain.entities.support_tickets import SupportTicket, SupportTicketAttachment
from app.presentation.schemas.support import (
    SupportTicketAttachmentSchema,
    SupportTicketSchema,
)


def support_attachment_to_response(
    item: SupportTicketAttachment,
) -> SupportTicketAttachmentSchema:
    """Маппинг вложения тикета в схему ответа."""
    return SupportTicketAttachmentSchema(
        id=item.id,
        mime_type=item.mime_type,
        size_bytes=item.size_bytes,
        original_filename=item.original_filename,
    )


def support_ticket_to_response(ticket: SupportTicket) -> SupportTicketSchema:
    """Маппинг тикета поддержки в схему ответа."""
    return SupportTicketSchema(
        id=ticket.id,
        contact=ticket.contact,
        subject=ticket.subject,
        description=ticket.description,
        status=ticket.status.value,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        attachments=[
            support_attachment_to_response(item) for item in ticket.attachments
        ],
    )
