"""Adapter registry for managing website adapters."""


from resource_fetcher.adapters.izanmei import IzanmeiAdapter
from resource_fetcher.core.interfaces import SiteAdapter

# Registry of available adapters
ADAPTERS = [
    IzanmeiAdapter(),
]


def get_adapter(url: str) -> SiteAdapter | None:
    """
    Get appropriate adapter for a URL.

    Args:
        url: The URL to find an adapter for

    Returns:
        SiteAdapter instance if found, None otherwise
    """
    for adapter in ADAPTERS:
        if adapter.can_handle(url):
            return adapter
    return None


def register_adapter(adapter: SiteAdapter) -> None:
    """
    Register a new adapter.

    Args:
        adapter: SiteAdapter instance to register
    """
    ADAPTERS.append(adapter)  # type: ignore[arg-type]


def list_supported_sites() -> list[str]:
    """
    List all supported websites.

    Returns:
        List of supported website names
    """
    return [adapter.__class__.__name__.replace('Adapter', '') for adapter in ADAPTERS]
