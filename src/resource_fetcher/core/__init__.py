"""Core models and interfaces for music downloader."""

from resource_fetcher.core.models import (
    Song,
    Album,
    DownloadResult,
    DownloadStatus,
)

__all__ = ["Song", "Album", "DownloadResult", "DownloadStatus"]
