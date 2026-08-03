import uuid

import pytest

from src.application.use_cases.queries import GetCurrentUserUseCase
from src.domain.entities.users import User
from src.domain.exceptions.auth import UserInactiveError
from src.domain.exceptions.users import UserNotFoundError
from src.domain.values.telegram_id import TelegramId
from tests.application.fakes import InMemoryUnitOfWork


@pytest.mark.asyncio
async def test_get_current_user_returns_profile() -> None:
    uow = InMemoryUnitOfWork()
    user = User(
        telegram_id=TelegramId("12345"),
        first_name="Анна",
        last_name="Иванова",
        username="anya",
        language_code="ru",
    )
    await uow.users.add(user)

    result = await GetCurrentUserUseCase(uow).execute(user_id=user.id)

    assert result.id == user.id
    assert result.first_name == "Анна"
    assert result.username == "anya"


@pytest.mark.asyncio
async def test_get_current_user_not_found() -> None:
    uow = InMemoryUnitOfWork()
    with pytest.raises(UserNotFoundError):
        await GetCurrentUserUseCase(uow).execute(user_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_get_current_user_inactive() -> None:
    uow = InMemoryUnitOfWork()
    user = User(
        telegram_id=TelegramId("99"),
        first_name="X",
        is_active=False,
    )
    await uow.users.add(user)

    with pytest.raises(UserInactiveError):
        await GetCurrentUserUseCase(uow).execute(user_id=user.id)
