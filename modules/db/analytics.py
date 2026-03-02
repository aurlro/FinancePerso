"""Couche de données pour les analytics."""

import json
import os
import sqlite3
from datetime import datetime
from typing import Optional

import pandas as pd
import streamlit as st

from modules.db.connection import get_db_connection
from modules.logger import logger


def init_analytics_tables():
    """Crée les tables analytics si elles n'existent pas."""
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analytics_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                event_data TEXT,
                session_id TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS analytics_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                user_id TEXT,
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_time DATETIME,
                device_type TEXT,
                total_interactions INTEGER DEFAULT 0
            )
        """)

        # Créer les index pour les performances
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_analytics_events_type 
            ON analytics_events(event_type)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_analytics_events_time 
            ON analytics_events(timestamp)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_analytics_events_session 
            ON analytics_events(session_id)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_analytics_sessions_id 
            ON analytics_sessions(session_id)
        """)

        conn.commit()
        logger.debug("Tables analytics initialisées")


def track_event(event_type: str, event_data: Optional[dict] = None) -> bool:
    """Enregistre un événement analytics.

    Args:
        event_type: Type d'événement (utiliser EventType)
        event_data: Données associées à l'événement (dict)

    Returns:
        True si l'événement a été enregistré, False sinon
    """
    try:
        session_id = st.session_state.get("session_id", "unknown")

        with get_db_connection() as conn:
            conn.execute(
                """INSERT INTO analytics_events 
                   (event_type, event_data, session_id) 
                   VALUES (?, ?, ?)""",
                (event_type, json.dumps(event_data) if event_data else None, session_id),
            )
            conn.commit()
        return True
    except Exception as e:
        logger.warning(f"Erreur tracking événement {event_type}: {e}")
        return False


def start_session(session_id: str, device_type: Optional[str] = None) -> bool:
    """Démarre une nouvelle session analytics.

    Args:
        session_id: ID unique de session
        device_type: Type de device (desktop, mobile, tablet)

    Returns:
        True si la session a été créée, False sinon
    """
    try:
        with get_db_connection() as conn:
            conn.execute(
                """INSERT INTO analytics_sessions 
                   (session_id, device_type) 
                   VALUES (?, ?)
                   ON CONFLICT(session_id) DO NOTHING""",
                (session_id, device_type),
            )
            conn.commit()
        return True
    except Exception as e:
        logger.warning(f"Erreur création session analytics: {e}")
        return False


def end_session(session_id: str) -> bool:
    """Termine une session analytics.

    Args:
        session_id: ID de la session à terminer

    Returns:
        True si la session a été mise à jour, False sinon
    """
    try:
        with get_db_connection() as conn:
            conn.execute(
                """UPDATE analytics_sessions 
                   SET end_time = CURRENT_TIMESTAMP 
                   WHERE session_id = ?""",
                (session_id,),
            )
            conn.commit()
        return True
    except Exception as e:
        logger.warning(f"Erreur fin session analytics: {e}")
        return False


def increment_session_interactions(session_id: str) -> bool:
    """Incrémente le compteur d'interactions d'une session.

    Args:
        session_id: ID de la session

    Returns:
        True si le compteur a été mis à jour, False sinon
    """
    try:
        with get_db_connection() as conn:
            conn.execute(
                """UPDATE analytics_sessions 
                   SET total_interactions = total_interactions + 1 
                   WHERE session_id = ?""",
                (session_id,),
            )
            conn.commit()
        return True
    except Exception as e:
        logger.warning(f"Erreur incrémentation interactions: {e}")
        return False


def get_events_count(event_type: Optional[str] = None, since: Optional[datetime] = None) -> int:
    """Compte les événements.

    Args:
        event_type: Filtrer par type d'événement (optionnel)
        since: Date de début (optionnel)

    Returns:
        Nombre d'événements correspondants
    """
    with get_db_connection() as conn:
        query = "SELECT COUNT(*) FROM analytics_events WHERE 1=1"
        params = []

        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)

        if since:
            query += " AND timestamp > ?"
            params.append(since.isoformat())

        cursor = conn.execute(query, params)
        result = cursor.fetchone()
        return result[0] if result else 0


def get_daily_stats(days: int = 30) -> pd.DataFrame:
    """Retourne les statistiques quotidiennes.

    Args:
        days: Nombre de jours à analyser

    Returns:
        DataFrame avec colonnes: date, event_type, count
    """
    with get_db_connection() as conn:
        return pd.read_sql(
            """SELECT 
                DATE(timestamp) as date,
                event_type,
                COUNT(*) as count
            FROM analytics_events
            WHERE timestamp > datetime('now', '-{} days')
            GROUP BY DATE(timestamp), event_type
            ORDER BY date DESC""".format(days),
            conn,
        )


def get_session_stats(days: int = 30) -> dict:
    """Retourne les statistiques de sessions.

    Args:
        days: Nombre de jours à analyser

    Returns:
        Dict avec les métriques de session
    """
    with get_db_connection() as conn:
        # Nombre total de sessions
        cursor = conn.execute("""SELECT COUNT(*) FROM analytics_sessions 
               WHERE start_time > datetime('now', '-{} days')""".format(days))
        total_sessions = cursor.fetchone()[0]

        # Durée moyenne des sessions (en minutes)
        cursor = conn.execute("""SELECT AVG(
                (julianday(end_time) - julianday(start_time)) * 24 * 60
            ) FROM analytics_sessions 
            WHERE end_time IS NOT NULL 
            AND start_time > datetime('now', '-{} days')""".format(days))
        avg_duration = cursor.fetchone()[0] or 0

        # Interactions moyennes par session
        cursor = conn.execute("""SELECT AVG(total_interactions) FROM analytics_sessions 
               WHERE start_time > datetime('now', '-{} days')""".format(days))
        avg_interactions = cursor.fetchone()[0] or 0

        return {
            "total_sessions": total_sessions,
            "avg_duration_minutes": round(avg_duration, 2),
            "avg_interactions": round(avg_interactions, 2),
        }


def get_events_by_type(days: int = 30) -> pd.DataFrame:
    """Retourne les événements groupés par type.

    Args:
        days: Nombre de jours à analyser

    Returns:
        DataFrame avec colonnes: event_type, count
    """
    with get_db_connection() as conn:
        return pd.read_sql(
            """SELECT 
                event_type,
                COUNT(*) as count
            FROM analytics_events
            WHERE timestamp > datetime('now', '-{} days')
            GROUP BY event_type
            ORDER BY count DESC""".format(days),
            conn,
        )


def get_conversion_funnel(days: int = 30) -> dict:
    """Calcule le funnel de conversion (session -> import -> validation).

    Args:
        days: Nombre de jours à analyser

    Returns:
        Dict avec les étapes du funnel
    """
    with get_db_connection() as conn:
        # Sessions
        cursor = conn.execute("""SELECT COUNT(DISTINCT session_id) FROM analytics_events 
               WHERE timestamp > datetime('now', '-{} days')""".format(days))
        sessions = cursor.fetchone()[0]

        # Imports démarrés
        cursor = conn.execute("""SELECT COUNT(*) FROM analytics_events 
               WHERE event_type = 'import_started'
               AND timestamp > datetime('now', '-{} days')""".format(days))
        imports_started = cursor.fetchone()[0]

        # Imports complétés
        cursor = conn.execute("""SELECT COUNT(*) FROM analytics_events 
               WHERE event_type = 'import_completed'
               AND timestamp > datetime('now', '-{} days')""".format(days))
        imports_completed = cursor.fetchone()[0]

        # Validations complétées
        cursor = conn.execute("""SELECT COUNT(*) FROM analytics_events 
               WHERE event_type = 'validation_completed'
               AND timestamp > datetime('now', '-{} days')""".format(days))
        validations = cursor.fetchone()[0]

        return {
            "sessions": sessions,
            "imports_started": imports_started,
            "imports_completed": imports_completed,
            "validations": validations,
            "import_start_rate": (
                round((imports_started / sessions * 100), 2) if sessions > 0 else 0
            ),
            "import_completion_rate": (
                round((imports_completed / imports_started * 100), 2) if imports_started > 0 else 0
            ),
            "validation_rate": (
                round((validations / imports_completed * 100), 2) if imports_completed > 0 else 0
            ),
        }


def cleanup_old_events(days_to_keep: int = 90) -> int:
    """Nettoie les événements anciens.

    Args:
        days_to_keep: Nombre de jours à conserver

    Returns:
        Nombre d'événements supprimés
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("""DELETE FROM analytics_events 
                   WHERE timestamp < datetime('now', '-{} days')""".format(days_to_keep))
            conn.commit()
            deleted = cursor.rowcount
            logger.info(f"Nettoyage analytics: {deleted} événements supprimés")
            return deleted
    except Exception as e:
        logger.error(f"Erreur nettoyage analytics: {e}")
        return 0
