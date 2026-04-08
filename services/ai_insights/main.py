"""
Focus Flow - AI Insights Service
Main FastAPI application for AI-powered coaching, pattern discovery, and insights
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import uvicorn
import logging

from ai_insights.config.ai_settings import get_settings
from ai_insights.database import connection as db_connection
from ai_insights.routers import insights, patterns, coaching

# initialize settings and logging
settings = get_settings()
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """application lifespan management"""
    logger.info("AI Insights service starting up...")
    # create database tables
    db_connection.create_tables()

    # start Redis subscriber as background task
    subscriber_task = None
    try:
        import redis.asyncio as aioredis

        redis_client = aioredis.from_url(
            settings.redis_url, decode_responses=False
        )
        app.state.redis = redis_client

        from ai_insights.events.subscriber import start_subscriber

        db_connection._ensure_engine()

        subscriber_task = asyncio.create_task(
            start_subscriber(redis_client, db_connection._SessionLocal)
        )
        logger.info("Event subscriber started as background task")
    except Exception:
        logger.warning(
            "Redis not available -- running without event subscriber",
            exc_info=True,
        )

    yield

    # shutdown
    if subscriber_task is not None:
        subscriber_task.cancel()
        try:
            await subscriber_task
        except asyncio.CancelledError:
            pass

    if hasattr(app.state, "redis") and app.state.redis is not None:
        await app.state.redis.close()

    logger.info("AI Insights service shutting down...")


# create fastapi application
app = FastAPI(
    title="Focus Flow - AI Insights Service",
    description="AI-powered coaching tips, session reviews, daily briefings, and pattern discovery",
    version="1.0.0",
    docs_url="/docs" if settings.debug_mode else None,
    redoc_url="/redoc" if settings.debug_mode else None,
    lifespan=lifespan,
)

# configure cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(
    insights.router,
    prefix=f"{settings.api_prefix}/insights",
    tags=["insights"],
)
app.include_router(
    patterns.router,
    prefix=f"{settings.api_prefix}/patterns",
    tags=["patterns"],
)
app.include_router(
    coaching.router,
    prefix=f"{settings.api_prefix}/coaching",
    tags=["coaching"],
)


@app.get("/health")
async def health_check():
    """health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-insights",
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """root endpoint with service information"""
    return {
        "service": "Focus Flow - AI Insights Service",
        "version": "1.0.0",
        "status": "operational",
        "description": "AI-powered coaching, pattern discovery, and productivity insights",
        "port": settings.port,
    }


if __name__ == "__main__":
    uvicorn.run(
        "ai_insights.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug_mode,
        log_level=settings.log_level.lower(),
    )
