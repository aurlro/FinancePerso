"""
Gestion des feedbacks utilisateur sur les récurrences détectées.
Permet de confirmer/rejeter les récurrences et de les persister en DB.
"""

from modules.db.connection import get_db_connection
from modules.logger import logger


def init_recurrence_feedback_table():
    """Create table for storing user feedback on recurrences."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS recurrence_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label_pattern TEXT NOT NULL,
                category TEXT,
                is_recurring BOOLEAN NOT NULL,
                user_feedback TEXT CHECK(user_feedback IN ('confirmed', 'rejected', 'pending')),
                confidence_score REAL DEFAULT 0.5,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(label_pattern, category)
            )
        """
        )

        # Create index for fast lookup
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_recurrence_feedback_lookup 
            ON recurrence_feedback(label_pattern, category)
        """
        )
        conn.commit()


def get_recurrence_feedback(label_pattern: str, category: str = None) -> dict | None:
    """
    Get existing feedback for a label pattern.

    Args:
        label_pattern: The normalized label pattern
        category: Optional category filter

    Returns:
        Dict with feedback info or None
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            if category:
                cursor.execute(
                    """
                    SELECT * FROM recurrence_feedback 
                    WHERE label_pattern = ? AND (category = ? OR category IS NULL)
                    ORDER BY updated_at DESC LIMIT 1
                """,
                    (label_pattern, category),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM recurrence_feedback 
                    WHERE label_pattern = ?
                    ORDER BY updated_at DESC LIMIT 1
                """,
                    (label_pattern,),
                )

            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "label_pattern": row[1],
                    "category": row[2],
                    "is_recurring": bool(row[3]),
                    "user_feedback": row[4],
                    "confidence_score": row[5],
                    "notes": row[6],
                    "created_at": row[7],
                    "updated_at": row[8],
                }
            return None

    except Exception as e:
        logger.error(f"Error getting recurrence feedback: {e}")
        return None


def set_recurrence_feedback(
    label_pattern: str,
    is_recurring: bool,
    category: str = None,
    notes: str = None,
    confidence_score: float = 0.5,
) -> bool:
    """
    Save or update user feedback for a recurrence detection.

    Args:
        label_pattern: The normalized label pattern
        is_recurring: True if user confirms it's recurring, False otherwise
        category: Optional category
        notes: Optional user notes
        confidence_score: Detection confidence (0-1)

    Returns:
        True if successful
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            user_feedback = "confirmed" if is_recurring else "rejected"

            cursor.execute(
                """
                INSERT INTO recurrence_feedback 
                    (label_pattern, category, is_recurring, user_feedback, 
                     confidence_score, notes, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(label_pattern, category) DO UPDATE SET
                    is_recurring = excluded.is_recurring,
                    user_feedback = excluded.user_feedback,
                    confidence_score = excluded.confidence_score,
                    notes = COALESCE(excluded.notes, recurrence_feedback.notes),
                    updated_at = CURRENT_TIMESTAMP
            """,
                (label_pattern, category, is_recurring, user_feedback, confidence_score, notes),
            )

            conn.commit()
            logger.info(f"Recurrence feedback saved: {label_pattern} -> {user_feedback}")
            return True

    except Exception as e:
        logger.error(f"Error saving recurrence feedback: {e}")
        return False


def get_all_feedback(status: str = None) -> list[dict]:
    """
    Get all recurrence feedback entries.

    Args:
        status: Filter by 'confirmed', 'rejected', or None for all

    Returns:
        List of feedback dicts
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            if status:
                cursor.execute(
                    """
                    SELECT * FROM recurrence_feedback 
                    WHERE user_feedback = ?
                    ORDER BY updated_at DESC
                """,
                    (status,),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM recurrence_feedback 
                    ORDER BY updated_at DESC
                """
                )

            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "label_pattern": row[1],
                    "category": row[2],
                    "is_recurring": bool(row[3]),
                    "user_feedback": row[4],
                    "confidence_score": row[5],
                    "notes": row[6],
                    "created_at": row[7],
                    "updated_at": row[8],
                }
                for row in rows
            ]

    except Exception as e:
        logger.error(f"Error getting all feedback: {e}")
        return []


def get_confirmed_recurring() -> list[str]:
    """Get list of label patterns confirmed as recurring by user."""
    feedback = get_all_feedback(status="confirmed")
    return [f["label_pattern"] for f in feedback]


def get_rejected_recurring() -> list[str]:
    """Get list of label patterns rejected by user (not recurring)."""
    feedback = get_all_feedback(status="rejected")
    return [f["label_pattern"] for f in feedback]


def delete_feedback(label_pattern: str, category: str = None) -> bool:
    """
    Delete a feedback entry (allows re-evaluation).

    Args:
        label_pattern: The pattern to delete
        category: Optional category filter

    Returns:
        True if deleted
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            if category:
                cursor.execute(
                    """
                    DELETE FROM recurrence_feedback 
                    WHERE label_pattern = ? AND category = ?
                """,
                    (label_pattern, category),
                )
            else:
                cursor.execute(
                    """
                    DELETE FROM recurrence_feedback 
                    WHERE label_pattern = ?
                """,
                    (label_pattern,),
                )

            conn.commit()
            return cursor.rowcount > 0

    except Exception as e:
        logger.error(f"Error deleting feedback: {e}")
        return False


def get_feedback_stats() -> dict:
    """Get statistics about user feedback."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN user_feedback = 'confirmed' THEN 1 ELSE 0 END) as confirmed,
                    SUM(CASE WHEN user_feedback = 'rejected' THEN 1 ELSE 0 END) as rejected
                FROM recurrence_feedback
            """
            )

            row = cursor.fetchone()
            return {"total": row[0] or 0, "confirmed": row[1] or 0, "rejected": row[2] or 0}

    except Exception as e:
        logger.error(f"Error getting feedback stats: {e}")
        return {"total": 0, "confirmed": 0, "rejected": 0}


def is_pattern_rejected(label_pattern: str, category: str = None) -> bool:
    """Check if a pattern has been explicitly rejected by user."""
    feedback = get_recurrence_feedback(label_pattern, category)
    return feedback is not None and feedback["user_feedback"] == "rejected"


def is_pattern_confirmed(label_pattern: str, category: str = None) -> bool:
    """Check if a pattern has been explicitly confirmed by user."""
    feedback = get_recurrence_feedback(label_pattern, category)
    return feedback is not None and feedback["user_feedback"] == "confirmed"
