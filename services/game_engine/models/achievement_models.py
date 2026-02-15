from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, Enum as SQLEnum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import uuid4
from enum import Enum

from game_engine.database.connection import Base


class AchievementType(str, Enum):
    """Types of achievements that can be unlocked"""
    FIRST_SESSION = "first_session"
    STREAK_3 = "streak_3"
    STREAK_7 = "streak_7"
    STREAK_30 = "streak_30"
    STREAK_100 = "streak_100"
    TOTAL_SESSIONS_10 = "total_sessions_10"
    TOTAL_SESSIONS_50 = "total_sessions_50"
    TOTAL_SESSIONS_100 = "total_sessions_100"
    DEEP_WORK_MASTER = "deep_work_master"
    EARLY_BIRD = "early_bird"
    NIGHT_OWL = "night_owl"


class AchievementCategory(str, Enum):
    """Categories for organizing achievements"""
    MILESTONE = "milestone"
    STREAK = "streak"
    CONSISTENCY = "consistency"
    MASTERY = "mastery"
    TIME_BASED = "time_based"


class Achievement(Base):
    """SQLAlchemy model for user achievements"""
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    achievement_id = Column(String, unique=True, index=True, default=lambda: str(uuid4()))
    user_id = Column(String, index=True, nullable=False)
    achievement_type = Column(SQLEnum(AchievementType), nullable=False)
    category = Column(SQLEnum(AchievementCategory), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    icon = Column(String, nullable=False)
    unlocked_at = Column(DateTime, nullable=True)
    progress_current = Column(Integer, default=0)
    progress_required = Column(Integer, nullable=False)
    is_unlocked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AchievementProgress(BaseModel):
    """Pydantic model for tracking achievement progress"""
    achievement_id: str
    achievement_type: AchievementType
    title: str
    description: str
    icon: str
    progress_current: int
    progress_required: int
    progress_percentage: float
    is_unlocked: bool
    category: AchievementCategory


class AchievementResponse(BaseModel):
    """Pydantic model for achievement API responses"""
    achievement_id: str
    user_id: str
    achievement_type: AchievementType
    category: AchievementCategory
    title: str
    description: str
    icon: str
    unlocked_at: Optional[datetime] = None
    progress_current: int
    progress_required: int
    is_unlocked: bool
    
    class Config:
        from_attributes = True


class UserAchievementStats(BaseModel):
    """Pydantic model for user achievement statistics"""
    user_id: str
    total_unlocked: int
    total_available: int
    completion_percentage: float
    recent_unlocks: List[AchievementResponse] = Field(default_factory=list)
    by_category: dict = Field(default_factory=dict)


class AchievementUnlockEvent(BaseModel):
    """Pydantic model for achievement unlock notifications"""
    achievement_id: str
    user_id: str
    achievement_type: AchievementType
    title: str
    description: str
    icon: str
    unlocked_at: datetime
    category: AchievementCategory