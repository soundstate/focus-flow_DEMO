"""
Session Template Service
Customizable session templates, productivity presets, and user configurations
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
import logging

from ..models.session_models import FocusSession

logger = logging.getLogger("focus_engine.templates")


class TemplateCategory(Enum):
    """Categories for session templates"""
    PRODUCTIVITY = "productivity"
    STUDY = "study"
    CREATIVE = "creative"
    WELLNESS = "wellness"
    WORK = "work"
    PERSONAL = "personal"
    CUSTOM = "custom"


class DifficultyLevel(Enum):
    """Difficulty levels for templates"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class SessionTemplate:
    """Structure for session templates"""
    id: str
    user_id: Optional[str]  # None for system templates
    name: str
    description: str
    category: TemplateCategory
    difficulty: DifficultyLevel
    
    # Session configuration
    session_type: str
    duration_minutes: int
    break_duration_minutes: int
    
    # Advanced settings
    allow_interruptions: bool = False
    auto_start_breaks: bool = True
    reminder_intervals: List[int] = None  # Minutes before session to remind
    
    # Productivity features
    focus_music_enabled: bool = False
    distraction_blocking: bool = False
    productivity_tracking: bool = True
    
    # Customizations
    background_theme: Optional[str] = None
    notification_sound: Optional[str] = None
    completion_reward: Optional[str] = None
    
    # Metadata
    tags: List[str] = None
    is_favorite: bool = False
    is_system_template: bool = False
    usage_count: int = 0
    average_completion_rate: float = 0.0
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.reminder_intervals is None:
            self.reminder_intervals = [15, 5]  # 15 and 5 minutes before
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class ProductivityPreset:
    """Predefined productivity configurations"""
    id: str
    name: str
    description: str
    templates: List[str]  # Template IDs in sequence
    daily_goal_sessions: int
    daily_goal_minutes: int
    weekly_goal_sessions: int
    weekly_goal_minutes: int
    
    # Scheduling
    suggested_start_times: List[str]  # "HH:MM" format
    suggested_days: List[str]  # Days of week
    
    # Features
    includes_breaks: bool = True
    adaptive_difficulty: bool = False
    progress_tracking: bool = True
    
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class SystemTemplates:
    """Predefined system templates for common use cases"""
    
    @staticmethod
    def get_all_system_templates() -> List[SessionTemplate]:
        """Get all predefined system templates"""
        return [
            # Pomodoro variants
            SessionTemplate(
                id="pomodoro_classic",
                user_id=None,
                name="Classic Pomodoro",
                description="Traditional 25-minute focus session with 5-minute break",
                category=TemplateCategory.PRODUCTIVITY,
                difficulty=DifficultyLevel.BEGINNER,
                session_type="pomodoro",
                duration_minutes=25,
                break_duration_minutes=5,
                tags=["traditional", "beginner-friendly"],
                is_system_template=True
            ),
            
            SessionTemplate(
                id="pomodoro_extended",
                user_id=None,
                name="Extended Pomodoro",
                description="Longer 45-minute focus session with 10-minute break",
                category=TemplateCategory.PRODUCTIVITY,
                difficulty=DifficultyLevel.INTERMEDIATE,
                session_type="pomodoro",
                duration_minutes=45,
                break_duration_minutes=10,
                tags=["extended", "intermediate"],
                is_system_template=True
            ),
            
            # Deep work sessions
            SessionTemplate(
                id="deep_work_90",
                user_id=None,
                name="Deep Work 90",
                description="90-minute deep focus session for complex tasks",
                category=TemplateCategory.WORK,
                difficulty=DifficultyLevel.ADVANCED,
                session_type="deep_work",
                duration_minutes=90,
                break_duration_minutes=20,
                distraction_blocking=True,
                tags=["deep-work", "complex-tasks"],
                is_system_template=True
            ),
            
            SessionTemplate(
                id="deep_work_120",
                user_id=None,
                name="Deep Work 120",
                description="2-hour intensive deep work session",
                category=TemplateCategory.WORK,
                difficulty=DifficultyLevel.EXPERT,
                session_type="deep_work",
                duration_minutes=120,
                break_duration_minutes=30,
                distraction_blocking=True,
                focus_music_enabled=True,
                tags=["intensive", "expert-level"],
                is_system_template=True
            ),
            
            # Study sessions
            SessionTemplate(
                id="study_focused",
                user_id=None,
                name="Focused Study",
                description="50-minute study session with active recall techniques",
                category=TemplateCategory.STUDY,
                difficulty=DifficultyLevel.INTERMEDIATE,
                session_type="study",
                duration_minutes=50,
                break_duration_minutes=10,
                productivity_tracking=True,
                tags=["study", "active-recall"],
                is_system_template=True
            ),
            
            SessionTemplate(
                id="exam_prep",
                user_id=None,
                name="Exam Preparation",
                description="Intensive 75-minute exam prep session",
                category=TemplateCategory.STUDY,
                difficulty=DifficultyLevel.ADVANCED,
                session_type="study",
                duration_minutes=75,
                break_duration_minutes=15,
                distraction_blocking=True,
                reminder_intervals=[30, 15, 5],
                tags=["exam-prep", "intensive"],
                is_system_template=True
            ),
            
            # Creative sessions
            SessionTemplate(
                id="creative_flow",
                user_id=None,
                name="Creative Flow",
                description="60-minute creative work session with minimal interruptions",
                category=TemplateCategory.CREATIVE,
                difficulty=DifficultyLevel.INTERMEDIATE,
                session_type="creative",
                duration_minutes=60,
                break_duration_minutes=15,
                allow_interruptions=False,
                focus_music_enabled=True,
                tags=["creative", "flow-state"],
                is_system_template=True
            ),
            
            # Quick sessions
            SessionTemplate(
                id="quick_task",
                user_id=None,
                name="Quick Task",
                description="15-minute sprint for small tasks",
                category=TemplateCategory.PRODUCTIVITY,
                difficulty=DifficultyLevel.BEGINNER,
                session_type="quick",
                duration_minutes=15,
                break_duration_minutes=5,
                reminder_intervals=[5],
                tags=["quick", "small-tasks"],
                is_system_template=True
            ),
            
            # Wellness/break sessions
            SessionTemplate(
                id="mindful_break",
                user_id=None,
                name="Mindful Break",
                description="10-minute mindfulness and relaxation break",
                category=TemplateCategory.WELLNESS,
                difficulty=DifficultyLevel.BEGINNER,
                session_type="break",
                duration_minutes=10,
                break_duration_minutes=0,
                focus_music_enabled=True,
                tags=["mindfulness", "relaxation"],
                is_system_template=True
            )
        ]
    
    @staticmethod
    def get_productivity_presets() -> List[ProductivityPreset]:
        """Get predefined productivity presets"""
        return [
            ProductivityPreset(
                id="beginner_routine",
                name="Beginner's Routine",
                description="Perfect for starting your focus journey",
                templates=["pomodoro_classic", "quick_task", "mindful_break"],
                daily_goal_sessions=4,
                daily_goal_minutes=120,
                weekly_goal_sessions=20,
                weekly_goal_minutes=600,
                suggested_start_times=["09:00", "14:00", "19:00"],
                suggested_days=["monday", "tuesday", "wednesday", "thursday", "friday"]
            ),
            
            ProductivityPreset(
                id="professional_flow",
                name="Professional Flow",
                description="Optimized for professional productivity",
                templates=["pomodoro_extended", "deep_work_90", "quick_task"],
                daily_goal_sessions=6,
                daily_goal_minutes=240,
                weekly_goal_sessions=30,
                weekly_goal_minutes=1200,
                suggested_start_times=["09:00", "11:00", "14:00", "16:00"],
                suggested_days=["monday", "tuesday", "wednesday", "thursday", "friday"],
                adaptive_difficulty=True
            ),
            
            ProductivityPreset(
                id="student_intensive",
                name="Student Intensive",
                description="Designed for serious study sessions",
                templates=["study_focused", "exam_prep", "mindful_break"],
                daily_goal_sessions=5,
                daily_goal_minutes=200,
                weekly_goal_sessions=35,
                weekly_goal_minutes=1400,
                suggested_start_times=["09:00", "14:00", "19:00"],
                suggested_days=["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            ),
            
            ProductivityPreset(
                id="creative_artist",
                name="Creative Artist",
                description="For artists, writers, and creative professionals",
                templates=["creative_flow", "pomodoro_extended", "mindful_break"],
                daily_goal_sessions=4,
                daily_goal_minutes=180,
                weekly_goal_sessions=24,
                weekly_goal_minutes=1080,
                suggested_start_times=["10:00", "14:00", "20:00"],
                suggested_days=["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
            ),
            
            ProductivityPreset(
                id="deep_work_expert",
                name="Deep Work Expert",
                description="For advanced practitioners of deep work",
                templates=["deep_work_120", "deep_work_90", "pomodoro_extended"],
                daily_goal_sessions=4,
                daily_goal_minutes=300,
                weekly_goal_sessions=20,
                weekly_goal_minutes=1500,
                suggested_start_times=["09:00", "14:00"],
                suggested_days=["monday", "tuesday", "wednesday", "thursday", "friday"],
                adaptive_difficulty=True
            )
        ]


class TemplateService:
    """Service for managing session templates and presets"""
    
    def __init__(self):
        self.user_templates: Dict[str, List[SessionTemplate]] = {}
        self.user_presets: Dict[str, List[ProductivityPreset]] = {}
        self.system_templates = SystemTemplates.get_all_system_templates()
        self.system_presets = SystemTemplates.get_productivity_presets()
    
    def get_templates_for_user(self, user_id: str, 
                              category: Optional[TemplateCategory] = None,
                              difficulty: Optional[DifficultyLevel] = None,
                              include_system: bool = True) -> List[SessionTemplate]:
        """Get templates available to a user"""
        
        templates = []
        
        # Add system templates
        if include_system:
            templates.extend(self.system_templates)
        
        # Add user's custom templates
        user_templates = self.user_templates.get(user_id, [])
        templates.extend(user_templates)
        
        # Filter by criteria
        if category:
            templates = [t for t in templates if t.category == category]
        
        if difficulty:
            templates = [t for t in templates if t.difficulty == difficulty]
        
        # Sort by usage and favorites
        templates.sort(key=lambda t: (t.is_favorite, t.usage_count, t.name), reverse=True)
        
        return templates
    
    def get_template_by_id(self, template_id: str, user_id: Optional[str] = None) -> Optional[SessionTemplate]:
        """Get a specific template by ID"""
        
        # Check system templates
        for template in self.system_templates:
            if template.id == template_id:
                return template
        
        # Check user templates
        if user_id:
            user_templates = self.user_templates.get(user_id, [])
            for template in user_templates:
                if template.id == template_id:
                    return template
        
        return None
    
    def create_custom_template(self, user_id: str, template_data: Dict[str, Any]) -> SessionTemplate:
        """Create a new custom template for a user"""
        
        import uuid
        template_id = str(uuid.uuid4())
        
        template = SessionTemplate(
            id=template_id,
            user_id=user_id,
            name=template_data["name"],
            description=template_data.get("description", ""),
            category=TemplateCategory(template_data.get("category", "custom")),
            difficulty=DifficultyLevel(template_data.get("difficulty", "intermediate")),
            session_type=template_data["session_type"],
            duration_minutes=template_data["duration_minutes"],
            break_duration_minutes=template_data.get("break_duration_minutes", 5),
            allow_interruptions=template_data.get("allow_interruptions", False),
            auto_start_breaks=template_data.get("auto_start_breaks", True),
            reminder_intervals=template_data.get("reminder_intervals", [15, 5]),
            focus_music_enabled=template_data.get("focus_music_enabled", False),
            distraction_blocking=template_data.get("distraction_blocking", False),
            productivity_tracking=template_data.get("productivity_tracking", True),
            background_theme=template_data.get("background_theme"),
            notification_sound=template_data.get("notification_sound"),
            completion_reward=template_data.get("completion_reward"),
            tags=template_data.get("tags", [])
        )
        
        # Store template
        if user_id not in self.user_templates:
            self.user_templates[user_id] = []
        self.user_templates[user_id].append(template)
        
        logger.info(f"Created custom template {template_id} for user {user_id}")
        return template
    
    def update_template(self, template_id: str, user_id: str, 
                       updates: Dict[str, Any]) -> Optional[SessionTemplate]:
        """Update an existing template"""
        
        template = self.get_template_by_id(template_id, user_id)
        if not template or template.user_id != user_id:
            return None  # Can only update own templates
        
        # Update fields
        for field, value in updates.items():
            if hasattr(template, field):
                setattr(template, field, value)
        
        template.updated_at = datetime.utcnow()
        
        logger.info(f"Updated template {template_id} for user {user_id}")
        return template
    
    def delete_template(self, template_id: str, user_id: str) -> bool:
        """Delete a user's custom template"""
        
        user_templates = self.user_templates.get(user_id, [])
        
        for i, template in enumerate(user_templates):
            if template.id == template_id and template.user_id == user_id:
                del user_templates[i]
                logger.info(f"Deleted template {template_id} for user {user_id}")
                return True
        
        return False
    
    def track_template_usage(self, template_id: str, user_id: Optional[str], 
                           completed: bool = True):
        """Track usage statistics for a template"""
        
        template = self.get_template_by_id(template_id, user_id)
        if template:
            template.usage_count += 1
            
            # Update completion rate
            if completed:
                # Simple running average update
                old_rate = template.average_completion_rate
                new_rate = (old_rate * (template.usage_count - 1) + 1.0) / template.usage_count
                template.average_completion_rate = new_rate
            else:
                # Session not completed
                old_rate = template.average_completion_rate
                new_rate = (old_rate * (template.usage_count - 1) + 0.0) / template.usage_count
                template.average_completion_rate = new_rate
    
    def get_recommended_templates(self, user_id: str, 
                                db: Session,
                                count: int = 5) -> List[SessionTemplate]:
        """Get personalized template recommendations"""
        
        # Analyze user's session history
        from ..services.analytics_service import SessionAnalytics
        
        try:
            user_stats = SessionAnalytics.calculate_user_stats(db, user_id, 30)
            type_performance = SessionAnalytics.calculate_session_type_performance(db, user_id, 30)
            
            # Get all available templates
            all_templates = self.get_templates_for_user(user_id)
            
            # Score templates based on user patterns
            scored_templates = []
            for template in all_templates:
                score = self._calculate_template_score(template, user_stats, type_performance)
                scored_templates.append((template, score))
            
            # Sort by score and return top recommendations
            scored_templates.sort(key=lambda x: x[1], reverse=True)
            return [template for template, score in scored_templates[:count]]
            
        except Exception as e:
            logger.error(f"Failed to get recommendations for user {user_id}: {e}")
            # Fallback to popular system templates
            return sorted(self.system_templates, 
                        key=lambda t: t.usage_count, reverse=True)[:count]
    
    def _calculate_template_score(self, template: SessionTemplate, 
                                user_stats: Dict[str, Any],
                                type_performance: Dict[str, Any]) -> float:
        """Calculate recommendation score for a template"""
        
        score = 0.0
        
        # Base score from template's success rate
        score += template.average_completion_rate * 0.3
        
        # Bonus for user's successful session types
        template_type = template.session_type
        if template_type in type_performance:
            user_success_rate = type_performance[template_type].get("completion_rate", 0)
            score += user_success_rate * 0.4
        
        # Duration preference matching
        avg_user_duration = user_stats.get("average_planned_duration", 30)
        duration_diff = abs(template.duration_minutes - avg_user_duration)
        duration_score = max(0, 1.0 - (duration_diff / 60))  # Penalize large differences
        score += duration_score * 0.2
        
        # Popularity bonus
        score += min(template.usage_count / 100, 0.1)  # Max 0.1 bonus for popular templates
        
        return score
    
    def get_presets_for_user(self, user_id: str) -> List[ProductivityPreset]:
        """Get productivity presets available to a user"""
        
        presets = list(self.system_presets)  # System presets
        user_presets = self.user_presets.get(user_id, [])
        presets.extend(user_presets)  # User's custom presets
        
        return presets
    
    def get_preset_by_id(self, preset_id: str, user_id: Optional[str] = None) -> Optional[ProductivityPreset]:
        """Get a specific preset by ID"""
        
        # Check system presets
        for preset in self.system_presets:
            if preset.id == preset_id:
                return preset
        
        # Check user presets
        if user_id:
            user_presets = self.user_presets.get(user_id, [])
            for preset in user_presets:
                if preset.id == preset_id:
                    return preset
        
        return None


# Global template service instance
template_service = TemplateService()
