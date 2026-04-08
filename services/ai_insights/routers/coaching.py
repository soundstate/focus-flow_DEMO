"""Coaching router for the AI Insights service API."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/users/{user_id}/goals")
async def get_goals(user_id: str):
    """Get user goals (hardcoded for now, will be dynamic later)."""
    return {
        "user_id": user_id,
        "goals": [
            {
                "id": "goal_1",
                "title": "Improve focus consistency",
                "description": "Complete at least 4 focus sessions per day",
                "target": 4,
                "unit": "sessions/day",
                "status": "active",
            },
            {
                "id": "goal_2",
                "title": "Reduce interruptions",
                "description": "Keep interruptions below 3 per session",
                "target": 3,
                "unit": "interruptions/session",
                "status": "active",
            },
            {
                "id": "goal_3",
                "title": "Build a streak",
                "description": "Maintain a 7-day focus streak",
                "target": 7,
                "unit": "days",
                "status": "active",
            },
        ],
    }
