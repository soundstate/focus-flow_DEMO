"""Export router for the Analytics service API."""
from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from analytics.database.connection import get_db
from analytics.services.export_service import ExportService

router = APIRouter()


@router.get("/users/{user_id}")
def export_data(
    user_id: str,
    format: str = "json",
    days: int = 30,
    db: Session = Depends(get_db),
):
    """Export daily aggregates for a user.

    Query params:
        format: 'csv' or 'json' (default: 'json')
        days: Number of days to include (default: 30)
    """
    svc = ExportService(db)
    result = svc.export(user_id, format=format, days=days)

    if format == "csv":
        return PlainTextResponse(content=result, media_type="text/csv")
    return PlainTextResponse(content=result, media_type="application/json")
