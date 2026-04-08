"""Coaching generator -- uses OpenAI to produce coaching tips, session reviews, and daily briefings."""

import json
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ai_insights.clients.openai_client import OpenAIClient
from ai_insights.config.ai_settings import get_settings
from ai_insights.config.prompt_config import (
    get_coaching_prompt,
    get_session_review_prompt,
    get_daily_briefing_prompt,
)
from ai_insights.models.insights_models import (
    CoachingResponse,
    CoachingTip,
    SessionReviewResponse,
    DailyBriefingResponse,
)

logger = logging.getLogger(__name__)


class CoachingGenerator:
    """Generates AI-powered coaching insights."""

    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.client = OpenAIClient(db)

    def generate_coaching(self, user_id: str, user_context: dict) -> CoachingResponse:
        """Generate personalised coaching tips.

        Args:
            user_id: User identifier.
            user_context: Dict with session history context.

        Returns:
            CoachingResponse with tips and summary.
        """
        template = get_coaching_prompt()
        prompt = template.format(
            user_context=json.dumps(user_context, indent=2),
            session_data=json.dumps(user_context.get("recent_sessions", []), indent=2),
        )

        result = self.client.generate(
            prompt=prompt,
            user_id=user_id,
            insight_type="coaching",
            ttl_seconds=self.settings.coaching_cache_ttl,
        )

        tips = [
            CoachingTip(**t) for t in result.get("tips", [])
        ]

        return CoachingResponse(
            user_id=user_id,
            tips=tips,
            summary=result.get("summary", ""),
            generated_at=datetime.now(timezone.utc).isoformat(),
            cached=False,
        )

    def generate_session_review(
        self, user_id: str, session_data: dict, user_context: dict
    ) -> SessionReviewResponse:
        """Generate a review for a completed focus session.

        Args:
            user_id: User identifier.
            session_data: Dict describing the session to review.
            user_context: Dict with historical context.

        Returns:
            SessionReviewResponse with review, strengths, and improvements.
        """
        template = get_session_review_prompt()
        prompt = template.format(
            session_data=json.dumps(session_data, indent=2),
            user_context=json.dumps(user_context, indent=2),
        )

        result = self.client.generate(
            prompt=prompt,
            user_id=user_id,
            insight_type="session_review",
            ttl_seconds=self.settings.coaching_cache_ttl,
        )

        return SessionReviewResponse(
            user_id=user_id,
            session_id=session_data.get("session_id"),
            review=result.get("review", ""),
            strengths=result.get("strengths", []),
            improvements=result.get("improvements", []),
            score_analysis=result.get("score_analysis"),
            generated_at=datetime.now(timezone.utc).isoformat(),
            cached=False,
        )

    def generate_daily_briefing(
        self, user_id: str, user_context: dict, goals: list = None
    ) -> DailyBriefingResponse:
        """Generate a daily briefing for the user.

        Args:
            user_id: User identifier.
            user_context: Dict with historical context.
            goals: Optional list of user goals.

        Returns:
            DailyBriefingResponse with greeting, plan, and motivation.
        """
        template = get_daily_briefing_prompt()
        prompt = template.format(
            user_context=json.dumps(user_context, indent=2),
            yesterday_data=json.dumps(
                user_context.get("recent_sessions", [])[:3], indent=2
            ),
            goals=json.dumps(goals or ["Improve focus consistency"], indent=2),
        )

        result = self.client.generate(
            prompt=prompt,
            user_id=user_id,
            insight_type="daily_briefing",
            ttl_seconds=self.settings.briefing_cache_ttl,
        )

        return DailyBriefingResponse(
            user_id=user_id,
            greeting=result.get("greeting", ""),
            focus_plan=result.get("focus_plan", []),
            yesterday_summary=result.get("yesterday_summary"),
            motivation=result.get("motivation", ""),
            generated_at=datetime.now(timezone.utc).isoformat(),
            cached=False,
        )
