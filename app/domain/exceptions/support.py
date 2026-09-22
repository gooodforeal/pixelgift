from app.domain.exceptions.base import BaseException
import uuid


class SupportTicketError(BaseException):
    """Базовая ошибка обращений в поддержку."""


class SupportTicketNotFoundError(SupportTicketError):
    status_code = 404

    def __init__(self, ticket_id: uuid.UUID) -> None:
        self.ticket_id = ticket_id
        super().__init__(f"Support ticket not found: {ticket_id}")


class SupportTicketValidationError(SupportTicketError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class SupportTicketAttachmentNotFoundError(SupportTicketError):
    status_code = 404

    def __init__(self, attachment_id: uuid.UUID) -> None:
        self.attachment_id = attachment_id
        super().__init__(f"Support ticket attachment not found: {attachment_id}")
