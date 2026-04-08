"""Tests for AI Insights ORM models."""
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ai_insights.database.connection import Base
from ai_insights.models.insights_models import (
    InsightCache,
    TokenUsage,
    CoachingResponse,
    DailyBriefingResponse,
    SessionReviewResponse,
)
from ai_insights.models.pattern_models import (
    UserPattern,
    PatternResponse,
)


def test_insight_cache_table_name():
    assert InsightCache.__tablename__ == "ai_insight_cache"


def test_token_usage_table_name():
    assert TokenUsage.__tablename__ == "ai_token_usage"


def test_user_pattern_table_name():
    assert UserPattern.__tablename__ == "ai_user_patterns"


def test_insight_cache_create():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    record = InsightCache(
        user_id="user_1",
        prompt_hash="abc123hash",
        insight_type="coaching",
        response_data={"tips": ["Take a break"]},
        model_used="gpt-4o-mini",
    )
    db.add(record)
    db.commit()
    assert record.id is not None
    assert record.user_id == "user_1"
    assert record.insight_type == "coaching"
    assert record.response_data == {"tips": ["Take a break"]}
    db.close()


def test_token_usage_create():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    record = TokenUsage(
        user_id="user_1",
        model="gpt-4o-mini",
        prompt_tokens=150,
        completion_tokens=200,
        total_tokens=350,
        insight_type="coaching",
    )
    db.add(record)
    db.commit()
    assert record.id is not None
    assert record.total_tokens == 350
    assert record.model == "gpt-4o-mini"
    db.close()


def test_user_pattern_create():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    record = UserPattern(
        user_id="user_1",
        pattern_type="peak_hours",
        pattern_data={"best_hours": [9, 10, 14, 15]},
        confidence=0.85,
    )
    db.add(record)
    db.commit()
    assert record.id is not None
    assert record.pattern_type == "peak_hours"
    assert record.confidence == 0.85
    db.close()


def test_insight_cache_query_by_prompt_hash():
    """Test that we can look up cached insights by prompt hash."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    # Insert two records with different hashes
    db.add(InsightCache(
        user_id="user_1",
        prompt_hash="hash_aaa",
        insight_type="coaching",
        response_data={"tips": ["First"]},
        model_used="gpt-4o-mini",
    ))
    db.add(InsightCache(
        user_id="user_1",
        prompt_hash="hash_bbb",
        insight_type="daily_briefing",
        response_data={"greeting": "Good morning"},
        model_used="gpt-4o-mini",
    ))
    db.commit()

    # Query by hash
    cached = db.query(InsightCache).filter_by(prompt_hash="hash_aaa").first()
    assert cached is not None
    assert cached.insight_type == "coaching"
    assert cached.response_data == {"tips": ["First"]}

    # Query non-existent hash
    miss = db.query(InsightCache).filter_by(prompt_hash="hash_zzz").first()
    assert miss is None
    db.close()


def test_coaching_response_pydantic():
    response = CoachingResponse(
        user_id="user_1",
        tips=[{"category": "focus", "tip": "Use pomodoro", "priority": "high"}],
        summary="You're doing great",
        generated_at="2026-04-08T10:00:00Z",
        cached=False,
    )
    assert response.user_id == "user_1"
    assert len(response.tips) == 1
    assert response.tips[0].category == "focus"


def test_daily_briefing_response_pydantic():
    response = DailyBriefingResponse(
        user_id="user_1",
        greeting="Good morning!",
        focus_plan=["Deep work 9-11am", "Review at 2pm"],
        motivation="You've been on a 5-day streak!",
    )
    assert response.user_id == "user_1"
    assert len(response.focus_plan) == 2


def test_session_review_response_pydantic():
    response = SessionReviewResponse(
        user_id="user_1",
        session_id="sess_123",
        review="Good session with minimal distractions",
        strengths=["Good focus duration"],
        improvements=["Try fewer tab switches"],
    )
    assert response.user_id == "user_1"
    assert len(response.strengths) == 1


def test_pattern_response_pydantic():
    response = PatternResponse(
        user_id="user_1",
        patterns=[
            {
                "pattern_type": "peak_hours",
                "description": "Most productive 9-11am",
                "confidence": 0.9,
                "data": {"hours": [9, 10, 11]},
            }
        ],
        interpretation="You work best in the morning",
    )
    assert response.user_id == "user_1"
    assert len(response.patterns) == 1
    assert response.patterns[0].confidence == 0.9
