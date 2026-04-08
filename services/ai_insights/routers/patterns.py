"""Patterns router for the AI Insights service API."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ai_insights.database.connection import get_db
from ai_insights.services.session_analyzer import SessionAnalyzer
from ai_insights.services.pattern_discoverer import PatternDiscoverer
from ai_insights.services.correlation_engine import CorrelationEngine
from ai_insights.models.pattern_models import PatternResponse

router = APIRouter()


@router.get("/users/{user_id}/discover", response_model=PatternResponse)
async def discover_patterns(user_id: str, db: Session = Depends(get_db)):
    """Discover productivity patterns for a user using AI analysis."""
    analyzer = SessionAnalyzer()
    user_context = await analyzer.get_user_context(user_id)

    discoverer = PatternDiscoverer(db)
    return discoverer.discover(user_id, user_context)


@router.get("/users/{user_id}/interpreted-correlations")
async def get_interpreted_correlations(user_id: str, db: Session = Depends(get_db)):
    """Get AI-interpreted correlations for a user."""
    engine = CorrelationEngine(db)
    correlations = await engine.get_correlations(user_id)
    return engine.interpret_correlations(user_id, correlations)
