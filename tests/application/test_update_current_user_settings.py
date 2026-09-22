import uuid

import pytest

from app.application.dto.auth import UpdateCurrentUserSettingsCommand
from app.application.use_cases.auth import UpdateCurrentUserSettingsUseCase
from app.domain.entities.users import User
from app.domain.exceptions.auth import UserInactiveError
from app.domain.exceptions.users import UserNotFoundError
from app.domain.values.telegram_id import TelegramId
from tests.application.fakes import InMemoryUnitOfWork


@pytest.mark.asyncio
async def test_update_notifications_enabled() -> None:
    uow = InMemoryUnitOfWork()
    user = User(
        telegram_id=TelegramId("12345"),
        first_name="Анна",
        notifications_enabled=True,
    )
    await uow.users.add(user)

    result = await UpdateCurrentUserSettingsUseCase(uow).execute(
        UpdateCurrentUserSettingsCommand(
            user_id=user.id,
            notifications_enabled=False,
        )
    )

    assert result.notifications_enabled is False
    stored = await uow.users.get_by_id(user.id)
    assert stored is not None
    assert stored.notifications_enabled is False


@pytest.mark.asyncio
async def test_update_notifications_not_found() -> None:
    uow = InMemoryUnitOfWork()
    with pytest.raises(UserNotFoundError):
        await UpdateCurrentUserSettingsUseCase(uow).execute(
            UpdateCurrentUserSettingsCommand(
                user_id=uuid.uuid4(),
                notifications_enabled=True,
            )
        )


@pytest.mark.asyncio
async def test_update_notifications_inactive() -> None:
    uow = InMemoryUnitOfWork()
    user = User(
        telegram_id=TelegramId("99"),
        first_name="X",
        is_active=False,
    )
    await uow.users.add(user)

    with pytest.raises(UserInactiveError):
        await UpdateCurrentUserSettingsUseCase(uow).execute(
            UpdateCurrentUserSettingsCommand(
                user_id=user.id,
                notifications_enabled=False,
            )
        )
