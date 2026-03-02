"""
Daily login streak tracking.
Motivates regular app usage.
"""

from dataclasses import dataclass
from datetime import date, datetime

import streamlit as st

from modules.db.connection import get_db_connection
from modules.logger import logger


@dataclass
class StreakInfo:
    """Information about user's login streak."""

    current_streak: int
    longest_streak: int
    last_login: date | None
    total_logins: int


class StreakManager:
    """Manages daily login streaks."""

    TABLE_NAME = "user_streaks"

    @classmethod
    def _ensure_table(cls):
        """Create streak table if not exists."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {cls.TABLE_NAME} (
                        id INTEGER PRIMARY KEY,
                        current_streak INTEGER DEFAULT 0,
                        longest_streak INTEGER DEFAULT 0,
                        last_login DATE,
                        total_logins INTEGER DEFAULT 0
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.warning(f"Could not create streak table: {e}")

    @classmethod
    def get_streak(cls) -> StreakInfo:
        """Get current streak information."""
        try:
            cls._ensure_table()
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    SELECT current_streak, longest_streak, last_login, total_logins
                    FROM {cls.TABLE_NAME} LIMIT 1
                """)
                row = cursor.fetchone()

                if row:
                    return StreakInfo(
                        current_streak=row[0] or 0,
                        longest_streak=row[1] or 0,
                        last_login=datetime.fromisoformat(row[2]).date() if row[2] else None,
                        total_logins=row[3] or 0,
                    )
                return StreakInfo(0, 0, None, 0)
        except Exception as e:
            logger.warning(f"Could not get streak: {e}")
            return StreakInfo(0, 0, None, 0)

    @classmethod
    def record_login(cls) -> tuple[int, bool]:
        """
        Record a login and update streak.

        Returns:
            Tuple of (current_streak, is_new_record)
        """
        try:
            cls._ensure_table()
            streak = cls.get_streak()
            today = date.today()

            # Check if already logged in today
            if streak.last_login == today:
                return streak.current_streak, False

            # Calculate new streak
            if streak.last_login:
                days_diff = (today - streak.last_login).days
                if days_diff == 1:
                    new_streak = streak.current_streak + 1
                elif days_diff > 1:
                    new_streak = 1  # Reset streak
                else:
                    return streak.current_streak, False
            else:
                new_streak = 1

            is_new_record = new_streak > streak.longest_streak

            with get_db_connection() as conn:
                cursor = conn.cursor()

                # Insert or update
                cursor.execute(
                    f"""
                    INSERT INTO {cls.TABLE_NAME} (id, current_streak, longest_streak, last_login, total_logins)
                    VALUES (1, ?, ?, ?, COALESCE((SELECT total_logins FROM {cls.TABLE_NAME} WHERE id=1), 0) + 1)
                    ON CONFLICT(id) DO UPDATE SET
                        current_streak = excluded.current_streak,
                        longest_streak = MAX(excluded.longest_streak, {cls.TABLE_NAME}.longest_streak),
                        last_login = excluded.last_login,
                        total_logins = excluded.total_logins
                """,
                    (new_streak, max(new_streak, streak.longest_streak), today.isoformat()),
                )

                conn.commit()

            return new_streak, is_new_record

        except Exception as e:
            logger.error(f"Could not record login: {e}")
            return 0, False


def get_current_streak() -> int:
    """Get current login streak."""
    return StreakManager.get_streak().current_streak


def record_daily_login() -> tuple[int, bool]:
    """
    Record daily login and return streak info.
    Call this once per session in app.py.
    """
    return StreakManager.record_login()


def render_streak_badge():
    """Render streak badge in Streamlit."""
    streak = StreakManager.get_streak()

    if streak.current_streak > 0:
        fire_emoji = "🔥"
        if streak.current_streak >= 30:
            fire_emoji = "🔥🔥🔥"
        elif streak.current_streak >= 7:
            fire_emoji = "🔥🔥"

        st.markdown(f"**{fire_emoji} {streak.current_streak} jours**")

        if streak.current_streak == streak.longest_streak and streak.current_streak > 1:
            st.caption("🏆 Record personnel!")
