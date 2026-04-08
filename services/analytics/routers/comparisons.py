"""Comparisons router for the Analytics service API."""
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from analytics.database.connection import get_db
from analytics.services.trend_analyzer import TrendAnalyzer

router = APIRouter()


@router.get("/users/{user_id}/periods")
def compare_periods(
    user_id: str,
    start1: date = Query(..., description="Start date of first period"),
    end1: date = Query(..., description="End date of first period"),
    start2: date = Query(..., description="Start date of second period"),
    end2: date = Query(..., description="End date of second period"),
    db: Session = Depends(get_db),
):
    """Compare two arbitrary date ranges for a user."""
    analyzer = TrendAnalyzer(db)
    return analyzer.compare_periods(user_id, start1, end1, start2, end2)
