"""Insights router for the AI Insights service API."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ai_insights.database.connection import get_db
from ai_insights.services.session_analyzer import SessionAnalyzer
from ai_insights.services.coaching_generator import CoachingGenerator
from ai_insights.models.insights_models import (
    CoachingResponse,
    DailyBriefingResponse,
    SessionReviewResponse,
)

router = APIRouter()


@router.get("/users/{user_id}/coaching", response_model=CoachingResponse)
async def get_coaching(user_id: str, db: Session = Depends(get_db)):
    """Get personalised coaching tips for a user."""
    analyzer = SessionAnalyzer()
    user_context = await analyzer.get_user_context(user_id)

    generator = CoachingGenerator(db)
    return generator.generate_coaching(user_id, user_context)


@router.get("/users/{user_id}/daily-briefing", response_model=DailyBriefingResponse)
async def get_daily_briefing(user_id: str, db: Session = Depends(get_db)):
    """Get a daily briefing for a user."""
    analyzer = SessionAnalyzer()
    user_context = await analyzer.get_user_context(user_id)

    generator = CoachingGenerator(db)
    return generator.generate_daily_briefing(user_id, user_context)


@router.post("/users/{user_id}/session-review", response_model=SessionReviewResponse)
async def create_session_review(
    user_id: str, session_data: dict, db: Session = Depends(get_db)
):
    """Generate a review for a completed focus session."""
    analyzer = SessionAnalyzer()
    user_context = await analyzer.get_user_context(user_id)

    generator = CoachingGenerator(db)
    return generator.generate_session_review(user_id, session_data, user_context)
