"""Схемы обращений в поддержку."""

from datetime import datetime
from typing import Literal
import uuid

from pydantic import BaseModel, Field

from app.presentation.schemas.base import BaseResponseSchema


class SupportConfigSchema(BaseModel):
    """Публичные ссылки поддержки."""
    telegram_url: str


class SupportConfigResponse(BaseResponseSchema[SupportConfigSchema]):
    """Ответ GET /support/config."""
    pass


class SupportTicketAttachmentSchema(BaseModel):
    """Метаданные вложения тикета."""
    id: uuid.UUID
    mime_type: str
    size_bytes: int
    original_filename: str | None = None


class SupportTicketSchema(BaseModel):
    """Тикет поддержки."""
    id: uuid.UUID
    contact: str
    subject: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
    attachments: list[SupportTicketAttachmentSchema] = Field(default_factory=list)


class SupportTicketResponse(BaseResponseSchema[SupportTicketSchema]):
    """Ответ с одним тикетом."""
    pass


class UpdateSupportTicketStatusRequest(BaseModel):
    """Смена статуса тикета (админ)."""
    status: Literal["new", "in_progress", "resolved", "closed"]


class PaginatedSupportTicketsSchema(BaseModel):
    """Страница тикетов."""
    items: list[SupportTicketSchema]
    total: int
    page: int
    page_size: int


class PaginatedSupportTicketsResponse(BaseResponseSchema[PaginatedSupportTicketsSchema]):
    """Ответ списка тикетов (админ)."""
    pass
