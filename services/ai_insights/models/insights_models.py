"""AI Insights ORM models and Pydantic response schemas."""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional, List

from ai_insights.database.connection import Base


def _utcnow():
    """Return timezone-aware UTC now."""
    return datetime.now(timezone.utc)


class InsightCache(Base):
    """Cached AI-generated insight results to reduce API costs."""
    __tablename__ = "ai_insight_cache"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    prompt_hash = Column(String, index=True, nullable=False)
    insight_type = Column(String, nullable=False)  # coaching, session_review, daily_briefing
    response_data = Column(JSON, nullable=True)
    model_used = Column(String, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    expires_at = Column(DateTime, nullable=True)


class TokenUsage(Base):
    """Track OpenAI token usage for cost monitoring."""
    __tablename__ = "ai_token_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    model = Column(String, nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    insight_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=_utcnow)


# --- Pydantic response models ---

class CoachingTip(BaseModel):
    """Individual coaching tip."""
    category: str
    tip: str
    priority: str = "medium"


class CoachingResponse(BaseModel):
    """Response model for coaching endpoint."""
    user_id: str
    tips: List[CoachingTip] = []
    summary: str = ""
    generated_at: Optional[str] = None
    cached: bool = False


class SessionReviewResponse(BaseModel):
    """Response model for session review endpoint."""
    user_id: str
    session_id: Optional[str] = None
    review: str = ""
    strengths: List[str] = []
    improvements: List[str] = []
    score_analysis: Optional[str] = None
    generated_at: Optional[str] = None
    cached: bool = False


class DailyBriefingResponse(BaseModel):
    """Response model for daily briefing endpoint."""
    user_id: str
    greeting: str = ""
    focus_plan: List[str] = []
    yesterday_summary: Optional[str] = None
    motivation: str = ""
    generated_at: Optional[str] = None
    cached: bool = False
