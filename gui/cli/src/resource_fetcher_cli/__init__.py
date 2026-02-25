"""
Resource Fetcher CLI - Command-line interface for batch downloads.

This package provides the command-line tool for the Resource Fetcher framework.
"""

__version__ = "0.2.0"

from resource_fetcher_core.core.models import Album, Song

__all__ = ["Song", "Album", "__version__"]
