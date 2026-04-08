"""
Focus Flow - Music Control Service
Main FastAPI application for YouTube Music integration, playback control,
playlist management, and music effectiveness tracking.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import uvicorn
import logging

from music_control.config.settings import get_settings
from music_control.database import connection as db_connection
from music_control.routers import auth, playlists, playback, effectiveness, websockets

# initialize settings and logging
settings = get_settings()
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """application lifespan management"""
    logger.info("Music Control service starting up...")
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

        from music_control.events.subscriber import start_subscriber

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

    logger.info("Music Control service shutting down...")


# create fastapi application
app = FastAPI(
    title="Focus Flow - Music Control Service",
    description="YouTube Music integration, playback control, playlist management, and effectiveness tracking",
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
    auth.router,
    prefix=f"{settings.api_prefix}/auth",
    tags=["auth"],
)
app.include_router(
    playlists.router,
    prefix=f"{settings.api_prefix}/playlists",
    tags=["playlists"],
)
app.include_router(
    playback.router,
    prefix=f"{settings.api_prefix}/playback",
    tags=["playback"],
)
app.include_router(
    effectiveness.router,
    prefix=f"{settings.api_prefix}/effectiveness",
    tags=["effectiveness"],
)
app.include_router(
    websockets.router,
    prefix="/ws",
    tags=["websockets"],
)


@app.get("/health")
async def health_check():
    """health check endpoint"""
    return {
        "status": "healthy",
        "service": "music-control",
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """root endpoint with service information"""
    return {
        "service": "Focus Flow - Music Control Service",
        "version": "1.0.0",
        "status": "operational",
        "description": "YouTube Music integration, playback control, and effectiveness tracking",
        "port": settings.port,
    }


if __name__ == "__main__":
    uvicorn.run(
        "music_control.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug_mode,
        log_level=settings.log_level.lower(),
    )
