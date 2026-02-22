"""Abstract interface for site adapters."""

from abc import ABC, abstractmethod
from resource_fetcher.core.models import Album


class SiteAdapter(ABC):
    """
    Abstract base class for site-specific adapters.

    Each adapter is responsible for:
    1. Identifying if a URL belongs to its supported site
    2. Extracting album information from the URL
    3. Constructing audio download URLs
    """

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """
        Check if this adapter can handle the given URL.

        Args:
            url: The URL to check

        Returns:
            True if this adapter supports the URL, False otherwise
        """
        pass

    @abstractmethod
    def extract_album(self, url: str) -> Album:
        """
        Extract album information from the given URL.

        Args:
            url: The album page URL

        Returns:
            Album object containing song information

        Raises:
            ValueError: If the URL cannot be processed or no songs found
            requests.RequestException: If network request fails
        """
        pass
