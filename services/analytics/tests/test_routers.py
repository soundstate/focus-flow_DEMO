"""Tests for Analytics service routers using TestClient."""
from datetime import date
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from analytics.database.connection import Base, get_db

# Import all ORM models so Base.metadata knows about every table
from analytics.models.metrics_models import DailyAggregate, CorrelationCache  # noqa: F401
from analytics.models.metrics_models import WeeklyAggregate  # noqa: F401

from analytics.routers import metrics, trends, comparisons, export, correlations


def _build_app():
    """Create a test FastAPI app with in-memory SQLite.

    Uses StaticPool so all connections share the same in-memory database.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestSessionLocal = sessionmaker(bind=engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = FastAPI()

    # Health and root endpoints
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "analytics", "version": "1.0.0"}

    @app.get("/")
    async def root():
        return {
            "service": "Focus Flow - Analytics Service",
            "version": "1.0.0",
            "status": "operational",
            "port": 8003,
        }

    app.include_router(metrics.router, prefix="/api/v1/metrics")
    app.include_router(trends.router, prefix="/api/v1/trends")
    app.include_router(comparisons.router, prefix="/api/v1/comparisons")
    app.include_router(correlations.router, prefix="/api/v1/correlations")
    app.include_router(export.router, prefix="/api/v1/export")
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app), TestSessionLocal


# --- Health / Root ---


def test_health_check():
    client, _ = _build_app()
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "analytics"


def test_root_endpoint():
    client, _ = _build_app()
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Focus Flow - Analytics Service"
    assert data["port"] == 8003


# --- Metrics ---


def test_get_summary_empty():
    client, _ = _build_app()
    response = client.get("/api/v1/metrics/users/user_unknown/summary?period=weekly")
    assert response.status_code == 200
    data = response.json()
    assert data["total_sessions"] == 0
    assert data["period"] == "weekly"


def test_get_summary_with_data():
    client, SessionLocal = _build_app()
    db = SessionLocal()
    db.add(DailyAggregate(
        user_id="user_summary",
        date=date.today(),
        total_sessions=5,
        total_focus_minutes=125,
        avg_productivity_score=0.9,
        total_xp_earned=500,
        total_interruptions=2,
    ))
    db.commit()
    db.close()

    response = client.get("/api/v1/metrics/users/user_summary/summary?period=daily")
    assert response.status_code == 200
    data = response.json()
    assert data["total_sessions"] == 5
    assert data["total_focus_minutes"] == 125


# --- Trends ---


def test_weekly_trend_empty():
    client, _ = _build_app()
    response = client.get("/api/v1/trends/users/user_empty/weekly")
    assert response.status_code == 200
    data = response.json()
    assert "this_week" in data
    assert "last_week" in data
    assert "change" in data


def test_monthly_trend_empty():
    client, _ = _build_app()
    response = client.get("/api/v1/trends/users/user_empty/monthly")
    assert response.status_code == 200
    data = response.json()
    assert "this_month" in data
    assert "last_month" in data


def test_productivity_curve():
    client, _ = _build_app()
    response = client.get("/api/v1/trends/users/user_1/productivity-curve")
    assert response.status_code == 200
    assert response.json() == []


# --- Comparisons ---


def test_compare_periods():
    client, _ = _build_app()
    response = client.get(
        "/api/v1/comparisons/users/user_1/periods"
        "?start1=2026-03-01&end1=2026-03-07"
        "&start2=2026-03-08&end2=2026-03-14"
    )
    assert response.status_code == 200
    data = response.json()
    assert "period_1" in data
    assert "period_2" in data
    assert "change" in data


# --- Export ---


def test_export_json():
    client, _ = _build_app()
    response = client.get("/api/v1/export/users/user_1?format=json&days=7")
    assert response.status_code == 200


def test_export_csv():
    client, _ = _build_app()
    response = client.get("/api/v1/export/users/user_1?format=csv&days=7")
    assert response.status_code == 200


# --- Correlations ---


def test_correlations_empty():
    client, _ = _build_app()
    response = client.get("/api/v1/correlations/users/user_empty")
    assert response.status_code == 200
    assert response.json() == []


def test_correlations_with_data():
    client, SessionLocal = _build_app()
    db = SessionLocal()
    db.add(CorrelationCache(
        user_id="user_corr",
        correlation_type="duration_vs_productivity",
        result={"r": 0.75, "p": 0.01},
    ))
    db.commit()
    db.close()

    response = client.get("/api/v1/correlations/users/user_corr")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["correlation_type"] == "duration_vs_productivity"
    assert data[0]["result"]["r"] == 0.75
