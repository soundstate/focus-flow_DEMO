"""OpenAI API client with caching and graceful fallback."""

import hashlib
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from ai_insights.config.ai_settings import get_settings
from ai_insights.models.insights_models import InsightCache, TokenUsage

logger = logging.getLogger(__name__)


# Default fallback responses when API key is missing
FALLBACK_RESPONSES = {
    "coaching": {
        "tips": [
            {
                "category": "focus",
                "tip": "Try the Pomodoro technique: 25 minutes of focused work followed by a 5-minute break.",
                "priority": "high",
            },
            {
                "category": "breaks",
                "tip": "Stand up and stretch every hour to maintain energy levels.",
                "priority": "medium",
            },
            {
                "category": "habits",
                "tip": "Start your day with your most challenging task when willpower is highest.",
                "priority": "medium",
            },
        ],
        "summary": "Keep building consistent focus habits. Small improvements compound over time.",
    },
    "session_review": {
        "review": "Your session showed solid focus. Continue building on this momentum.",
        "strengths": ["Completed a full focus session", "Maintained consistent effort"],
        "improvements": ["Try to minimize context switching", "Consider longer sessions as stamina builds"],
        "score_analysis": "Your productivity score is on track. Consistency is key.",
    },
    "daily_briefing": {
        "greeting": "Good day! Ready to make progress on your goals.",
        "focus_plan": [
            "Start with a 25-minute deep work session",
            "Take a short break, then do another focused block",
            "Review your progress in the afternoon",
        ],
        "yesterday_summary": "You made progress yesterday. Let's build on that momentum.",
        "motivation": "Every focused session brings you closer to your goals. You've got this!",
    },
    "pattern_discovery": {
        "patterns": [
            {
                "pattern_type": "peak_hours",
                "description": "Morning sessions tend to be most productive based on general research.",
                "confidence": 0.5,
                "data": {"suggested_peak": "9:00-11:00 AM"},
            }
        ],
        "interpretation": "More session data will help identify your personal productivity patterns.",
    },
}


def _hash_prompt(prompt: str) -> str:
    """Generate a deterministic hash for a prompt string."""
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:32]


class OpenAIClient:
    """Client for OpenAI API with DB-backed caching and token tracking."""

    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def _get_cached(self, prompt_hash: str) -> Optional[dict]:
        """Check for a cached response that hasn't expired."""
        now = datetime.now(timezone.utc)
        cached = (
            self.db.query(InsightCache)
            .filter(
                InsightCache.prompt_hash == prompt_hash,
                InsightCache.expires_at > now,
            )
            .order_by(InsightCache.created_at.desc())
            .first()
        )
        if cached and cached.response_data:
            return cached.response_data
        return None

    def _store_cache(
        self,
        user_id: str,
        prompt_hash: str,
        insight_type: str,
        response_data: dict,
        model: str,
        ttl_seconds: int,
    ) -> None:
        """Store a response in the cache."""
        now = datetime.now(timezone.utc)
        record = InsightCache(
            user_id=user_id,
            prompt_hash=prompt_hash,
            insight_type=insight_type,
            response_data=response_data,
            model_used=model,
            created_at=now,
            expires_at=now + timedelta(seconds=ttl_seconds),
        )
        self.db.add(record)
        self.db.commit()

    def _track_tokens(
        self,
        user_id: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        insight_type: str,
    ) -> None:
        """Record token usage for cost monitoring."""
        record = TokenUsage(
            user_id=user_id,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            insight_type=insight_type,
        )
        self.db.add(record)
        self.db.commit()

    def generate(
        self,
        prompt: str,
        user_id: str,
        insight_type: str,
        ttl_seconds: int = 14400,
        use_advanced_model: bool = False,
    ) -> dict:
        """Generate an AI response, checking cache first.

        Args:
            prompt: The formatted prompt to send to OpenAI.
            user_id: User identifier for caching and tracking.
            insight_type: Type of insight (coaching, session_review, etc.).
            ttl_seconds: Cache time-to-live in seconds.
            use_advanced_model: Use the advanced model (gpt-4o) instead of mini.

        Returns:
            Parsed JSON response dict.
        """
        prompt_hash = _hash_prompt(prompt)

        # Check cache first
        cached = self._get_cached(prompt_hash)
        if cached is not None:
            logger.info("Cache hit for %s (hash=%s)", insight_type, prompt_hash[:8])
            return cached

        # If no API key, return fallback
        if not self.settings.openai_api_key:
            logger.warning(
                "No OpenAI API key configured -- returning fallback for %s",
                insight_type,
            )
            fallback = FALLBACK_RESPONSES.get(insight_type, {"message": "No API key configured"})
            self._store_cache(user_id, prompt_hash, insight_type, fallback, "fallback", ttl_seconds)
            return fallback

        # Call OpenAI
        model = (
            self.settings.openai_model_advanced
            if use_advanced_model
            else self.settings.openai_model
        )

        try:
            import openai

            client = openai.OpenAI(api_key=self.settings.openai_api_key)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a productivity coaching AI. Always respond with valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1000,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            result = json.loads(content)

            # Track token usage
            usage = response.usage
            if usage:
                self._track_tokens(
                    user_id=user_id,
                    model=model,
                    prompt_tokens=usage.prompt_tokens,
                    completion_tokens=usage.completion_tokens,
                    insight_type=insight_type,
                )

            # Cache the result
            self._store_cache(user_id, prompt_hash, insight_type, result, model, ttl_seconds)

            logger.info("Generated %s for user %s using %s", insight_type, user_id, model)
            return result

        except Exception as exc:
            logger.error("OpenAI API error for %s: %s", insight_type, exc)
            fallback = FALLBACK_RESPONSES.get(insight_type, {"error": str(exc)})
            return fallback
