"""
Validation Utilities
Input validation and data sanitization functions
"""

from typing import List, Optional
from datetime import datetime
import re


class SessionValidators:
    """Validators for focus session data"""
    
    # Valid session types
    VALID_SESSION_TYPES = {
        "pomodoro": {"min_duration": 15, "max_duration": 60},
        "long_focus": {"min_duration": 60, "max_duration": 180},
        "deep_work": {"min_duration": 120, "max_duration": 240},
        "study": {"min_duration": 30, "max_duration": 120},
        "custom": {"min_duration": 5, "max_duration": 300}
    }
    
    # Valid session statuses
    VALID_STATUSES = ["active", "paused", "completed", "cancelled"]
    
    @classmethod
    def validate_user_id(cls, user_id: str) -> bool:
        """Validate user ID format"""
        if not user_id or not isinstance(user_id, str):
            return False
        
        # Basic validation: non-empty, reasonable length
        if len(user_id) < 3 or len(user_id) > 50:
            return False
        
        # Allow alphanumeric and common separators
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, user_id))
    
    @classmethod
    def validate_session_type(cls, session_type: str) -> bool:
        """Validate session type"""
        return session_type in cls.VALID_SESSION_TYPES
    
    @classmethod
    def validate_duration(cls, duration: int, session_type: str) -> bool:
        """Validate session duration based on type"""
        if not isinstance(duration, int) or duration <= 0:
            return False
        
        if session_type not in cls.VALID_SESSION_TYPES:
            return False
        
        limits = cls.VALID_SESSION_TYPES[session_type]
        return limits["min_duration"] <= duration <= limits["max_duration"]
    
    @classmethod
    def validate_session_status(cls, status: str) -> bool:
        """Validate session status"""
        return status in cls.VALID_STATUSES
    
    @classmethod
    def validate_session_id(cls, session_id: str) -> bool:
        """Validate session ID format"""
        if not session_id or not isinstance(session_id, str):
            return False
        
        # UUID-like format or simple ID
        uuid_pattern = r'^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'
        simple_id_pattern = r'^[a-zA-Z0-9_-]{1,50}$'
        
        return bool(re.match(uuid_pattern, session_id) or re.match(simple_id_pattern, session_id))


class InputSanitizers:
    """Input sanitization utilities"""
    
    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 255) -> str:
        """Sanitize string input"""
        if not isinstance(input_str, str):
            return ""
        
        # Strip whitespace and limit length
        sanitized = input_str.strip()[:max_length]
        
        # Remove potentially dangerous characters
        # Keep alphanumeric, spaces, and common punctuation
        sanitized = re.sub(r'[^a-zA-Z0-9\s\-_.,!?()\[\]{}:;"\']', '', sanitized)
        
        return sanitized
    
    @staticmethod
    def sanitize_user_id(user_id: str) -> str:
        """Sanitize user ID"""
        if not isinstance(user_id, str):
            return ""
        
        # Keep only alphanumeric and common separators
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', user_id.strip())
        
        return sanitized[:50]  # Limit length
    
    @staticmethod
    def sanitize_session_type(session_type: str) -> str:
        """Sanitize session type"""
        if not isinstance(session_type, str):
            return "custom"
        
        sanitized = session_type.lower().strip()
        
        # Only allow valid session types
        if sanitized in SessionValidators.VALID_SESSION_TYPES:
            return sanitized
        
        return "custom"


class BusinessRuleValidators:
    """Business logic validation"""
    
    @staticmethod
    def can_start_session(user_active_sessions: int, max_concurrent: int = 1) -> bool:
        """Check if user can start a new session"""
        return user_active_sessions < max_concurrent
    
    @staticmethod
    def can_pause_session(session_status: str, session_start_time: Optional[datetime]) -> bool:
        """Check if session can be paused"""
        if session_status != "active":
            return False
        
        if not session_start_time:
            return False
        
        # Don't allow pausing very new sessions (less than 1 minute)
        elapsed = datetime.utcnow() - session_start_time
        return elapsed.total_seconds() >= 60
    
    @staticmethod
    def can_resume_session(session_status: str, pause_time: Optional[datetime]) -> bool:
        """Check if session can be resumed"""
        return session_status == "paused" and pause_time is not None
    
    @staticmethod
    def can_complete_session(session_status: str) -> bool:
        """Check if session can be completed"""
        return session_status in ["active", "paused"]
    
    @staticmethod
    def is_reasonable_session_duration(duration_minutes: int) -> bool:
        """Check if session duration is reasonable"""
        # Between 5 minutes and 5 hours
        return 5 <= duration_minutes <= 300
    
    @staticmethod
    def validate_completion_reason(reason: str) -> bool:
        """Validate session completion reason"""
        valid_reasons = [
            "completed", "interrupted", "cancelled", "timeout", 
            "break", "emergency", "voluntary_stop"
        ]
        return reason in valid_reasons


def validate_session_creation_data(user_id: str, session_type: str, duration: int) -> List[str]:
    """Validate all data required for session creation"""
    errors = []
    
    # Validate user ID
    if not SessionValidators.validate_user_id(user_id):
        errors.append("Invalid user ID format")
    
    # Validate session type
    if not SessionValidators.validate_session_type(session_type):
        errors.append(f"Invalid session type. Must be one of: {list(SessionValidators.VALID_SESSION_TYPES.keys())}")
    
    # Validate duration
    if not SessionValidators.validate_duration(duration, session_type):
        if session_type in SessionValidators.VALID_SESSION_TYPES:
            limits = SessionValidators.VALID_SESSION_TYPES[session_type]
            errors.append(f"Duration must be between {limits['min_duration']} and {limits['max_duration']} minutes for {session_type} sessions")
        else:
            errors.append("Invalid duration")
    
    # Business rule validations
    if not BusinessRuleValidators.is_reasonable_session_duration(duration):
        errors.append("Session duration must be between 5 and 300 minutes")
    
    return errors
