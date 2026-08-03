from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.uow.base import BaseUnitOfWork
from src.domain.repository.boxes import BaseBoxesRepository
from src.domain.repository.box_designs import BaseBoxDesignsRepository
from src.domain.repository.design_assets import BaseDesignAssetsRepository
from src.domain.repository.media_files import BaseMediaFilesRepository
from src.domain.repository.telegram_login_challenges import (
    BaseTelegramLoginChallengesRepository,
)
from src.domain.repository.user_sessions import BaseUserSessionsRepository
from src.domain.repository.users import BaseUsersRepository
from src.infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork


class _FakeUnitOfWork(BaseUnitOfWork):
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


class TestBaseUnitOfWork:
    @pytest.mark.asyncio
    async def test_rollback_on_exception(self):
        uow = _FakeUnitOfWork()

        with pytest.raises(RuntimeError, match="boom"):
            async with uow:
                raise RuntimeError("boom")

        assert uow.rolled_back is True
        assert uow.committed is False

    @pytest.mark.asyncio
    async def test_no_rollback_without_exception(self):
        uow = _FakeUnitOfWork()

        async with uow:
            await uow.commit()

        assert uow.committed is True
        assert uow.rolled_back is False


class TestSqlAlchemyUnitOfWorkWiring:
    @pytest.mark.asyncio
    async def test_repositories_are_wired(self):
        session = AsyncMock(spec=AsyncSession)
        uow = SqlAlchemyUnitOfWork(session_factory=lambda: session)
        async with uow:
            assert isinstance(uow.users, BaseUsersRepository)
            assert isinstance(uow.boxes, BaseBoxesRepository)
            assert isinstance(uow.box_designs, BaseBoxDesignsRepository)
            assert isinstance(uow.design_assets, BaseDesignAssetsRepository)
            assert isinstance(uow.media_files, BaseMediaFilesRepository)
            assert isinstance(
                uow.telegram_login_challenges, BaseTelegramLoginChallengesRepository
            )
            assert isinstance(uow.user_sessions, BaseUserSessionsRepository)
            assert not hasattr(uow, "box_items")

        session.close.assert_awaited_once()
