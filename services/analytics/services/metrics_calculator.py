"""Metrics calculation service for the Analytics service."""
import logging
from datetime import date, timedelta
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from analytics.models.metrics_models import (
    DailyAggregate,
    WeeklyAggregate,
    DashboardMetrics,
    PeriodSummary,
)
from analytics.clients.game_engine_client import GameEngineClient

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Calculates and retrieves analytics metrics for users."""

    def __init__(self, db: Session):
        self.db = db

    async def get_dashboard(self, user_id: str) -> DashboardMetrics:
        """Build dashboard metrics from aggregates and live game engine data.

        Args:
            user_id: The user identifier.

        Returns:
            DashboardMetrics populated with today/weekly stats and game data.
        """
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        # today's aggregate
        today_agg = (
            self.db.query(DailyAggregate)
            .filter_by(user_id=user_id, date=today)
            .first()
        )

        # weekly aggregates
        weekly_rows = (
            self.db.query(DailyAggregate)
            .filter(
                DailyAggregate.user_id == user_id,
                DailyAggregate.date >= week_start,
                DailyAggregate.date <= today,
            )
            .all()
        )

        weekly_sessions = sum(r.total_sessions for r in weekly_rows)
        weekly_minutes = sum(r.total_focus_minutes for r in weekly_rows)
        weekly_xp = sum(r.total_xp_earned for r in weekly_rows)
        weekly_scores = [r.avg_productivity_score for r in weekly_rows if r.avg_productivity_score]
        avg_prod = sum(weekly_scores) / len(weekly_scores) if weekly_scores else 0.0

        # live game engine data
        game_client = GameEngineClient()
        level_data = await game_client.get_user_level(user_id)
        streak_data = await game_client.get_user_streak(user_id)

        return DashboardMetrics(
            user_id=user_id,
            today_sessions=today_agg.total_sessions if today_agg else 0,
            today_focus_minutes=today_agg.total_focus_minutes if today_agg else 0,
            today_xp=today_agg.total_xp_earned if today_agg else 0,
            weekly_sessions=weekly_sessions,
            weekly_focus_minutes=weekly_minutes,
            weekly_xp=weekly_xp,
            avg_productivity=round(avg_prod, 2),
            current_level=level_data.get("current_level") if level_data else None,
            current_streak=streak_data.get("current_streak") if streak_data else None,
        )

    def get_period_summary(self, user_id: str, period: str) -> PeriodSummary:
        """Return aggregated summary for a given period.

        Args:
            user_id: The user identifier.
            period: One of 'daily', 'weekly', 'monthly'.

        Returns:
            PeriodSummary with totals for the requested period.
        """
        today = date.today()

        if period == "daily":
            start = today
            end = today
        elif period == "weekly":
            start = today - timedelta(days=today.weekday())
            end = today
        elif period == "monthly":
            start = today.replace(day=1)
            end = today
        else:
            start = today
            end = today

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
        avg_score = sum(scores) / len(scores) if scores else 0.0

        return PeriodSummary(
            user_id=user_id,
            period=period,
            total_sessions=total_sessions,
            total_focus_minutes=total_minutes,
            avg_productivity_score=round(avg_score, 2),
            total_xp_earned=total_xp,
            start_date=start,
            end_date=end,
        )

    def update_daily_aggregate(self, user_id: str, session_data: dict) -> DailyAggregate:
        """Create or update today's daily aggregate for a user.

        Args:
            user_id: The user identifier.
            session_data: Dict with keys like duration, productivity_score,
                          xp_earned, interruptions.

        Returns:
            The updated DailyAggregate record.
        """
        today = date.today()
        agg = (
            self.db.query(DailyAggregate)
            .filter_by(user_id=user_id, date=today)
            .first()
        )

        duration = session_data.get("duration", 25)
        productivity = session_data.get("productivity_score", 0.0)
        xp = session_data.get("xp_earned", 0)
        interruptions = session_data.get("interruptions", 0)

        if agg is None:
            agg = DailyAggregate(
                user_id=user_id,
                date=today,
                total_sessions=1,
                total_focus_minutes=duration,
                avg_productivity_score=productivity,
                total_xp_earned=xp,
                total_interruptions=interruptions,
            )
            self.db.add(agg)
        else:
            # incremental update with running average for productivity
            prev_total = agg.avg_productivity_score * agg.total_sessions
            agg.total_sessions += 1
            agg.total_focus_minutes += duration
            agg.avg_productivity_score = round(
                (prev_total + productivity) / agg.total_sessions, 2
            )
            agg.total_xp_earned += xp
            agg.total_interruptions += interruptions

        self.db.commit()
        self.db.refresh(agg)
        return agg
