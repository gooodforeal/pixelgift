import uuid

from fastapi import APIRouter, Depends, Query

from app.application.dto.assistant import (
    BoxEditorFormSnapshot,
    ChatBoxAssistantCommand,
    ListBoxAssistantHistoryCommand,
)
from app.application.use_cases.assistant import (
    ChatBoxAssistantUseCase,
    ListBoxAssistantHistoryUseCase,
)
from app.presentation.deps.assistant import (
    get_chat_box_assistant_uc,
    get_list_box_assistant_history_uc,
)
from app.presentation.deps.auth import get_current_user_id
from app.presentation.schemas.assistant import (
    AssistantHistoryMessageSchema,
    BoxAssistantHistoryResponse,
    BoxAssistantHistorySchema,
    ChatBoxAssistantRequest,
    ChatBoxAssistantResponse,
    ChatBoxAssistantSchema,
)

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.get("/box-editor/history", response_model=BoxAssistantHistoryResponse)
async def get_box_editor_assistant_history(
    box_id: uuid.UUID | None = Query(default=None),
    thread_id: uuid.UUID | None = Query(default=None),
    user_id: uuid.UUID = Depends(get_current_user_id),
    uc: ListBoxAssistantHistoryUseCase = Depends(get_list_box_assistant_history_uc),
) -> BoxAssistantHistoryResponse:
    result = await uc.execute(
        ListBoxAssistantHistoryCommand(
            user_id=user_id,
            box_id=box_id,
            thread_id=thread_id,
        )
    )
    return BoxAssistantHistoryResponse(
        message="Success",
        result=BoxAssistantHistorySchema(
            thread_id=result.thread_id,
            messages=[
                AssistantHistoryMessageSchema(role=item.role, content=item.content)
                for item in result.messages
            ],
        ),
    )


@router.post("/box-editor", response_model=ChatBoxAssistantResponse)
async def chat_box_editor_assistant(
    body: ChatBoxAssistantRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    uc: ChatBoxAssistantUseCase = Depends(get_chat_box_assistant_uc),
) -> ChatBoxAssistantResponse:
    form = None
    if body.form is not None:
        form = BoxEditorFormSnapshot(
            design_id=body.form.design_id,
            title=body.form.title,
            recipient_name=body.form.recipient_name,
            recipient_email=body.form.recipient_email,
            unlock_password_set=body.form.unlock_password_set,
            activates_at=body.form.activates_at,
            timezone=body.form.timezone,
            message=body.form.message,
            preview_title=body.form.preview_title,
        )

    result = await uc.execute(
        ChatBoxAssistantCommand(
            user_id=user_id,
            message=body.message,
            step=body.step,
            thread_id=body.thread_id,
            box_id=body.box_id,
            form=form,
        )
    )
    return ChatBoxAssistantResponse(
        message="Success",
        result=ChatBoxAssistantSchema(
            reply=result.reply,
            thread_id=result.thread_id,
            context=result.context,
        ),
    )
