"""
Analytics Service
Session statistics, productivity trends, and performance metrics
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import statistics
import logging

from ..models.session_models import FocusSession
from ..utils.timer import TimerUtils

logger = logging.getLogger("focus_engine.analytics")


class SessionAnalytics:
    """Core analytics calculations for focus sessions"""
    
    @staticmethod
    def calculate_user_stats(db: Session, user_id: str, 
                           days: int = 30) -> Dict[str, Any]:
        """Calculate comprehensive user statistics"""
        
        # Date range for analysis
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Base query for user sessions in date range
        sessions = db.query(FocusSession).filter(
            and_(
                FocusSession.user_id == user_id,
                FocusSession.start_time >= start_date,
                FocusSession.start_time <= end_date
            )
        ).all()
        
        if not sessions:
            return SessionAnalytics._empty_stats()
        
        # Basic counts
        total_sessions = len(sessions)
        completed_sessions = [s for s in sessions if s.status == "completed"]
        
        # Duration statistics
        total_minutes = sum(s.actual_duration or s.planned_duration for s in sessions)
        completed_minutes = sum(s.actual_duration or s.planned_duration for s in completed_sessions)
        
        # Completion rate
        completion_rate = len(completed_sessions) / total_sessions if total_sessions > 0 else 0
        
        # Average session duration
        avg_planned_duration = statistics.mean([s.planned_duration for s in sessions]) if sessions else 0
        avg_actual_duration = statistics.mean([
            s.actual_duration for s in sessions if s.actual_duration is not None
        ]) if any(s.actual_duration for s in sessions) else 0
        
        # Productivity score statistics
        productivity_scores = [s.productivity_score for s in sessions if s.productivity_score is not None]
        avg_productivity = statistics.mean(productivity_scores) if productivity_scores else 0
        
        # Focus quality distribution
        focus_quality_counts = defaultdict(int)
        for session in sessions:
            if session.focus_quality:
                focus_quality_counts[session.focus_quality] += 1
        
        # Session type distribution
        session_type_counts = defaultdict(int)
        for session in sessions:
            session_type_counts[session.session_type or "unknown"] += 1
        
        # Interruption statistics
        total_interruptions = sum(s.interruption_count or 0 for s in sessions)
        avg_interruptions = total_interruptions / total_sessions if total_sessions > 0 else 0
        
        # Streak calculation
        current_streak = SessionAnalytics._calculate_current_streak(sessions)
        longest_streak = SessionAnalytics._calculate_longest_streak(sessions)
        
        return {
            "period_days": days,
            "total_sessions": total_sessions,
            "completed_sessions": len(completed_sessions),
            "completion_rate": round(completion_rate, 3),
            "total_focus_time_minutes": total_minutes,
            "completed_focus_time_minutes": completed_minutes,
            "average_planned_duration": round(avg_planned_duration, 1),
            "average_actual_duration": round(avg_actual_duration, 1),
            "average_productivity_score": round(avg_productivity, 2),
            "total_interruptions": total_interruptions,
            "average_interruptions_per_session": round(avg_interruptions, 2),
            "focus_quality_distribution": dict(focus_quality_counts),
            "session_type_distribution": dict(session_type_counts),
            "current_streak_days": current_streak,
            "longest_streak_days": longest_streak,
            "analysis_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
    
    @staticmethod
    def calculate_daily_trends(db: Session, user_id: str, 
                             days: int = 30) -> List[Dict[str, Any]]:
        """Calculate daily productivity trends"""
        
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        # Get sessions grouped by date
        sessions = db.query(FocusSession).filter(
            and_(
                FocusSession.user_id == user_id,
                func.date(FocusSession.start_time) >= start_date,
                func.date(FocusSession.start_time) <= end_date
            )
        ).all()
        
        # Group sessions by date
        daily_sessions = defaultdict(list)
        for session in sessions:
            session_date = session.start_time.date()
            daily_sessions[session_date].append(session)
        
        # Calculate trends for each day
        trends = []
        for single_date in (start_date + timedelta(n) for n in range(days + 1)):
            day_sessions = daily_sessions.get(single_date, [])
            
            if day_sessions:
                completed = [s for s in day_sessions if s.status == "completed"]
                total_time = sum(s.actual_duration or s.planned_duration for s in day_sessions)
                avg_productivity = statistics.mean([
                    s.productivity_score for s in day_sessions 
                    if s.productivity_score is not None
                ]) if any(s.productivity_score for s in day_sessions) else 0
                
                trends.append({
                    "date": single_date.isoformat(),
                    "total_sessions": len(day_sessions),
                    "completed_sessions": len(completed),
                    "completion_rate": len(completed) / len(day_sessions),
                    "total_focus_time_minutes": total_time,
                    "average_productivity_score": round(avg_productivity, 2),
                    "total_interruptions": sum(s.interruption_count or 0 for s in day_sessions)
                })
            else:
                trends.append({
                    "date": single_date.isoformat(),
                    "total_sessions": 0,
                    "completed_sessions": 0,
                    "completion_rate": 0,
                    "total_focus_time_minutes": 0,
                    "average_productivity_score": 0,
                    "total_interruptions": 0
                })
        
        return trends
    
    @staticmethod
    def calculate_hourly_patterns(db: Session, user_id: str, 
                                days: int = 30) -> Dict[str, Any]:
        """Analyze productivity patterns by hour of day"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        sessions = db.query(FocusSession).filter(
            and_(
                FocusSession.user_id == user_id,
                FocusSession.start_time >= start_date,
                FocusSession.start_time <= end_date
            )
        ).all()
        
        # Group sessions by hour
        hourly_data = defaultdict(lambda: {
            "sessions": [],
            "total_sessions": 0,
            "completed_sessions": 0,
            "total_time": 0,
            "productivity_scores": []
        })
        
        for session in sessions:
            hour = session.start_time.hour
            hourly_data[hour]["sessions"].append(session)
            hourly_data[hour]["total_sessions"] += 1
            
            if session.status == "completed":
                hourly_data[hour]["completed_sessions"] += 1
            
            hourly_data[hour]["total_time"] += session.actual_duration or session.planned_duration
            
            if session.productivity_score is not None:
                hourly_data[hour]["productivity_scores"].append(session.productivity_score)
        
        # Calculate statistics for each hour
        hourly_stats = []
        for hour in range(24):
            data = hourly_data[hour]
            
            avg_productivity = statistics.mean(data["productivity_scores"]) if data["productivity_scores"] else 0
            completion_rate = data["completed_sessions"] / data["total_sessions"] if data["total_sessions"] > 0 else 0
            
            hourly_stats.append({
                "hour": hour,
                "total_sessions": data["total_sessions"],
                "completed_sessions": data["completed_sessions"],
                "completion_rate": round(completion_rate, 3),
                "total_focus_time_minutes": data["total_time"],
                "average_productivity_score": round(avg_productivity, 2)
            })
        
        # Find peak productivity hours
        productive_hours = sorted(
            [h for h in hourly_stats if h["total_sessions"] > 0],
            key=lambda x: x["average_productivity_score"],
            reverse=True
        )
        
        return {
            "hourly_breakdown": hourly_stats,
            "peak_productivity_hours": productive_hours[:5],  # Top 5 hours
            "most_active_hours": sorted(
                hourly_stats, 
                key=lambda x: x["total_sessions"], 
                reverse=True
            )[:5]
        }
    
    @staticmethod
    def calculate_session_type_performance(db: Session, user_id: str, 
                                         days: int = 30) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by session type"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        sessions = db.query(FocusSession).filter(
            and_(
                FocusSession.user_id == user_id,
                FocusSession.start_time >= start_date,
                FocusSession.start_time <= end_date
            )
        ).all()
        
        # Group by session type
        type_data = defaultdict(list)
        for session in sessions:
            session_type = session.session_type or "unknown"
            type_data[session_type].append(session)
        
        # Calculate statistics for each type
        type_stats = {}
        for session_type, type_sessions in type_data.items():
            completed = [s for s in type_sessions if s.status == "completed"]
            
            productivity_scores = [s.productivity_score for s in type_sessions if s.productivity_score is not None]
            avg_productivity = statistics.mean(productivity_scores) if productivity_scores else 0
            
            avg_duration = statistics.mean([s.planned_duration for s in type_sessions])
            avg_actual = statistics.mean([
                s.actual_duration for s in type_sessions if s.actual_duration is not None
            ]) if any(s.actual_duration for s in type_sessions) else 0
            
            type_stats[session_type] = {
                "total_sessions": len(type_sessions),
                "completed_sessions": len(completed),
                "completion_rate": len(completed) / len(type_sessions),
                "average_productivity_score": round(avg_productivity, 2),
                "average_planned_duration": round(avg_duration, 1),
                "average_actual_duration": round(avg_actual, 1),
                "total_interruptions": sum(s.interruption_count or 0 for s in type_sessions),
                "average_interruptions": sum(s.interruption_count or 0 for s in type_sessions) / len(type_sessions)
            }
        
        return type_stats
    
    @staticmethod
    def _empty_stats() -> Dict[str, Any]:
        """Return empty stats structure"""
        return {
            "total_sessions": 0,
            "completed_sessions": 0,
            "completion_rate": 0,
            "total_focus_time_minutes": 0,
            "completed_focus_time_minutes": 0,
            "average_planned_duration": 0,
            "average_actual_duration": 0,
            "average_productivity_score": 0,
            "total_interruptions": 0,
            "average_interruptions_per_session": 0,
            "focus_quality_distribution": {},
            "session_type_distribution": {},
            "current_streak_days": 0,
            "longest_streak_days": 0
        }
    
    @staticmethod
    def _calculate_current_streak(sessions: List[FocusSession]) -> int:
        """Calculate current consecutive days with completed sessions"""
        if not sessions:
            return 0
        
        # Sort sessions by date (most recent first)
        sessions_by_date = defaultdict(list)
        for session in sessions:
            session_date = session.start_time.date()
            if session.status == "completed":
                sessions_by_date[session_date].append(session)
        
        # Check consecutive days from today backwards
        current_date = datetime.utcnow().date()
        streak = 0
        
        while current_date in sessions_by_date:
            streak += 1
            current_date -= timedelta(days=1)
        
        return streak
    
    @staticmethod
    def _calculate_longest_streak(sessions: List[FocusSession]) -> int:
        """Calculate longest consecutive days streak"""
        if not sessions:
            return 0
        
        # Get unique dates with completed sessions
        completed_dates = set()
        for session in sessions:
            if session.status == "completed":
                completed_dates.add(session.start_time.date())
        
        if not completed_dates:
            return 0
        
        # Sort dates
        sorted_dates = sorted(completed_dates)
        
        longest_streak = 1
        current_streak = 1
        
        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1
        
        return longest_streak


class ProductivityInsights:
    """Generate insights and recommendations from session data"""
    
    @staticmethod
    def generate_insights(db: Session, user_id: str, 
                         days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive productivity insights"""
        
        stats = SessionAnalytics.calculate_user_stats(db, user_id, days)
        hourly_patterns = SessionAnalytics.calculate_hourly_patterns(db, user_id, days)
        type_performance = SessionAnalytics.calculate_session_type_performance(db, user_id, days)
        
        insights = {
            "summary": ProductivityInsights._generate_summary_insights(stats),
            "recommendations": ProductivityInsights._generate_recommendations(stats, hourly_patterns, type_performance),
            "achievements": ProductivityInsights._identify_achievements(stats),
            "areas_for_improvement": ProductivityInsights._identify_improvement_areas(stats, type_performance),
            "optimal_schedule": ProductivityInsights._suggest_optimal_schedule(hourly_patterns)
        }
        
        return insights
    
    @staticmethod
    def _generate_summary_insights(stats: Dict[str, Any]) -> List[str]:
        """Generate summary insights from user stats"""
        insights = []
        
        # Completion rate insights
        if stats["completion_rate"] >= 0.8:
            insights.append(f"Excellent consistency! You complete {stats['completion_rate']:.1%} of your sessions.")
        elif stats["completion_rate"] >= 0.6:
            insights.append(f"Good focus habits with {stats['completion_rate']:.1%} completion rate.")
        else:
            insights.append(f"Room for improvement: {stats['completion_rate']:.1%} completion rate.")
        
        # Productivity insights
        if stats["average_productivity_score"] >= 8:
            insights.append("Your self-assessed productivity is consistently high!")
        elif stats["average_productivity_score"] >= 6:
            insights.append("Your productivity levels are solid with room for optimization.")
        
        # Focus time insights
        total_hours = stats["total_focus_time_minutes"] / 60
        if total_hours >= 40:
            insights.append(f"Impressive! You've focused for {total_hours:.1f} hours this period.")
        elif total_hours >= 20:
            insights.append(f"Good progress with {total_hours:.1f} hours of focused work.")
        
        # Streak insights
        if stats["current_streak_days"] >= 7:
            insights.append(f"Amazing! You're on a {stats['current_streak_days']}-day streak!")
        elif stats["current_streak_days"] >= 3:
            insights.append(f"Keep it up! {stats['current_streak_days']} days in a row.")
        
        return insights
    
    @staticmethod
    def _generate_recommendations(stats: Dict[str, Any], 
                                hourly_patterns: Dict[str, Any],
                                type_performance: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Timing recommendations
        if hourly_patterns["peak_productivity_hours"]:
            best_hour = hourly_patterns["peak_productivity_hours"][0]["hour"]
            recommendations.append(f"Schedule important work around {best_hour}:00 for peak performance.")
        
        # Session type recommendations
        if type_performance:
            best_type = max(type_performance.items(), key=lambda x: x[1]["completion_rate"])
            if best_type[1]["completion_rate"] > 0.8:
                recommendations.append(f"You excel at {best_type[0]} sessions - consider doing more of these.")
        
        # Interruption management
        if stats["average_interruptions_per_session"] > 2:
            recommendations.append("Consider using 'Do Not Disturb' mode to reduce interruptions.")
        
        # Duration optimization
        if stats["average_actual_duration"] < stats["average_planned_duration"] * 0.8:
            recommendations.append("Try shorter planned sessions to improve completion rates.")
        
        return recommendations
    
    @staticmethod
    def _identify_achievements(stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify achievements and milestones"""
        achievements = []
        
        # Focus time achievements
        total_hours = stats["total_focus_time_minutes"] / 60
        if total_hours >= 100:
            achievements.append({"type": "focus_time", "title": "Century Club", "description": "100+ hours of focused work!"})
        elif total_hours >= 50:
            achievements.append({"type": "focus_time", "title": "Half Century", "description": "50+ hours of focused work!"})
        
        # Streak achievements
        if stats["longest_streak_days"] >= 30:
            achievements.append({"type": "streak", "title": "Monthly Master", "description": "30+ day focus streak!"})
        elif stats["longest_streak_days"] >= 7:
            achievements.append({"type": "streak", "title": "Week Warrior", "description": "7+ day focus streak!"})
        
        # Completion achievements
        if stats["completion_rate"] >= 0.95:
            achievements.append({"type": "completion", "title": "Nearly Perfect", "description": "95%+ session completion rate!"})
        elif stats["completion_rate"] >= 0.8:
            achievements.append({"type": "completion", "title": "Consistent Performer", "description": "80%+ session completion rate!"})
        
        return achievements
    
    @staticmethod
    def _identify_improvement_areas(stats: Dict[str, Any], 
                                  type_performance: Dict[str, Dict[str, Any]]) -> List[str]:
        """Identify areas needing improvement"""
        improvements = []
        
        if stats["completion_rate"] < 0.6:
            improvements.append("Focus on completing more sessions - try shorter durations")
        
        if stats["average_productivity_score"] < 6:
            improvements.append("Work on minimizing distractions during focus sessions")
        
        if stats["average_interruptions_per_session"] > 3:
            improvements.append("Reduce interruptions by setting boundaries and using focus tools")
        
        # Session type specific improvements
        for session_type, performance in type_performance.items():
            if performance["completion_rate"] < 0.5:
                improvements.append(f"Consider shorter {session_type} sessions for better completion rates")
        
        return improvements
    
    @staticmethod
    def _suggest_optimal_schedule(hourly_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest optimal daily schedule based on patterns"""
        peak_hours = hourly_patterns["peak_productivity_hours"][:3]
        active_hours = hourly_patterns["most_active_hours"][:3]
        
        return {
            "recommended_focus_hours": [h["hour"] for h in peak_hours],
            "most_active_hours": [h["hour"] for h in active_hours],
            "suggestions": [
                f"Peak productivity: {peak_hours[0]['hour']}:00" if peak_hours else "Need more data",
                f"Most active period: {active_hours[0]['hour']}:00" if active_hours else "Need more data"
            ]
        }
