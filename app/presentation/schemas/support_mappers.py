from app.domain.entities.support_tickets import SupportTicket, SupportTicketAttachment
from app.presentation.schemas.support import (
    SupportTicketAttachmentResponse,
    SupportTicketResponse,
)


def support_attachment_to_response(
    item: SupportTicketAttachment,
) -> SupportTicketAttachmentResponse:
    return SupportTicketAttachmentResponse(
        id=item.id,
        mime_type=item.mime_type,
        size_bytes=item.size_bytes,
        original_filename=item.original_filename,
    )


def support_ticket_to_response(ticket: SupportTicket) -> SupportTicketResponse:
    return SupportTicketResponse(
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
