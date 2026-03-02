"""
Gamification system for FinancePerso.
Challenges, badges, and streaks to motivate users.
"""

# Legacy compatibility
from modules.gamification_legacy import GamificationManager

from modules.gamification.challenges import (
    Challenge,
    ChallengeManager,
    check_challenges,
    get_active_challenges,
)
from modules.gamification.badges import (
    Badge,
    BadgeManager,
    get_user_badges,
    has_badge,
)
from modules.gamification.streaks import (
    StreakManager,
    get_current_streak,
    record_daily_login,
)

__all__ = [
    # Legacy
    "GamificationManager",
    # Challenges
    "Challenge",
    "ChallengeManager",
    "check_challenges",
    "get_active_challenges",
    # Badges
    "Badge",
    "BadgeManager",
    "get_user_badges",
    "has_badge",
    # Streaks
    "StreakManager",
    "get_current_streak",
    "record_daily_login",
]
