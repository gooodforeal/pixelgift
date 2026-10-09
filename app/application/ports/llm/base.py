"""Порт клиента большой языковой модели для ассистента редактора."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, kw_only=True, slots=True)
class LlmMessage:
    """Одно сообщение диалога для провайдера LLM."""

    role: Literal["user", "assistant"]
    content: str


class BaseLlmClient(ABC):
    """Контракт адаптера LLM: завершение диалога с системным промптом.

    Реализация обращается к внешнему API (OpenAI-совместимому и т.п.).
    """

    @abstractmethod
    async def complete(
        self,
        *,
        messages: Sequence[LlmMessage],
        system: str,
    ) -> str:
        """Генерирует ответ ассистента по истории и системной инструкции.

        Args:
            messages: Пользовательские и ассистентские реплики (без system).
            system: Системный промпт с контекстом редактора и правилами продукта.

        Returns:
            Текст ответа модели.
        """
