"""Tests for streak calculator."""
from datetime import date, timedelta
from game_engine.calculators.streak_calculator import StreakCalculator


def test_first_session_starts_streak():
    result = StreakCalculator.update_streak(last_session_date=None, current_streak=0)
    assert result["new_streak"] == 1
    assert result["is_broken"] is False


def test_same_day_keeps_streak():
    result = StreakCalculator.update_streak(
        last_session_date=date.today(), current_streak=5
    )
    assert result["new_streak"] == 5


def test_next_day_increments():
    result = StreakCalculator.update_streak(
        last_session_date=date.today() - timedelta(days=1), current_streak=5
    )
    assert result["new_streak"] == 6


def test_missed_days_breaks_streak():
    result = StreakCalculator.update_streak(
        last_session_date=date.today() - timedelta(days=3), current_streak=10
    )
    assert result["new_streak"] == 1
    assert result["is_broken"] is True


def test_milestone_detection():
    result = StreakCalculator.update_streak(
        last_session_date=date.today() - timedelta(days=1), current_streak=6
    )
    assert result["is_milestone"] is True
    assert result["milestone_type"] == "7_day"


def test_no_milestone_at_non_milestone():
    result = StreakCalculator.update_streak(
        last_session_date=date.today() - timedelta(days=1), current_streak=4
    )
    assert result["is_milestone"] is False
