from datetime import datetime, timedelta, timezone

import pytest

from app.domain.entities.promo_codes import PromoCode
from app.domain.exceptions.commerce import (
    PromoCodeExhaustedError,
    PromoCodeExpiredError,
    PromoCodeInactiveError,
)


def _promo(**kwargs) -> PromoCode:
    defaults = {
        "code": "TEST1",
        "discount_percent": 10,
        "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
    }
    defaults.update(kwargs)
    return PromoCode(**defaults)


class TestPromoCodeStatus:
    def test_resolve_status_priority(self):
        now = datetime.now(timezone.utc)
        assert _promo().resolve_status(now=now) == "active"
        assert (
            _promo(is_active=False).resolve_status(now=now) == "inactive"
        )
        assert (
            _promo(
                expires_at=now - timedelta(minutes=1),
            ).resolve_status(now=now)
            == "expired"
        )
        assert (
            _promo(max_usages=1, usage_count=1).resolve_status(now=now)
            == "exhausted"
        )
        # Manual off wins over expired/exhausted.
        assert (
            _promo(
                is_active=False,
                max_usages=1,
                usage_count=1,
                expires_at=now - timedelta(days=1),
            ).resolve_status(now=now)
            == "inactive"
        )

    def test_assert_usable_guards(self):
        now = datetime.now(timezone.utc)
        with pytest.raises(PromoCodeInactiveError):
            _promo(is_active=False).assert_usable(now=now)
        with pytest.raises(PromoCodeExpiredError):
            _promo(expires_at=now - timedelta(seconds=1)).assert_usable(
                now=now
            )
        with pytest.raises(PromoCodeExhaustedError):
            _promo(max_usages=3, usage_count=3).assert_usable(now=now)
        _promo(max_usages=3, usage_count=2).assert_usable(now=now)
