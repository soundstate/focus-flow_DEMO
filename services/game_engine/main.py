"""
Focus Flow - Game Engine Service
Main FastAPI application for gamification features
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging

from game_engine.config.settings import get_settings
from game_engine.database.connection import create_tables

# initialize settings and logging
settings = get_settings()
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """application lifespan management"""
    logger.info("🎮 game engine service starting up...")
    # create database tables
    create_tables()
    yield
    logger.info("📴 game engine service shutting down...")

# create fastapi application
app = FastAPI(
    title="Focus Flow - Game Engine",
    description="Gamification features including achievements, levels, streaks, and leaderboards",
    version="1.0.0",
    docs_url="/docs" if settings.debug_mode else None,
    redoc_url="/redoc" if settings.debug_mode else None,
    lifespan=lifespan
)

# configure cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# todo_cmt include routers when implemented
# from game_engine.routers import achievements, levels, streaks, leaderboards
# app.include_router(achievements.router, prefix=f"{settings.api_prefix}/achievements", tags=["achievements"])
# app.include_router(levels.router, prefix=f"{settings.api_prefix}/levels", tags=["levels"])
# app.include_router(streaks.router, prefix=f"{settings.api_prefix}/streaks", tags=["streaks"])
# app.include_router(leaderboards.router, prefix=f"{settings.api_prefix}/leaderboards", tags=["leaderboards"])

@app.get("/health")
async def health_check():
    """health check endpoint"""
    return {
        "status": "healthy",
        "service": "game_engine",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """root endpoint with service information"""
    return {
        "service": "Focus Flow - Game Engine",
        "version": "1.0.0",
        "status": "operational",
        "description": "Gamification features including achievements, levels, streaks, and leaderboards",
        "port": settings.port
    }

if __name__ == "__main__":
    uvicorn.run(
        "game_engine.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug_mode,
        log_level=settings.log_level.lower()
    )