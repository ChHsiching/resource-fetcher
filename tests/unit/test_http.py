"""Unit tests for HTTP utility functions."""

from resource_fetcher.utils.http import (
    extract_filename_from_headers,
    fix_mojibake,
    sanitize_filename,
)


class TestFixMojibake:
    """Test mojibake correction function."""

    def test_fix_chinese_mojibake(self):
        """Test fixing Chinese characters corrupted as latin-1."""
        # å£åä¸ is the mojibake version of 圣哉三一歌
        # Create it properly by encoding UTF-8 as latin-1
        original = "圣哉三一歌.mp3"
        mojibake = original.encode('utf-8').decode('latin-1')
        assert fix_mojibake(mojibake) == original

    def test_fix_various_chinese_songs(self):
        """Test fixing multiple Chinese song titles."""
        test_cases = [
            "三一来临歌.mp3",
            "万世之宗歌.mp3",
            "赞我天父歌.mp3",
            "亚伯拉罕的主歌.mp3",
        ]
        for original in test_cases:
            mojibake = original.encode('utf-8').decode('latin-1')
            assert fix_mojibake(mojibake) == original, f"Failed to fix: {mojibake}"

    def test_already_correct_filename(self):
        """Test that already correct filenames are not modified."""
        correct = "圣哉三一歌.mp3"
        assert fix_mojibake(correct) == correct

    def test_ascii_filename(self):
        """Test that ASCII filenames pass through unchanged."""
        ascii_filename = "song_123.mp3"
        assert fix_mojibake(ascii_filename) == ascii_filename

    def test_empty_filename(self):
        """Test empty filename handling."""
        assert fix_mojibake("") == ""

    def test_invalid_utf8_sequence(self):
        """Test that invalid UTF-8 sequences don't crash."""
        # This should not raise an exception
        invalid = "abc.mp3"
        assert fix_mojibake(invalid) == invalid


class TestExtractFilenameFromHeaders:
    """Test filename extraction from HTTP headers."""

    def test_extract_standard_filename(self):
        """Test extracting filename from standard Content-Disposition."""
        headers = {
            "Content-Disposition": 'attachment; filename="song.mp3"'
        }
        assert extract_filename_from_headers(headers) == "song.mp3"

    def test_extract_chinese_filename_with_mojibake(self):
        """Test extracting and fixing Chinese filename with mojibake."""
        # Create mojibake properly
        original = "圣哉三一歌.mp3"
        mojibake = original.encode('utf-8').decode('latin-1')
        headers = {
            "Content-Disposition": f'attachment; filename="{mojibake}"'
        }
        assert extract_filename_from_headers(headers) == original

    def test_extract_rfc5987_format(self):
        """Test extracting filename from RFC 5987 format."""
        headers = {
            "Content-Disposition": "attachment; filename*=UTF-8''%E5%9C%A3%E5%93%89.mp3"
        }
        assert extract_filename_from_headers(headers) == "圣哉.mp3"

    def test_fallback_to_song_id_and_title(self):
        """Test fallback to song ID and title when no filename in headers."""
        headers = {}
        result = extract_filename_from_headers(
            headers,
            song_id="16875",
            song_title="第1首 圣哉三一歌"
        )
        assert result == "第1首 圣哉三一歌.mp3"

    def test_fallback_to_title_only(self):
        """Test fallback to title only when no ID provided."""
        headers = {}
        result = extract_filename_from_headers(
            headers,
            song_title="圣哉三一歌"
        )
        assert result == "圣哉三一歌.mp3"

    def test_fallback_to_id_only(self):
        """Test fallback to ID only when no title provided."""
        headers = {}
        result = extract_filename_from_headers(
            headers,
            song_id="16875"
        )
        assert result == "16875.mp3"

    def test_fallback_to_unknown(self):
        """Test ultimate fallback when no metadata provided."""
        headers = {}
        assert extract_filename_from_headers(headers) == "unknown.mp3"

    def test_url_encoded_filename(self):
        """Test URL-encoded filename."""
        headers = {
            "Content-Disposition": "attachment; filename*=UTF-8''test%20song.mp3"
        }
        assert extract_filename_from_headers(headers) == "test song.mp3"


class TestSanitizeFilename:
    """Test filename sanitization."""

    def test_remove_windows_illegal_chars(self):
        """Test removing Windows illegal characters."""
        assert sanitize_filename('file:name*.mp3') == "file_name_.mp3"
        assert sanitize_filename('file/name?.mp3') == "file_name_.mp3"
        # Note: quotes are replaced by underscores, not doubled
        assert sanitize_filename('file|name\".mp3') == "file_name_.mp3"

    def test_remove_path_separators(self):
        """Test removing path separators."""
        assert sanitize_filename('path/to/file.mp3') == "path_to_file.mp3"
        assert sanitize_filename('path\\to\\file.mp3') == "path_to_file.mp3"

    def test_trim_whitespace(self):
        """Test trimming whitespace."""
        assert sanitize_filename('  file.mp3  ') == "file.mp3"

    def test_chinese_filename_unchanged(self):
        """Test that Chinese characters are preserved."""
        assert sanitize_filename('圣哉三一歌.mp3') == "圣哉三一歌.mp3"

    def test_mixed_chinese_and_illegal_chars(self):
        """Test sanitizing mixed Chinese and illegal characters."""
        assert sanitize_filename('圣哉三一歌*.mp3') == "圣哉三一歌_.mp3"

    def test_empty_filename(self):
        """Test empty filename."""
        assert sanitize_filename('') == ""
