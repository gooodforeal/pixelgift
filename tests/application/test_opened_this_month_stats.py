from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.application.use_cases.queries import GetOpenedThisMonthStatsUseCase
from app.domain.aggregates.boxes import Box, BoxStatus
from app.domain.values.activates_at import ActivatesAt
from app.domain.values.box_recipient_name import BoxRecipientName
from app.domain.values.box_title import BoxTitle
from app.domain.values.public_slug import PublicSlug
from tests.application.fakes import InMemoryUnitOfWork
import uuid


def _opened_box(*, opened_at: datetime) -> Box:
    box = Box(
        owner_id=uuid.uuid4(),
        design_id=uuid.uuid4(),
        public_slug=PublicSlug(f"slug-{uuid.uuid4().hex[:8]}"),
        title=BoxTitle("Test"),
        recipient_name=BoxRecipientName("Alice"),
        activates_at=ActivatesAt.reconstitute(opened_at),
        status=BoxStatus.OPENED,
        timezone="Europe/Moscow",
    )
    box.first_opened_at = opened_at
    return box


@pytest.mark.asyncio
async def test_opened_this_month_counts_moscow_month() -> None:
    uow = InMemoryUnitOfWork()
    tz = ZoneInfo("Europe/Moscow")
    now = datetime(2026, 9, 22, 15, 0, tzinfo=tz)

    await uow.boxes.add(_opened_box(opened_at=datetime(2026, 9, 1, 0, 0, tzinfo=tz)))
    await uow.boxes.add(_opened_box(opened_at=datetime(2026, 9, 15, 12, 0, tzinfo=tz)))
    await uow.boxes.add(_opened_box(opened_at=datetime(2026, 8, 31, 23, 59, tzinfo=tz)))
    await uow.boxes.add(_opened_box(opened_at=datetime(2026, 10, 1, 0, 0, tzinfo=tz)))

    result = await GetOpenedThisMonthStatsUseCase(uow).execute(now=now)

    assert result.count == 2
    assert result.timezone == "Europe/Moscow"
    assert result.period_start == datetime(2026, 9, 1, tzinfo=tz)
    assert result.period_end == datetime(2026, 10, 1, tzinfo=tz)
