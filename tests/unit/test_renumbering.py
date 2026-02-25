"""Unit tests for song renumbering functionality."""


from resource_fetcher_core.utils.http import add_track_number_prefix


class TestAddTrackNumberPrefix:
    """Test suite for add_track_number_prefix function."""

    def test_single_digit_padding_5_songs(self):
        """Test padding for 1-9 songs (no leading zeros needed)."""
        result = add_track_number_prefix("第1首 xxx.mp3", 1, 5)
        assert result == "1_第1首 xxx.mp3"

        result = add_track_number_prefix("第5首 yyy.mp3", 5, 5)
        assert result == "5_第5首 yyy.mp3"

    def test_double_digit_padding_50_songs(self):
        """Test padding for 10-99 songs (2-digit padding)."""
        result = add_track_number_prefix("第1首 xxx.mp3", 1, 50)
        assert result == "01_第1首 xxx.mp3"

        result = add_track_number_prefix("第10首 yyy.mp3", 10, 50)
        assert result == "10_第10首 yyy.mp3"

        result = add_track_number_prefix("第42首 zzz.mp3", 42, 50)
        assert result == "42_第42首 zzz.mp3"

        result = add_track_number_prefix("第99首 last.mp3", 99, 50)
        assert result == "99_第99首 last.mp3"

    def test_triple_digit_padding_200_songs(self):
        """Test padding for 100+ songs (3-digit padding)."""
        result = add_track_number_prefix("第1首 xxx.mp3", 1, 200)
        assert result == "001_第1首 xxx.mp3"

        result = add_track_number_prefix("第42首 yyy.mp3", 42, 200)
        assert result == "042_第42首 yyy.mp3"

        result = add_track_number_prefix("第99首 zzz.mp3", 99, 200)
        assert result == "099_第99首 zzz.mp3"

        result = add_track_number_prefix("第100首 aaa.mp3", 100, 200)
        assert result == "100_第100首 aaa.mp3"

    def test_extract_track_number_automatically(self):
        """Test automatic track number extraction from filename."""
        result = add_track_number_prefix("第7首 xxx.mp3", None, 9)
        assert result == "7_第7首 xxx.mp3"

        result = add_track_number_prefix("第42首 yyy.mp3", None, 50)
        assert result == "42_第42首 yyy.mp3"

        result = add_track_number_prefix("第1首 zzz.mp3", None, 100)
        assert result == "001_第1首 zzz.mp3"

    def test_no_track_number_returns_original(self):
        """Test filename without track number returns unchanged."""
        result = add_track_number_prefix("random_song.mp3", None, 10)
        assert result == "random_song.mp3"

        result = add_track_number_prefix("music track.mp3", None, 50)
        assert result == "music track.mp3"

        result = add_track_number_prefix("song_without_number.mp3", None, 100)
        assert result == "song_without_number.mp3"

    def test_edge_cases(self):
        """Test edge cases for padding calculation."""
        # Exactly 9 songs -> 1 digit padding
        result = add_track_number_prefix("第9首 xxx.mp3", 9, 9)
        assert result == "9_第9首 xxx.mp3"

        # Exactly 10 songs -> 2 digit padding
        result = add_track_number_prefix("第10首 xxx.mp3", 10, 10)
        assert result == "10_第10首 xxx.mp3"

        # Exactly 99 songs -> 2 digit padding
        result = add_track_number_prefix("第99首 xxx.mp3", 99, 99)
        assert result == "99_第99首 xxx.mp3"

        # Exactly 100 songs -> 3 digit padding
        result = add_track_number_prefix("第100首 xxx.mp3", 100, 100)
        assert result == "100_第100首 xxx.mp3"

    def test_preserves_extension(self):
        """Test that file extension is preserved."""
        result = add_track_number_prefix("第1首 圣哉三一歌.mp3", 1, 9)
        assert result == "1_第1首 圣哉三一歌.mp3"

        result = add_track_number_prefix("第5首 test.mp3", 5, 50)
        assert result == "05_第5首 test.mp3"

    def test_special_characters_in_filename(self):
        """Test filenames with special characters work correctly."""
        # Test with characters that might appear in Chinese song titles
        result = add_track_number_prefix("第1首 圣哉三一歌（修订版）.mp3", 1, 9)
        assert result == "1_第1首 圣哉三一歌（修订版）.mp3"

        result = add_track_number_prefix("第2首 赞美之泉.mp3", 2, 100)
        assert result == "002_第2首 赞美之泉.mp3"
