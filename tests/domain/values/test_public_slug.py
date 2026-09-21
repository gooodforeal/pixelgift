import pytest

from app.domain.exceptions.boxes import (
    PublicSlugFormatError,
    PublicSlugSurroundingWhitespaceError,
)
from app.domain.values.public_slug import PublicSlug


class TestPublicSlug:
    def test_valid_slug(self):
        slug = PublicSlug("gift-box-42")
        assert slug.value == "gift-box-42"

    def test_single_character(self):
        assert PublicSlug("a").value == "a"

    def test_max_length(self):
        value = "a" + "b" * 30 + "c"
        assert len(value) == 32
        assert PublicSlug(value).value == value

    def test_empty(self):
        with pytest.raises(PublicSlugFormatError):
            PublicSlug("")

    def test_uppercase(self):
        with pytest.raises(PublicSlugFormatError):
            PublicSlug("Gift")

    def test_leading_hyphen(self):
        with pytest.raises(PublicSlugFormatError):
            PublicSlug("-gift")

    def test_trailing_underscore(self):
        with pytest.raises(PublicSlugFormatError):
            PublicSlug("gift_")

    def test_too_long(self):
        with pytest.raises(PublicSlugFormatError):
            PublicSlug("a" * 33)

    def test_whitespace_padding(self):
        with pytest.raises(PublicSlugSurroundingWhitespaceError):
            PublicSlug(" gift ")
