"""Общие FastAPI-зависимости: настройки, инфраструктура, пагинация."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from functools import lru_cache

from fastapi import Depends, Query

from app.application.services.jwt import JwtService
from app.infrastructure.llm.openai_compatible import OpenAICompatibleLlmClient
from app.infrastructure.storage.s3_storage import S3ObjectStorage
from app.infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork
from app.infrastructure.worker.task_queue import TaskiqTaskQueue
from app.settings import Settings, settings


@lru_cache
def get_settings() -> Settings:
    """Возвращает синглтон настроек приложения."""
    return settings


def get_jwt_service(cfg: Settings = Depends(get_settings)) -> JwtService:
    """Сервис кодирования и проверки JWT access-токенов."""
    return JwtService(cfg)


def get_storage(cfg: Settings = Depends(get_settings)) -> S3ObjectStorage:
    """Клиент объектного хранилища MinIO/S3."""
    return S3ObjectStorage(
        endpoint_url=cfg.minio_endpoint,
        access_key=cfg.minio_access_key,
        secret_key=cfg.minio_secret_key,
        bucket=cfg.minio_bucket,
        region=cfg.minio_region,
    )


def get_llm_client(cfg: Settings = Depends(get_settings)) -> OpenAICompatibleLlmClient:
    """HTTP-клиент OpenAI-совместимого LLM API."""
    return OpenAICompatibleLlmClient(cfg)


def uow_factory() -> Callable[[], SqlAlchemyUnitOfWork]:
    """Фабрика unit of work для SQLAlchemy."""
    return SqlAlchemyUnitOfWork


def get_task_queue() -> TaskiqTaskQueue:
    """Очередь фоновых задач Taskiq."""
    return TaskiqTaskQueue()


@dataclass(frozen=True, slots=True)
class PaginationParams:
    """Параметры постраничной выборки."""

    page: int = 1
    page_size: int = 10

    @property
    def offset(self) -> int:
        """Смещение SQL для текущей страницы."""
        return (self.page - 1) * self.page_size


def pagination_dep(
    page: int = Query(1, ge=1, description="Номер страницы (с 1)"),
    page_size: int = Query(10, ge=1, le=50, description="Размер страницы"),
) -> PaginationParams:
    """Парсит query-параметры `page` и `page_size` в PaginationParams."""
    return PaginationParams(page=page, page_size=page_size)
