from src.application.use_cases.designs import ListBoxDesignsUseCase
from src.domain.entities.box_designs import BoxDesign
from src.domain.values.box_design_name import BoxDesignName
from src.domain.values.sort_order import SortOrder
from src.domain.values.url import Url
from tests.application.fakes import InMemoryUnitOfWork


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

        assert [design.code for design in designs] == ["first", "second"]
