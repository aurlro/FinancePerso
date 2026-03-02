"""
Système de tracking d'événements pour Analytics interne
Stockage SQLite local (pas de données externes)
"""

import json
import sqlite3
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

import streamlit as st


class EventType(Enum):
    """Types d'événements trackés."""

    # Onboarding
    EMPTY_STATE_CTA_CLICK = "empty_state_cta_click"
    ONBOARDING_STEP_VIEW = "onboarding_step_view"
    ONBOARDING_COMPLETE = "onboarding_complete"

    # Navigation
    PAGE_VIEW = "page_view"
    NAVIGATION_CLICK = "navigation_click"

    # Actions principales
    IMPORT_START = "import_start"
    IMPORT_COMPLETE = "import_complete"
    VALIDATION_START = "validation_start"
    VALIDATION_COMPLETE = "validation_complete"

    # Dashboard
    KPI_HOVER = "kpi_hover"
    KPI_CLICK = "kpi_click"
    CHART_INTERACTION = "chart_interaction"

    # Engagement
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    FEATURE_DISCOVER = "feature_discover"


class AnalyticsTracker:
    """Tracker d'analytics interne avec SQLite."""

    DB_PATH = Path("Data/analytics.db")

    def __init__(self):
        """Initialise le tracker et crée la DB si nécessaire."""
        self._ensure_db()

    def _ensure_db(self):
        """Crée la base de données et les tables si elles n'existent pas."""
        self.DB_PATH.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.DB_PATH) as conn:
            # Table des événements
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    user_id TEXT,
                    session_id TEXT,
                    page TEXT,
                    properties TEXT,  -- JSON
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Table des sessions
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    duration_seconds INTEGER,
                    pages_viewed TEXT,  -- JSON list
                    user_id TEXT
                )
            """)

            # Index pour performances
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_session ON events(session_id)")

    def track(
        self, event_type: EventType, properties: Optional[Dict] = None, page: Optional[str] = None
    ) -> None:
        """Enregistre un événement."""
        try:
            with sqlite3.connect(self.DB_PATH) as conn:
                conn.execute(
                    """INSERT INTO events 
                       (timestamp, event_type, user_id, session_id, page, properties)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        datetime.now().isoformat(),
                        event_type.value,
                        self._get_user_id(),
                        self._get_session_id(),
                        page or st.session_state.get("current_page", "unknown"),
                        json.dumps(properties or {}),
                    ),
                )
        except Exception:
            # Silencieux en cas d'erreur (analytics non critique)
            pass

    def start_session(self) -> str:
        """Démarre une nouvelle session et retourne son ID."""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S_") + str(id(st.session_state))

        try:
            with sqlite3.connect(self.DB_PATH) as conn:
                conn.execute(
                    """INSERT INTO sessions (id, started_at, pages_viewed, user_id)
                       VALUES (?, ?, ?, ?)""",
                    (session_id, datetime.now().isoformat(), json.dumps([]), self._get_user_id()),
                )
        except Exception:
            pass

        st.session_state["analytics_session_id"] = session_id
        st.session_state["analytics_session_start"] = datetime.now()

        return session_id

    def end_session(self) -> None:
        """Termine la session en cours."""
        session_id = st.session_state.get("analytics_session_id")
        if not session_id:
            return

        start_time = st.session_state.get("analytics_session_start")
        if start_time:
            duration = (datetime.now() - start_time).total_seconds()
        else:
            duration = 0

        pages = st.session_state.get("analytics_pages_viewed", [])

        try:
            with sqlite3.connect(self.DB_PATH) as conn:
                conn.execute(
                    """UPDATE sessions 
                       SET ended_at = ?, duration_seconds = ?, pages_viewed = ?
                       WHERE id = ?""",
                    (datetime.now().isoformat(), int(duration), json.dumps(pages), session_id),
                )
        except Exception:
            pass

    def get_stats(self, days: int = 30) -> Dict[str, Any]:
        """Récupère les statistiques sur les derniers jours."""
        try:
            with sqlite3.connect(self.DB_PATH) as conn:
                since = (datetime.now() - timedelta(days=days)).isoformat()

                # Nombre total d'événements
                cursor = conn.execute("SELECT COUNT(*) FROM events WHERE timestamp > ?", (since,))
                total_events = cursor.fetchone()[0]

                # Événements par type
                cursor = conn.execute(
                    """SELECT event_type, COUNT(*) as count 
                       FROM events WHERE timestamp > ?
                       GROUP BY event_type ORDER BY count DESC""",
                    (since,),
                )
                events_by_type = {row[0]: row[1] for row in cursor.fetchall()}

                # Nombre de sessions
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM sessions WHERE started_at > ?", (since,)
                )
                total_sessions = cursor.fetchone()[0]

                # Durée moyenne des sessions
                cursor = conn.execute(
                    """SELECT AVG(duration_seconds) FROM sessions 
                       WHERE started_at > ? AND duration_seconds IS NOT NULL""",
                    (since,),
                )
                avg_duration = cursor.fetchone()[0] or 0

                return {
                    "total_events": total_events,
                    "total_sessions": total_sessions,
                    "avg_session_duration": round(avg_duration, 2),
                    "events_by_type": events_by_type,
                    "period_days": days,
                }
        except Exception:
            return {}

    def _get_user_id(self) -> str:
        """Récupère ou crée un ID utilisateur anonyme."""
        if "analytics_user_id" not in st.session_state:
            st.session_state["analytics_user_id"] = f"user_{id(st.session_state)}"
        return st.session_state["analytics_user_id"]

    def _get_session_id(self) -> str:
        """Récupère l'ID de session actuel."""
        if "analytics_session_id" not in st.session_state:
            return self.start_session()
        return st.session_state["analytics_session_id"]


# Instance singleton
_tracker: Optional[AnalyticsTracker] = None


def get_tracker() -> AnalyticsTracker:
    """Récupère l'instance du tracker."""
    global _tracker
    if _tracker is None:
        _tracker = AnalyticsTracker()
    return _tracker


def track_event(
    event_type: EventType, properties: Optional[Dict] = None, page: Optional[str] = None
) -> None:
    """Fonction utilitaire pour tracker un événement."""
    tracker = get_tracker()
    tracker.track(event_type, properties, page)


def get_analytics_summary(days: int = 30) -> Dict[str, Any]:
    """Récupère un résumé des analytics."""
    tracker = get_tracker()
    return tracker.get_stats(days)


# Session management
def init_analytics():
    """Initialise les analytics au démarrage de l'app."""
    tracker = get_tracker()
    if "analytics_session_id" not in st.session_state:
        tracker.start_session()
        track_event(EventType.SESSION_START)


def track_page_view(page_name: str):
    """Track la visite d'une page."""
    st.session_state["current_page"] = page_name

    # Ajouter à la liste des pages vues
    if "analytics_pages_viewed" not in st.session_state:
        st.session_state["analytics_pages_viewed"] = []
    st.session_state["analytics_pages_viewed"].append(
        {"page": page_name, "timestamp": datetime.now().isoformat()}
    )

    track_event(EventType.PAGE_VIEW, {"page": page_name})
