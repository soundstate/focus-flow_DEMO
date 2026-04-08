"""Export service for the Analytics service."""
import csv
import io
import json
import logging
from datetime import date, timedelta

from sqlalchemy.orm import Session

from analytics.models.metrics_models import DailyAggregate

logger = logging.getLogger(__name__)


class ExportService:
    """Exports analytics data in CSV or JSON format."""

    def __init__(self, db: Session):
        self.db = db

    def export(self, user_id: str, format: str = "json", days: int = 30) -> str:
        """Export daily aggregates for a user.

        Args:
            user_id: The user identifier.
            format: 'csv' or 'json'.
            days: Number of days to include (default 30).

        Returns:
            Formatted string (CSV or JSON).
        """
        end = date.today()
        start = end - timedelta(days=days)

        rows = (
            self.db.query(DailyAggregate)
            .filter(
                DailyAggregate.user_id == user_id,
                DailyAggregate.date >= start,
                DailyAggregate.date <= end,
            )
            .order_by(DailyAggregate.date.asc())
            .all()
        )

        records = [
            {
                "date": str(r.date),
                "total_sessions": r.total_sessions,
                "total_focus_minutes": r.total_focus_minutes,
                "avg_productivity_score": r.avg_productivity_score,
                "total_xp_earned": r.total_xp_earned,
                "total_interruptions": r.total_interruptions,
            }
            for r in rows
        ]

        if format == "csv":
            return self._to_csv(records)
        return json.dumps(records, indent=2)

    def _to_csv(self, records: list) -> str:
        """Convert records to CSV string."""
        if not records:
            return ""

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
        return output.getvalue()
