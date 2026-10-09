"""Клиент LLM через OpenAI-compatible Chat Completions API."""

from collections.abc import Sequence
from typing import Any

import httpx
from openai import APIStatusError, AsyncOpenAI

from app.application.ports.llm.base import BaseLlmClient, LlmMessage
from app.settings import Settings


class OpenAICompatibleLlmClient(BaseLlmClient):
    """AsyncOpenAI с опциональным proxy; fallback на reasoning/refusal при пустом content."""

    def __init__(self, settings: Settings) -> None:
        self._api_key = settings.llm_api_key.strip()
        self._model = settings.llm_model.strip()

        client_kwargs: dict[str, Any] = {
            "api_key": self._api_key or "missing",
            "base_url": settings.llm_base_url.strip(),
            "timeout": settings.llm_timeout_seconds,
        }
        proxy = settings.llm_proxy_url.strip()
        if proxy:
            client_kwargs["http_client"] = httpx.AsyncClient(
                proxy=proxy,
                timeout=settings.llm_timeout_seconds,
            )

        self._client = AsyncOpenAI(**client_kwargs)

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key)

    async def complete(
        self,
        *,
        messages: Sequence[LlmMessage],
        system: str,
    ) -> str:
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system},
                    *[
                        {"role": message.role, "content": message.content}
                        for message in messages
                    ],
                ],
            )
        except APIStatusError as exc:
            raise RuntimeError(self._friendly_status_error(exc)) from exc

        choice = response.choices[0].message
        content = choice.content
        if isinstance(content, str) and content.strip():
            return content.strip()

        # Reasoning models (e.g. openai/gpt-oss-*) may leave content empty.
        reasoning = getattr(choice, "reasoning", None)
        if isinstance(reasoning, str) and reasoning.strip():
            return reasoning.strip()

        refusal = getattr(choice, "refusal", None)
        if isinstance(refusal, str) and refusal.strip():
            return refusal.strip()

        return "Не удалось сформировать ответ. Попробуйте ещё раз."

    @staticmethod
    def _friendly_status_error(exc: APIStatusError) -> str:
        status = exc.status_code
        body = ""
        try:
            if exc.response is not None:
                payload = exc.response.json()
                err = payload.get("error") if isinstance(payload, dict) else None
                if isinstance(err, dict):
                    body = str(err.get("message") or err.get("code") or "")
                elif isinstance(err, str):
                    body = err
        except Exception:
            body = (exc.message or "").strip()

        body = body.strip() or (exc.message or "").strip() or exc.__class__.__name__

        if status == 403:
            return (
                "AI provider forbidden (403): модель недоступна для этого ключа "
                "или заблокирована в Groq Console → Settings → Limits. "
                f"Детали: {body}"
            )
        if status == 401:
            return f"AI provider unauthorized (401): проверьте LLM_API_KEY. Детали: {body}"
        if status == 429:
            return f"AI provider rate limit (429): подождите и повторите. Детали: {body}"
        return f"AI provider request failed ({status}): {body}"
