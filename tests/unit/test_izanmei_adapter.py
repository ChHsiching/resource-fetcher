"""Test IzanmeiAdapter for izanmei.cc website."""

import pytest

from resource_fetcher.adapters.izanmei import IzanmeiAdapter


class TestIzanmeiAdapter:
    """Test IzanmeiAdapter implementation."""

    def test_can_handle_izanmei_urls(self):
        """Test URL identification for izanmei.cc."""
        adapter = IzanmeiAdapter()

        assert adapter.can_handle("https://www.izanmei.cc/album/hymns-442-1.html") is True
        assert adapter.can_handle("http://izanmei.cc/song/12345.html") is True
        assert adapter.can_handle("https://music.163.com/album/123") is False
        assert adapter.can_handle("https://youtube.com/watch?v=123") is False

    def test_extract_album_from_html(self, sample_izanmei_html):
        """Test extracting album from HTML fixture."""
        adapter = IzanmeiAdapter()

        album = adapter.extract_album(sample_izanmei_html)

        assert album.title == "新编赞美诗442首(001-100)"
        assert album.url == "https://www.izanmei.cc/album/hymns-442-1.html"
        assert album.source == "izanmei.cc"
        assert len(album.songs) == 5

        # Verify first song
        first_song = album.songs[0]
        assert first_song.id == "16875"
        assert first_song.title == "第1首 圣哉三一歌"
        assert first_song.url == "https://play.xiaoh.ai/song/p/16875.mp3"
        assert first_song.metadata["source"] == "izanmei.cc"
        assert first_song.metadata["track_number"] == "1"

        # Verify last song
        last_song = album.songs[-1]
        assert last_song.id == "16879"
        assert last_song.title == "第5首 亚伯拉罕的主歌"
        assert last_song.metadata["track_number"] == "5"

    def test_extract_album_audio_urls(self, sample_izanmei_html):
        """Test that audio URLs are correctly constructed."""
        adapter = IzanmeiAdapter()
        album = adapter.extract_album(sample_izanmei_html)

        urls = [song.url for song in album.songs]

        assert urls == [
            "https://play.xiaoh.ai/song/p/16875.mp3",
            "https://play.xiaoh.ai/song/p/16876.mp3",
            "https://play.xiaoh.ai/song/p/16877.mp3",
            "https://play.xiaoh.ai/song/p/16878.mp3",
            "https://play.xiaoh.ai/song/p/16879.mp3",
        ]


@pytest.fixture
def sample_izanmei_html():
    """Load sample HTML from fixture file."""
    import os
    fixture_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "fixtures",
        "html",
        "izanmei_album.html"
    )
    with open(fixture_path, encoding="utf-8") as f:
        return f.read()
