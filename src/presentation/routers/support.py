from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel

from src.application.dto.support import (
    CreateSupportTicketCommand,
    SupportAttachmentUpload,
)
from src.application.use_cases.support import CreateSupportTicketUseCase
from src.domain.exceptions.support import SupportTicketValidationError
from src.presentation.deps.common import get_settings
from src.presentation.deps.support import get_create_support_ticket_uc
from src.presentation.schemas.support import SupportTicketResponse
from src.presentation.schemas.support_mappers import support_ticket_to_response
from src.settings import Settings

router = APIRouter(prefix="/support", tags=["support"])


class SupportConfigResponse(BaseModel):
    telegram_url: str


@router.get("/config", response_model=SupportConfigResponse)
async def support_config(
    cfg: Settings = Depends(get_settings),
) -> SupportConfigResponse:
    return SupportConfigResponse(telegram_url=cfg.support_telegram_url)


@router.post("", response_model=SupportTicketResponse, status_code=status.HTTP_201_CREATED)
async def create_support_ticket(
    contact: str = Form(...),
    subject: str = Form(...),
    description: str = Form(...),
    files: list[UploadFile] | None = File(default=None),
    uc: CreateSupportTicketUseCase = Depends(get_create_support_ticket_uc),
) -> SupportTicketResponse:
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

    try:
        ticket = await uc.execute(
            CreateSupportTicketCommand(
                contact=contact,
                subject=subject,
                description=description,
                files=tuple(uploads),
            )
        )
    except SupportTicketValidationError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return support_ticket_to_response(ticket)
