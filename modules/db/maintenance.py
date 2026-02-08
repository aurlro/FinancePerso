"""
Maintenance and automated cleanup scheduler.
Handles periodic tasks like the weekly "Magic Fix" audit.
"""

from datetime import datetime
import sqlite3
from modules.db.connection import get_db_connection
from modules.db.audit import auto_fix_common_inconsistencies
from modules.logger import logger


def should_run_weekly_cleanup() -> bool:
    """
    Checks if a weekly cleanup should be performed.
    Criteria:
    1. It's Sunday (weekday == 6)
    2. The last cleanup was not performed this week.
    """
    now = datetime.now()
    if now.weekday() != 6:  # Sunday is 6 in Python's datetime.weekday()
        return False

    today_str = now.strftime("%Y-%m-%d")
    current_week = now.strftime("%Y-%W")  # Year-WeekNumber

    try:
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Check last cleanup date
            cursor.execute("SELECT value FROM app_settings WHERE key = 'last_weekly_cleanup_week'")
            row = cursor.fetchone()

            if row and row["value"] == current_week:
                return False  # Already done this week

            return True
    except Exception as e:
        logger.error(f"Error checking weekly cleanup eligibility: {e}")
        return False


def run_weekly_cleanup():
    """
    Performs the weekly maintenance tasks.
    """
    logger.info("📅 Starting automated weekly cleanup...")

    try:
        # 1. Run the Magic Fix (includes data audit, deduplication, and link integrity)
        fixes_count = auto_fix_common_inconsistencies()

        # 2. Update last cleanup week
        current_week = datetime.now().strftime("%Y-%W")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO app_settings (key, value, updated_at)
                VALUES ('last_weekly_cleanup_week', ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
            """,
                (current_week,),
            )
            conn.commit()

        logger.info(f"✅ Automated weekly cleanup completed. {fixes_count} fixes applied.")
        return fixes_count
    except Exception as e:
        logger.error(f"❌ Automated weekly cleanup failed: {e}")
        return 0


def check_and_perform_maintenance():
    """
    Entry point to be called on app startup.
    """
    if should_run_weekly_cleanup():
        run_weekly_cleanup()
