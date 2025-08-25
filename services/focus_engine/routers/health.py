"""
Health Check Router
Service health monitoring endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_database
from config.settings import get_settings
import redis
import logging

logger = logging.getLogger("focus_engine.health")
router = APIRouter()
settings = get_settings()

@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "service": "focus-engine",
        "status": "healthy",
        "version": "1.0.0"
    }

@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_database)):
    """Detailed health check with dependency validation"""
    health_status = {
        "service": "focus-engine",
        "status": "healthy",
        "version": "1.0.0",
        "checks": {}
    }

    # Database connection check
    try:
        db.execute("SELECT 1")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["checks"]["database"] = "unhealthy"
        health_status["status"] = "degraded"

    # Redis connection check
    try:
        r = redis.from_url(settings.redis_url)
        r.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["checks"]["redis"] = "unhealthy"
        health_status["status"] = "degraded"

    return health_status
