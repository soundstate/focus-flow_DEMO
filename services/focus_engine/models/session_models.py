"""
Focus Session Data Models
SQLAlchemy models for focus sessions and related data
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, JSON, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from database.connection import Base
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid
from pydantic import BaseModel, Field, validator

class FocusSession(Base):
    """Focus session database model"""
    __tablename__ = "focus_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    user_id = Column(String(255), index=True)  # Future multi-user support

    # Session timing
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=True)
    planned_duration = Column(Integer, default=50)  # minutes
    actual_duration = Column(Integer, nullable=True)
    break_duration = Column(Integer, default=10)

    # Session quality metrics
    completion_rate = Column(Float, nullable=True)  # 0.0 to 1.0
    productivity_score = Column(Float, nullable=True)  # 0.0 to 10.0
    interruptions = Column(Integer, default=0)
    interruption_types = Column(JSON, nullable=True)
    focus_quality = Column(String(50), nullable=True)  # "high", "medium", "low"

    # Session context
    session_type = Column(String(50), default="work")  # "work", "break", "deep_work"
    time_of_day_category = Column(String(50), nullable=True)  # "morning", "afternoon", "evening"

    # Music integration
    playlist_id = Column(String(255), nullable=True)
    playlist_name = Column(String(500), nullable=True)

    # AI-generated insights
    ai_insights = Column(Text, nullable=True)
    optimal_time_suggestions = Column(Text, nullable=True)
    improvement_recommendations = Column(JSON, nullable=True)

    # Gamification
    experience_points = Column(Integer, default=0)
    achievements_unlocked = Column(JSON, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    """User model for future multi-user support"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)

    # User preferences
    default_session_duration = Column(Integer, default=50)
    default_break_duration = Column(Integer, default=10)
    notification_preferences = Column(JSON, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

# Pydantic models for API
class SessionStartRequest(BaseModel):
    """Request model for starting a focus session"""
    duration: int = Field(default=50, ge=1, le=180, description="Session duration in minutes")
    session_type: str = Field(default="work", description="Type of session")
    playlist_id: Optional[str] = Field(None, description="Music playlist ID")
    user_id: str = Field(default="demo_user", description="User identifier")

class SessionCompletionRequest(BaseModel):
    """Request model for completing a focus session"""
    completion_rate: float = Field(ge=0.0, le=1.0, description="Session completion percentage")
    productivity_score: float = Field(ge=0.0, le=10.0, description="Self-assessed productivity score")
    interruptions: int = Field(ge=0, description="Number of interruptions")
    interruption_types: Optional[List[str]] = Field(None, description="Types of interruptions")

class SessionResponse(BaseModel):
    """Response model for focus session data"""
    id: int
    session_uuid: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime]
    planned_duration: int
    actual_duration: Optional[int]
    completion_rate: Optional[float]
    productivity_score: Optional[float]
    interruptions: int
    session_type: str
    playlist_id: Optional[str]
    playlist_name: Optional[str]
    ai_insights: Optional[str]
    experience_points: int
    created_at: datetime

    class Config:
        from_attributes = True

# Additional models for the new service layer architecture
class FocusSessionCreate(BaseModel):
    """Model for creating a new focus session"""
    user_id: str = Field(..., min_length=3, max_length=50)
    session_type: str = Field(default="pomodoro")
    planned_duration: int = Field(..., ge=5, le=300)
    
    @validator('session_type')
    def validate_session_type(cls, v):
        valid_types = ["pomodoro", "long_focus", "deep_work", "study", "custom"]
        if v not in valid_types:
            raise ValueError(f"session_type must be one of: {valid_types}")
        return v

class FocusSessionUpdate(BaseModel):
    """Model for updating a focus session"""
    status: Optional[str] = None
    end_time: Optional[datetime] = None
    actual_duration: Optional[int] = None
    completion_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    productivity_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    interruptions: Optional[int] = Field(None, ge=0)
    interruption_types: Optional[List[str]] = None
    notes: Optional[str] = None
    
class FocusSessionResponse(BaseModel):
    """Enhanced response model for focus session data"""
    id: str
    user_id: str
    session_type: str
    planned_duration: int
    actual_duration: Optional[int]
    start_time: datetime
    end_time: Optional[datetime]
    planned_end_time: Optional[datetime]
    status: str
    completion_reason: Optional[str]
    productivity_score: Optional[float]
    focus_quality: Optional[str]
    interruption_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class FocusSessionList(BaseModel):
    """Model for list of focus sessions"""
    sessions: List[FocusSessionResponse]
    total: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
