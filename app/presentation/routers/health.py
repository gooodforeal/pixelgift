"""Эндпоинт проверки доступности API."""

from fastapi import APIRouter

from app.presentation.schemas.health import HealthResponse, HealthSchema

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """GET /health — возвращает статус ok."""
    return HealthResponse(message="Success", result=HealthSchema(status="ok"))
