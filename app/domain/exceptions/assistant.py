"""Ошибки AI-ассистента и доступа к тредам."""

from app.domain.exceptions.base import BaseException


class AssistantError(BaseException):
    """Базовая ошибка ассистента."""


class AssistantNotConfiguredError(AssistantError):
    """Ассистент не сконфигурирован (нет LLM/настроек)."""
    status_code = 503

    def __init__(self) -> None:
        super().__init__("AI assistant is not configured")


class AssistantValidationError(AssistantError):
    """Некорректный запрос к ассистенту."""
    def __init__(self, message: str) -> None:
        super().__init__(message)


class AssistantLlmError(AssistantError):
    """Ошибка вызова LLM-провайдера."""
    status_code = 502

    def __init__(self, message: str = "AI provider request failed") -> None:
        super().__init__(message)


class AssistantThreadAccessDeniedError(AssistantError):
    """Нет доступа к треду ассистента."""
    status_code = 403

    def __init__(self, thread_id) -> None:
        super().__init__(f"Access denied to assistant thread {thread_id}")
        self.thread_id = thread_id
