"""Unit tests for OutputParser."""


from resource_fetcher_gui.gui.core.output_parser import (
    AlbumInfo,
    DownloadSummary,
    OutputParser,
    SongProgress,
)


class TestSongProgress:
    """Test SongProgress dataclass."""

    def test_default_values(self) -> None:
        """Test default song progress values."""
        progress = SongProgress(index=1, total=10, title="Test Song", status="downloading")

        assert progress.index == 1
        assert progress.total == 10
        assert progress.title == "Test Song"
        assert progress.status == "downloading"


class TestAlbumInfo:
    """Test AlbumInfo dataclass."""

    def test_default_values(self) -> None:
        """Test default album info values."""
        info = AlbumInfo(title="Test Album", source="test.com", song_count=15)

        assert info.title == "Test Album"
        assert info.source == "test.com"
        assert info.song_count == 15


class TestDownloadSummary:
    """Test DownloadSummary dataclass."""

    def test_default_values(self) -> None:
        """Test default summary values."""
        summary = DownloadSummary(
            success=10, failed=2, skipped=1, total=13, elapsed_time=45.5, speed=0.28
        )

        assert summary.success == 10
        assert summary.failed == 2
        assert summary.skipped == 1
        assert summary.total == 13
        assert summary.elapsed_time == 45.5
        assert summary.speed == 0.28


class TestOutputParser:
    """Test OutputParser functionality."""

    def test_initialization(self) -> None:
        """Test parser initialization."""
        parser = OutputParser()

        assert parser._current_album is None
        assert parser._in_summary is False
        assert parser._summary_data == {}

    def test_parse_song_progress_basic(self) -> None:
        """Test parsing basic song progress line."""
        parser = OutputParser()
        # Use ASCII-only test for reliability
        line = "[5/10] Song Title"

        result = parser.parse_line(line)

        assert isinstance(result, SongProgress)
        assert result.index == 5
        assert result.total == 10
        assert result.title == "Song Title"
        assert result.status == "downloading"

    def test_parse_song_progress_with_numbers(self) -> None:
        """Test parsing song progress with various numbers."""
        parser = OutputParser()

        # Test different number formats
        test_cases = [
            ("[1/1] Only Song", 1, 1),
            ("[100/200] Middle Song", 100, 200),
            ("[999/999] Last Song", 999, 999),
        ]

        for line, expected_index, expected_total in test_cases:
            result = parser.parse_line(line)
            assert isinstance(result, SongProgress)
            assert result.index == expected_index
            assert result.total == expected_total

    def test_parse_empty_line(self) -> None:
        """Test parsing empty line returns None."""
        parser = OutputParser()

        result = parser.parse_line("")

        assert result is None

    def test_parse_unrecognized_line(self) -> None:
        """Test parsing unrecognized line returns None."""
        parser = OutputParser()
        line = "Some random text that doesn't match any pattern"

        result = parser.parse_line(line)

        assert result is None

    def test_parse_song_progress_convenience_method(self) -> None:
        """Test parse_song_progress convenience method."""
        parser = OutputParser()
        line = "[3/50] Test Song"

        result = parser.parse_song_progress(line)

        assert isinstance(result, SongProgress)
        assert result.index == 3
        assert result.total == 50

    def test_parse_song_progress_convenience_method_non_match(self) -> None:
        """Test parse_song_progress returns None for non-progress line."""
        parser = OutputParser()
        line = "Not a progress line"

        result = parser.parse_song_progress(line)

        assert result is None

    def test_reset(self) -> None:
        """Test parser reset functionality."""
        parser = OutputParser()

        # Set some state
        parser._current_album = AlbumInfo(title="Test", source="test.com", song_count=10)
        parser._in_summary = True
        parser._summary_data = {"success": 5}

        # Reset
        parser.reset()

        # Verify state is cleared
        assert parser._current_album is None
        assert parser._in_summary is False
        assert parser._summary_data == {}

    def test_parse_multiple_song_progress_updates(self) -> None:
        """Test parsing multiple consecutive song progress updates."""
        parser = OutputParser()

        lines = [
            "[1/10] First Song",
            "[2/10] Second Song",
            "[3/10] Third Song",
        ]

        results = [parser.parse_line(line) for line in lines]

        for i, result in enumerate(results, 1):
            assert isinstance(result, SongProgress)
            assert result.index == i
            assert result.total == 10
            assert result.status == "downloading"

    def test_regex_patterns_compilation(self) -> None:
        """Test that regex patterns are compiled correctly."""
        parser = OutputParser()

        # Check that patterns were compiled
        assert "album_title" in parser._compiled_patterns
        assert "song_progress" in parser._compiled_patterns
        assert "summary_header" in parser._compiled_patterns

        # Verify they are compiled regex objects
        import re

        for pattern in parser._compiled_patterns.values():
            assert isinstance(pattern, re.Pattern)

    def test_patterns_match_expected_formats(self) -> None:
        """Test that regex patterns match expected format strings."""
        parser = OutputParser()

        # Test song_progress pattern directly
        pattern = parser._compiled_patterns["song_progress"]
        match = pattern.match("[5/10] Test Song")
        assert match is not None
        assert match.group(1) == "5"
        assert match.group(2) == "10"
        assert match.group(3) == "Test Song"

    def test_parser_state_isolation(self) -> None:
        """Test that multiple parsers have independent state."""
        parser1 = OutputParser()
        parser2 = OutputParser()

        parser1._current_album = AlbumInfo(title="Album1", source="test.com", song_count=10)
        parser2._current_album = AlbumInfo(title="Album2", source="test.com", song_count=20)

        assert parser1._current_album.song_count == 10
        assert parser2._current_album.song_count == 20
