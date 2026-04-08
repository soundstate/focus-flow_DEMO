"""Correlations router for the Analytics service API."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from analytics.database.connection import get_db
from analytics.models.metrics_models import CorrelationCache

router = APIRouter()


@router.get("/users/{user_id}")
def get_correlations(user_id: str, db: Session = Depends(get_db)):
    """Get cached correlation analysis results for a user."""
    rows = (
        db.query(CorrelationCache)
        .filter_by(user_id=user_id)
        .order_by(CorrelationCache.computed_at.desc())
        .all()
    )

    return [
        {
            "correlation_type": r.correlation_type,
            "result": r.result,
            "computed_at": r.computed_at.isoformat() if r.computed_at else None,
        }
        for r in rows
    ]
