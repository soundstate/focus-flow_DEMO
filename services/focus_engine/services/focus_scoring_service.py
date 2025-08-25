"""
Focus Quality Scoring Service
Algorithms to calculate session quality scores and focus metrics
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import math
import statistics
import logging

from ..models.session_models import FocusSession
from ..utils.timer import TimerUtils

logger = logging.getLogger("focus_engine.focus_scoring")


@dataclass
class FocusQualityFactors:
    """Factors that contribute to focus quality scoring"""
    completion_rate: float  # 0.0 to 1.0
    duration_consistency: float  # 0.0 to 1.0 - how close actual is to planned
    interruption_penalty: float  # 0.0 to 1.0 - penalty for interruptions
    time_of_day_bonus: float  # 0.0 to 0.2 - bonus for optimal timing
    session_type_multiplier: float  # 0.8 to 1.2 - type-specific multiplier
    streak_bonus: float  # 0.0 to 0.15 - bonus for consistency streak
    productivity_alignment: float  # 0.0 to 1.0 - self-assessment alignment


class FocusQualityScorer:
    """Advanced focus quality scoring algorithms"""
    
    # Scoring weights for different factors
    WEIGHTS = {
        "completion": 0.30,      # 30% - Did they finish?
        "consistency": 0.25,     # 25% - Duration consistency
        "interruptions": 0.20,   # 20% - Interruption management
        "timing": 0.10,          # 10% - Optimal timing
        "type_performance": 0.10, # 10% - Session type performance
        "streak": 0.05           # 5% - Consistency bonus
    }
    
    # Optimal hours for different activities (can be personalized)
    OPTIMAL_HOURS = {
        "deep_work": [9, 10, 11, 14, 15],
        "pomodoro": [9, 10, 11, 14, 15, 16],
        "study": [9, 10, 11, 14, 15, 16, 19, 20],
        "long_focus": [9, 10, 11, 14, 15]
    }
    
    @staticmethod
    def calculate_session_quality_score(session: FocusSession, 
                                      user_context: Optional[Dict[str, Any]] = None) -> float:
        """Calculate quality score for a single session"""
        
        factors = FocusQualityScorer._analyze_quality_factors(session, user_context or {})
        
        # Calculate weighted score
        score = (
            factors.completion_rate * FocusQualityScorer.WEIGHTS["completion"] +
            factors.duration_consistency * FocusQualityScorer.WEIGHTS["consistency"] +
            (1.0 - factors.interruption_penalty) * FocusQualityScorer.WEIGHTS["interruptions"] +
            factors.time_of_day_bonus * FocusQualityScorer.WEIGHTS["timing"] +
            factors.session_type_multiplier * FocusQualityScorer.WEIGHTS["type_performance"] +
            factors.streak_bonus * FocusQualityScorer.WEIGHTS["streak"]
        )
        
        # Normalize to 0-10 scale
        quality_score = min(10.0, max(0.0, score * 10))
        
        logger.debug(f"Session {session.id} quality score: {quality_score:.2f}")
        return round(quality_score, 2)
    
    @staticmethod
    def calculate_batch_quality_scores(db: Session, user_id: str, 
                                     days: int = 30) -> Dict[str, float]:
        """Calculate quality scores for all user sessions in a period"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        sessions = db.query(FocusSession).filter(
            FocusSession.user_id == user_id,
            FocusSession.start_time >= start_date,
            FocusSession.start_time <= end_date
        ).order_by(FocusSession.start_time).all()
        
        if not sessions:
            return {}
        
        # Get user context for personalized scoring
        user_context = FocusQualityScorer._build_user_context(sessions)
        
        # Calculate scores for each session
        session_scores = {}
        for session in sessions:
            score = FocusQualityScorer.calculate_session_quality_score(session, user_context)
            session_scores[str(session.id)] = score
            
            # Update session with calculated quality
            quality_category = FocusQualityScorer._categorize_quality(score)
            if session.focus_quality != quality_category:
                session.focus_quality = quality_category
        
        # Commit quality updates
        db.commit()
        
        return session_scores
    
    @staticmethod
    def get_quality_insights(db: Session, user_id: str, 
                           days: int = 30) -> Dict[str, Any]:
        """Get comprehensive quality insights and improvement suggestions"""
        
        scores = FocusQualityScorer.calculate_batch_quality_scores(db, user_id, days)
        
        if not scores:
            return {"message": "No sessions found for analysis"}
        
        score_values = list(scores.values())
        
        # Statistical analysis
        avg_quality = statistics.mean(score_values)
        quality_trend = FocusQualityScorer._calculate_quality_trend(score_values)
        quality_distribution = FocusQualityScorer._analyze_quality_distribution(score_values)
        
        # Factor analysis
        factor_analysis = FocusQualityScorer._analyze_quality_factors_batch(db, user_id, days)
        
        # Improvement recommendations
        recommendations = FocusQualityScorer._generate_quality_recommendations(factor_analysis)
        
        return {
            "average_quality_score": round(avg_quality, 2),
            "quality_trend": quality_trend,
            "quality_distribution": quality_distribution,
            "factor_analysis": factor_analysis,
            "recommendations": recommendations,
            "total_sessions_analyzed": len(score_values)
        }
    
    @staticmethod
    def _analyze_quality_factors(session: FocusSession, 
                               user_context: Dict[str, Any]) -> FocusQualityFactors:
        """Analyze individual factors contributing to session quality"""
        
        # Completion rate factor
        completion_rate = 1.0 if session.status == "completed" else 0.0
        
        # Duration consistency factor
        if session.actual_duration and session.planned_duration:
            consistency_ratio = session.actual_duration / session.planned_duration
            # Penalize both over and under performance
            duration_consistency = 1.0 - abs(1.0 - consistency_ratio)
            duration_consistency = max(0.0, duration_consistency)
        else:
            duration_consistency = 0.5  # Neutral if no actual duration
        
        # Interruption penalty
        interruption_count = session.interruption_count or 0
        max_interruptions = 5  # Assume 5+ interruptions is maximum penalty
        interruption_penalty = min(1.0, interruption_count / max_interruptions)
        
        # Time of day bonus
        session_hour = session.start_time.hour
        session_type = session.session_type or "pomodoro"
        optimal_hours = FocusQualityScorer.OPTIMAL_HOURS.get(session_type, [9, 10, 11, 14, 15])
        
        if session_hour in optimal_hours:
            time_of_day_bonus = 0.2
        elif session_hour in [h for sublist in FocusQualityScorer.OPTIMAL_HOURS.values() for h in sublist]:
            time_of_day_bonus = 0.1
        else:
            time_of_day_bonus = 0.0
        
        # Session type multiplier based on historical performance
        type_performance = user_context.get("type_performance", {}).get(session_type, {})
        if type_performance:
            avg_completion = type_performance.get("completion_rate", 0.7)
            session_type_multiplier = 0.8 + (avg_completion * 0.4)  # 0.8 to 1.2 range
        else:
            session_type_multiplier = 1.0
        
        # Streak bonus
        current_streak = user_context.get("current_streak", 0)
        if current_streak >= 7:
            streak_bonus = 0.15
        elif current_streak >= 3:
            streak_bonus = 0.10
        elif current_streak >= 1:
            streak_bonus = 0.05
        else:
            streak_bonus = 0.0
        
        # Productivity alignment
        if session.productivity_score is not None:
            # Align self-assessment with objective metrics
            expected_productivity = 7.0  # Expected baseline
            productivity_alignment = min(1.0, session.productivity_score / expected_productivity)
        else:
            productivity_alignment = 0.7  # Neutral assumption
        
        return FocusQualityFactors(
            completion_rate=completion_rate,
            duration_consistency=duration_consistency,
            interruption_penalty=interruption_penalty,
            time_of_day_bonus=time_of_day_bonus,
            session_type_multiplier=session_type_multiplier,
            streak_bonus=streak_bonus,
            productivity_alignment=productivity_alignment
        )
    
    @staticmethod
    def _build_user_context(sessions: List[FocusSession]) -> Dict[str, Any]:
        """Build user context for personalized scoring"""
        
        # Session type performance
        from collections import defaultdict
        type_data = defaultdict(list)
        
        for session in sessions:
            session_type = session.session_type or "unknown"
            type_data[session_type].append(session)
        
        type_performance = {}
        for session_type, type_sessions in type_data.items():
            completed = sum(1 for s in type_sessions if s.status == "completed")
            completion_rate = completed / len(type_sessions) if type_sessions else 0
            type_performance[session_type] = {
                "completion_rate": completion_rate,
                "total_sessions": len(type_sessions)
            }
        
        # Current streak calculation
        completed_dates = set()
        for session in sessions:
            if session.status == "completed":
                completed_dates.add(session.start_time.date())
        
        current_streak = 0
        current_date = datetime.utcnow().date()
        while current_date in completed_dates:
            current_streak += 1
            current_date -= timedelta(days=1)
        
        return {
            "type_performance": type_performance,
            "current_streak": current_streak,
            "total_sessions": len(sessions)
        }
    
    @staticmethod
    def _categorize_quality(score: float) -> str:
        """Categorize quality score into high/medium/low"""
        if score >= 8.0:
            return "high"
        elif score >= 5.0:
            return "medium"
        else:
            return "low"
    
    @staticmethod
    def _calculate_quality_trend(scores: List[float]) -> str:
        """Calculate if quality is improving, declining, or stable"""
        if len(scores) < 5:
            return "insufficient_data"
        
        # Use linear regression slope to determine trend
        n = len(scores)
        x = list(range(n))
        
        # Calculate slope
        sum_x = sum(x)
        sum_y = sum(scores)
        sum_xy = sum(x[i] * scores[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.1:
            return "improving"
        elif slope < -0.1:
            return "declining"
        else:
            return "stable"
    
    @staticmethod
    def _analyze_quality_distribution(scores: List[float]) -> Dict[str, Any]:
        """Analyze distribution of quality scores"""
        
        high_quality = sum(1 for s in scores if s >= 8.0)
        medium_quality = sum(1 for s in scores if 5.0 <= s < 8.0)
        low_quality = sum(1 for s in scores if s < 5.0)
        
        total = len(scores)
        
        return {
            "high_quality_sessions": high_quality,
            "medium_quality_sessions": medium_quality,
            "low_quality_sessions": low_quality,
            "high_quality_percentage": round((high_quality / total) * 100, 1) if total > 0 else 0,
            "medium_quality_percentage": round((medium_quality / total) * 100, 1) if total > 0 else 0,
            "low_quality_percentage": round((low_quality / total) * 100, 1) if total > 0 else 0
        }
    
    @staticmethod
    def _analyze_quality_factors_batch(db: Session, user_id: str, days: int) -> Dict[str, Any]:
        """Analyze quality factors across multiple sessions"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        sessions = db.query(FocusSession).filter(
            FocusSession.user_id == user_id,
            FocusSession.start_time >= start_date,
            FocusSession.start_time <= end_date
        ).all()
        
        if not sessions:
            return {}
        
        # Aggregate factor analysis
        completion_rates = [1.0 if s.status == "completed" else 0.0 for s in sessions]
        interruption_counts = [s.interruption_count or 0 for s in sessions]
        
        duration_consistencies = []
        for s in sessions:
            if s.actual_duration and s.planned_duration:
                consistency = 1.0 - abs(1.0 - (s.actual_duration / s.planned_duration))
                duration_consistencies.append(max(0.0, consistency))
        
        return {
            "average_completion_rate": statistics.mean(completion_rates),
            "average_interruptions": statistics.mean(interruption_counts),
            "average_duration_consistency": statistics.mean(duration_consistencies) if duration_consistencies else 0,
            "consistency_std_dev": statistics.stdev(duration_consistencies) if len(duration_consistencies) > 1 else 0,
            "total_sessions": len(sessions)
        }
    
    @staticmethod
    def _generate_quality_recommendations(factor_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on factor analysis"""
        recommendations = []
        
        if factor_analysis.get("average_completion_rate", 0) < 0.7:
            recommendations.append("Focus on completing more sessions - try shorter durations or better planning")
        
        if factor_analysis.get("average_interruptions", 0) > 2:
            recommendations.append("Work on reducing interruptions - use 'Do Not Disturb' mode and set boundaries")
        
        if factor_analysis.get("average_duration_consistency", 0) < 0.6:
            recommendations.append("Improve time estimation - track actual vs planned durations and adjust accordingly")
        
        if factor_analysis.get("consistency_std_dev", 0) > 0.3:
            recommendations.append("Work on consistency - try to maintain similar session patterns")
        
        return recommendations


class PersonalizedScoring:
    """Personalized scoring based on individual patterns"""
    
    @staticmethod
    def create_personal_profile(db: Session, user_id: str, 
                              days: int = 90) -> Dict[str, Any]:
        """Create personalized scoring profile for user"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        sessions = db.query(FocusSession).filter(
            FocusSession.user_id == user_id,
            FocusSession.start_time >= start_date,
            FocusSession.start_time <= end_date
        ).all()
        
        if not sessions:
            return {}
        
        # Personal optimal hours analysis
        hourly_performance = defaultdict(list)
        for session in sessions:
            if session.productivity_score:
                hour = session.start_time.hour
                hourly_performance[hour].append(session.productivity_score)
        
        personal_optimal_hours = []
        for hour, scores in hourly_performance.items():
            if len(scores) >= 3:  # Minimum sessions for reliability
                avg_score = statistics.mean(scores)
                if avg_score >= 7.0:
                    personal_optimal_hours.append(hour)
        
        # Personal session type preferences
        type_performance = {}
        from collections import defaultdict
        type_data = defaultdict(list)
        
        for session in sessions:
            session_type = session.session_type or "unknown"
            type_data[session_type].append(session)
        
        for session_type, type_sessions in type_data.items():
            if len(type_sessions) >= 5:  # Minimum for reliability
                completed = sum(1 for s in type_sessions if s.status == "completed")
                avg_productivity = statistics.mean([
                    s.productivity_score for s in type_sessions if s.productivity_score
                ]) if any(s.productivity_score for s in type_sessions) else 0
                
                type_performance[session_type] = {
                    "completion_rate": completed / len(type_sessions),
                    "average_productivity": avg_productivity,
                    "total_sessions": len(type_sessions)
                }
        
        return {
            "personal_optimal_hours": sorted(personal_optimal_hours),
            "session_type_performance": type_performance,
            "analysis_period_days": days,
            "total_sessions": len(sessions),
            "profile_reliability": "high" if len(sessions) >= 50 else "medium" if len(sessions) >= 20 else "low"
        }
