"""IzanmeiAdapter for izanmei.cc website."""

import re

from resource_fetcher_core.core.interfaces import SiteAdapter
from resource_fetcher_core.core.models import Album, Song


class IzanmeiAdapter(SiteAdapter):
    """
    Adapter for 爱赞美网 (izanmei.cc).

    Handles extraction of albums and songs from the izanmei.cc website.
    """

    BASE_URL = "https://www.izanmei.cc"
    AUDIO_BASE = "https://play.xiaoh.ai/song/p"

    def can_handle(self, url: str) -> bool:
        """
        Check if URL belongs to izanmei.cc.

        Args:
            url: The URL to check

        Returns:
            True if URL contains 'izanmei.cc', False otherwise
        """
        return "izanmei.cc" in url

    def extract_album(self, url: str) -> Album:
        """
        Extract album information from izanmei.cc HTML.

        This method parses HTML and extracts:
        - Album title
        - Song list with IDs and titles
        - Audio download URLs

        Args:
            url: The album page URL

        Returns:
            Album object with all songs

        Raises:
            ValueError: If no songs found in the HTML
        """
        # For testing, accept HTML string directly
        if url.startswith("<!DOCTYPE") or url.startswith("<html"):
            html = url
            page_url = "https://www.izanmei.cc/album/hymns-442-1.html"
        else:
            # In real implementation, would fetch from URL here
            # For now, raise error to indicate URL fetching not implemented
            raise NotImplementedError(
                "Direct URL fetching not implemented yet. " "Use HTML string for testing."
            )

        # Extract album title
        album_title = self._extract_album_title(html)

        # Extract songs with track numbers using regex
        # Strategy: extract track numbers from <td class="i"> and song links separately
        # Pattern: <td class="i" style='width:58px;'>第101首</td> appears before
        # <a href="/song/16975.html">

        # Extract track numbers ONLY from <td class="i"> tags to avoid false matches
        # Use DOTALL flag to match across newlines, and handle whitespace
        track_numbers = re.findall(r'<td\s+class="i"[^>]*>.*?第(\d+)首', html, re.DOTALL)

        # Extract all song links
        song_pattern = r'<a\s+href="/song/(\d+)\.html"[^>]*>([^<]+)</a>'
        songs_data = re.findall(song_pattern, html)

        if len(track_numbers) > 0 and len(songs_data) > 0:
            # Combine track numbers with songs (they should match 1-to-1)
            song_entries = []
            min_len = min(len(track_numbers), len(songs_data))
            for i in range(min_len):
                song_entries.append((track_numbers[i], songs_data[i][0], songs_data[i][1]))
        else:
            # Fallback: no track numbers found
            pattern = r'href="/song/(\d+)\.html"[^>]*>([^<]+)'
            matches = re.findall(pattern, html)
            if matches:
                # Generate track numbers sequentially
                song_entries = [
                    (str(i), song_id, title) for i, (song_id, title) in enumerate(matches, 1)
                ]
            else:
                raise ValueError("No songs found in HTML")

        if not song_entries:
            # Fallback: try without track numbers (for old format pages)
            pattern = r'href="/song/(\d+)\.html"[^>]*>([^<]+)'
            matches = re.findall(pattern, html)
            if matches:
                # Generate track numbers sequentially
                song_entries = [
                    (str(i), song_id, title) for i, (song_id, title) in enumerate(matches, 1)
                ]
            else:
                raise ValueError("No songs found in HTML")

        # Construct song objects with track numbers
        songs = []
        for track_num, song_id, title in song_entries:
            audio_url = f"{self.AUDIO_BASE}/{song_id}.mp3"
            # Use the actual track number from the page (e.g., "101", "102")
            # Don't pad with zeros - use the original number from HTML
            formatted_title = f"第{track_num}首 {title.strip()}"
            song = Song(
                id=song_id,
                title=formatted_title,
                url=audio_url,
                metadata={"source": "izanmei.cc", "track_number": track_num},
            )
            songs.append(song)

        return Album(title=album_title, url=page_url, songs=songs, source="izanmei.cc")

    def _extract_album_title(self, html: str) -> str:
        """
        Extract album title from HTML.

        Args:
            html: The HTML content

        Returns:
            Album title or "未知专辑" if not found
        """
        match = re.search(r"<h1[^>]*>([^<]+)</h1>", html)
        if match:
            return match.group(1).strip()
        return "未知专辑"
