from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """AI Insights service configuration settings"""

    model_config = ConfigDict(env_prefix="AI_INSIGHTS_", case_sensitive=False)

    # Application settings
    debug_mode: bool = False
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8002

    # Database settings
    database_url: str = "postgresql://postgres:postgres@localhost:5432/focus_flow_db"

    # Redis settings
    redis_url: str = "redis://localhost:6379/0"

    # CORS settings
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # External service URLs
    focus_engine_url: str = "http://localhost:8000"
    analytics_url: str = "http://localhost:8003"

    # OpenAI settings
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_model_advanced: str = "gpt-4o"

    # Cache TTLs (seconds)
    coaching_cache_ttl: int = 14400
    briefing_cache_ttl: int = 43200


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
