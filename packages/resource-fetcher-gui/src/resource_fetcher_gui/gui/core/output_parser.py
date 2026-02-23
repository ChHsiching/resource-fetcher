"""Parser for CLI output to extract progress information."""

import logging
import re
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SongProgress:
    """Progress information for a single song.

    Attributes:
        index: Current song index (1-based).
        total: Total number of songs.
        title: Song title.
        status: Download status (pending, downloading, success, failed, skipped).
    """

    index: int
    total: int
    title: str
    status: str = "downloading"  # pending, downloading, success, failed, skipped


@dataclass
class AlbumInfo:
    """Album information extracted from CLI output.

    Attributes:
        title: Album title.
        source: Source website.
        song_count: Number of songs in album.
    """

    title: str
    source: str
    song_count: int


@dataclass
class DownloadSummary:
    """Final download summary from CLI output.

    Attributes:
        success: Number of successful downloads.
        failed: Number of failed downloads.
        skipped: Number of skipped downloads.
        total: Total number of songs.
        elapsed_time: Time elapsed in seconds.
        speed: Download speed (songs per second).
    """

    success: int
    failed: int
    skipped: int
    total: int
    elapsed_time: float
    speed: float


class OutputParser:
    """Parser for CLI output.

    Extracts structured information from CLI stdout using regex patterns.
    Handles bilingual output (Chinese/English) from the CLI.
    """

    # Regex patterns for parsing CLI output
    PATTERNS = {
        "album_title": r"专辑\s*\(Album\):\s*(.+)",
        "album_source": r"来源\s*\(Source\):\s*(.+)",
        "album_songs": r"歌曲数\s*\(Songs\):\s*(\d+)",
        "song_progress": r"\[(\d+)/(\d+)\]\s+(.+)",  # [1/10] Song Title
        "summary_header": r"下载完成! Download Summary",
        "summary_success": r"\s+成功\s*\(Success\):\s*(\d+)",
        "summary_failed": r"\s+失败\s*\(Failed\):\s*(\d+)",
        "summary_skipped": r"\s+跳过\s*\(Skipped\):\s*(\d+)",
        "summary_total": r"\s+总计\s*\(Total\):\s*(\d+)",
        "summary_time": r"\s+耗时\s*\(Time\):\s+([\d.]+)\s+秒",
        "summary_speed": r"\s+速度\s*\(Speed\):\s+([\d.]+)\s+首/秒",
        "error": r"(错误|Error):\s*(.+)",
    }

    def __init__(self) -> None:
        """Initialize output parser."""
        self._current_album: AlbumInfo | None = None
        self._in_summary = False
        self._summary_data: dict[str, Any] = {}

        # Compile regex patterns for better performance
        self._compiled_patterns = {
            name: re.compile(pattern) for name, pattern in self.PATTERNS.items()
        }

        logger.debug("OutputParser initialized")

    def parse_line(
        self, line: str
    ) -> SongProgress | AlbumInfo | DownloadSummary | dict[str, Any] | None:
        """Parse a single line of CLI output.

        Attempts to match the line against known patterns and returns
        appropriate data object if match found.

        Args:
            line: A single line of CLI output.

        Returns:
            Parsed object (SongProgress, AlbumInfo, DownloadSummary, or dict)
            or None if line doesn't match any known pattern.
        """
        if not line or not line.strip():
            return None

        # Check for album title
        if match := self._compiled_patterns["album_title"].search(line):
            title = match.group(1).strip()
            logger.debug(f"Parsed album title: {title}")
            # Don't return yet, wait for complete album info

        # Check for album source
        elif match := self._compiled_patterns["album_source"].search(line):
            source = match.group(1).strip()
            if self._current_album is None:
                self._current_album = AlbumInfo(title="", source=source, song_count=0)
            else:
                self._current_album.source = source
            logger.debug(f"Parsed album source: {source}")

        # Check for song count
        elif match := self._compiled_patterns["album_songs"].search(line):
            count = int(match.group(1))
            if self._current_album is None:
                self._current_album = AlbumInfo(title="", source="", song_count=count)
            else:
                self._current_album.song_count = count
            logger.debug(f"Parsed song count: {count}")
            return self._current_album

        # Check for song progress
        elif match := self._compiled_patterns["song_progress"].search(line):
            index = int(match.group(1))
            total = int(match.group(2))
            title = match.group(3).strip()
            progress = SongProgress(index=index, total=total, title=title, status="downloading")
            logger.debug(f"Parsed song progress: [{index}/{total}] {title}")
            return progress

        # Check for summary header
        elif self._compiled_patterns["summary_header"].search(line):
            logger.debug("Summary section started")
            self._in_summary = True
            self._summary_data = {}

        # Check for summary lines
        elif self._in_summary:
            # Success count
            if match := self._compiled_patterns["summary_success"].search(line):
                self._summary_data["success"] = int(match.group(1))

            # Failed count
            elif match := self._compiled_patterns["summary_failed"].search(line):
                self._summary_data["failed"] = int(match.group(1))

            # Skipped count
            elif match := self._compiled_patterns["summary_skipped"].search(line):
                self._summary_data["skipped"] = int(match.group(1))

            # Total count
            elif match := self._compiled_patterns["summary_total"].search(line):
                self._summary_data["total"] = int(match.group(1))

            # Elapsed time
            elif match := self._compiled_patterns["summary_time"].search(line):
                self._summary_data["elapsed_time"] = float(match.group(1))

            # Speed
            elif match := self._compiled_patterns["summary_speed"].search(line):
                self._summary_data["speed"] = float(match.group(1))

                # Speed is usually the last line, create summary
                if "total" in self._summary_data:
                    summary = DownloadSummary(
                        success=self._summary_data.get("success", 0),
                        failed=self._summary_data.get("failed", 0),
                        skipped=self._summary_data.get("skipped", 0),
                        total=self._summary_data["total"],
                        elapsed_time=self._summary_data.get("elapsed_time", 0.0),
                        speed=self._summary_data.get("speed", 0.0),
                    )
                    logger.debug(f"Parsed download summary: {summary}")
                    self._in_summary = False
                    return summary

        # Check for error messages
        elif match := self._compiled_patterns["error"].search(line):
            error_msg = match.group(2).strip()
            logger.warning(f"Parsed error message: {error_msg}")
            return {"type": "error", "message": error_msg}

        return None

    def reset(self) -> None:
        """Reset parser state.

        Clears current album info and summary data.
        Call this before starting a new download.
        """
        self._current_album = None
        self._in_summary = False
        self._summary_data = {}
        logger.debug("Parser state reset")

    def parse_song_progress(self, line: str) -> SongProgress | None:
        """Parse song progress from line.

        Convenience method that only returns SongProgress objects.

        Args:
            line: A single line of CLI output.

        Returns:
            SongProgress object if line contains song progress, None otherwise.
        """
        result = self.parse_line(line)
        if isinstance(result, SongProgress):
            return result
        return None

    def parse_summary(self, lines: list[str]) -> DownloadSummary | None:
        """Parse summary from multiple lines.

        Convenience method for parsing complete summary from a list of lines.

        Args:
            lines: List of CLI output lines containing summary.

        Returns:
            DownloadSummary object if successfully parsed, None otherwise.
        """
        self.reset()

        for line in lines:
            result = self.parse_line(line)
            if isinstance(result, DownloadSummary):
                return result

        return None
