"""
Focus Flow - Focus Engine Service
Main FastAPI application for focus session management
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from config.settings import get_settings
from config.logging_config import setup_logging
from routers import sessions, health, websockets
from database.connection import engine
from sqlalchemy.orm import Session

# Initialize settings and logging
settings = get_settings()
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🚀 Focus Engine service starting up...")
    yield
    logger.info("📴 Focus Engine service shutting down...")

# Create FastAPI application
app = FastAPI(
    title="Focus Flow - Focus Engine",
    description="Core focus session management and timer functionality",
    version="1.0.0",
    docs_url="/docs" if settings.debug_mode else None,
    redoc_url="/redoc" if settings.debug_mode else None,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions"])
app.include_router(websockets.router, prefix="/ws", tags=["websockets"])

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Focus Flow - Focus Engine",
        "version": "1.0.0",
        "status": "operational",
        "description": "Core focus session management and timer functionality"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug_mode,
        log_level=settings.log_level.lower()
    )
