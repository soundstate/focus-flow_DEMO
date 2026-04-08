"""Trends router for the Analytics service API."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from analytics.database.connection import get_db
from analytics.services.trend_analyzer import TrendAnalyzer

router = APIRouter()


@router.get("/users/{user_id}/weekly")
def get_weekly_comparison(user_id: str, db: Session = Depends(get_db)):
    """Compare this week vs last week for a user."""
    analyzer = TrendAnalyzer(db)
    return analyzer.weekly_comparison(user_id)


@router.get("/users/{user_id}/monthly")
def get_monthly_comparison(user_id: str, db: Session = Depends(get_db)):
    """Compare this month vs last month for a user."""
    analyzer = TrendAnalyzer(db)
    return analyzer.monthly_comparison(user_id)


@router.get("/users/{user_id}/productivity-curve")
def get_productivity_curve(user_id: str, db: Session = Depends(get_db)):
    """Get productivity curve data points for a user."""
    analyzer = TrendAnalyzer(db)
    return analyzer.productivity_curve(user_id)
