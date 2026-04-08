"""YouTube Music client wrapping ytmusicapi for playlist and track access."""

import logging
from typing import Optional
from sqlalchemy.orm import Session

logger = logging.getLogger("music_control.clients.youtube_music")

# Graceful import -- ytmusicapi may not be installed
try:
    from ytmusicapi import YTMusic
    YTMUSIC_AVAILABLE = True
except ImportError:
    YTMusic = None
    YTMUSIC_AVAILABLE = False
    logger.warning("ytmusicapi not installed -- YouTube Music features will return demo data")


class YouTubeMusicClient:
    """Wraps ytmusicapi to provide playlist and track operations."""

    def __init__(self, auth_header: Optional[str] = None):
        """Initialize the client with optional auth credentials.

        Args:
            auth_header: Raw browser auth header string for ytmusicapi.
        """
        self._yt: Optional[object] = None
        if YTMUSIC_AVAILABLE and auth_header:
            try:
                self._yt = YTMusic(auth_header)
            except Exception:
                logger.exception("Failed to initialize YTMusic with provided auth")

    def get_playlists(self) -> list[dict]:
        """Return user's YouTube Music playlists.

        Returns:
            List of dicts with playlist_id, title, description, track_count, thumbnail_url.
        """
        if not self._yt:
            return self._demo_playlists()

        try:
            raw = self._yt.get_library_playlists(limit=50)
            return [
                {
                    "playlist_id": p.get("playlistId", ""),
                    "title": p.get("title", "Untitled"),
                    "description": p.get("description", ""),
                    "track_count": p.get("count", 0),
                    "thumbnail_url": (
                        p["thumbnails"][0]["url"]
                        if p.get("thumbnails")
                        else None
                    ),
                }
                for p in raw
            ]
        except Exception:
            logger.exception("Failed to fetch playlists from YouTube Music")
            return self._demo_playlists()

    def get_playlist_tracks(self, playlist_id: str) -> list[dict]:
        """Return tracks for a given playlist.

        Args:
            playlist_id: The YouTube Music playlist ID.

        Returns:
            List of dicts with track_id, title, artist, album, duration_seconds, thumbnail_url.
        """
        if not self._yt:
            return self._demo_tracks(playlist_id)

        try:
            playlist = self._yt.get_playlist(playlist_id, limit=100)
            tracks = playlist.get("tracks", [])
            return [
                {
                    "track_id": t.get("videoId", ""),
                    "title": t.get("title", "Untitled"),
                    "artist": (
                        t["artists"][0]["name"]
                        if t.get("artists")
                        else "Unknown"
                    ),
                    "album": (
                        t["album"]["name"]
                        if t.get("album")
                        else None
                    ),
                    "duration_seconds": t.get("duration_seconds"),
                    "thumbnail_url": (
                        t["thumbnails"][0]["url"]
                        if t.get("thumbnails")
                        else None
                    ),
                }
                for t in tracks
            ]
        except Exception:
            logger.exception("Failed to fetch tracks for playlist %s", playlist_id)
            return self._demo_tracks(playlist_id)

    @staticmethod
    def setup_auth(db: Session, user_id: str, headers: str) -> dict:
        """Store YouTube Music auth credentials for a user.

        Args:
            db: SQLAlchemy database session.
            user_id: The user ID.
            headers: Raw browser request headers for ytmusicapi authentication.

        Returns:
            Dict with status information.
        """
        from music_control.models.session_music_models import YouTubeAuth

        existing = db.query(YouTubeAuth).filter_by(user_id=user_id).first()
        if existing:
            existing.credentials = {"headers": headers}
            existing.is_valid = True
        else:
            auth = YouTubeAuth(
                user_id=user_id,
                credentials={"headers": headers},
                is_valid=True,
            )
            db.add(auth)
        db.commit()
        return {"status": "ok", "user_id": user_id, "message": "Auth credentials stored"}

    @staticmethod
    def check_auth_status(db: Session, user_id: str) -> dict:
        """Check whether a user has valid YouTube Music auth credentials.

        Args:
            db: SQLAlchemy database session.
            user_id: The user ID.

        Returns:
            Dict with authenticated bool and metadata.
        """
        from music_control.models.session_music_models import YouTubeAuth

        auth = db.query(YouTubeAuth).filter_by(user_id=user_id).first()
        if auth and auth.is_valid:
            return {
                "authenticated": True,
                "user_id": user_id,
                "created_at": auth.created_at.isoformat() if auth.created_at else None,
            }
        return {"authenticated": False, "user_id": user_id}

    # ---- Demo data for when ytmusicapi is unavailable ----

    @staticmethod
    def _demo_playlists() -> list[dict]:
        return [
            {
                "playlist_id": "demo_focus_beats",
                "title": "Focus Beats",
                "description": "Lo-fi beats for deep concentration",
                "track_count": 25,
                "thumbnail_url": None,
            },
            {
                "playlist_id": "demo_ambient_flow",
                "title": "Ambient Flow",
                "description": "Ambient soundscapes for flow state",
                "track_count": 18,
                "thumbnail_url": None,
            },
            {
                "playlist_id": "demo_classical_focus",
                "title": "Classical Focus",
                "description": "Classical music for productive work",
                "track_count": 30,
                "thumbnail_url": None,
            },
        ]

    @staticmethod
    def _demo_tracks(playlist_id: str) -> list[dict]:
        tracks_by_playlist = {
            "demo_focus_beats": [
                {"track_id": "demo_t1", "title": "Midnight Rain", "artist": "ChillHop", "album": "Night Sessions", "duration_seconds": 195, "thumbnail_url": None},
                {"track_id": "demo_t2", "title": "Coffee Shop Vibes", "artist": "Lo-Fi Girl", "album": "Study Time", "duration_seconds": 210, "thumbnail_url": None},
                {"track_id": "demo_t3", "title": "Deep Focus", "artist": "Ambient Works", "album": "Flow State", "duration_seconds": 240, "thumbnail_url": None},
            ],
            "demo_ambient_flow": [
                {"track_id": "demo_t4", "title": "Ocean Waves", "artist": "Nature Sounds", "album": "Serenity", "duration_seconds": 300, "thumbnail_url": None},
                {"track_id": "demo_t5", "title": "Forest Morning", "artist": "Nature Sounds", "album": "Serenity", "duration_seconds": 280, "thumbnail_url": None},
            ],
            "demo_classical_focus": [
                {"track_id": "demo_t6", "title": "Clair de Lune", "artist": "Debussy", "album": "Suite bergamasque", "duration_seconds": 310, "thumbnail_url": None},
                {"track_id": "demo_t7", "title": "Gymnopedies No.1", "artist": "Satie", "album": "Gymnopedies", "duration_seconds": 195, "thumbnail_url": None},
            ],
        }
        return tracks_by_playlist.get(playlist_id, [
            {"track_id": "demo_generic_1", "title": "Focus Track 1", "artist": "Unknown", "album": None, "duration_seconds": 200, "thumbnail_url": None},
        ])
