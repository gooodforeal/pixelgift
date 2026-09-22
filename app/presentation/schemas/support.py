from datetime import datetime
from typing import Literal
import uuid

from pydantic import BaseModel, Field

from app.presentation.schemas.base import BaseResponseSchema


class SupportConfigSchema(BaseModel):
    telegram_url: str


class SupportConfigResponse(BaseResponseSchema[SupportConfigSchema]):
    pass


class SupportTicketAttachmentSchema(BaseModel):
    id: uuid.UUID
    mime_type: str
    size_bytes: int
    original_filename: str | None = None


class SupportTicketSchema(BaseModel):
    id: uuid.UUID
    contact: str
    subject: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
    attachments: list[SupportTicketAttachmentSchema] = Field(default_factory=list)


class SupportTicketResponse(BaseResponseSchema[SupportTicketSchema]):
    pass


class UpdateSupportTicketStatusRequest(BaseModel):
    status: Literal["new", "in_progress", "resolved", "closed"]


class PaginatedSupportTicketsSchema(BaseModel):
    items: list[SupportTicketSchema]
    total: int
    page: int
    page_size: int


class PaginatedSupportTicketsResponse(BaseResponseSchema[PaginatedSupportTicketsSchema]):
    pass
