"""Trend analysis service for the Analytics service."""
import logging
from datetime import date, timedelta
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from analytics.models.metrics_models import DailyAggregate

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """Analyzes trends and comparisons across time periods."""

    def __init__(self, db: Session):
        self.db = db

    def weekly_comparison(self, user_id: str) -> dict:
        """Compare this week vs last week.

        Returns:
            Dict with this_week, last_week, and change fields.
        """
        today = date.today()
        this_week_start = today - timedelta(days=today.weekday())
        last_week_start = this_week_start - timedelta(days=7)
        last_week_end = this_week_start - timedelta(days=1)

        this_week = self._sum_period(user_id, this_week_start, today)
        last_week = self._sum_period(user_id, last_week_start, last_week_end)

        return {
            "this_week": this_week,
            "last_week": last_week,
            "change": {
                "sessions": this_week["total_sessions"] - last_week["total_sessions"],
                "focus_minutes": this_week["total_focus_minutes"] - last_week["total_focus_minutes"],
                "xp": this_week["total_xp_earned"] - last_week["total_xp_earned"],
            },
        }

    def monthly_comparison(self, user_id: str) -> dict:
        """Compare this month vs last month.

        Returns:
            Dict with this_month, last_month, and change fields.
        """
        today = date.today()
        this_month_start = today.replace(day=1)

        # last month boundaries
        last_month_end = this_month_start - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)

        this_month = self._sum_period(user_id, this_month_start, today)
        last_month = self._sum_period(user_id, last_month_start, last_month_end)

        return {
            "this_month": this_month,
            "last_month": last_month,
            "change": {
                "sessions": this_month["total_sessions"] - last_month["total_sessions"],
                "focus_minutes": this_month["total_focus_minutes"] - last_month["total_focus_minutes"],
                "xp": this_month["total_xp_earned"] - last_month["total_xp_earned"],
            },
        }

    def compare_periods(
        self,
        user_id: str,
        start1: date,
        end1: date,
        start2: date,
        end2: date,
    ) -> dict:
        """Compare two arbitrary date ranges.

        Args:
            user_id: The user identifier.
            start1/end1: First period boundaries.
            start2/end2: Second period boundaries.

        Returns:
            Dict with period_1, period_2, and change fields.
        """
        period1 = self._sum_period(user_id, start1, end1)
        period2 = self._sum_period(user_id, start2, end2)

        return {
            "period_1": period1,
            "period_2": period2,
            "change": {
                "sessions": period2["total_sessions"] - period1["total_sessions"],
                "focus_minutes": period2["total_focus_minutes"] - period1["total_focus_minutes"],
                "xp": period2["total_xp_earned"] - period1["total_xp_earned"],
            },
        }

    def productivity_curve(self, user_id: str) -> list:
        """Return productivity data points over time (placeholder).

        Returns:
            Empty list -- to be implemented with real time-series data.
        """
        return []

    def _sum_period(self, user_id: str, start: date, end: date) -> dict:
        """Sum daily aggregates over a date range.

        Args:
            user_id: The user identifier.
            start: Start date (inclusive).
            end: End date (inclusive).

        Returns:
            Dict with total_sessions, total_focus_minutes, avg_productivity_score,
            total_xp_earned.
        """
        rows = (
            self.db.query(DailyAggregate)
            .filter(
                DailyAggregate.user_id == user_id,
                DailyAggregate.date >= start,
                DailyAggregate.date <= end,
            )
            .all()
        )

        total_sessions = sum(r.total_sessions for r in rows)
        total_minutes = sum(r.total_focus_minutes for r in rows)
        total_xp = sum(r.total_xp_earned for r in rows)
        scores = [r.avg_productivity_score for r in rows if r.avg_productivity_score]
        avg_score = round(sum(scores) / len(scores), 2) if scores else 0.0

        return {
            "total_sessions": total_sessions,
            "total_focus_minutes": total_minutes,
            "avg_productivity_score": avg_score,
            "total_xp_earned": total_xp,
        }
