"""Metrics router for the Analytics service API."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from analytics.database.connection import get_db
from analytics.services.metrics_calculator import MetricsCalculator

router = APIRouter()


@router.get("/users/{user_id}/dashboard")
async def get_dashboard(user_id: str, db: Session = Depends(get_db)):
    """Get dashboard metrics for a user, including live game engine data."""
    calc = MetricsCalculator(db)
    return await calc.get_dashboard(user_id)


@router.get("/users/{user_id}/summary")
def get_summary(user_id: str, period: str = "weekly", db: Session = Depends(get_db)):
    """Get period summary for a user.

    Query params:
        period: 'daily', 'weekly', or 'monthly' (default: 'weekly')
    """
    calc = MetricsCalculator(db)
    return calc.get_period_summary(user_id, period)
