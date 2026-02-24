"""
Resource Fetcher GUI - Graphical interface for batch downloads.

This package provides the modern GUI for the Resource Fetcher framework,
built with ttkbootstrap.
"""

__version__ = "0.2.0"

from resource_fetcher_core.core.models import Album, Song

__all__ = ["Song", "Album", "__version__"]
