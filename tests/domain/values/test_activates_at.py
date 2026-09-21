import pytest
from datetime import datetime, timedelta, timezone

from app.domain.exceptions.boxes import BoxActivatesAtNotInFutureError
from app.domain.values.activates_at import ActivatesAt


class TestActivatesAt:
    def test_valid_future(self):
        future = datetime.now(timezone.utc) + timedelta(days=1)
        assert ActivatesAt(future).value == future

    def test_naive_treated_as_utc(self):
        now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
        future = datetime(2026, 1, 1, 14, 0)
        vo = ActivatesAt(datetime(2027, 1, 1, tzinfo=timezone.utc))
        vo.validate(future, now=now)

    def test_equal_to_now_rejected(self):
        now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
        vo = ActivatesAt(datetime(2027, 1, 1, tzinfo=timezone.utc))
        with pytest.raises(BoxActivatesAtNotInFutureError):
            vo.validate(now, now=now)

    def test_past_rejected(self):
        with pytest.raises(BoxActivatesAtNotInFutureError):
            ActivatesAt(datetime(2020, 1, 1, tzinfo=timezone.utc))

    def test_validate_past_with_explicit_now(self):
        now = datetime(2026, 6, 1, tzinfo=timezone.utc)
        past = datetime(2026, 1, 1, tzinfo=timezone.utc)
        future = datetime(2027, 1, 1, tzinfo=timezone.utc)
        vo = ActivatesAt(future)
        with pytest.raises(BoxActivatesAtNotInFutureError):
            vo.validate(past, now=now)
