"""Pattern discoverer -- uses OpenAI to find productivity patterns."""

import json
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ai_insights.clients.openai_client import OpenAIClient
from ai_insights.config.ai_settings import get_settings
from ai_insights.config.prompt_config import get_pattern_discovery_prompt
from ai_insights.models.pattern_models import (
    UserPattern,
    PatternResponse,
    PatternDetail,
)

logger = logging.getLogger(__name__)


class PatternDiscoverer:
    """Discovers and caches productivity patterns for users."""

    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.client = OpenAIClient(db)

    def discover(self, user_id: str, user_context: dict) -> PatternResponse:
        """Discover productivity patterns from user data.

        Args:
            user_id: User identifier.
            user_context: Dict with session history and metrics.

        Returns:
            PatternResponse with discovered patterns.
        """
        template = get_pattern_discovery_prompt()
        prompt = template.format(
            session_history=json.dumps(
                user_context.get("recent_sessions", []), indent=2
            ),
            metrics=json.dumps(
                {
                    "total_sessions": user_context.get("total_sessions", 0),
                    "total_focus_minutes": user_context.get("total_focus_minutes", 0),
                    "avg_productivity_score": user_context.get(
                        "avg_productivity_score", 0.0
                    ),
                },
                indent=2,
            ),
        )

        result = self.client.generate(
            prompt=prompt,
            user_id=user_id,
            insight_type="pattern_discovery",
            ttl_seconds=self.settings.coaching_cache_ttl,
        )

        # Store discovered patterns in the database
        raw_patterns = result.get("patterns", [])
        for p in raw_patterns:
            existing = (
                self.db.query(UserPattern)
                .filter_by(user_id=user_id, pattern_type=p.get("pattern_type", ""))
                .first()
            )
            if existing:
                existing.pattern_data = p.get("data")
                existing.confidence = p.get("confidence", 0.0)
                existing.updated_at = datetime.now(timezone.utc)
            else:
                self.db.add(
                    UserPattern(
                        user_id=user_id,
                        pattern_type=p.get("pattern_type", "unknown"),
                        pattern_data=p.get("data"),
                        confidence=p.get("confidence", 0.0),
                    )
                )
        self.db.commit()

        details = [
            PatternDetail(
                pattern_type=p.get("pattern_type", "unknown"),
                description=p.get("description", ""),
                confidence=p.get("confidence", 0.0),
                data=p.get("data"),
            )
            for p in raw_patterns
        ]

        return PatternResponse(
            user_id=user_id,
            patterns=details,
            interpretation=result.get("interpretation", ""),
            discovered_at=datetime.now(timezone.utc).isoformat(),
            cached=False,
        )

    def get_cached_patterns(self, user_id: str) -> PatternResponse:
        """Return previously discovered patterns from the database.

        Args:
            user_id: User identifier.

        Returns:
            PatternResponse with cached patterns.
        """
        rows = (
            self.db.query(UserPattern)
            .filter_by(user_id=user_id)
            .order_by(UserPattern.updated_at.desc())
            .all()
        )

        details = [
            PatternDetail(
                pattern_type=r.pattern_type,
                description=r.pattern_data.get("description", "") if isinstance(r.pattern_data, dict) else "",
                confidence=r.confidence or 0.0,
                data=r.pattern_data,
            )
            for r in rows
        ]

        return PatternResponse(
            user_id=user_id,
            patterns=details,
            interpretation="Previously discovered patterns",
            discovered_at=rows[0].updated_at.isoformat() if rows else None,
            cached=True,
        )
