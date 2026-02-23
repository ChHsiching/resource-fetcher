"""Test SiteAdapter interface contract."""

import pytest

from resource_fetcher_core.core.interfaces import SiteAdapter
from resource_fetcher_core.core.models import Album


class TestSiteAdapterInterface:
    """Test SiteAdapter interface contract."""

    def test_cannot_instantiate_abstract_adapter(self):
        """Test that SiteAdapter cannot be instantiated directly."""
        with pytest.raises(TypeError):
            SiteAdapter()

    def test_concrete_adapter_must_implement_can_handle(self):
        """Test that concrete adapters must implement can_handle method."""

        class ConcreteAdapter(SiteAdapter):
            """Incomplete adapter missing can_handle."""

            def extract_album(self, url: str) -> Album:
                return Album(
                    title="Test",
                    url=url,
                    songs=[],
                    source="test"
                )

        with pytest.raises(TypeError):
            ConcreteAdapter()

    def test_concrete_adapter_must_implement_extract_album(self):
        """Test that concrete adapters must implement extract_album method."""

        class ConcreteAdapter(SiteAdapter):
            """Incomplete adapter missing extract_album."""

            def can_handle(self, url: str) -> bool:
                return True

        with pytest.raises(TypeError):
            ConcreteAdapter()

    def test_valid_concrete_adapter(self):
        """Test that a valid concrete adapter can be instantiated."""

        class ConcreteAdapter(SiteAdapter):
            """Valid adapter implementation."""

            def can_handle(self, url: str) -> bool:
                return "example.com" in url

            def extract_album(self, url: str) -> Album:
                return Album(
                    title="Test Album",
                    url=url,
                    songs=[],
                    source="example.com"
                )

        adapter = ConcreteAdapter()
        assert adapter.can_handle("https://example.com/album") is True
        assert adapter.can_handle("https://other.com/album") is False

        album = adapter.extract_album("https://example.com/album")
        assert album.title == "Test Album"
        assert album.source == "example.com"
