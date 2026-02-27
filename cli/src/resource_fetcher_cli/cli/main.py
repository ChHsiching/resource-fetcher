"""Music Album Downloader - Professional CLI Tool."""

import argparse
import logging
import re
import sys
import time
from pathlib import Path
from typing import Any

import requests

from resource_fetcher_core.adapters.registry import get_adapter
from resource_fetcher_core.core.models import DownloadResult, DownloadStatus

# Import progress markers for GUI integration
try:
    from resource_fetcher_cli.cli.progress_markers import (
        album_complete,
        album_start,
        song_complete,
        song_start,
    )
    from resource_fetcher_cli.cli.progress_markers import (
        error as emit_error,
    )

    HAS_MARKERS = True
except ImportError:
    HAS_MARKERS = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("downloader.log", encoding="utf-8"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class DownloadProgress:
    """Track and display download progress."""

    def __init__(self, total: int):
        self.total = total
        self.success = 0
        self.failed = 0
        self.skipped = 0
        self.start_time = time.time()

    def update(self, result: DownloadResult) -> None:
        """Update progress with download result."""
        if result.status == DownloadStatus.SUCCESS:
            self.success += 1
        elif result.status == DownloadStatus.FAILED:
            self.failed += 1
        else:
            self.skipped += 1

    def summary(self) -> str:
        """Generate progress summary."""
        elapsed = time.time() - self.start_time
        speed = self.success / elapsed if elapsed > 0 else 0

        lines = [
            "\n" + "=" * 60,
            "下载完成! Download Summary",
            "=" * 60,
            f"  成功 (Success): {self.success}",
            f"  失败 (Failed): {self.failed}",
            f"  跳过 (Skipped): {self.skipped}",
            f"  总计 (Total): {self.total}",
            f"  耗时 (Time): {elapsed:.1f} 秒",
            f"  速度 (Speed): {speed:.2f} 首/秒" if speed > 0 else "  速度 (Speed): N/A",
            "=" * 60,
        ]
        return "\n".join(lines)


def _generate_backup_urls(primary_url: str, song_id: str) -> list[str]:
    """
    Generate backup URLs by replacing domain in primary URL.

    Args:
        primary_url: The primary URL that may fail
        song_id: Song ID for URL reconstruction

    Returns:
        List of backup URLs to try
    """
    from resource_fetcher_core.adapters.izanmei import IzanmeiAdapter

    audio_bases = IzanmeiAdapter.get_audio_bases()

    # Skip the first (primary) domain, return backups
    backup_urls = []
    for base in audio_bases[1:]:  # Skip primary
        backup_url = f"{base}/{song_id}.mp3"
        backup_urls.append(backup_url)

    return backup_urls


def download_song(
    url: str,
    output_dir: Path,
    song_id: str = "",
    song_title: str = "",
    timeout: int = 60,
    retries: int = 3,
    overwrite: bool = False,
    renumber: bool = False,
    total_songs: int = 1,
    progress_callback: Any | None = None,
    backup_urls: list[str] | None = None,
) -> DownloadResult:
    """
    Download a single song with retry logic and automatic domain failover.

    Args:
        url: Primary audio file URL
        output_dir: Output directory path
        song_id: Song ID for fallback
        song_title: Song title for filename
        timeout: Request timeout in seconds
        retries: Number of retry attempts per URL
        overwrite: Whether to overwrite existing files
        renumber: Whether to add leading zero prefix for sorting
        total_songs: Total number of songs (for padding calculation)
        progress_callback: Optional callback for progress updates
        backup_urls: Optional list of backup URLs (same file, different domains)

    Returns:
        DownloadResult with status and metadata
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # If backup URLs not provided but song_id is available, generate them
    if backup_urls is None and song_id:
        backup_urls = _generate_backup_urls(url, song_id)

    # Combine all URLs to try (primary first)
    all_urls = [url] + (backup_urls or [])

    # Try each URL with retries
    for url_idx, current_url in enumerate(all_urls):
        url_label = "primary" if url_idx == 0 else f"backup #{url_idx}"

        for attempt in range(retries):
            try:
                logger.debug(
                    f"Attempting download: {current_url} "
                    f"({url_label}, attempt {attempt + 1}/{retries})"
                )

                # 现有的下载逻辑从这里开始
                response = requests.get(current_url, stream=True, timeout=timeout)
                response.raise_for_status()

                # Get filename from headers or use title
                from resource_fetcher_core.utils.http import (
                    add_track_number_prefix,
                    extract_filename_from_headers,
                    sanitize_filename,
                )

                filename = extract_filename_from_headers(
                    dict(response.headers), song_id, song_title
                )
                filename = sanitize_filename(filename)

                # Apply renumbering if enabled
                if renumber:
                    filename = add_track_number_prefix(filename, total_songs=total_songs)

                output_path = output_dir / filename

                # Check if file exists
                if output_path.exists() and not overwrite:
                    logger.info(f"File exists, skipping: {filename}")
                    return DownloadResult(
                        status=DownloadStatus.SKIPPED,
                        path=output_path,
                        message="File already exists",
                    )

                # Download with progress tracking
                total_size = int(response.headers.get("content-length", 0))
                downloaded_size = 0
                last_progress = 0

                with open(output_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)

                            # Progress callback (every 10%)
                            if progress_callback and total_size > 0:
                                progress = int(downloaded_size / total_size * 100)
                                if progress - last_progress >= 10:
                                    progress_callback(progress)
                                    last_progress = progress

                # Verify file integrity
                if total_size > 0 and downloaded_size != total_size:
                    output_path.unlink()
                    raise ValueError(f"File incomplete: {downloaded_size}/{total_size} bytes")

                logger.info(
                    f"Downloaded successfully from {url_label}: {filename} "
                    f"({downloaded_size:,} bytes)"
                )
                return DownloadResult(
                    status=DownloadStatus.SUCCESS,
                    path=output_path,
                    size=downloaded_size,
                    message=f"Download successful from {url_label}",
                )

            except requests.exceptions.RequestException as e:
                is_last_attempt = attempt == retries - 1
                is_last_url = url_idx == len(all_urls) - 1

                logger.warning(f"Request failed ({url_label}, attempt {attempt + 1}): {e}")

                # Only retry if not the last attempt for this URL
                if not is_last_attempt:
                    # Exponential backoff
                    wait_time = 2**attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)

                # If this was the last attempt for this URL, move to next URL
                elif is_last_attempt and not is_last_url:
                    logger.info("Trying next backup URL...")
                    break  # Break inner retry loop, move to next URL

                # If this was the last attempt on last URL, give up
                elif is_last_attempt and is_last_url:
                    logger.error(
                        f"Failed to download from all {len(all_urls)} URLs "
                        f"after {retries} attempts each"
                    )
                    return DownloadResult(
                        status=DownloadStatus.FAILED,
                        path=None,
                        message=f"Download failed: {str(e)}",
                    )

            except Exception as e:
                # Non-request exceptions fail immediately
                logger.error(f"Unexpected error: {e}")
                return DownloadResult(
                    status=DownloadStatus.FAILED, path=None, message=f"Error: {str(e)}"
                )

    return DownloadResult(status=DownloadStatus.FAILED, message="Unknown error")


def renumber_directory(directory: Path, dry_run: bool = False) -> None:
    """
    Renumber all MP3 files in a directory with leading zero prefixes.

    Args:
        directory: Directory containing song files
        dry_run: If True, only show what would be renamed
    """
    directory = Path(directory)

    if not directory.exists():
        logger.error(f"Directory not found: {directory}")
        return

    from resource_fetcher_core.utils.http import add_track_number_prefix

    mp3_files = sorted(directory.glob("*.mp3"))
    total_files = len(mp3_files)

    if total_files == 0:
        logger.info(f"No MP3 files found in {directory}")
        return

    logger.info(f"Found {total_files} files in {directory}")
    print(f"\n找到 {total_files} 个文件 in {directory}\n")

    renamed_count = 0
    skipped_count = 0

    for mp3_file in mp3_files:
        # Extract track number from filename
        match = re.search(r"第(\d+)首", mp3_file.stem)

    mp3_files = sorted(directory.glob("*.mp3"))
    total_files = len(mp3_files)

    if total_files == 0:
        logger.info(f"No MP3 files found in {directory}")
        return

    logger.info(f"Found {total_files} files in {directory}")
    print(f"\n找到 {total_files} 个文件 in {directory}\n")

    renamed_count = 0
    skipped_count = 0

    for mp3_file in mp3_files:
        # Extract track number from filename
        match = re.search(r"第(\d+)首", mp3_file.stem)
        if not match:
            logger.info(f"Skip: {mp3_file.name} (no track number)")
            skipped_count += 1
            continue

        track_number = int(match.group(1))
        old_name = mp3_file.name
        new_name = add_track_number_prefix(old_name, track_number, total_files)

        if old_name == new_name:
            logger.info(f"Skip: {old_name} (already has prefix)")
            skipped_count += 1
            continue

        if dry_run:
            print(f"Would rename: {old_name} -> {new_name}")
        else:
            new_path = mp3_file.parent / new_name
            try:
                mp3_file.rename(new_path)
                print(f"Renamed: {old_name} -> {new_name}")
                renamed_count += 1
            except Exception as e:
                logger.error(f"Failed to rename {old_name}: {e}")
                print(f"Error: Failed to rename {old_name}: {e}")

    print("\n完成! Summary:")
    print(f"  重命名 (Renamed): {renamed_count}")
    print(f"  跳过 (Skipped): {skipped_count}")
    print(f"  总计 (Total): {total_files}")


def download_album(
    url: str,
    output_dir: Path,
    limit: int | None = None,
    overwrite: bool = False,
    timeout: int = 60,
    retries: int = 3,
    delay: float = 0.5,
    renumber: bool = False,
    backup_domains: list[str] | None = None,
) -> bool:
    """
    Download an entire album.

    Args:
        url: Album page URL
        output_dir: Output directory path
        limit: Optional limit on number of songs
        overwrite: Whether to overwrite existing files
        timeout: Request timeout in seconds
        retries: Number of retry attempts
        delay: Delay between downloads in seconds
        renumber: Whether to add leading zero prefix for sorting
        backup_domains: Optional list of additional backup domains

    Returns:
        True if all downloads succeeded, False otherwise
    """
    try:
        # Fetch album page
        logger.info(f"Fetching album page: {url}")
        response = requests.get(url, timeout=30)
        response.encoding = "utf-8"
        html = response.text

        # Get appropriate adapter
        adapter = get_adapter(url)
        if not adapter:
            logger.error(f"No adapter found for URL: {url}")
            return False

        # Extract album information
        logger.info("Parsing album information...")
        album = adapter.extract_album(html)

        # Display album info
        print("\n" + "=" * 60)
        print(f"专辑 (Album): {album.title}")
        print(f"来源 (Source): {album.source}")
        print(f"歌曲数 (Songs): {len(album.songs)}")
        print(f"输出目录 (Output): {output_dir}")
        print("=" * 60 + "\n")

        # Emit album start event for GUI
        if HAS_MARKERS:
            album_start(album.title, album.source, len(album.songs))

        # Apply limit
        songs = album.songs[:limit] if limit else album.songs
        if limit:
            print(f"限制下载 (Limit): {len(songs)} 首\n")

        # Initialize progress tracker
        progress = DownloadProgress(len(songs))

        # Download songs
        for idx, song in enumerate(songs, 1):
            # Safe print for Windows console
            try:
                print(f"[{idx}/{len(songs)}] {song.title}")
            except UnicodeEncodeError:
                print(f"[{idx}/{len(songs)}] Downloading song {idx}...")

            # Emit song start event for GUI
            if HAS_MARKERS:
                song_start(idx, len(songs), song.title)

            # Generate backup URLs for this song if backup domains provided
            song_backup_urls = None
            if backup_domains:
                song_backup_urls = [f"{domain}/song/p/{song.id}.mp3" for domain in backup_domains]

            # Download song with failover support
            result = download_song(
                url=song.url,
                output_dir=output_dir,
                song_id=song.id,
                song_title=song.title,
                timeout=timeout,
                retries=retries,
                overwrite=overwrite,
                renumber=renumber,
                total_songs=len(album.songs),
                backup_urls=song_backup_urls,
            )

            # Update progress
            progress.update(result)

            # Emit song complete event for GUI
            if HAS_MARKERS:
                song_complete(
                    idx,
                    song.title,
                    result.status.value,
                    result.size or 0,
                    result.message or "",
                )

            # Small delay between downloads to be polite to the server
            if idx < len(songs):
                time.sleep(delay)

        # Display summary
        print(progress.summary())

        # Emit album complete event for GUI
        if HAS_MARKERS:
            album_complete(progress.success, progress.failed, progress.skipped, len(songs))

        # Return success status
        return progress.failed == 0

    except Exception as e:
        logger.error(f"Album download failed: {e}")
        print(f"\n错误: {e}")
        if HAS_MARKERS:
            emit_error(str(e))
        return False


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="resource-fetcher",
        description="Resource Fetcher - Batch download resources from various websites",
        epilog="""
Examples:
  # Download entire album
  %(prog)s --url https://www.izanmei.cc/album/hymns-442-1.html

  # Download to custom directory
  %(prog)s --url https://www.izanmei.cc/album/hymns-442-1.html --output ./my_music

  # Download first 10 songs only
  %(prog)s --url https://www.izanmei.cc/album/hymns-442-1.html --limit 10

  # Overwrite existing files
  %(prog)s --url https://www.izanmei.cc/album/hymns-442-1.html --overwrite

  # Increase timeout and retries for slow connections
  %(prog)s --url https://www.izanmei.cc/album/hymns-442-1.html --timeout 120 --retries 5

For more information, visit: https://github.com/ChHsiching/resource-fetcher
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Create mutually exclusive group for URL and renumber-dir
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--url", help="Album page URL to download")
    mode_group.add_argument(
        "--renumber-dir",
        type=Path,
        metavar="DIRECTORY",
        help="Renumber existing MP3 files in DIRECTORY with leading zero prefixes",
    )

    parser.add_argument(
        "--output",
        "-o",
        default="./downloads",
        help="Output directory for downloaded songs (default: ./downloads)",
    )

    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        metavar="N",
        help="Limit number of songs to download (e.g., --limit 10 for first 10 songs)",
    )

    parser.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing files instead of skipping them"
    )

    parser.add_argument(
        "--renumber",
        action="store_true",
        help="Add leading zero prefixes for proper sorting (e.g., 001_, 010_, ...)",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        metavar="SECONDS",
        help="Request timeout in seconds (default: 60)",
    )

    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        metavar="N",
        help="Number of retry attempts per URL (default: 3)",
    )

    parser.add_argument(
        "--backup-domains",
        nargs="*",
        metavar="DOMAIN",
        help="Additional backup domains to try if primary fails (e.g., --backup-domains https://cdn.example.com)",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        metavar="SECONDS",
        help="Delay between downloads in seconds (default: 0.5)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output for debugging"
    )

    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    return parser


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")

    # Handle --renumber-dir mode
    if args.renumber_dir:
        renumber_directory(args.renumber_dir)
        sys.exit(0)

    # Validate URL for download mode
    if not args.url.startswith("http"):
        parser.error(f"Invalid URL: {args.url}")

    # Convert output to Path
    output_dir = Path(args.output)

    # Download album
    success = download_album(
        url=args.url,
        output_dir=output_dir,
        limit=args.limit,
        overwrite=args.overwrite,
        timeout=args.timeout,
        retries=args.retries,
        delay=args.delay,
        renumber=args.renumber,
        backup_domains=getattr(args, 'backup_domains', None),
    )

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
