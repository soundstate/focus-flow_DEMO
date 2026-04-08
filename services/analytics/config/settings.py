from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Analytics service configuration settings"""

    model_config = ConfigDict(env_prefix="ANALYTICS_", case_sensitive=False)

    # Application settings
    debug_mode: bool = False
    log_level: str = "INFO"
    environment: str = "development"
    api_prefix: str = "/api/v1"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8003

    # Database settings
    database_url: str = "postgresql://postgres:postgres@localhost:5432/focus_flow_db"

    # Redis settings
    redis_url: str = "redis://localhost:6379/0"

    # CORS settings
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # External service URLs
    focus_engine_url: str = "http://localhost:8000"
    game_engine_url: str = "http://localhost:8001"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
