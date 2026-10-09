"""Публичные обращения в поддержку."""

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.application.dto.support import (
    CreateSupportTicketCommand,
    SupportAttachmentUpload,
)
from app.application.use_cases.support import CreateSupportTicketUseCase
from app.presentation.deps.common import get_settings
from app.presentation.deps.support import get_create_support_ticket_uc
from app.presentation.schemas.support import (
    SupportConfigResponse,
    SupportConfigSchema,
    SupportTicketResponse,
)
from app.presentation.schemas.support_mappers import support_ticket_to_response
from app.settings import Settings

router = APIRouter(prefix="/support", tags=["support"])


@router.get("/config", response_model=SupportConfigResponse)
async def support_config(
    cfg: Settings = Depends(get_settings),
) -> SupportConfigResponse:
    """GET /support/config — ссылка на Telegram поддержки."""
    return SupportConfigResponse(
        message="Success",
        result=SupportConfigSchema(telegram_url=cfg.support_telegram_url),
    )


@router.post(
    "",
    response_model=SupportTicketResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_support_ticket(
    contact: str = Form(...),
    subject: str = Form(...),
    description: str = Form(...),
    files: list[UploadFile] | None = File(default=None),
    uc: CreateSupportTicketUseCase = Depends(get_create_support_ticket_uc),
) -> SupportTicketResponse:
    """POST /support — создание тикета с вложениями."""
    uploads: list[SupportAttachmentUpload] = []
    for upload in files or []:
        data = await upload.read()
        uploads.append(
            SupportAttachmentUpload(
                data=data,
                mime_type=upload.content_type or "application/octet-stream",
                original_filename=upload.filename,
            )
        )

    ticket = await uc.execute(
        CreateSupportTicketCommand(
            contact=contact,
            subject=subject,
            description=description,
            files=tuple(uploads),
        )
    )
    return SupportTicketResponse(
        message="Success", result=support_ticket_to_response(ticket)
    )
