"""Pattern discovery ORM models and Pydantic response schemas."""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional, List

from ai_insights.database.connection import Base


def _utcnow():
    """Return timezone-aware UTC now."""
    return datetime.now(timezone.utc)


class UserPattern(Base):
    """Discovered productivity patterns for a user."""
    __tablename__ = "ai_user_patterns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    pattern_type = Column(String, nullable=False)  # peak_hours, session_length, break_pattern
    pattern_data = Column(JSON, nullable=True)
    confidence = Column(Float, default=0.0)
    discovered_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)


# --- Pydantic response models ---

class PatternDetail(BaseModel):
    """Individual pattern detail."""
    pattern_type: str
    description: str
    confidence: float = 0.0
    data: Optional[dict] = None


class PatternResponse(BaseModel):
    """Response model for pattern discovery endpoint."""
    user_id: str
    patterns: List[PatternDetail] = []
    interpretation: str = ""
    discovered_at: Optional[str] = None
    cached: bool = False
