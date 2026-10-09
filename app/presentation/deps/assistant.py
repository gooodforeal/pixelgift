"""Зависимости LLM-ассистента редактора бокса."""

from fastapi import Depends

from app.application.use_cases.assistant import (
    ChatBoxAssistantUseCase,
    ListBoxAssistantHistoryUseCase,
)
from app.infrastructure.llm.openai_compatible import OpenAICompatibleLlmClient
from app.infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork
from app.presentation.deps.common import get_llm_client, get_settings
from app.settings import Settings


def get_chat_box_assistant_uc(
    llm: OpenAICompatibleLlmClient = Depends(get_llm_client),
    cfg: Settings = Depends(get_settings),
) -> ChatBoxAssistantUseCase:
    """Use case диалога с ассистентом на шаге редактора."""
    return ChatBoxAssistantUseCase(
        SqlAlchemyUnitOfWork(),
        llm,
        llm_configured=bool(cfg.llm_api_key.strip()),
        max_messages=cfg.llm_assistant_max_messages,
    )


def get_list_box_assistant_history_uc(
    cfg: Settings = Depends(get_settings),
) -> ListBoxAssistantHistoryUseCase:
    """Use case истории сообщений ассистента по thread/box."""
    return ListBoxAssistantHistoryUseCase(
        SqlAlchemyUnitOfWork(),
        max_messages=cfg.llm_assistant_max_messages,
    )
