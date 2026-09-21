from app.domain.entities.box_designs import BoxDesign
from app.domain.values.box_design_description import BoxDesignDescription
from app.domain.values.box_design_name import BoxDesignName
from app.domain.values.sort_order import SortOrder
from app.domain.values.url import Url


class TestBoxDesign:
    def test_create_minimal(self):
        design = BoxDesign(
            code="romantic_red",
            name=BoxDesignName("Romantic Red"),
            preview_image_url=Url("https://example.com/design.png"),
        )

        assert design.code == "romantic_red"
        assert design.name.value == "Romantic Red"
        assert design.description is None
        assert design.theme_config == {}
        assert design.is_active is True
        assert design.sort_order.value == 1

    def test_create_with_optional_fields(self):
        design = BoxDesign(
            code="minimal",
            name=BoxDesignName("Minimal"),
            preview_image_url=Url("https://example.com/m.png"),
            description=BoxDesignDescription("Clean look"),
            theme_config={"primary": "#ff0000"},
            is_active=False,
            sort_order=SortOrder(10),
        )

        assert design.description is not None
        assert design.description.value == "Clean look"
        assert design.theme_config["primary"] == "#ff0000"
        assert design.is_active is False
        assert design.sort_order.value == 10

    def test_base_entity_fields(self):
        design = BoxDesign(
            code="x",
            name=BoxDesignName("X"),
            preview_image_url=Url("https://example.com/x.png"),
        )

        assert design.id is not None
        assert design.created_at.tzinfo is not None
        assert design.updated_at.tzinfo is not None
