from datetime import datetime
from typing import Literal
import uuid

from pydantic import BaseModel, Field


class SupportTicketAttachmentResponse(BaseModel):
    id: uuid.UUID
    mime_type: str
    size_bytes: int
    original_filename: str | None = None


class SupportTicketResponse(BaseModel):
    id: uuid.UUID
    contact: str
    subject: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
    attachments: list[SupportTicketAttachmentResponse] = Field(default_factory=list)


class UpdateSupportTicketStatusRequest(BaseModel):
    status: Literal["new", "in_progress", "resolved", "closed"]


class PaginatedSupportTicketsResponse(BaseModel):
    items: list[SupportTicketResponse]
    total: int
    page: int
    page_size: int
