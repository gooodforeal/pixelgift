"""Публичный экспорт LLM-клиента инфраструктуры."""

from app.infrastructure.llm.openai_compatible import OpenAICompatibleLlmClient

__all__ = ["OpenAICompatibleLlmClient"]
