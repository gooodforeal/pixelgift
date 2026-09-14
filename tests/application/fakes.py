from datetime import datetime
from typing import Optional
import uuid

from src.application.uow.base import BaseUnitOfWork
from src.domain.aggregates.boxes import Box
from src.domain.entities.box_designs import BoxDesign
from src.domain.entities.design_assets import DesignAsset
from src.domain.entities.design_ratings import DesignRating
from src.domain.entities.media_files import MediaFile
from src.domain.entities.notification_jobs import (
    NotificationJob,
    NotificationJobStatus,
    NotificationTemplate,
)
from src.domain.entities.telegram_login_challenges import TelegramLoginChallenge
from src.domain.entities.user_sessions import UserSession
from src.domain.entities.users import User
from src.domain.repository.box_designs import BaseBoxDesignsRepository
from src.domain.repository.boxes import BaseBoxesRepository
from src.domain.repository.design_assets import BaseDesignAssetsRepository
from src.domain.repository.design_ratings import (
    BaseDesignRatingsRepository,
    DesignRatingAggregate,
)
from src.domain.repository.media_files import BaseMediaFilesRepository
from src.domain.repository.notification_jobs import BaseNotificationJobsRepository
from src.domain.repository.telegram_login_challenges import (
    BaseTelegramLoginChallengesRepository,
)
from src.domain.repository.user_sessions import BaseUserSessionsRepository
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

    async def list_active(self) -> list[BoxDesign]:
        designs = [design for design in self.items.values() if design.is_active]
        return sorted(designs, key=lambda design: (design.sort_order.value, design.name.value))

    async def list_all(self) -> list[BoxDesign]:
        return sorted(
            self.items.values(),
            key=lambda design: (design.sort_order.value, design.name.value),
        )


class InMemoryDesignAssetsRepository(BaseDesignAssetsRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, DesignAsset] = {}

    async def add(self, entity: DesignAsset) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[DesignAsset]:
        return self.items.get(id_)

    async def update(self, entity: DesignAsset) -> DesignAsset:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)


class InMemoryDesignRatingsRepository(BaseDesignRatingsRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, DesignRating] = {}

    async def add(self, entity: DesignRating) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[DesignRating]:
        return self.items.get(id_)

    async def update(self, entity: DesignRating) -> DesignRating:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)

    async def get_by_user_and_design(
        self,
        *,
        user_id: uuid.UUID,
        design_id: uuid.UUID,
    ) -> Optional[DesignRating]:
        for rating in self.items.values():
            if rating.user_id == user_id and rating.design_id == design_id:
                return rating
        return None

    async def list_aggregates_by_design_ids(
        self,
        design_ids: list[uuid.UUID],
    ) -> list[DesignRatingAggregate]:
        by_design: dict[uuid.UUID, list[int]] = {design_id: [] for design_id in design_ids}
        for rating in self.items.values():
            if rating.design_id in by_design:
                by_design[rating.design_id].append(rating.stars.value)

        aggregates: list[DesignRatingAggregate] = []
        for design_id, stars in by_design.items():
            if not stars:
                continue
            aggregates.append(
                DesignRatingAggregate(
                    design_id=design_id,
                    average=sum(stars) / len(stars),
                    count=len(stars),
                )
            )
        return aggregates

    async def list_user_ratings_for_designs(
        self,
        *,
        user_id: uuid.UUID,
        design_ids: list[uuid.UUID],
    ) -> list[DesignRating]:
        design_id_set = set(design_ids)
        return [
            rating
            for rating in self.items.values()
            if rating.user_id == user_id and rating.design_id in design_id_set
        ]


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

    async def get_by_code(
        self, code: str, *, for_update: bool = False
    ) -> Optional[TelegramLoginChallenge]:
        del for_update  # in-memory store has no row locks
        for challenge in self.items.values():
            if challenge.code == code:
                return challenge
        return None


class InMemoryUserSessionsRepository(BaseUserSessionsRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, UserSession] = {}

    async def add(self, entity: UserSession) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[UserSession]:
        return self.items.get(id_)

    async def update(self, entity: UserSession) -> UserSession:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)

    async def get_by_refresh_token_hash(
        self, refresh_token_hash: str
    ) -> UserSession | None:
        for session in self.items.values():
            if session.refresh_token_hash == refresh_token_hash:
                return session
        return None

    async def list_by_user_id(self, user_id: uuid.UUID) -> list[UserSession]:
        return [
            session for session in self.items.values() if session.user_id == user_id
        ]


class InMemoryNotificationJobsRepository(BaseNotificationJobsRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, NotificationJob] = {}

    async def add(self, entity: NotificationJob) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id_: uuid.UUID) -> Optional[NotificationJob]:
        return self.items.get(id_)

    async def update(self, entity: NotificationJob) -> NotificationJob:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id_: uuid.UUID) -> None:
        self.items.pop(id_, None)

    async def get_by_box_and_template(
        self,
        box_id: uuid.UUID,
        template: NotificationTemplate,
    ) -> NotificationJob | None:
        for job in self.items.values():
            if job.box_id == box_id and job.template == template:
                return job
        return None

    async def claim_due(
        self,
        now: datetime,
        *,
        limit: int = 20,
    ) -> list[NotificationJob]:
        due = [
            job
            for job in self.items.values()
            if job.status == NotificationJobStatus.SCHEDULED and job.run_at <= now
        ]
        due.sort(key=lambda job: job.run_at)
        claimed: list[NotificationJob] = []
        for job in due[:limit]:
            job.mark_processing()
            claimed.append(job)
        return claimed


class InMemoryUnitOfWork(BaseUnitOfWork):
    def __init__(self) -> None:
        self.boxes = InMemoryBoxesRepository()
        self.box_designs = InMemoryBoxDesignsRepository()
        self.design_assets = InMemoryDesignAssetsRepository()
        self.design_ratings = InMemoryDesignRatingsRepository()
        self.media_files = InMemoryMediaFilesRepository()
        self.notification_jobs = InMemoryNotificationJobsRepository()
        self.users = InMemoryUsersRepository()
        self.telegram_login_challenges = InMemoryTelegramLoginChallengesRepository()
        self.user_sessions = InMemoryUserSessionsRepository()
        self.committed = False
        self.rolled_back = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True
