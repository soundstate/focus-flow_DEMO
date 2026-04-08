"""Analytics ORM models and Pydantic response schemas."""

from sqlalchemy import Column, String, Integer, Float, DateTime, Date, JSON
from pydantic import BaseModel
from datetime import datetime, date, timezone
from typing import Optional

from analytics.database.connection import Base


def _utcnow():
    """Return timezone-aware UTC now."""
    return datetime.now(timezone.utc)


class DailyAggregate(Base):
    """Pre-computed daily metrics per user."""
    __tablename__ = "an_daily_aggregates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    date = Column(Date, nullable=False)
    total_sessions = Column(Integer, default=0)
    total_focus_minutes = Column(Integer, default=0)
    avg_productivity_score = Column(Float, default=0.0)
    total_xp_earned = Column(Integer, default=0)
    total_interruptions = Column(Integer, default=0)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)


class WeeklyAggregate(Base):
    """Pre-computed weekly metrics per user."""
    __tablename__ = "an_weekly_aggregates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    week_start = Column(Date, nullable=False)
    total_sessions = Column(Integer, default=0)
    total_focus_minutes = Column(Integer, default=0)
    avg_productivity_score = Column(Float, default=0.0)
    total_xp_earned = Column(Integer, default=0)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)


class CorrelationCache(Base):
    """Cached correlation analysis results."""
    __tablename__ = "an_correlation_cache"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    correlation_type = Column(String, nullable=False)
    result = Column(JSON, nullable=True)
    computed_at = Column(DateTime, default=_utcnow)


class DashboardMetrics(BaseModel):
    """Pydantic model for dashboard API response."""
    user_id: str
    today_sessions: int = 0
    today_focus_minutes: int = 0
    today_xp: int = 0
    weekly_sessions: int = 0
    weekly_focus_minutes: int = 0
    weekly_xp: int = 0
    avg_productivity: float = 0.0
    current_level: Optional[int] = None
    current_streak: Optional[int] = None


class PeriodSummary(BaseModel):
    """Pydantic model for period summary response."""
    user_id: str
    period: str
    total_sessions: int = 0
    total_focus_minutes: int = 0
    avg_productivity_score: float = 0.0
    total_xp_earned: int = 0
    start_date: Optional[date] = None
    end_date: Optional[date] = None
