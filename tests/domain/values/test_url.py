import pytest

from app.domain.exceptions.url import (
    UrlEmptyError,
    UrlMissingHostError,
    UrlSurroundingWhitespaceError,
    UrlUnsupportedSchemeError,
)
from app.domain.values.url import Url


class TestUrl:
    def test_valid_https(self):
        url = Url("https://example.com/path?q=1")
        assert url.value == "https://example.com/path?q=1"

    def test_valid_http(self):
        assert Url("http://localhost:8080/img.png").value == "http://localhost:8080/img.png"

    def test_empty(self):
        with pytest.raises(UrlEmptyError):
            Url("")

    def test_whitespace_padded(self):
        with pytest.raises(UrlSurroundingWhitespaceError):
            Url(" https://example.com ")

    def test_no_scheme(self):
        with pytest.raises(UrlUnsupportedSchemeError):
            Url("example.com/image.png")

    def test_invalid_scheme(self):
        with pytest.raises(UrlUnsupportedSchemeError):
            Url("ftp://example.com/file")

    def test_no_netloc(self):
        with pytest.raises(UrlMissingHostError):
            Url("https://")
