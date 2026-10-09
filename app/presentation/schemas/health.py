"""Схемы health-check."""

from pydantic import BaseModel

from app.presentation.schemas.base import BaseResponseSchema


class HealthSchema(BaseModel):
    """Статус работоспособности сервиса."""

    status: str


class HealthResponse(BaseResponseSchema[HealthSchema]):
    """Ответ GET /health."""

    pass
