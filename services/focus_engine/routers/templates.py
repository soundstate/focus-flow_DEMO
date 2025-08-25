"""
Templates Router
Endpoints for session templates and productivity presets
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from ..database.connection import get_db
from ..services.template_service import template_service, TemplateCategory, DifficultyLevel

router = APIRouter()


class TemplateCreateRequest(BaseModel):
    """Request model for creating templates"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field("", max_length=500)
    category: str = Field("custom")
    difficulty: str = Field("intermediate")
    session_type: str = Field(..., min_length=1)
    duration_minutes: int = Field(..., ge=5, le=300)
    break_duration_minutes: int = Field(5, ge=0, le=60)
    allow_interruptions: bool = Field(False)
    auto_start_breaks: bool = Field(True)
    reminder_intervals: List[int] = Field([15, 5])
    focus_music_enabled: bool = Field(False)
    distraction_blocking: bool = Field(False)
    productivity_tracking: bool = Field(True)
    background_theme: Optional[str] = None
    notification_sound: Optional[str] = None
    completion_reward: Optional[str] = None
    tags: List[str] = Field([])


class TemplateUpdateRequest(BaseModel):
    """Request model for updating templates"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = None
    difficulty: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=5, le=300)
    break_duration_minutes: Optional[int] = Field(None, ge=0, le=60)
    allow_interruptions: Optional[bool] = None
    auto_start_breaks: Optional[bool] = None
    reminder_intervals: Optional[List[int]] = None
    focus_music_enabled: Optional[bool] = None
    distraction_blocking: Optional[bool] = None
    productivity_tracking: Optional[bool] = None
    background_theme: Optional[str] = None
    notification_sound: Optional[str] = None
    completion_reward: Optional[str] = None
    tags: Optional[List[str]] = None
    is_favorite: Optional[bool] = None


@router.get("/users/{user_id}/templates")
def get_user_templates(
    user_id: str,
    category: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    include_system: bool = Query(True)
):
    """Get templates available to a user"""
    
    # Parse category and difficulty enums
    category_enum = None
    if category:
        try:
            category_enum = TemplateCategory(category.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
    
    difficulty_enum = None
    if difficulty:
        try:
            difficulty_enum = DifficultyLevel(difficulty.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid difficulty: {difficulty}")
    
    templates = template_service.get_templates_for_user(
        user_id, category_enum, difficulty_enum, include_system
    )
    
    return {
        "templates": [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "category": t.category.value,
                "difficulty": t.difficulty.value,
                "session_type": t.session_type,
                "duration_minutes": t.duration_minutes,
                "break_duration_minutes": t.break_duration_minutes,
                "is_favorite": t.is_favorite,
                "is_system_template": t.is_system_template,
                "usage_count": t.usage_count,
                "average_completion_rate": t.average_completion_rate,
                "tags": t.tags,
                "created_at": t.created_at.isoformat() if t.created_at else None
            } for t in templates
        ],
        "total_count": len(templates)
    }


@router.get("/users/{user_id}/templates/{template_id}")
def get_template_details(user_id: str, template_id: str):
    """Get detailed information about a specific template"""
    
    template = template_service.get_template_by_id(template_id, user_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {
        "id": template.id,
        "user_id": template.user_id,
        "name": template.name,
        "description": template.description,
        "category": template.category.value,
        "difficulty": template.difficulty.value,
        "session_type": template.session_type,
        "duration_minutes": template.duration_minutes,
        "break_duration_minutes": template.break_duration_minutes,
        "allow_interruptions": template.allow_interruptions,
        "auto_start_breaks": template.auto_start_breaks,
        "reminder_intervals": template.reminder_intervals,
        "focus_music_enabled": template.focus_music_enabled,
        "distraction_blocking": template.distraction_blocking,
        "productivity_tracking": template.productivity_tracking,
        "background_theme": template.background_theme,
        "notification_sound": template.notification_sound,
        "completion_reward": template.completion_reward,
        "tags": template.tags,
        "is_favorite": template.is_favorite,
        "is_system_template": template.is_system_template,
        "usage_count": template.usage_count,
        "average_completion_rate": template.average_completion_rate,
        "created_at": template.created_at.isoformat() if template.created_at else None,
        "updated_at": template.updated_at.isoformat() if template.updated_at else None
    }


@router.post("/users/{user_id}/templates")
def create_custom_template(user_id: str, template_data: TemplateCreateRequest):
    """Create a new custom template for a user"""
    
    try:
        template = template_service.create_custom_template(
            user_id, template_data.dict()
        )
        
        return {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "category": template.category.value,
            "difficulty": template.difficulty.value,
            "session_type": template.session_type,
            "duration_minutes": template.duration_minutes,
            "created_at": template.created_at.isoformat()
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/users/{user_id}/templates/{template_id}")
def update_template(user_id: str, template_id: str, updates: TemplateUpdateRequest):
    """Update an existing template"""
    
    # Filter out None values
    update_data = {k: v for k, v in updates.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No updates provided")
    
    template = template_service.update_template(template_id, user_id, update_data)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found or not owned by user")
    
    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "updated_at": template.updated_at.isoformat()
    }


@router.delete("/users/{user_id}/templates/{template_id}")
def delete_template(user_id: str, template_id: str):
    """Delete a user's custom template"""
    
    success = template_service.delete_template(template_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found or not owned by user")
    
    return {"message": "Template deleted successfully"}


@router.get("/users/{user_id}/templates/recommendations")
def get_template_recommendations(user_id: str, count: int = Query(5, ge=1, le=20), db: Session = Depends(get_db)):
    """Get personalized template recommendations for a user"""
    
    templates = template_service.get_recommended_templates(user_id, db, count)
    
    return {
        "recommendations": [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "category": t.category.value,
                "difficulty": t.difficulty.value,
                "session_type": t.session_type,
                "duration_minutes": t.duration_minutes,
                "usage_count": t.usage_count,
                "average_completion_rate": t.average_completion_rate,
                "tags": t.tags,
                "is_system_template": t.is_system_template
            } for t in templates
        ]
    }


@router.get("/users/{user_id}/presets")
def get_user_presets(user_id: str):
    """Get productivity presets available to a user"""
    
    presets = template_service.get_presets_for_user(user_id)
    
    return {
        "presets": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "templates": p.templates,
                "daily_goal_sessions": p.daily_goal_sessions,
                "daily_goal_minutes": p.daily_goal_minutes,
                "weekly_goal_sessions": p.weekly_goal_sessions,
                "weekly_goal_minutes": p.weekly_goal_minutes,
                "suggested_start_times": p.suggested_start_times,
                "suggested_days": p.suggested_days,
                "includes_breaks": p.includes_breaks,
                "adaptive_difficulty": p.adaptive_difficulty,
                "progress_tracking": p.progress_tracking
            } for p in presets
        ]
    }


@router.get("/users/{user_id}/presets/{preset_id}")
def get_preset_details(user_id: str, preset_id: str):
    """Get detailed information about a specific preset"""
    
    preset = template_service.get_preset_by_id(preset_id, user_id)
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    
    # Get template details for the preset
    template_details = []
    for template_id in preset.templates:
        template = template_service.get_template_by_id(template_id)
        if template:
            template_details.append({
                "id": template.id,
                "name": template.name,
                "duration_minutes": template.duration_minutes,
                "session_type": template.session_type,
                "description": template.description
            })
    
    return {
        "id": preset.id,
        "name": preset.name,
        "description": preset.description,
        "templates": preset.templates,
        "template_details": template_details,
        "daily_goal_sessions": preset.daily_goal_sessions,
        "daily_goal_minutes": preset.daily_goal_minutes,
        "weekly_goal_sessions": preset.weekly_goal_sessions,
        "weekly_goal_minutes": preset.weekly_goal_minutes,
        "suggested_start_times": preset.suggested_start_times,
        "suggested_days": preset.suggested_days,
        "includes_breaks": preset.includes_breaks,
        "adaptive_difficulty": preset.adaptive_difficulty,
        "progress_tracking": preset.progress_tracking,
        "created_at": preset.created_at.isoformat() if preset.created_at else None
    }


@router.get("/categories")
def get_template_categories():
    """Get available template categories"""
    
    return {
        "categories": [
            {
                "id": category.value,
                "name": category.value.replace("_", " ").title(),
                "description": _get_category_description(category)
            } for category in TemplateCategory
        ]
    }


@router.get("/difficulties")
def get_difficulty_levels():
    """Get available difficulty levels"""
    
    return {
        "difficulties": [
            {
                "id": difficulty.value,
                "name": difficulty.value.title(),
                "description": _get_difficulty_description(difficulty)
            } for difficulty in DifficultyLevel
        ]
    }


def _get_category_description(category: TemplateCategory) -> str:
    """Get description for template category"""
    descriptions = {
        TemplateCategory.PRODUCTIVITY: "General productivity and focus sessions",
        TemplateCategory.STUDY: "Academic study and learning sessions",
        TemplateCategory.CREATIVE: "Creative work and artistic sessions",
        TemplateCategory.WELLNESS: "Mindfulness and wellness breaks",
        TemplateCategory.WORK: "Professional and deep work sessions",
        TemplateCategory.PERSONAL: "Personal development and hobbies",
        TemplateCategory.CUSTOM: "User-created custom templates"
    }
    return descriptions.get(category, "")


def _get_difficulty_description(difficulty: DifficultyLevel) -> str:
    """Get description for difficulty level"""
    descriptions = {
        DifficultyLevel.BEGINNER: "Perfect for those new to focused work sessions",
        DifficultyLevel.INTERMEDIATE: "Suitable for users with some focus experience",
        DifficultyLevel.ADVANCED: "Challenging sessions for experienced users",
        DifficultyLevel.EXPERT: "Intensive sessions for focus masters"
    }
    return descriptions.get(difficulty, "")
