"""Progress markers for real-time GUI updates."""

import json
import sys
from typing import Any


def emit_progress(event_type: str, data: dict[str, Any]) -> None:
    """
    Emit a progress marker to stdout for GUI parsing.

    Markers use special format >>>PROGRESS:JSON that can be easily
    parsed by Rust/React frontend while keeping human-readable output.

    Args:
        event_type: Type of progress event (album_start, song_start, etc.)
        data: Event data as dictionary
    """
    marker = json.dumps({"type": event_type, **data})
    # Use special marker that GUI can parse
    print(f">>>PROGRESS:{marker}", file=sys.stderr, flush=True)


def album_start(title: str, source: str, total: int) -> None:
    """Emit album start event."""
    emit_progress("album_start", {"title": title, "source": source, "total": total})


def song_start(index: int, total: int, title: str) -> None:
    """Emit song download start event."""
    emit_progress("song_start", {"index": index, "total": total, "title": title})


def song_progress(index: int, percent: int) -> None:
    """Emit song download progress event."""
    emit_progress("song_progress", {"index": index, "percent": percent})


def song_complete(index: int, title: str, status: str, size: int, message: str) -> None:
    """Emit song download complete event."""
    emit_progress(
        "song_complete",
        {"index": index, "title": title, "status": status, "size": size, "message": message},
    )


def album_complete(success: int, failed: int, skipped: int, total: int) -> None:
    """Emit album complete event."""
    emit_progress(
        "album_complete",
        {"success": success, "failed": failed, "skipped": skipped, "total": total},
    )


def error(message: str) -> None:
    """Emit error event."""
    emit_progress("error", {"message": message})
