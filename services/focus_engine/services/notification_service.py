"""
Notification Service
Session reminders, break alerts, achievement notifications, and productivity milestones
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, asdict
import asyncio
import logging
from abc import ABC, abstractmethod

from ..models.session_models import FocusSession
from ..routers.websockets import broadcast_session_update

logger = logging.getLogger("focus_engine.notifications")


class NotificationType(Enum):
    """Types of notifications"""
    SESSION_REMINDER = "session_reminder"
    BREAK_REMINDER = "break_reminder"
    SESSION_COMPLETE = "session_complete"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    STREAK_MILESTONE = "streak_milestone"
    PRODUCTIVITY_MILESTONE = "productivity_milestone"
    OPTIMAL_TIME_SUGGESTION = "optimal_time_suggestion"
    INTERRUPTION_ALERT = "interruption_alert"
    WEEKLY_SUMMARY = "weekly_summary"
    GOAL_PROGRESS = "goal_progress"


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class NotificationMessage:
    """Structure for notification messages"""
    id: str
    user_id: str
    type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    scheduled_time: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = None
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(hours=24)


class NotificationChannel(ABC):
    """Abstract base class for notification channels"""
    
    @abstractmethod
    async def send(self, notification: NotificationMessage) -> bool:
        """Send notification through this channel"""
        pass


class WebSocketChannel(NotificationChannel):
    """WebSocket notification channel for real-time updates"""
    
    async def send(self, notification: NotificationMessage) -> bool:
        """Send notification via WebSocket"""
        try:
            await broadcast_session_update(notification.user_id, {
                "type": "notification",
                "notification": {
                    "id": notification.id,
                    "type": notification.type.value,
                    "priority": notification.priority.value,
                    "title": notification.title,
                    "message": notification.message,
                    "data": notification.data,
                    "timestamp": notification.created_at.isoformat()
                }
            })
            return True
        except Exception as e:
            logger.error(f"Failed to send WebSocket notification: {e}")
            return False


class EmailChannel(NotificationChannel):
    """Email notification channel (placeholder for future implementation)"""
    
    async def send(self, notification: NotificationMessage) -> bool:
        """Send notification via email (placeholder)"""
        # TODO: Implement email sending
        logger.info(f"EMAIL: {notification.title} - {notification.message}")
        return True


class PushChannel(NotificationChannel):
    """Push notification channel (placeholder for future implementation)"""
    
    async def send(self, notification: NotificationMessage) -> bool:
        """Send push notification (placeholder)"""
        # TODO: Implement push notifications
        logger.info(f"PUSH: {notification.title} - {notification.message}")
        return True


class NotificationService:
    """Core notification management service"""
    
    def __init__(self):
        self.channels = {
            "websocket": WebSocketChannel(),
            "email": EmailChannel(),
            "push": PushChannel()
        }
        self.pending_notifications: List[NotificationMessage] = []
        self.user_preferences: Dict[str, Dict[str, Any]] = {}
    
    async def create_notification(self, 
                                user_id: str,
                                type: NotificationType,
                                title: str,
                                message: str,
                                priority: NotificationPriority = NotificationPriority.MEDIUM,
                                data: Optional[Dict[str, Any]] = None,
                                scheduled_time: Optional[datetime] = None) -> NotificationMessage:
        """Create a new notification"""
        
        import uuid
        notification = NotificationMessage(
            id=str(uuid.uuid4()),
            user_id=user_id,
            type=type,
            priority=priority,
            title=title,
            message=message,
            data=data,
            scheduled_time=scheduled_time
        )
        
        # Send immediately if not scheduled
        if scheduled_time is None or scheduled_time <= datetime.utcnow():
            await self._send_notification(notification)
        else:
            # Store for later sending
            self.pending_notifications.append(notification)
            logger.info(f"Scheduled notification {notification.id} for {scheduled_time}")
        
        return notification
    
    async def _send_notification(self, notification: NotificationMessage) -> bool:
        """Send notification through appropriate channels"""
        
        # Check user preferences
        user_prefs = self.user_preferences.get(notification.user_id, {})
        enabled_channels = user_prefs.get("channels", ["websocket"])
        
        # Check if this notification type is enabled
        disabled_types = user_prefs.get("disabled_types", [])
        if notification.type.value in disabled_types:
            logger.debug(f"Notification type {notification.type.value} disabled for user {notification.user_id}")
            return False
        
        success = False
        for channel_name in enabled_channels:
            if channel_name in self.channels:
                try:
                    channel_success = await self.channels[channel_name].send(notification)
                    success = success or channel_success
                except Exception as e:
                    logger.error(f"Failed to send via {channel_name}: {e}")
        
        if success:
            notification.sent_at = datetime.utcnow()
            logger.info(f"Notification {notification.id} sent successfully")
        
        return success
    
    async def process_scheduled_notifications(self):
        """Process and send scheduled notifications"""
        current_time = datetime.utcnow()
        
        to_send = [
            notif for notif in self.pending_notifications 
            if notif.scheduled_time and notif.scheduled_time <= current_time
        ]
        
        for notification in to_send:
            await self._send_notification(notification)
            self.pending_notifications.remove(notification)
    
    def set_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Set notification preferences for a user"""
        self.user_preferences[user_id] = preferences
        logger.info(f"Updated notification preferences for user {user_id}")
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get notification preferences for a user"""
        return self.user_preferences.get(user_id, {
            "channels": ["websocket"],
            "disabled_types": [],
            "quiet_hours": {"start": "22:00", "end": "08:00"},
            "break_reminders": True,
            "session_reminders": True,
            "achievement_notifications": True
        })


class SessionReminderService:
    """Service for session-related reminders and alerts"""
    
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service
    
    async def schedule_session_reminder(self, 
                                      user_id: str,
                                      session_type: str = "pomodoro",
                                      reminder_time: datetime = None) -> NotificationMessage:
        """Schedule a session start reminder"""
        
        if reminder_time is None:
            reminder_time = datetime.utcnow() + timedelta(minutes=15)
        
        return await self.notification_service.create_notification(
            user_id=user_id,
            type=NotificationType.SESSION_REMINDER,
            title="Focus Session Reminder",
            message=f"Time for your {session_type} session! Ready to focus?",
            priority=NotificationPriority.MEDIUM,
            data={"session_type": session_type},
            scheduled_time=reminder_time
        )
    
    async def schedule_break_reminder(self,
                                    user_id: str,
                                    session_id: str,
                                    break_duration: int = 5) -> NotificationMessage:
        """Schedule a break reminder after session completion"""
        
        reminder_time = datetime.utcnow() + timedelta(minutes=break_duration)
        
        return await self.notification_service.create_notification(
            user_id=user_id,
            type=NotificationType.BREAK_REMINDER,
            title="Break Time Over",
            message=f"Your {break_duration}-minute break is over. Ready for another session?",
            priority=NotificationPriority.MEDIUM,
            data={"session_id": session_id, "break_duration": break_duration},
            scheduled_time=reminder_time
        )
    
    async def notify_session_complete(self,
                                    user_id: str,
                                    session: FocusSession) -> NotificationMessage:
        """Notify when a session is completed"""
        
        duration = session.actual_duration or session.planned_duration
        
        return await self.notification_service.create_notification(
            user_id=user_id,
            type=NotificationType.SESSION_COMPLETE,
            title="Session Complete!",
            message=f"Great job! You completed a {duration}-minute {session.session_type} session.",
            priority=NotificationPriority.HIGH,
            data={
                "session_id": str(session.id),
                "duration": duration,
                "session_type": session.session_type
            }
        )
    
    async def notify_interruption_alert(self,
                                      user_id: str,
                                      session_id: str,
                                      interruption_count: int) -> NotificationMessage:
        """Alert about excessive interruptions"""
        
        if interruption_count >= 3:
            return await self.notification_service.create_notification(
                user_id=user_id,
                type=NotificationType.INTERRUPTION_ALERT,
                title="High Interruption Alert",
                message=f"You've had {interruption_count} interruptions. Consider enabling 'Do Not Disturb' mode.",
                priority=NotificationPriority.HIGH,
                data={"session_id": session_id, "interruption_count": interruption_count}
            )


class AchievementNotificationService:
    """Service for achievement and milestone notifications"""
    
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service
    
    async def notify_streak_milestone(self,
                                    user_id: str,
                                    streak_days: int) -> NotificationMessage:
        """Notify about streak milestones"""
        
        milestone_messages = {
            3: "3-day streak! You're building great habits!",
            7: "One week streak! You're on fire! 🔥",
            14: "Two week streak! Incredible consistency!",
            30: "One month streak! You're a focus master! 🏆",
            50: "50-day streak! Absolutely phenomenal!",
            100: "100-day streak! You're a legend! 🎉"
        }
        
        if streak_days in milestone_messages:
            return await self.notification_service.create_notification(
                user_id=user_id,
                type=NotificationType.STREAK_MILESTONE,
                title=f"{streak_days}-Day Streak!",
                message=milestone_messages[streak_days],
                priority=NotificationPriority.HIGH,
                data={"streak_days": streak_days, "milestone": True}
            )
    
    async def notify_productivity_milestone(self,
                                          user_id: str,
                                          total_hours: float,
                                          milestone_type: str) -> NotificationMessage:
        """Notify about productivity milestones"""
        
        return await self.notification_service.create_notification(
            user_id=user_id,
            type=NotificationType.PRODUCTIVITY_MILESTONE,
            title=f"Productivity Milestone: {milestone_type}",
            message=f"Amazing! You've completed {total_hours:.1f} hours of focused work!",
            priority=NotificationPriority.HIGH,
            data={"total_hours": total_hours, "milestone_type": milestone_type}
        )
    
    async def notify_achievement_unlocked(self,
                                        user_id: str,
                                        achievement: Dict[str, Any]) -> NotificationMessage:
        """Notify about unlocked achievements"""
        
        return await self.notification_service.create_notification(
            user_id=user_id,
            type=NotificationType.ACHIEVEMENT_UNLOCKED,
            title="Achievement Unlocked!",
            message=f"🏆 {achievement['title']}: {achievement['description']}",
            priority=NotificationPriority.HIGH,
            data={"achievement": achievement}
        )


class SmartReminderService:
    """Intelligent reminder service based on user patterns"""
    
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service
    
    async def suggest_optimal_session_time(self,
                                         db: Session,
                                         user_id: str) -> Optional[NotificationMessage]:
        """Suggest optimal time for next session based on patterns"""
        
        # Analyze user's peak productivity hours
        from ..services.analytics_service import SessionAnalytics
        
        hourly_patterns = SessionAnalytics.calculate_hourly_patterns(db, user_id, 30)
        
        if hourly_patterns["peak_productivity_hours"]:
            current_hour = datetime.utcnow().hour
            best_hours = [h["hour"] for h in hourly_patterns["peak_productivity_hours"][:3]]
            
            # Find next optimal hour
            next_optimal = None
            for hour in best_hours:
                if hour > current_hour:
                    next_optimal = hour
                    break
            
            if next_optimal:
                optimal_time = datetime.utcnow().replace(
                    hour=next_optimal, minute=0, second=0, microsecond=0
                )
                
                if optimal_time > datetime.utcnow():
                    reminder_time = optimal_time - timedelta(minutes=10)
                    
                    return await self.notification_service.create_notification(
                        user_id=user_id,
                        type=NotificationType.OPTIMAL_TIME_SUGGESTION,
                        title="Optimal Focus Time",
                        message=f"Based on your patterns, {next_optimal}:00 is one of your most productive hours. Ready to start a session?",
                        priority=NotificationPriority.MEDIUM,
                        data={"optimal_hour": next_optimal, "pattern_based": True},
                        scheduled_time=reminder_time
                    )
    
    async def generate_weekly_summary(self,
                                    db: Session,
                                    user_id: str) -> NotificationMessage:
        """Generate weekly productivity summary"""
        
        from ..services.analytics_service import SessionAnalytics
        
        stats = SessionAnalytics.calculate_user_stats(db, user_id, 7)
        
        summary_message = f"""
        📊 Your Week in Focus:
        • {stats['total_sessions']} sessions completed
        • {stats['total_focus_time_minutes']//60:.1f} hours of focused work
        • {stats['completion_rate']:.1%} completion rate
        • Current streak: {stats['current_streak_days']} days
        """
        
        return await self.notification_service.create_notification(
            user_id=user_id,
            type=NotificationType.WEEKLY_SUMMARY,
            title="Weekly Focus Summary",
            message=summary_message.strip(),
            priority=NotificationPriority.LOW,
            data=stats
        )


# Global notification service instance
notification_service = NotificationService()
session_reminder_service = SessionReminderService(notification_service)
achievement_service = AchievementNotificationService(notification_service)
smart_reminder_service = SmartReminderService(notification_service)
