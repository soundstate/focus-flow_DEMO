"""
Session Service Layer
Business logic for focus sessions
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional, List
import logging

from ..models.session_models import FocusSession
from ..routers.websockets import broadcast_session_update

logger = logging.getLogger("focus_engine.session_service")

class SessionService:
    """Business logic for focus sessions"""

    @staticmethod
    async def start_session(db: Session, user_id: str, duration_minutes: int, 
                           session_type: str = "pomodoro") -> FocusSession:
        """Start a new focus session"""
        
        # Check if user has an active session
        active_session = db.query(FocusSession).filter(
            FocusSession.user_id == user_id,
            FocusSession.status == "active"
        ).first()
        
        if active_session:
            raise ValueError("User already has an active session")
        
        # Calculate end time
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Create session
        session = FocusSession(
            user_id=user_id,
            session_type=session_type,
            planned_duration=duration_minutes,
            start_time=start_time,
            planned_end_time=end_time,
            status="active"
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # Broadcast session start
        await broadcast_session_update(str(session.id), {
            "event": "session_started",
            "session": {
                "id": str(session.id),
                "user_id": session.user_id,
                "duration": duration_minutes,
                "start_time": session.start_time.isoformat(),
                "end_time": session.planned_end_time.isoformat()
            }
        })
        
        logger.info(f"Started session {session.id} for user {user_id}")
        return session
    
    @staticmethod
    async def pause_session(db: Session, session_id: str) -> FocusSession:
        """Pause an active session"""
        
        session = db.query(FocusSession).filter(
            FocusSession.id == session_id
        ).first()
        
        if not session:
            raise ValueError("Session not found")
        
        if session.status != "active":
            raise ValueError("Session is not active")
        
        session.status = "paused"
        session.paused_at = datetime.utcnow()
        
        db.commit()
        db.refresh(session)
        
        # Broadcast session pause
        await broadcast_session_update(session_id, {
            "event": "session_paused",
            "session_id": session_id,
            "paused_at": session.paused_at.isoformat()
        })
        
        logger.info(f"Paused session {session_id}")
        return session
    
    @staticmethod
    async def resume_session(db: Session, session_id: str) -> FocusSession:
        """Resume a paused session"""
        
        session = db.query(FocusSession).filter(
            FocusSession.id == session_id
        ).first()
        
        if not session:
            raise ValueError("Session not found")
        
        if session.status != "paused":
            raise ValueError("Session is not paused")
        
        # Calculate new end time accounting for pause duration
        if session.paused_at:
            pause_duration = datetime.utcnow() - session.paused_at
            session.planned_end_time += pause_duration
        
        session.status = "active"
        session.resumed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(session)
        
        # Broadcast session resume
        await broadcast_session_update(session_id, {
            "event": "session_resumed",
            "session_id": session_id,
            "resumed_at": session.resumed_at.isoformat(),
            "new_end_time": session.planned_end_time.isoformat()
        })
        
        logger.info(f"Resumed session {session_id}")
        return session
    
    @staticmethod
    async def complete_session(db: Session, session_id: str, 
                             completion_reason: str = "completed") -> FocusSession:
        """Complete a session"""
        
        session = db.query(FocusSession).filter(
            FocusSession.id == session_id
        ).first()
        
        if not session:
            raise ValueError("Session not found")
        
        if session.status not in ["active", "paused"]:
            raise ValueError("Session is already completed or canceled")
        
        session.status = "completed"
        session.end_time = datetime.utcnow()
        session.completion_reason = completion_reason
        
        # Calculate actual duration
        if session.start_time:
            session.actual_duration = int(
                (session.end_time - session.start_time).total_seconds() / 60
            )
        
        db.commit()
        db.refresh(session)
        
        # Broadcast session completion
        await broadcast_session_update(session_id, {
            "event": "session_completed",
            "session_id": session_id,
            "completion_reason": completion_reason,
            "actual_duration": session.actual_duration
        })
        
        logger.info(f"Completed session {session_id} - {completion_reason}")
        return session
    
    @staticmethod
    def get_user_sessions(db: Session, user_id: str, 
                         limit: int = 10) -> List[FocusSession]:
        """Get recent sessions for a user"""
        
        return db.query(FocusSession).filter(
            FocusSession.user_id == user_id
        ).order_by(
            FocusSession.start_time.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_active_session(db: Session, user_id: str) -> Optional[FocusSession]:
        """Get user's currently active session if any"""
        
        return db.query(FocusSession).filter(
            FocusSession.user_id == user_id,
            FocusSession.status.in_(["active", "paused"])
        ).first()
