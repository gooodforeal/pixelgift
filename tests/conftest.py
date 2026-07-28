import uuid
from datetime import datetime, timedelta, timezone

import pytest

from src.domain.values.activates_at import ActivatesAt


@pytest.fixture
def future_datetime() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=1)


@pytest.fixture
def activates_at(future_datetime: datetime) -> ActivatesAt:
    return ActivatesAt(future_datetime)


@pytest.fixture
def user_id() -> uuid.UUID:
    return uuid.uuid4()
