"""
Resource Fetcher - Universal resource fetching framework.

This package provides an extensible architecture for batch downloading resources
from various websites.
"""

__version__ = "0.1.0"

from resource_fetcher.core.models import Song, Album

__all__ = ["Song", "Album", "__version__"]
