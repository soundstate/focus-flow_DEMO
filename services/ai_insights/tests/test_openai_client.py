"""Tests for OpenAI client caching and fallback behaviour."""

from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ai_insights.database.connection import Base
from ai_insights.models.insights_models import InsightCache, TokenUsage
from ai_insights.clients.openai_client import OpenAIClient, _hash_prompt, FALLBACK_RESPONSES


def _make_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_hash_prompt_deterministic():
    h1 = _hash_prompt("hello world")
    h2 = _hash_prompt("hello world")
    assert h1 == h2
    assert len(h1) == 32


def test_hash_prompt_differs_for_different_input():
    h1 = _hash_prompt("prompt A")
    h2 = _hash_prompt("prompt B")
    assert h1 != h2


def test_fallback_when_no_api_key():
    """OpenAI client returns fallback response when API key is empty."""
    db = _make_db()
    client = OpenAIClient(db)
    # settings.openai_api_key defaults to "" so fallback is expected
    result = client.generate(
        prompt="Give me coaching tips",
        user_id="user_test",
        insight_type="coaching",
        ttl_seconds=3600,
    )
    # Should get fallback coaching response
    assert "tips" in result
    assert len(result["tips"]) > 0
    assert result["summary"] != ""


def test_cache_hit_returns_cached_data():
    """When a cached entry exists and hasn't expired, it should be returned."""
    db = _make_db()
    prompt = "Give me coaching tips for user_1"
    prompt_hash = _hash_prompt(prompt)

    # Pre-populate cache with naive UTC datetimes (SQLite compat)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    cached_data = {"tips": [{"category": "focus", "tip": "cached tip", "priority": "high"}]}
    db.add(InsightCache(
        user_id="user_1",
        prompt_hash=prompt_hash,
        insight_type="coaching",
        response_data=cached_data,
        model_used="gpt-4o-mini",
        created_at=now,
        expires_at=now + timedelta(hours=4),
    ))
    db.commit()

    client = OpenAIClient(db)
    result = client.generate(
        prompt=prompt,
        user_id="user_1",
        insight_type="coaching",
        ttl_seconds=14400,
    )
    assert result == cached_data


def test_expired_cache_is_not_returned():
    """When a cached entry has expired, it should not be returned (fallback instead)."""
    db = _make_db()
    prompt = "Give me coaching tips for user_expired"
    prompt_hash = _hash_prompt(prompt)

    # Pre-populate with an expired cache entry (naive UTC)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    expired_data = {"tips": [{"category": "focus", "tip": "old tip", "priority": "low"}]}
    db.add(InsightCache(
        user_id="user_expired",
        prompt_hash=prompt_hash,
        insight_type="coaching",
        response_data=expired_data,
        model_used="gpt-4o-mini",
        created_at=now - timedelta(hours=10),
        expires_at=now - timedelta(hours=6),
    ))
    db.commit()

    client = OpenAIClient(db)
    result = client.generate(
        prompt=prompt,
        user_id="user_expired",
        insight_type="coaching",
        ttl_seconds=14400,
    )
    # Should NOT return the expired data; should be fallback
    assert result != expired_data
    assert "tips" in result  # fallback has tips


def test_fallback_is_cached_after_generation():
    """Even fallback responses should be stored in the cache."""
    db = _make_db()
    client = OpenAIClient(db)
    prompt = "unique prompt for caching test"
    prompt_hash = _hash_prompt(prompt)

    client.generate(
        prompt=prompt,
        user_id="user_cache_test",
        insight_type="coaching",
        ttl_seconds=3600,
    )

    # Check the cache table
    cached = db.query(InsightCache).filter_by(prompt_hash=prompt_hash).first()
    assert cached is not None
    assert cached.model_used == "fallback"
    assert cached.insight_type == "coaching"


def test_fallback_responses_all_types():
    """Verify all insight types have valid fallback responses."""
    db = _make_db()
    client = OpenAIClient(db)

    for insight_type in ["coaching", "session_review", "daily_briefing", "pattern_discovery"]:
        result = client.generate(
            prompt=f"Test {insight_type}",
            user_id="user_fallback",
            insight_type=insight_type,
            ttl_seconds=100,
        )
        assert isinstance(result, dict)
        assert len(result) > 0


def test_coaching_generator_with_fallback():
    """Integration test: CoachingGenerator produces valid response with no API key."""
    db = _make_db()
    from ai_insights.services.coaching_generator import CoachingGenerator

    gen = CoachingGenerator(db)
    user_context = {
        "user_id": "user_1",
        "total_sessions": 10,
        "total_focus_minutes": 250,
        "avg_productivity_score": 0.75,
        "recent_sessions": [],
    }

    response = gen.generate_coaching("user_1", user_context)
    assert response.user_id == "user_1"
    assert len(response.tips) > 0
    assert response.generated_at is not None


def test_session_review_with_fallback():
    """Integration test: session review with no API key."""
    db = _make_db()
    from ai_insights.services.coaching_generator import CoachingGenerator

    gen = CoachingGenerator(db)
    session_data = {"session_id": "sess_1", "duration": 25, "productivity_score": 0.8}
    user_context = {"user_id": "user_1", "total_sessions": 5, "recent_sessions": []}

    response = gen.generate_session_review("user_1", session_data, user_context)
    assert response.user_id == "user_1"
    assert response.review != ""


def test_daily_briefing_with_fallback():
    """Integration test: daily briefing with no API key."""
    db = _make_db()
    from ai_insights.services.coaching_generator import CoachingGenerator

    gen = CoachingGenerator(db)
    user_context = {"user_id": "user_1", "total_sessions": 5, "recent_sessions": []}

    response = gen.generate_daily_briefing("user_1", user_context)
    assert response.user_id == "user_1"
    assert len(response.focus_plan) > 0
