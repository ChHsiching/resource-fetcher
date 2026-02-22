"""Test models for music downloader."""

import pytest
from resource_fetcher.core.models import Song, Album, DownloadStatus, DownloadResult


class TestSong:
    """Test Song model."""

    def test_create_song_with_required_fields(self):
        """Test creating a Song with all required fields."""
        song = Song(
            id="16875",
            title="圣哉三一歌",
            url="https://play.xiaoh.ai/song/p/16875.mp3",
            metadata={"source": "izanmei.cc"}
        )

        assert song.id == "16875"
        assert song.title == "圣哉三一歌"
        assert song.url == "https://play.xiaoh.ai/song/p/16875.mp3"
        assert song.metadata == {"source": "izanmei.cc"}

    def test_create_song_without_metadata(self):
        """Test creating a Song without metadata (should default to empty dict)."""
        song = Song(
            id="16876",
            title="三一来临歌",
            url="https://play.xiaoh.ai/song/p/16876.mp3"
        )

        assert song.metadata == {}

    def test_song_equality(self):
        """Test Song equality based on ID."""
        song1 = Song(id="16875", title="圣哉三一歌", url="http://example.com/1.mp3")
        song2 = Song(id="16875", title="Different Title", url="http://example.com/2.mp3")
        song3 = Song(id="16876", title="圣哉三一歌", url="http://example.com/1.mp3")

        assert song1 == song2  # Same ID
        assert song1 != song3  # Different ID


class TestAlbum:
    """Test Album model."""

    def test_create_album_with_required_fields(self):
        """Test creating an Album with all required fields."""
        songs = [
            Song(id="16875", title="圣哉三一歌", url="https://example.com/1.mp3"),
            Song(id="16876", title="三一来临歌", url="https://example.com/2.mp3"),
        ]

        album = Album(
            title="新编赞美诗442首(001-100)",
            url="https://www.izanmei.cc/album/hymns-442-1.html",
            songs=songs,
            source="izanmei.cc"
        )

        assert album.title == "新编赞美诗442首(001-100)"
        assert album.url == "https://www.izanmei.cc/album/hymns-442-1.html"
        assert len(album.songs) == 2
        assert album.source == "izanmei.cc"

    def test_album_song_count(self):
        """Test getting the number of songs in an album."""
        songs = [Song(id=str(i), title=f"Song {i}", url=f"http://example.com/{i}.mp3") for i in range(100)]

        album = Album(
            title="Test Album",
            url="https://example.com/album",
            songs=songs,
            source="test"
        )

        assert len(album) == 100

    def test_empty_album(self):
        """Test creating an album with no songs."""
        album = Album(
            title="Empty Album",
            url="https://example.com/empty",
            songs=[],
            source="test"
        )

        assert len(album) == 0
        assert album.songs == []


class TestDownloadResult:
    """Test DownloadResult model."""

    def test_success_result(self):
        """Test creating a successful download result."""
        result = DownloadResult(
            status=DownloadStatus.SUCCESS,
            path= "path/to/song.mp3",
            size=1024000,
            message="Download successful"
        )

        assert result.status == DownloadStatus.SUCCESS
        assert result.path == "path/to/song.mp3"
        assert result.size == 1024000
        assert result.message == "Download successful"
        assert result.is_success()

    def test_failed_result(self):
        """Test creating a failed download result."""
        result = DownloadResult(
            status=DownloadStatus.FAILED,
            path=None,
            message="Network error"
        )

        assert result.status == DownloadStatus.FAILED
        assert result.path is None
        assert result.size == 0
        assert not result.is_success()

    def test_skipped_result(self):
        """Test creating a skipped download result."""
        result = DownloadResult(
            status=DownloadStatus.SKIPPED,
            path="path/to/existing.mp3",
            message="File already exists"
        )

        assert result.status == DownloadStatus.SKIPPED
        assert not result.is_success()
        assert not result.is_failed()

    def test_is_failed_method(self):
        """Test the is_failed helper method."""
        failed_result = DownloadResult(
            status=DownloadStatus.FAILED,
            path=None,
            message="Error"
        )
        success_result = DownloadResult(
            status=DownloadStatus.SUCCESS,
            path="path.mp3",
            message="OK"
        )

        assert failed_result.is_failed()
        assert not success_result.is_failed()
