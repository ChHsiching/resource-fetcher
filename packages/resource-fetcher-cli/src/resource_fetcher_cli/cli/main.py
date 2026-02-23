"""Music Album Downloader - Professional CLI Tool."""

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Any

import requests

from resource_fetcher_core.adapters.registry import get_adapter
from resource_fetcher_core.core.models import DownloadResult, DownloadStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('downloader.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
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
            "=" * 60
        ]
        return "\n".join(lines)


def download_song(
    url: str,
    output_dir: Path,
    song_id: str = "",
    song_title: str = "",
    timeout: int = 60,
    retries: int = 3,
    overwrite: bool = False,
    progress_callback: Any | None = None,
) -> DownloadResult:
    """
    Download a single song with retry logic.

    Args:
        url: Audio file URL
        output_dir: Output directory path
        song_id: Song ID for fallback
        song_title: Song title for filename
        timeout: Request timeout in seconds
        retries: Number of retry attempts
        overwrite: Whether to overwrite existing files
        progress_callback: Optional callback for progress updates

    Returns:
        DownloadResult with status and metadata
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for attempt in range(retries):
        try:
            logger.debug(f"Attempting download: {url} (attempt {attempt + 1}/{retries})")
            response = requests.get(url, stream=True, timeout=timeout)
            response.raise_for_status()

            # Get filename from headers or use title
            from resource_fetcher_core.utils.http import extract_filename_from_headers, sanitize_filename
            filename = extract_filename_from_headers(dict(response.headers), song_id, song_title)
            filename = sanitize_filename(filename)
            output_path = output_dir / filename

            # Check if file exists
            if output_path.exists() and not overwrite:
                logger.info(f"File exists, skipping: {filename}")
                return DownloadResult(
                    status=DownloadStatus.SKIPPED,
                    path=output_path,
                    message="File already exists"
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

            logger.info(f"Downloaded successfully: {filename} ({downloaded_size:,} bytes)")
            return DownloadResult(
                status=DownloadStatus.SUCCESS,
                path=output_path,
                size=downloaded_size,
                message="Download successful"
            )

        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
            if attempt == retries - 1:
                logger.error(f"Failed to download after {retries} attempts: {url}")
                return DownloadResult(
                    status=DownloadStatus.FAILED,
                    path=None,
                    message=f"Download failed: {str(e)}"
                )
            # Exponential backoff
            wait_time = 2 ** attempt
            logger.info(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return DownloadResult(
                status=DownloadStatus.FAILED,
                path=None,
                message=f"Error: {str(e)}"
            )

    return DownloadResult(status=DownloadStatus.FAILED, message="Unknown error")


def download_album(
    url: str,
    output_dir: Path,
    limit: int | None = None,
    overwrite: bool = False,
    timeout: int = 60,
    retries: int = 3,
    delay: float = 0.5
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

    Returns:
        True if all downloads succeeded, False otherwise
    """
    try:
        # Fetch album page
        logger.info(f"Fetching album page: {url}")
        response = requests.get(url, timeout=30)
        response.encoding = 'utf-8'
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

            # Download song
            result = download_song(
                url=song.url,
                output_dir=output_dir,
                song_id=song.id,
                song_title=song.title,
                timeout=timeout,
                retries=retries,
                overwrite=overwrite
            )

            # Update progress
            progress.update(result)

            # Small delay between downloads to be polite to the server
            if idx < len(songs):
                time.sleep(delay)

        # Display summary
        print(progress.summary())

        # Return success status
        return progress.failed == 0

    except Exception as e:
        logger.error(f"Album download failed: {e}")
        print(f"\n错误: {e}")
        return False


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog='resource-fetcher',
        description='Resource Fetcher - Batch download resources from various websites',
        epilog='''
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
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--url',
        required=True,
        help='Album page URL to download'
    )

    parser.add_argument(
        '--output', '-o',
        default='./downloads',
        help='Output directory for downloaded songs (default: ./downloads)'
    )

    parser.add_argument(
        '--limit', '-l',
        type=int,
        metavar='N',
        help='Limit number of songs to download (e.g., --limit 10 for first 10 songs)'
    )

    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing files instead of skipping them'
    )

    parser.add_argument(
        '--timeout',
        type=int,
        default=60,
        metavar='SECONDS',
        help='Request timeout in seconds (default: 60)'
    )

    parser.add_argument(
        '--retries',
        type=int,
        default=3,
        metavar='N',
        help='Number of retry attempts for failed downloads (default: 3)'
    )

    parser.add_argument(
        '--delay',
        type=float,
        default=0.5,
        metavar='SECONDS',
        help='Delay between downloads in seconds (default: 0.5)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output for debugging'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    return parser


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")

    # Validate URL
    if not args.url.startswith('http'):
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
        delay=args.delay
    )

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
