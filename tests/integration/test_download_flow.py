"""Integration tests for complete download flow."""

import pytest
from pathlib import Path
import tempfile
import shutil

from resource_fetcher.adapters.izanmei import IzanmeiAdapter
from resource_fetcher.cli.main import download_song
from resource_fetcher.core.models import DownloadStatus


class TestIzanmeiAdapterIntegration:
    """Integration tests for IzanmeiAdapter."""

    def test_extract_album_from_html(self):
        """Test extracting complete album information."""
        adapter = IzanmeiAdapter()

        # Use real HTML from the website
        import requests
        response = requests.get("https://www.izanmei.cc/album/hymns-442-1.html", timeout=30)
        response.encoding = 'utf-8'
        html = response.text

        album = adapter.extract_album(html)

        # Verify album structure (title may vary slightly on website)
        assert "新编赞美诗442首" in album.title
        assert album.url == "https://www.izanmei.cc/album/hymns-442-1.html"
        assert album.source == "izanmei.cc"
        assert len(album.songs) == 100

        # Verify first song
        first_song = album.songs[0]
        assert first_song.id == "16875"
        assert first_song.title == "第1首 圣哉三一歌"
        assert first_song.url == "https://play.xiaoh.ai/song/p/16875.mp3"
        assert first_song.metadata["source"] == "izanmei.cc"
        assert first_song.metadata["track_number"] == "1"

        # Verify last song
        last_song = album.songs[-1]
        assert last_song.id == "16974"
        assert last_song.title == "第100首 万古磐石歌"
        assert last_song.url == "https://play.xiaoh.ai/song/p/16974.mp3"
        assert last_song.metadata["track_number"] == "100"

    def test_can_handle_url(self):
        """Test URL recognition."""
        adapter = IzanmeiAdapter()
        assert adapter.can_handle("https://www.izanmei.cc/album/hymns-442-1.html")
        assert adapter.can_handle("http://izanmei.cc/song/16875.html")
        assert not adapter.can_handle("https://music.163.com")


class TestDownloadFlowIntegration:
    """Integration tests for download flow."""

    def test_download_single_song_with_correct_filename(self):
        """Test downloading a single song and verify filename is correct."""
        with tempfile.TemporaryDirectory() as tmpdir:
            url = "https://play.xiaoh.ai/song/p/16875.mp3"
            result = download_song(
                url=url,
                output_dir=Path(tmpdir),
                song_id="16875",
                song_title="圣哉三一歌"
            )

            # Verify download success
            assert result.status == DownloadStatus.SUCCESS
            assert result.path is not None
            assert result.size > 0

            # Verify filename is correct Chinese (not mojibake)
            filename = result.path.name
            assert filename == "圣哉三一歌.mp3", f"Expected '圣哉三一歌.mp3' but got '{filename}'"

            # Verify file exists and has content
            assert result.path.exists()
            assert result.path.stat().st_size == result.size
            # Expected file size around 430KB
            assert 400000 < result.size < 500000

    def test_download_multiple_songs(self):
        """Test downloading multiple songs and verify all filenames."""
        with tempfile.TemporaryDirectory() as tmpdir:
            songs = [
                ("16875", "圣哉三一歌", "https://play.xiaoh.ai/song/p/16875.mp3"),
                ("16876", "三一来临歌", "https://play.xiaoh.ai/song/p/16876.mp3"),
                ("16877", "万世之宗歌", "https://play.xiaoh.ai/song/p/16877.mp3"),
            ]

            expected_files = []
            for song_id, title, url in songs:
                result = download_song(
                    url=url,
                    output_dir=Path(tmpdir),
                    song_id=song_id,
                    song_title=title
                )
                assert result.status == DownloadStatus.SUCCESS
                expected_filename = f"{title}.mp3"
                expected_files.append(expected_filename)

                # Verify filename is correct
                assert result.path.name == expected_filename

            # Verify all files exist in directory
            downloaded_files = [f.name for f in Path(tmpdir).glob("*.mp3")]
            assert set(downloaded_files) == set(expected_files)

    def test_skip_existing_files(self):
        """Test that existing files are skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            url = "https://play.xiaoh.ai/song/p/16875.mp3"
            song_id = "16875"
            song_title = "圣哉三一歌"

            # First download
            result1 = download_song(
                url=url,
                output_dir=Path(tmpdir),
                song_id=song_id,
                song_title=song_title
            )
            assert result1.status == DownloadStatus.SUCCESS

            # Second download should skip
            result2 = download_song(
                url=url,
                output_dir=Path(tmpdir),
                song_id=song_id,
                song_title=song_title
            )
            assert result2.status == DownloadStatus.SKIPPED
            assert "exists" in result2.message.lower()

    def test_download_with_mojibake_in_headers(self):
        """Test that mojibake in HTTP headers is correctly fixed."""
        # This test verifies the real-world scenario where the server
        # sends mojibake in Content-Disposition header
        with tempfile.TemporaryDirectory() as tmpdir:
            url = "https://play.xiaoh.ai/song/p/16875.mp3"

            result = download_song(
                url=url,
                output_dir=Path(tmpdir),
                song_id="16875",
                song_title="圣哉三一歌"
            )

            # The filename should be correct Chinese, not mojibake
            # å£åä¸.mp3 is the mojibake version
            assert result.path.name == "圣哉三一歌.mp3"
            assert result.path.name != "å£åä¸.mp3"


class TestEndToEndAlbumDownload:
    """End-to-end tests for complete album download."""

    @pytest.mark.slow
    def test_download_first_5_songs(self):
        """Test downloading the first 5 songs from the album."""
        with tempfile.TemporaryDirectory() as tmpdir:
            adapter = IzanmeiAdapter()

            # Fetch album
            import requests
            response = requests.get("https://www.izanmei.cc/album/hymns-442-1.html", timeout=30)
            response.encoding = 'utf-8'
            html = response.text
            album = adapter.extract_album(html)

            # Download first 5 songs
            first_5 = album.songs[:5]
            results = []
            for song in first_5:
                result = download_song(
                    url=song.url,
                    output_dir=Path(tmpdir),
                    song_id=song.id,
                    song_title=song.title
                )
                results.append(result)

            # Verify all downloads succeeded
            assert all(r.status == DownloadStatus.SUCCESS for r in results)

            # Verify filenames
            expected_names = [s.title + ".mp3" for s in first_5]
            actual_names = [r.path.name for r in results]
            assert actual_names == expected_names

            # Verify files exist
            for result in results:
                assert result.path.exists()
                assert result.path.stat().st_size > 0

    @pytest.mark.slow
    def test_verify_file_integrity(self):
        """Test that downloaded files match expected sizes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Known file sizes from the server
            known_sizes = {
                "16875": 430632,  # 圣哉三一歌.mp3
                "16876": 274104,  # 三一来临歌.mp3
                "16877": 246456,  # 万世之宗歌.mp3
            }

            for song_id, expected_size in known_sizes.items():
                url = f"https://play.xiaoh.ai/song/p/{song_id}.mp3"
                result = download_song(
                    url=url,
                    output_dir=Path(tmpdir),
                    song_id=song_id,
                    song_title=f"Song{song_id}"
                )

                assert result.status == DownloadStatus.SUCCESS
                assert result.size == expected_size, \
                    f"File size mismatch for {song_id}: expected {expected_size}, got {result.size}"
