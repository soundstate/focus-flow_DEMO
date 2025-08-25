"""
Analytics Router
Endpoints for analytics, trends, and insights
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..database.connection import get_db
from ..services.analytics_service import SessionAnalytics, ProductivityInsights
from ..services.focus_scoring_service import FocusQualityScorer

router = APIRouter()

@router.get("/users/{user_id}/stats")
def get_user_stats(user_id: str, days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    """Get comprehensive user statistics for a period"""
    return SessionAnalytics.calculate_user_stats(db, user_id, days)

@router.get("/users/{user_id}/trends/daily")
def get_daily_trends(user_id: str, days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    """Get daily productivity trends"""
    return SessionAnalytics.calculate_daily_trends(db, user_id, days)

@router.get("/users/{user_id}/patterns/hourly")
def get_hourly_patterns(user_id: str, days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    """Get hourly productivity patterns"""
    return SessionAnalytics.calculate_hourly_patterns(db, user_id, days)

@router.get("/users/{user_id}/performance/types")
def get_session_type_performance(user_id: str, days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    """Get performance breakdown by session type"""
    return SessionAnalytics.calculate_session_type_performance(db, user_id, days)

@router.get("/users/{user_id}/quality/insights")
def get_quality_insights(user_id: str, days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    """Get focus quality insights and recommendations"""
    return FocusQualityScorer.get_quality_insights(db, user_id, days)

@router.get("/users/{user_id}/insights")
def get_productivity_insights(user_id: str, days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    """Get comprehensive productivity insights including recommendations"""
    return ProductivityInsights.generate_insights(db, user_id, days)
