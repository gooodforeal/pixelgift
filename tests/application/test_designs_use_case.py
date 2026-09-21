import pytest

from app.application.use_cases.designs import ListBoxDesignsUseCase, RateDesignUseCase
from app.domain.entities.box_designs import BoxDesign
from app.domain.exceptions.boxes import BoxDesignNotAvailableError
from app.domain.exceptions.design_ratings import (
    DesignAlreadyRatedError,
    DesignRatingStarsOutOfRangeError,
)
from app.domain.values.box_design_name import BoxDesignName
from app.domain.values.sort_order import SortOrder
from app.domain.values.url import Url
from tests.application.fakes import InMemoryUnitOfWork
import uuid


def _design(*, code: str, sort_order: int, is_active: bool = True) -> BoxDesign:
    return BoxDesign(
        code=code,
        name=BoxDesignName(code.title()),
        preview_image_url=Url(f"https://example.com/{code}.png"),
        sort_order=SortOrder(sort_order),
        is_active=is_active,
    )


class TestListBoxDesignsUseCase:
    async def test_returns_only_active_designs_in_sort_order(self):
        uow = InMemoryUnitOfWork()
        await uow.box_designs.add(_design(code="second", sort_order=2))
        await uow.box_designs.add(_design(code="first", sort_order=1))
        await uow.box_designs.add(
            _design(code="hidden", sort_order=3, is_active=False)
        )

        designs = await ListBoxDesignsUseCase(uow).execute()

        assert [item.design.code for item in designs] == ["first", "second"]
        assert all(item.rating_count == 0 for item in designs)
        assert all(item.my_rating is None for item in designs)


class TestRateDesignUseCase:
    async def test_rates_design_once(self):
        uow = InMemoryUnitOfWork()
        design = _design(code="romantic", sort_order=1)
        await uow.box_designs.add(design)
        user_id = uuid.uuid4()

        result = await RateDesignUseCase(uow).execute(
            user_id=user_id,
            design_id=design.id,
            stars=5,
        )

        assert result.stars == 5
        assert result.rating_avg == 5.0
        assert result.rating_count == 1
        assert uow.committed is True

        listed = await ListBoxDesignsUseCase(uow).execute(user_id=user_id)
        assert listed[0].my_rating == 5
        assert listed[0].rating_avg == 5.0
        assert listed[0].rating_count == 1

    async def test_rejects_second_rating_from_same_user(self):
        uow = InMemoryUnitOfWork()
        design = _design(code="romantic", sort_order=1)
        await uow.box_designs.add(design)
        user_id = uuid.uuid4()
        uc = RateDesignUseCase(uow)

        await uc.execute(user_id=user_id, design_id=design.id, stars=4)

        with pytest.raises(DesignAlreadyRatedError):
            await uc.execute(user_id=user_id, design_id=design.id, stars=5)

    async def test_rejects_inactive_design(self):
        uow = InMemoryUnitOfWork()
        design = _design(code="hidden", sort_order=1, is_active=False)
        await uow.box_designs.add(design)

        with pytest.raises(BoxDesignNotAvailableError):
            await RateDesignUseCase(uow).execute(
                user_id=uuid.uuid4(),
                design_id=design.id,
                stars=3,
            )

    async def test_rejects_stars_out_of_range(self):
        uow = InMemoryUnitOfWork()
        design = _design(code="romantic", sort_order=1)
        await uow.box_designs.add(design)

        with pytest.raises(DesignRatingStarsOutOfRangeError):
            await RateDesignUseCase(uow).execute(
                user_id=uuid.uuid4(),
                design_id=design.id,
                stars=6,
            )
