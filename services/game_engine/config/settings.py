from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Game Engine service configuration settings"""
    
    # Application settings
    debug_mode: bool = False
    log_level: str = "INFO"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8001
    
    # Database settings
    database_url: str = "postgresql://postgres:postgres@localhost:5432/focus_flow_game"
    
    # Redis settings
    redis_url: str = "redis://localhost:6379/1"
    
    # CORS settings
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # XP calculation settings
    base_xp_per_session: int = 50
    completion_bonus: int = 25
    streak_multiplier: float = 1.1
    quality_multiplier_max: float = 1.5
    
    # Achievement unlock thresholds
    streak_3_threshold: int = 3
    streak_7_threshold: int = 7
    streak_30_threshold: int = 30
    streak_100_threshold: int = 100
    total_sessions_10_threshold: int = 10
    total_sessions_50_threshold: int = 50
    total_sessions_100_threshold: int = 100
    
    # Leaderboard settings
    leaderboard_refresh_interval: int = 300  # 5 minutes in seconds
    leaderboard_max_entries: int = 50
    leaderboard_cache_ttl: int = 300
    
    # Level progression
    xp_base: int = 100
    xp_multiplier: float = 1.5
    
    class Config:
        env_prefix = "GAME_ENGINE_"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
