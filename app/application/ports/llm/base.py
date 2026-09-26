from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, kw_only=True, slots=True)
class LlmMessage:
    role: Literal["user", "assistant"]
    content: str


class BaseLlmClient(ABC):
    @abstractmethod
    async def complete(
        self,
        *,
        messages: Sequence[LlmMessage],
        system: str,
    ) -> str: ...
