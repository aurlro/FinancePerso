"""Repository pour l'accès aux données des notifications.

Abstraction de la couche de persistance (SQLite).
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Optional

from modules.db.connection import get_db_connection

from .models import (
    Notification,
    NotificationAction,
    NotificationLevel,
    NotificationPreferences,
    NotificationType,
)


class NotificationRepository:
    """Repository pour les notifications."""

    def __init__(self):
        """Initialise le repository."""
        self._ensure_table_exists()

    def _ensure_table_exists(self) -> None:
        """Vérifie que la table existe."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='notifications'
            """)
            if not cursor.fetchone():
                raise RuntimeError(
                    "Table notifications not found. " "Run migration 007_notifications.sql first."
                )

    def create(self, notification: Notification) -> Notification:
        """Crée une notification en base."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO notifications (
                    id, level, type, title, message, icon,
                    created_at, expires_at, category, source,
                    actions_json, metadata_json, dedup_key,
                    is_read, is_dismissed, is_pinned
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    notification.id,
                    notification.level.value,
                    notification.type.value,
                    notification.title,
                    notification.message,
                    notification.icon,
                    notification.created_at.isoformat(),
                    notification.expires_at.isoformat() if notification.expires_at else None,
                    notification.category,
                    notification.source,
                    json.dumps([a.to_dict() for a in notification.actions]),
                    json.dumps(notification.metadata),
                    notification.dedup_key,
                    notification.is_read,
                    notification.is_dismissed,
                    notification.is_pinned,
                ),
            )
            conn.commit()
        return notification

    def get_by_id(self, notification_id: str) -> Optional[Notification]:
        """Récupère une notification par son ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM notifications WHERE id = ?
            """,
                (notification_id,),
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_notification(row)
        return None

    def get_unread(
        self,
        user_id: int = 1,
        limit: int = 50,
        offset: int = 0,
        category: Optional[str] = None,
    ) -> list[Notification]:
        """Récupère les notifications non lues."""
        query = """
            SELECT * FROM notifications 
            WHERE user_id = ? AND is_read = 0 AND is_dismissed = 0
            AND (expires_at IS NULL OR expires_at > datetime('now'))
        """
        params = [user_id]

        if category:
            query += " AND category = ?"
            params.append(category)

        query += """
            ORDER BY 
                CASE level 
                    WHEN 'critical' THEN 1
                    WHEN 'warning' THEN 2
                    WHEN 'info' THEN 3
                    WHEN 'success' THEN 4
                    WHEN 'achievement' THEN 5
                END,
                created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [self._row_to_notification(row) for row in cursor.fetchall()]

    def get_all(
        self,
        user_id: int = 1,
        limit: int = 50,
        offset: int = 0,
        include_dismissed: bool = False,
    ) -> list[Notification]:
        """Récupère toutes les notifications."""
        query = "SELECT * FROM notifications WHERE user_id = ?"
        params = [user_id]

        if not include_dismissed:
            query += " AND is_dismissed = 0"

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [self._row_to_notification(row) for row in cursor.fetchall()]

    def count_unread(self, user_id: int = 1) -> int:
        """Compte les notifications non lues."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COUNT(*) FROM notifications 
                WHERE user_id = ? AND is_read = 0 AND is_dismissed = 0
                AND (expires_at IS NULL OR expires_at > datetime('now'))
            """,
                (user_id,),
            )
            return cursor.fetchone()[0]

    def mark_read(self, notification_id: str) -> bool:
        """Marque une notification comme lue."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE notifications 
                SET is_read = 1, read_at = datetime('now')
                WHERE id = ?
            """,
                (notification_id,),
            )
            conn.commit()
            return cursor.rowcount > 0

    def mark_all_read(self, user_id: int = 1) -> int:
        """Marque toutes les notifications comme lues."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE notifications 
                SET is_read = 1, read_at = datetime('now')
                WHERE user_id = ? AND is_read = 0
            """,
                (user_id,),
            )
            conn.commit()
            return cursor.rowcount

    def dismiss(self, notification_id: str) -> bool:
        """Marque une notification comme ignorée."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE notifications 
                SET is_dismissed = 1, dismissed_at = datetime('now')
                WHERE id = ?
            """,
                (notification_id,),
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete(self, notification_id: str) -> bool:
        """Supprime définitivement une notification."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notifications WHERE id = ?", (notification_id,))
            conn.commit()
            return cursor.rowcount > 0

    def cleanup_expired(self, days: int = 30) -> int:
        """Nettoie les notifications expirées depuis X jours."""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM notifications 
                WHERE dismissed_at < ? OR 
                (expires_at < datetime('now') AND is_read = 1)
            """,
                (cutoff,),
            )
            conn.commit()
            return cursor.rowcount

    def dedup_exists(self, dedup_key: str, since_hours: int = 24) -> bool:
        """Vérifie si une notification avec cette clé de déduplication existe déjà."""
        since = (datetime.now() - timedelta(hours=since_hours)).isoformat()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 1 FROM notifications 
                WHERE dedup_key = ? AND created_at > ?
            """,
                (dedup_key, since),
            )
            return cursor.fetchone() is not None

    def get_preferences(self, user_id: int = 1) -> NotificationPreferences:
        """Récupère les préférences utilisateur."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM notification_preferences WHERE user_id = ?
            """,
                (user_id,),
            )
            row = cursor.fetchone()

            if row:
                return NotificationPreferences(
                    user_id=row[0],
                    critical_enabled=row[1],
                    warning_enabled=row[2],
                    info_enabled=row[3],
                    success_enabled=row[4],
                    achievement_enabled=row[5],
                    type_preferences=json.loads(row[6]) if row[6] else {},
                    desktop_enabled=row[7],
                    email_enabled=row[8],
                    sms_enabled=row[9],
                    email_address=row[10],
                    budget_warning_threshold=row[11],
                    budget_critical_threshold=row[12],
                    daily_digest_enabled=row[13],
                    weekly_summary_enabled=row[14],
                )

            # Retourner les préférences par défaut
            return NotificationPreferences(user_id=user_id)

    def save_preferences(self, prefs: NotificationPreferences) -> None:
        """Sauvegarde les préférences utilisateur."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO notification_preferences (
                    user_id, critical_enabled, warning_enabled, info_enabled,
                    success_enabled, achievement_enabled, type_preferences_json,
                    desktop_enabled, email_enabled, sms_enabled, email_address,
                    budget_warning_threshold, budget_critical_threshold,
                    daily_digest_enabled, weekly_summary_enabled
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    prefs.user_id,
                    prefs.critical_enabled,
                    prefs.warning_enabled,
                    prefs.info_enabled,
                    prefs.success_enabled,
                    prefs.achievement_enabled,
                    json.dumps(prefs.type_preferences),
                    prefs.desktop_enabled,
                    prefs.email_enabled,
                    prefs.sms_enabled,
                    prefs.email_address,
                    prefs.budget_warning_threshold,
                    prefs.budget_critical_threshold,
                    prefs.daily_digest_enabled,
                    prefs.weekly_summary_enabled,
                ),
            )
            conn.commit()

    def _row_to_notification(self, row) -> Notification:
        """Convertit une ligne DB en objet Notification."""
        return Notification(
            id=row[0],
            level=NotificationLevel(row[1]),
            type=NotificationType(row[2]),
            title=row[3],
            message=row[4],
            icon=row[5],
            created_at=datetime.fromisoformat(row[6]),
            read_at=datetime.fromisoformat(row[7]) if row[7] else None,
            dismissed_at=datetime.fromisoformat(row[8]) if row[8] else None,
            expires_at=datetime.fromisoformat(row[9]) if row[9] else None,
            category=row[10],
            source=row[11],
            actions=(
                [NotificationAction.from_dict(a) for a in json.loads(row[12])] if row[12] else []
            ),
            metadata=json.loads(row[13]) if row[13] else {},
            dedup_key=row[14],
            is_read=bool(row[16]),
            is_dismissed=bool(row[17]),
            is_pinned=bool(row[18]),
        )
