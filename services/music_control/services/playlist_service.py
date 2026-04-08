"""Playlist service for retrieving playlists, tracks, and focus recommendations."""

import logging
from music_control.clients.youtube_music_client import YouTubeMusicClient

logger = logging.getLogger("music_control.services.playlist")

# Focus-oriented keywords used to filter recommendations
FOCUS_KEYWORDS = [
    "focus", "study", "concentration", "lo-fi", "lofi", "ambient",
    "chill", "deep work", "instrumental", "classical", "meditation",
    "flow", "calm", "relax", "productivity", "brain",
]


class PlaylistService:
    """Service layer for playlist operations."""

    def __init__(self, client: YouTubeMusicClient | None = None):
        self._client = client or YouTubeMusicClient()

    def get_playlists(self) -> list[dict]:
        """Get all user playlists.

        Returns:
            List of playlist dicts.
        """
        return self._client.get_playlists()

    def get_playlist_tracks(self, playlist_id: str) -> list[dict]:
        """Get tracks for a specific playlist.

        Args:
            playlist_id: The playlist identifier.

        Returns:
            List of track dicts.
        """
        return self._client.get_playlist_tracks(playlist_id)

    def get_focus_recommendations(self) -> list[dict]:
        """Return playlists likely to aid focus based on title/description keywords.

        Returns:
            List of playlist dicts matching focus-related keywords.
        """
        all_playlists = self._client.get_playlists()
        recommendations = []
        for playlist in all_playlists:
            title_lower = (playlist.get("title") or "").lower()
            desc_lower = (playlist.get("description") or "").lower()
            combined = title_lower + " " + desc_lower
            if any(kw in combined for kw in FOCUS_KEYWORDS):
                recommendations.append(playlist)

        # If no matches, return all playlists as fallback
        if not recommendations:
            recommendations = all_playlists

        return recommendations
