"""Tests for Analytics ORM models."""
from datetime import datetime, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from analytics.database.connection import Base
from analytics.models.metrics_models import (
    DailyAggregate,
    WeeklyAggregate,
    CorrelationCache,
    DashboardMetrics,
    PeriodSummary,
)


def test_daily_aggregate_table_name():
    assert DailyAggregate.__tablename__ == "an_daily_aggregates"


def test_weekly_aggregate_table_name():
    assert WeeklyAggregate.__tablename__ == "an_weekly_aggregates"


def test_correlation_cache_table_name():
    assert CorrelationCache.__tablename__ == "an_correlation_cache"


def test_daily_aggregate_create():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    record = DailyAggregate(
        user_id="user_1",
        date=date.today(),
        total_sessions=3,
        total_focus_minutes=75,
        avg_productivity_score=0.85,
        total_xp_earned=150,
        total_interruptions=2,
    )
    db.add(record)
    db.commit()
    assert record.id is not None
    assert record.total_sessions == 3
    assert record.total_focus_minutes == 75
    db.close()


def test_weekly_aggregate_create():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    record = WeeklyAggregate(
        user_id="user_1",
        week_start=date(2026, 4, 6),
        total_sessions=15,
        total_focus_minutes=375,
        avg_productivity_score=0.82,
        total_xp_earned=750,
    )
    db.add(record)
    db.commit()
    assert record.id is not None
    assert record.total_sessions == 15
    db.close()


def test_correlation_cache_create():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    record = CorrelationCache(
        user_id="user_1",
        correlation_type="session_duration_vs_productivity",
        result={"correlation": 0.72, "p_value": 0.01},
    )
    db.add(record)
    db.commit()
    assert record.id is not None
    assert record.correlation_type == "session_duration_vs_productivity"
    db.close()


def test_dashboard_metrics_pydantic():
    metrics = DashboardMetrics(
        user_id="user_1",
        today_sessions=3,
        today_focus_minutes=75,
        today_xp=150,
        weekly_sessions=15,
        weekly_focus_minutes=375,
        weekly_xp=750,
        avg_productivity=0.85,
        current_level=5,
        current_streak=7,
    )
    assert metrics.user_id == "user_1"
    assert metrics.today_sessions == 3
    assert metrics.current_level == 5


def test_period_summary_pydantic():
    summary = PeriodSummary(
        user_id="user_1",
        period="weekly",
        total_sessions=15,
        total_focus_minutes=375,
        avg_productivity_score=0.82,
        total_xp_earned=750,
        start_date=date(2026, 4, 6),
        end_date=date(2026, 4, 12),
    )
    assert summary.period == "weekly"
    assert summary.total_sessions == 15
