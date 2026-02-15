from sqlalchemy import Column, String, Integer, Float, DateTime
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

from game_engine.database.connection import Base

# level progression constants
XP_BASE = 100
XP_MULTIPLIER = 1.5


class UserLevel(Base):
    """SQLAlchemy model for user level and experience"""
    __tablename__ = "user_levels"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    current_level = Column(Integer, default=1)
    current_xp = Column(Integer, default=0)
    total_xp = Column(Integer, default=0)
    xp_to_next_level = Column(Integer, default=XP_BASE)
    level_up_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LevelResponse(BaseModel):
    """Pydantic model for level API responses"""
    user_id: str
    current_level: int
    current_xp: int
    total_xp: int
    xp_to_next_level: int
    progress_percentage: float
    level_up_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LevelUpEvent(BaseModel):
    """Pydantic model for level-up notifications"""
    user_id: str
    level_reached: int
    xp_earned: int
    total_xp: int
    rewards_unlocked: List[str]
    timestamp: datetime


class ExperienceGain(BaseModel):
    """Pydantic model for tracking XP gains"""
    session_id: str
    user_id: str
    base_xp: int
    bonus_xp: int
    total_xp: int
    reason: str
    multipliers_applied: dict = {}


def calculate_xp_for_level(level: int) -> int:
    """Calculate XP required to reach a specific level"""
    return int(XP_BASE * (XP_MULTIPLIER ** (level - 1)))