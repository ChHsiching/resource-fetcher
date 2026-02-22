"""Core data models for music downloader."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class DownloadStatus(Enum):
    """Download status enumeration."""

    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    PENDING = "pending"


@dataclass(frozen=True)
class Song:
    """
    Represents a single song.

    Attributes:
        id: Unique identifier for the song
        title: Song title
        url: Download URL for the audio file
        metadata: Additional metadata about the song
    """

    id: str
    title: str
    url: str
    metadata: dict = field(default_factory=dict)

    def __eq__(self, other: object) -> bool:
        """Compare songs by ID."""
        if not isinstance(other, Song):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash song by ID."""
        return hash(self.id)


@dataclass
class Album:
    """
    Represents a music album.

    Attributes:
        title: Album title
        url: Album page URL
        songs: List of songs in the album
        source: Source website identifier
    """

    title: str
    url: str
    songs: list[Song]
    source: str

    def __len__(self) -> int:
        """Return the number of songs in the album."""
        return len(self.songs)


@dataclass
class DownloadResult:
    """
    Result of a download operation.

    Attributes:
        status: Download status
        path: Path to the downloaded file (if successful)
        size: Size of the downloaded file in bytes
        message: Result message
    """

    status: DownloadStatus
    path: Optional[Path] = None
    size: int = 0
    message: str = ""

    def is_success(self) -> bool:
        """Check if download was successful."""
        return self.status == DownloadStatus.SUCCESS

    def is_failed(self) -> bool:
        """Check if download failed."""
        return self.status == DownloadStatus.FAILED
