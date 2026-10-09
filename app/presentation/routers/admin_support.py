"""Админ-API тикетов поддержки."""

import uuid

from fastapi import APIRouter, Depends, Query, Response

from app.application.dto.support import UpdateSupportTicketStatusCommand
from app.application.use_cases.support import (
    GetSupportTicketAttachmentContentUseCase,
    GetSupportTicketUseCase,
    ListSupportTicketsUseCase,
    UpdateSupportTicketStatusUseCase,
)
from app.domain.entities.support_tickets import SupportTicketStatus
from app.domain.entities.users import User
from app.presentation.deps.common import PaginationParams, pagination_dep
from app.presentation.deps.support import (
    get_get_support_ticket_uc,
    get_list_support_tickets_uc,
    get_support_attachment_content_uc,
    get_update_support_ticket_status_uc,
)
from app.presentation.deps.users import require_admin
from app.presentation.schemas.support import (
    PaginatedSupportTicketsResponse,
    PaginatedSupportTicketsSchema,
    SupportTicketResponse,
    UpdateSupportTicketStatusRequest,
)
from app.presentation.schemas.support_mappers import support_ticket_to_response

router = APIRouter(prefix="/admin/support", tags=["admin-support"])


@router.get("", response_model=PaginatedSupportTicketsResponse)
async def list_support_tickets(
    status_filter: SupportTicketStatus | None = Query(default=None, alias="status"),
    sort: str = Query(default="desc", pattern="^(asc|desc)$"),
    pagination: PaginationParams = Depends(pagination_dep),
    _: User = Depends(require_admin),
    uc: ListSupportTicketsUseCase = Depends(get_list_support_tickets_uc),
) -> PaginatedSupportTicketsResponse:
    """GET /admin/support — список тикетов с фильтрами."""
    page = await uc.execute(
        status=status_filter,
        sort_asc=sort == "asc",
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return PaginatedSupportTicketsResponse(
        message="Success",
        result=PaginatedSupportTicketsSchema(
            items=[support_ticket_to_response(ticket) for ticket in page.items],
            total=page.total,
            page=page.page,
            page_size=page.page_size,
        ),
    )


@router.get("/{ticket_id}", response_model=SupportTicketResponse)
async def get_support_ticket(
    ticket_id: uuid.UUID,
    _: User = Depends(require_admin),
    uc: GetSupportTicketUseCase = Depends(get_get_support_ticket_uc),
) -> SupportTicketResponse:
    """GET /admin/support/{ticket_id} — один тикет."""
    ticket = await uc.execute(ticket_id=ticket_id)
    return SupportTicketResponse(
        message="Success", result=support_ticket_to_response(ticket)
    )


@router.patch("/{ticket_id}", response_model=SupportTicketResponse)
async def update_support_ticket_status(
    ticket_id: uuid.UUID,
    body: UpdateSupportTicketStatusRequest,
    _: User = Depends(require_admin),
    uc: UpdateSupportTicketStatusUseCase = Depends(get_update_support_ticket_status_uc),
) -> SupportTicketResponse:
    """PATCH /admin/support/{ticket_id} — смена статуса."""
    ticket = await uc.execute(
        UpdateSupportTicketStatusCommand(
            ticket_id=ticket_id,
            status=SupportTicketStatus(body.status),
        )
    )
    return SupportTicketResponse(
        message="Success", result=support_ticket_to_response(ticket)
    )


@router.get("/{ticket_id}/attachments/{attachment_id}/content")
async def get_support_attachment_content(
    ticket_id: uuid.UUID,
    attachment_id: uuid.UUID,
    _: User = Depends(require_admin),
    uc: GetSupportTicketAttachmentContentUseCase = Depends(
        get_support_attachment_content_uc
    ),
) -> Response:
    """GET .../attachments/{attachment_id}/content — файл вложения."""
    content = await uc.execute(ticket_id=ticket_id, attachment_id=attachment_id)
    return Response(
        content=content.data,
        media_type=content.mime_type,
        headers={"Cache-Control": "private, max-age=3600"},
    )
