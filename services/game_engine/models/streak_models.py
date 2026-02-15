from sqlalchemy import Column, String, Integer, Date, DateTime
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from enum import Enum

from game_engine.database.connection import Base

# streak calculation constants
STREAK_GRACE_PERIOD_HOURS = 36


class StreakMilestoneType(str, Enum):
    """Types of streak milestones"""
    STREAK_3_DAY = "3_day"
    STREAK_7_DAY = "7_day"
    STREAK_30_DAY = "30_day"
    STREAK_100_DAY = "100_day"


class UserStreak(Base):
    """SQLAlchemy model for user streak tracking"""
    __tablename__ = "user_streaks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_session_date = Column(Date, nullable=True)
    streak_start_date = Column(Date, nullable=True)
    total_sessions = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StreakResponse(BaseModel):
    """Pydantic model for streak API responses"""
    user_id: str
    current_streak: int
    longest_streak: int
    last_session_date: Optional[date] = None
    streak_start_date: Optional[date] = None
    total_sessions: int
    is_active: bool
    days_until_break: int
    
    class Config:
        from_attributes = True


class StreakUpdate(BaseModel):
    """Pydantic model for streak update notifications"""
    user_id: str
    previous_streak: int
    new_streak: int
    is_broken: bool
    is_milestone: bool
    milestone_type: Optional[StreakMilestoneType] = None


class StreakMilestone(BaseModel):
    """Pydantic model for streak milestone achievements"""
    user_id: str
    milestone_type: StreakMilestoneType
    streak_count: int
    reached_at: datetime
    reward: str