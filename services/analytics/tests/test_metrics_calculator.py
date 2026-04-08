"""Tests for MetricsCalculator service."""
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from analytics.database.connection import Base
from analytics.models.metrics_models import DailyAggregate
from analytics.services.metrics_calculator import MetricsCalculator


def _make_db():
    """Create a fresh in-memory SQLite session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_update_daily_aggregate_creates_new():
    """First session of the day creates a new aggregate record."""
    db = _make_db()
    calc = MetricsCalculator(db)

    session_data = {
        "duration": 25,
        "productivity_score": 0.8,
        "xp_earned": 100,
        "interruptions": 1,
    }
    agg = calc.update_daily_aggregate("user_1", session_data)

    assert agg.id is not None
    assert agg.user_id == "user_1"
    assert agg.date == date.today()
    assert agg.total_sessions == 1
    assert agg.total_focus_minutes == 25
    assert agg.avg_productivity_score == 0.8
    assert agg.total_xp_earned == 100
    assert agg.total_interruptions == 1
    db.close()


def test_update_daily_aggregate_increments_existing():
    """Subsequent sessions increment the existing aggregate."""
    db = _make_db()
    calc = MetricsCalculator(db)

    # first session
    calc.update_daily_aggregate("user_1", {
        "duration": 25,
        "productivity_score": 0.8,
        "xp_earned": 100,
        "interruptions": 1,
    })

    # second session
    agg = calc.update_daily_aggregate("user_1", {
        "duration": 50,
        "productivity_score": 0.6,
        "xp_earned": 200,
        "interruptions": 3,
    })

    assert agg.total_sessions == 2
    assert agg.total_focus_minutes == 75  # 25 + 50
    assert agg.total_xp_earned == 300    # 100 + 200
    assert agg.total_interruptions == 4  # 1 + 3
    # running average: (0.8 + 0.6) / 2 = 0.7
    assert agg.avg_productivity_score == 0.7
    db.close()


def test_update_daily_aggregate_separate_users():
    """Different users get separate aggregate records."""
    db = _make_db()
    calc = MetricsCalculator(db)

    calc.update_daily_aggregate("user_1", {
        "duration": 25,
        "productivity_score": 0.9,
        "xp_earned": 100,
    })
    calc.update_daily_aggregate("user_2", {
        "duration": 50,
        "productivity_score": 0.5,
        "xp_earned": 200,
    })

    rows = db.query(DailyAggregate).all()
    assert len(rows) == 2

    u1 = db.query(DailyAggregate).filter_by(user_id="user_1").first()
    u2 = db.query(DailyAggregate).filter_by(user_id="user_2").first()
    assert u1.total_focus_minutes == 25
    assert u2.total_focus_minutes == 50
    db.close()


def test_get_period_summary_daily():
    """Period summary for 'daily' returns today's data."""
    db = _make_db()
    calc = MetricsCalculator(db)

    calc.update_daily_aggregate("user_1", {
        "duration": 25,
        "productivity_score": 0.85,
        "xp_earned": 100,
    })

    summary = calc.get_period_summary("user_1", "daily")
    assert summary.user_id == "user_1"
    assert summary.period == "daily"
    assert summary.total_sessions == 1
    assert summary.total_focus_minutes == 25
    assert summary.total_xp_earned == 100
    db.close()


def test_get_period_summary_empty():
    """Period summary for a user with no data returns zeros."""
    db = _make_db()
    calc = MetricsCalculator(db)

    summary = calc.get_period_summary("nonexistent_user", "weekly")
    assert summary.total_sessions == 0
    assert summary.total_focus_minutes == 0
    assert summary.total_xp_earned == 0
    db.close()
