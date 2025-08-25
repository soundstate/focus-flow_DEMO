"""
Focus Engine Service Configuration
Environment-driven settings using Pydantic
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings"""

    # Application settings
    debug_mode: bool = True
    log_level: str = "INFO"
    environment: str = "development"

    # Database settings
    database_url: str = "postgresql://focus_user:focus_password@localhost:5432/focus_flow_db"

    # Redis settings
    redis_url: str = "redis://localhost:6379/0"

    # Security settings
    secret_key: str = "focus-flow-secret-key-change-in-production"
    jwt_secret: str = "focus-flow-jwt-secret-change-in-production"

    # API settings
    api_prefix: str = "/api/v1"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3001"]

    # Session settings
    max_sessions_per_user: int = 1000
    session_timeout_minutes: int = 60
    default_session_duration: int = 50  # minutes
    default_break_duration: int = 10    # minutes

    class Config:
        env_prefix = "FOCUS_FLOW_"
        env_file = ".env"

def get_settings() -> Settings:
    """Get application settings"""
    return Settings()
