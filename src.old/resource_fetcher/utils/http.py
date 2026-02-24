"""HTTP utility functions."""

import re
from urllib.parse import unquote


def fix_mojibake(filename: str) -> str:
    """
    Fix mojibake (UTF-8 bytes interpreted as latin-1/Windows-1252).

    When a server sends UTF-8 encoded text but declares it as latin-1/Windows-1252,
    the bytes get misinterpreted. This function reverses that by encoding back to
    latin-1 (getting the original bytes) and then decoding as UTF-8.

    Example:
        Input:  "å£åä¸.mp3" (mojibake for "圣哉三一歌.mp3")
        Output: "圣哉三一歌.mp3"

    Args:
        filename: The possibly corrupted filename

    Returns:
        Fixed filename if mojibake detected, otherwise original filename
    """
    try:
        # Try to fix: encode as latin-1 to get original bytes, then decode as UTF-8
        return filename.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        # Not mojibake, return as-is
        return filename


def extract_filename_from_headers(headers: dict, song_id: str = "", song_title: str = "") -> str:
    """
    Extract filename from HTTP response headers.

    Handles Content-Disposition header with mojibake correction:
    Content-Disposition: attachment; filename="圣哉三一歌.mp3"

    Priority:
    1. song_title (provided, includes track number)
    2. HTTP header filename
    3. song_id fallback

    Args:
        headers: HTTP response headers dictionary
        song_id: Optional song ID for fallback
        song_title: Optional song title for fallback (preferred if provided)

    Returns:
        Extracted filename or fallback name
    """
    # Priority 1: Use provided song_title (which includes track number)
    if song_title:
        safe_title = sanitize_filename(song_title)
        return f"{safe_title}.mp3"

    # Priority 2: Try to extract from HTTP headers
    content_disp = headers.get("Content-Disposition", "")
    match = re.search(r'filename="([^"]+)"', content_disp)
    if not match:
        # Try RFC 5987 format
        match = re.search(r"filename\*=UTF-8''([^;]+)", content_disp, re.IGNORECASE)

    if match:
        filename = match.group(1)
        # URL decode if needed
        if "%" in filename:
            filename = unquote(filename)
        # Fix mojibake if present (UTF-8 bytes interpreted as latin-1)
        filename = fix_mojibake(filename)
        return filename

    # Priority 3: Fallback to song ID
    return f"{song_id}.mp3" if song_id else "unknown.mp3"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to be safe for file system.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for Windows/Linux file systems
    """
    # Windows illegal characters: \ / : * ? " < > |
    illegal_chars = r'[\\/:*?"<>|]'
    clean_name = re.sub(illegal_chars, "_", filename)
    return clean_name.strip()
