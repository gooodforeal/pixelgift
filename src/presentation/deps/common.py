from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from functools import lru_cache

from fastapi import Depends, Query

from src.application.services.jwt import JwtService
from src.infrastructure.storage.s3_storage import S3ObjectStorage
from src.infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork
from src.infrastructure.worker.task_queue import TaskiqTaskQueue
from src.settings import Settings, settings


@lru_cache
def get_settings() -> Settings:
    return settings


def get_jwt_service(cfg: Settings = Depends(get_settings)) -> JwtService:
    return JwtService(cfg)


def get_storage(cfg: Settings = Depends(get_settings)) -> S3ObjectStorage:
    return S3ObjectStorage(
        endpoint_url=cfg.minio_endpoint,
        access_key=cfg.minio_access_key,
        secret_key=cfg.minio_secret_key,
        bucket=cfg.minio_bucket,
        region=cfg.minio_region,
    )


def uow_factory() -> Callable[[], SqlAlchemyUnitOfWork]:
    return SqlAlchemyUnitOfWork


def get_task_queue() -> TaskiqTaskQueue:
    return TaskiqTaskQueue()


@dataclass(frozen=True, slots=True)
class PaginationParams:
    page: int = 1
    page_size: int = 10

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def pagination_dep(
    page: int = Query(1, ge=1, description="Номер страницы (с 1)"),
    page_size: int = Query(10, ge=1, le=50, description="Размер страницы"),
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)
