from __future__ import annotations

import uuid
from typing import Optional

from src.application.uow.base import BaseUnitOfWork
from src.domain.aggregates.boxes import Box
from src.domain.entities.box_designs import BoxDesign
from src.domain.entities.media_files import MediaFile
from src.domain.entities.telegram_login_challenges import TelegramLoginChallenge
from src.domain.entities.users import User
from src.domain.repository.box_designs import BaseBoxDesignsRepository
from src.domain.repository.boxes import BaseBoxesRepository
from src.domain.repository.media_files import BaseMediaFilesRepository
from src.domain.repository.telegram_login_challenges import (
    BaseTelegramLoginChallengesRepository,
)
from src.domain.repository.users import BaseUsersRepository
from src.domain.values.public_slug import PublicSlug


class InMemoryBoxesRepository(BaseBoxesRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, Box] = {}

    async def add(self, entity: Box) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[Box]:
        return self.items.get(id_)

    async def update(self, entity: Box) -> Box:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)

    async def get_by_public_slug(self, public_slug: PublicSlug) -> Box | None:
        for box in self.items.values():
            if box.public_slug == public_slug:
                return box
        return None

    async def list_by_owner_id(self, owner_id: uuid.UUID) -> list[Box]:
        return [box for box in self.items.values() if box.owner_id == owner_id]


class InMemoryBoxDesignsRepository(BaseBoxDesignsRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, BoxDesign] = {}

    async def add(self, entity: BoxDesign) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[BoxDesign]:
        return self.items.get(id_)

    async def update(self, entity: BoxDesign) -> BoxDesign:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)

    async def get_by_code(self, code: str) -> Optional[BoxDesign]:
        for design in self.items.values():
            if design.code == code:
                return design
        return None


class InMemoryMediaFilesRepository(BaseMediaFilesRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, MediaFile] = {}

    async def add(self, entity: MediaFile) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[MediaFile]:
        return self.items.get(id_)

    async def update(self, entity: MediaFile) -> MediaFile:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)

    async def list_by_owner_id(self, owner_id: uuid.UUID) -> list[MediaFile]:
        return [
            media for media in self.items.values() if media.owner_id == owner_id
        ]


class InMemoryUsersRepository(BaseUsersRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, User] = {}

    async def add(self, entity: User) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[User]:
        return self.items.get(id_)

    async def update(self, entity: User) -> User:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        for user in self.items.values():
            if int(user.telegram_id.value) == telegram_id:
                return user
        return None


class InMemoryTelegramLoginChallengesRepository(
    BaseTelegramLoginChallengesRepository
):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, TelegramLoginChallenge] = {}

    async def add(self, entity: TelegramLoginChallenge) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[TelegramLoginChallenge]:
        return self.items.get(id_)

    async def update(self, entity: TelegramLoginChallenge) -> TelegramLoginChallenge:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)

    async def get_by_code(self, code: str) -> Optional[TelegramLoginChallenge]:
        for challenge in self.items.values():
            if challenge.code == code:
                return challenge
        return None


class _UnsupportedRepository:
    async def add(self, entity) -> None:
        raise NotImplementedError

    async def get_by_id(self, id_: uuid.UUID):
        raise NotImplementedError

    async def update(self, entity):
        raise NotImplementedError

    async def delete(self, id_: uuid.UUID) -> None:
        raise NotImplementedError


class InMemoryUnitOfWork(BaseUnitOfWork):
    def __init__(self) -> None:
        self.boxes = InMemoryBoxesRepository()
        self.box_designs = InMemoryBoxDesignsRepository()
        self.media_files = InMemoryMediaFilesRepository()
        self.users = InMemoryUsersRepository()
        self.telegram_login_challenges = InMemoryTelegramLoginChallengesRepository()
        self.user_sessions = _UnsupportedRepository()  # type: ignore[assignment]
        self.committed = False
        self.rolled_back = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True
