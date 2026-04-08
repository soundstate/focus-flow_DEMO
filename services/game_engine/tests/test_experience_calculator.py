"""Tests for experience point calculator."""
from game_engine.calculators.experience_calculator import ExperienceCalculator


def test_base_xp_for_completed_session():
    result = ExperienceCalculator.calculate(
        session_duration=25,
        session_completed=True,
        productivity_score=5.0,
        current_streak=0,
    )
    assert result["base_xp"] == 50
    assert result["total_xp"] >= 50


def test_completion_bonus():
    completed = ExperienceCalculator.calculate(
        session_duration=25,
        session_completed=True,
        productivity_score=5.0,
        current_streak=0,
    )
    abandoned = ExperienceCalculator.calculate(
        session_duration=25,
        session_completed=False,
        productivity_score=5.0,
        current_streak=0,
    )
    assert completed["total_xp"] > abandoned["total_xp"]


def test_streak_multiplier():
    no_streak = ExperienceCalculator.calculate(
        session_duration=25,
        session_completed=True,
        productivity_score=5.0,
        current_streak=0,
    )
    with_streak = ExperienceCalculator.calculate(
        session_duration=25,
        session_completed=True,
        productivity_score=5.0,
        current_streak=7,
    )
    assert with_streak["total_xp"] > no_streak["total_xp"]


def test_productivity_bonus():
    low = ExperienceCalculator.calculate(
        session_duration=25,
        session_completed=True,
        productivity_score=2.0,
        current_streak=0,
    )
    high = ExperienceCalculator.calculate(
        session_duration=25,
        session_completed=True,
        productivity_score=9.0,
        current_streak=0,
    )
    assert high["total_xp"] > low["total_xp"]


def test_longer_sessions_earn_more():
    short = ExperienceCalculator.calculate(
        session_duration=15,
        session_completed=True,
        productivity_score=5.0,
        current_streak=0,
    )
    long = ExperienceCalculator.calculate(
        session_duration=50,
        session_completed=True,
        productivity_score=5.0,
        current_streak=0,
    )
    assert long["base_xp"] > short["base_xp"]


def test_result_keys():
    result = ExperienceCalculator.calculate(
        session_duration=25,
        session_completed=True,
        productivity_score=5.0,
        current_streak=0,
    )
    assert all(
        k in result
        for k in ["base_xp", "bonus_xp", "total_xp", "reason", "multipliers_applied"]
    )
