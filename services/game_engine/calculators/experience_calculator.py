"""XP calculation for focus sessions."""

BASE_XP_PER_25_MIN = 50
COMPLETION_BONUS = 25
STREAK_MULTIPLIER_PER_DAY = 0.02
MAX_STREAK_MULTIPLIER = 0.5
PRODUCTIVITY_MULTIPLIER_MAX = 0.5


class ExperienceCalculator:
    @staticmethod
    def calculate(
        session_duration: int,
        session_completed: bool,
        productivity_score: float | None = None,
        current_streak: int = 0,
    ) -> dict:
        base_xp = int(BASE_XP_PER_25_MIN * (session_duration / 25))
        bonus_xp = 0
        multipliers = {}

        if session_completed:
            bonus_xp += COMPLETION_BONUS
            multipliers["completion"] = COMPLETION_BONUS

        if current_streak > 0:
            streak_mult = min(
                current_streak * STREAK_MULTIPLIER_PER_DAY, MAX_STREAK_MULTIPLIER
            )
            streak_bonus = int(base_xp * streak_mult)
            bonus_xp += streak_bonus
            multipliers["streak"] = streak_bonus

        if productivity_score is not None and productivity_score > 0:
            prod_mult = (productivity_score / 10.0) * PRODUCTIVITY_MULTIPLIER_MAX
            prod_bonus = int(base_xp * prod_mult)
            bonus_xp += prod_bonus
            multipliers["productivity"] = prod_bonus

        return {
            "base_xp": base_xp,
            "bonus_xp": bonus_xp,
            "total_xp": base_xp + bonus_xp,
            "reason": "session_completed" if session_completed else "session_abandoned",
            "multipliers_applied": multipliers,
        }
