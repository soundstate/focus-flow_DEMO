"""Effectiveness tracker for measuring music impact on productivity."""

import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from music_control.models.session_music_models import (
    SessionMusicLog,
    TrackEffectiveness,
)
from music_control.models.track_models import (
    TrackEffectivenessReport,
    EffectivenessReport,
)

logger = logging.getLogger("music_control.services.effectiveness")


class EffectivenessTracker:
    """Tracks and reports on the effectiveness of music for focus sessions."""

    def __init__(self, db: Session):
        self.db = db

    def get_report(self, user_id: str) -> dict:
        """Get overall effectiveness report for a user.

        Args:
            user_id: The user to report on.

        Returns:
            EffectivenessReport as dict.
        """
        rows = (
            self.db.query(TrackEffectiveness)
            .filter_by(user_id=user_id)
            .order_by(TrackEffectiveness.avg_productivity_score.desc())
            .all()
        )

        if not rows:
            return EffectivenessReport(user_id=user_id).model_dump()

        top_tracks = [
            TrackEffectivenessReport(
                track_id=r.track_id,
                genre=r.genre,
                avg_productivity_score=r.avg_productivity_score,
                session_count=r.session_count,
            )
            for r in rows[:10]
        ]

        # Aggregate genres
        genre_scores: dict[str, list[float]] = {}
        for r in rows:
            g = r.genre or "unknown"
            genre_scores.setdefault(g, []).append(r.avg_productivity_score)

        top_genres = sorted(
            [
                {"genre": g, "avg_score": round(sum(scores) / len(scores), 3)}
                for g, scores in genre_scores.items()
            ],
            key=lambda x: x["avg_score"],
            reverse=True,
        )[:5]

        total_sessions = sum(r.session_count for r in rows)
        avg_score = (
            sum(r.avg_productivity_score * r.session_count for r in rows) / total_sessions
            if total_sessions > 0
            else 0.0
        )

        report = EffectivenessReport(
            user_id=user_id,
            total_tracks_played=len(rows),
            top_tracks=top_tracks,
            top_genres=top_genres,
            avg_overall_score=round(avg_score, 3),
        )
        return report.model_dump()

    def get_track_report(self, user_id: str, track_id: str) -> dict:
        """Get effectiveness data for a specific track.

        Args:
            user_id: The user.
            track_id: The track identifier.

        Returns:
            TrackEffectivenessReport as dict or empty report.
        """
        row = (
            self.db.query(TrackEffectiveness)
            .filter_by(user_id=user_id, track_id=track_id)
            .first()
        )

        if not row:
            return TrackEffectivenessReport(track_id=track_id).model_dump()

        return TrackEffectivenessReport(
            track_id=row.track_id,
            genre=row.genre,
            avg_productivity_score=row.avg_productivity_score,
            session_count=row.session_count,
        ).model_dump()

    def log_session_music(
        self,
        user_id: str,
        session_id: str,
        track_id: str,
        track_title: str,
        artist: str | None = None,
        playlist_id: str | None = None,
        productivity_score: float | None = None,
        genre: str | None = None,
    ) -> dict:
        """Log a track played during a focus session and update effectiveness.

        Args:
            user_id: The user.
            session_id: Focus session ID.
            track_id: Track identifier.
            track_title: Track title.
            artist: Artist name.
            playlist_id: Source playlist.
            productivity_score: Productivity score for the session (0.0-1.0).
            genre: Track genre.

        Returns:
            Dict with log_id and status.
        """
        log = SessionMusicLog(
            user_id=user_id,
            session_id=session_id,
            track_id=track_id,
            track_title=track_title,
            artist=artist,
            playlist_id=playlist_id,
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(log)
        self.db.flush()

        # Update effectiveness if we have a productivity score
        if productivity_score is not None:
            self._update_effectiveness(user_id, track_id, genre, productivity_score)

        self.db.commit()
        return {"log_id": log.id, "status": "logged"}

    def _update_effectiveness(
        self, user_id: str, track_id: str, genre: str | None, score: float
    ) -> None:
        """Update running average effectiveness for a track."""
        existing = (
            self.db.query(TrackEffectiveness)
            .filter_by(user_id=user_id, track_id=track_id)
            .first()
        )

        if existing:
            total = existing.avg_productivity_score * existing.session_count + score
            existing.session_count += 1
            existing.avg_productivity_score = round(total / existing.session_count, 4)
            if genre:
                existing.genre = genre
        else:
            eff = TrackEffectiveness(
                user_id=user_id,
                track_id=track_id,
                genre=genre,
                avg_productivity_score=round(score, 4),
                session_count=1,
            )
            self.db.add(eff)
