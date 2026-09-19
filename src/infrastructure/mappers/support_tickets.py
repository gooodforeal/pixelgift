from src.domain.entities.support_tickets import (
    SupportTicket,
    SupportTicketAttachment,
    SupportTicketStatus,
)
from src.infrastructure.models.support_tickets import (
    SupportTicketAttachmentModel,
    SupportTicketModel,
)


def attachment_to_model(entity: SupportTicketAttachment) -> SupportTicketAttachmentModel:
    return SupportTicketAttachmentModel(
        id=entity.id,
        ticket_id=entity.ticket_id,
        storage_key=entity.storage_key,
        mime_type=entity.mime_type,
        size_bytes=entity.size_bytes,
        original_filename=entity.original_filename,
        created_at=entity.created_at,
    )


def attachment_to_entity(model: SupportTicketAttachmentModel) -> SupportTicketAttachment:
    return SupportTicketAttachment(
        id=model.id,
        ticket_id=model.ticket_id,
        storage_key=model.storage_key,
        mime_type=model.mime_type,
        size_bytes=model.size_bytes,
        original_filename=model.original_filename,
        created_at=model.created_at,
        updated_at=model.created_at,
    )


def support_ticket_to_model(entity: SupportTicket) -> SupportTicketModel:
    model = SupportTicketModel(
        id=entity.id,
        contact=entity.contact,
        subject=entity.subject,
        description=entity.description,
        status=entity.status.value,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )
    model.attachments = [attachment_to_model(item) for item in entity.attachments]
    return model


def support_ticket_to_entity(model: SupportTicketModel) -> SupportTicket:
    return SupportTicket(
        id=model.id,
        contact=model.contact,
        subject=model.subject,
        description=model.description,
        status=SupportTicketStatus(model.status),
        created_at=model.created_at,
        updated_at=model.updated_at,
        attachments=[attachment_to_entity(item) for item in model.attachments],
    )


def apply_support_ticket(entity: SupportTicket, model: SupportTicketModel) -> None:
    model.contact = entity.contact
    model.subject = entity.subject
    model.description = entity.description
    model.status = entity.status.value
    model.updated_at = entity.updated_at
