"""
Timer Utilities
Helper functions for time calculations and formatting
"""

from datetime import datetime, timedelta
from typing import Optional
import asyncio


class TimerUtils:
    """Utility class for timer-related operations"""
    
    @staticmethod
    def format_duration(minutes: int) -> str:
        """Format duration in minutes to human-readable string"""
        if minutes < 60:
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        
        hours = minutes // 60
        remaining_minutes = minutes % 60
        
        if remaining_minutes == 0:
            return f"{hours} hour{'s' if hours != 1 else ''}"
        
        return f"{hours}h {remaining_minutes}m"
    
    @staticmethod
    def get_remaining_time(start_time: datetime, planned_duration: int) -> Optional[int]:
        """Get remaining time in minutes for a session"""
        if not start_time:
            return None
            
        elapsed = datetime.utcnow() - start_time
        elapsed_minutes = int(elapsed.total_seconds() / 60)
        
        remaining = planned_duration - elapsed_minutes
        return max(0, remaining)
    
    @staticmethod
    def calculate_progress(start_time: datetime, planned_duration: int) -> float:
        """Calculate session progress as percentage (0.0 to 1.0)"""
        if not start_time:
            return 0.0
            
        elapsed = datetime.utcnow() - start_time
        elapsed_minutes = elapsed.total_seconds() / 60
        
        progress = elapsed_minutes / planned_duration
        return min(1.0, max(0.0, progress))
    
    @staticmethod
    def is_session_expired(start_time: datetime, planned_duration: int) -> bool:
        """Check if a session has exceeded its planned duration"""
        if not start_time:
            return False
            
        elapsed = datetime.utcnow() - start_time
        elapsed_minutes = elapsed.total_seconds() / 60
        
        return elapsed_minutes > planned_duration
    
    @staticmethod
    def get_next_break_time(session_type: str = "pomodoro") -> int:
        """Get recommended break duration based on session type"""
        break_times = {
            "pomodoro": 5,  # 5 minute break
            "long_focus": 15,  # 15 minute break
            "deep_work": 20,  # 20 minute break
            "study": 10,  # 10 minute break
        }
        
        return break_times.get(session_type, 5)


class CountdownTimer:
    """Async countdown timer for session management"""
    
    def __init__(self, duration_minutes: int):
        self.duration_minutes = duration_minutes
        self.start_time = None
        self.is_running = False
        self.is_paused = False
        self.pause_time = None
        self.total_pause_duration = 0
    
    async def start(self):
        """Start the countdown timer"""
        self.start_time = datetime.utcnow()
        self.is_running = True
        self.is_paused = False
    
    async def pause(self):
        """Pause the timer"""
        if self.is_running and not self.is_paused:
            self.pause_time = datetime.utcnow()
            self.is_paused = True
    
    async def resume(self):
        """Resume the timer from pause"""
        if self.is_running and self.is_paused and self.pause_time:
            # Add pause duration to total
            pause_duration = datetime.utcnow() - self.pause_time
            self.total_pause_duration += pause_duration.total_seconds()
            
            self.is_paused = False
            self.pause_time = None
    
    async def stop(self):
        """Stop the timer"""
        self.is_running = False
        self.is_paused = False
    
    def get_elapsed_minutes(self) -> int:
        """Get elapsed time in minutes (excluding pause time)"""
        if not self.start_time:
            return 0
        
        current_time = datetime.utcnow()
        
        # If paused, use pause time as end time
        if self.is_paused and self.pause_time:
            current_time = self.pause_time
        
        elapsed_seconds = (current_time - self.start_time).total_seconds()
        elapsed_seconds -= self.total_pause_duration
        
        return max(0, int(elapsed_seconds / 60))
    
    def get_remaining_minutes(self) -> int:
        """Get remaining time in minutes"""
        elapsed = self.get_elapsed_minutes()
        return max(0, self.duration_minutes - elapsed)
    
    def is_expired(self) -> bool:
        """Check if timer has expired"""
        return self.get_remaining_minutes() == 0
