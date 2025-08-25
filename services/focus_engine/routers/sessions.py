"""
Sessions Router
Endpoints for focus sessions management
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import logging

from ..database.connection import get_db
from ..models.session_models import (
    FocusSession, 
    FocusSessionCreate, 
    FocusSessionResponse,
    FocusSessionUpdate,
    FocusSessionList
)
from ..services.session_service import SessionService

logger = logging.getLogger("focus_engine.routers.sessions")
router = APIRouter()

@router.post("/sessions/", response_model=FocusSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_session(session: FocusSessionCreate, db: Session = Depends(get_db)):
    """Start a new focus session"""
    
    try:
        db_session = await SessionService.start_session(
            db=db,
            user_id=session.user_id,
            duration_minutes=session.planned_duration,
            session_type=session.session_type
        )
        return db_session
    except ValueError as e:
        logger.warning(f"Failed to start session: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sessions/{session_id}/pause", response_model=FocusSessionResponse)
async def pause_session(session_id: str, db: Session = Depends(get_db)):
    """Pause an active session"""
    
    try:
        db_session = await SessionService.pause_session(db=db, session_id=session_id)
        return db_session
    except ValueError as e:
        logger.warning(f"Failed to pause session: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sessions/{session_id}/resume", response_model=FocusSessionResponse)
async def resume_session(session_id: str, db: Session = Depends(get_db)):
    """Resume a paused session"""
    
    try:
        db_session = await SessionService.resume_session(db=db, session_id=session_id)
        return db_session
    except ValueError as e:
        logger.warning(f"Failed to resume session: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sessions/{session_id}/complete", response_model=FocusSessionResponse)
async def complete_session(session_id: str, completion_reason: str = "completed", db: Session = Depends(get_db)):
    """Complete a session"""
    
    try:
        db_session = await SessionService.complete_session(
            db=db, 
            session_id=session_id,
            completion_reason=completion_reason
        )
        return db_session
    except ValueError as e:
        logger.warning(f"Failed to complete session: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sessions/{session_id}", response_model=FocusSessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get a specific focus session"""
    
    db_session = db.query(FocusSession).filter(FocusSession.id == session_id).first()
    if db_session is None:
        logger.warning(f"Session with ID {session_id} not found")
        raise HTTPException(status_code=404, detail="Session not found")
    
    return db_session

@router.get("/sessions/user/{user_id}", response_model=FocusSessionList)
def get_user_sessions(user_id: str, limit: int = 10, db: Session = Depends(get_db)):
    """Get recent focus sessions for a user"""
    
    sessions = SessionService.get_user_sessions(db=db, user_id=user_id, limit=limit)
    return {"sessions": sessions}

@router.get("/sessions/user/{user_id}/active", response_model=FocusSessionResponse)
def get_active_session(user_id: str, db: Session = Depends(get_db)):
    """Get a user's active session if any"""
    
    session = SessionService.get_active_session(db=db, user_id=user_id)
    if session is None:
        raise HTTPException(status_code=404, detail="No active session found")
    
    return session

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Delete a focus session"""
    
    db_session = db.query(FocusSession).filter(FocusSession.id == session_id).first()
    if db_session is None:
        logger.warning(f"Session with ID {session_id} not found for deletion")
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(db_session)
    db.commit()
    
    logger.info(f"Deleted session with ID: {session_id}")
    return None
