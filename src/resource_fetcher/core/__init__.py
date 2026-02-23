"""Core models and interfaces for music downloader."""

from resource_fetcher.core.models import (
    Album,
    DownloadResult,
    DownloadStatus,
    Song,
)

__all__ = ["Song", "Album", "DownloadResult", "DownloadStatus"]
