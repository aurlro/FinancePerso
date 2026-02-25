"""
Challenge system for short-term goals.
"""

from datetime import datetime, timedelta, date
from dataclasses import dataclass
from enum import Enum
from typing import Callable

import streamlit as st

from modules.db.connection import get_db_connection
from modules.logger import logger


class ChallengeStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Challenge:
    """A challenge with a goal to achieve."""
    id: str
    title: str
    description: str
    icon: str
    target: int  # Target value to achieve
    current: int  # Current progress
    unit: str  # Unit of measurement ("transactions", "€", "jours")
    deadline: datetime  # When challenge ends
    reward: str  # Description of reward
    status: ChallengeStatus = ChallengeStatus.ACTIVE


# Predefined challenges
WEEKLY_CHALLENGES = [
    {
        "id": "validate_week",
        "title": "Validateur de la semaine",
        "description": "Valider 20 transactions cette semaine",
        "icon": "✅",
        "target": 20,
        "unit": "transactions",
        "reward": "🌟 Badge Validateur accéléré"
    },
    {
        "id": "categorize_week",
        "title": "Organisateur",
        "description": "Catégoriser 15 transactions en attente",
        "icon": "🏷️",
        "target": 15,
        "unit": "transactions",
        "reward": "🏷️ Points d'organisation"
    },
    {
        "id": "check_budget",
        "title": "Budget Watch",
        "description": "Consulter vos budgets 3 fois cette semaine",
        "icon": "👀",
        "target": 3,
        "unit": "vérifications",
        "reward": "📊 Alertes budget prioritaires"
    },
]


MONTHLY_CHALLENGES = [
    {
        "id": "complete_month",
        "title": "Mois complet",
        "description": "Valider toutes les transactions du mois",
        "icon": "📅",
        "target": 100,
        "unit": "% validé",
        "reward": "🏆 Badge du mois complet"
    },
    {
        "id": "stay_under_budget",
        "title": "Dans les clous",
        "description": "Respecter tous vos budgets ce mois",
        "icon": "🎯",
        "target": 1,
        "unit": "objectif",
        "reward": "💰 Conseils épargne personnalisés"
    },
]


class ChallengeManager:
    """Manages active challenges."""
    
    TABLE_NAME = "active_challenges"
    
    @classmethod
    def _ensure_table(cls):
        """Create challenges table if not exists."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {cls.TABLE_NAME} (
                        id TEXT PRIMARY KEY,
                        challenge_type TEXT,
                        target INTEGER,
                        current INTEGER DEFAULT 0,
                        deadline DATE,
                        status TEXT DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.warning(f"Could not create challenges table: {e}")
    
    @classmethod
    def get_active_challenges(cls) -> list[Challenge]:
        """Get currently active challenges."""
        try:
            cls._ensure_table()
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    SELECT id, challenge_type, target, current, deadline, status
                    FROM {cls.TABLE_NAME}
                    WHERE status = 'active' AND deadline >= DATE('now')
                """)
                
                challenges = []
                for row in cursor.fetchall():
                    # Map to Challenge object
                    challenge_def = cls._get_challenge_def(row[0])
                    if challenge_def:
                        challenges.append(Challenge(
                            id=row[0],
                            title=challenge_def["title"],
                            description=challenge_def["description"],
                            icon=challenge_def["icon"],
                            target=row[2],
                            current=row[3],
                            unit=challenge_def["unit"],
                            deadline=datetime.fromisoformat(row[4]),
                            reward=challenge_def["reward"],
                            status=ChallengeStatus(row[5])
                        ))
                
                return challenges
        except Exception as e:
            logger.error(f"Could not get challenges: {e}")
            return []
    
    @classmethod
    def _get_challenge_def(cls, challenge_id: str) -> dict | None:
        """Get challenge definition by ID."""
        for c in WEEKLY_CHALLENGES + MONTHLY_CHALLENGES:
            if c["id"] == challenge_id:
                return c
        return None
    
    @classmethod
    def update_progress(cls, challenge_id: str, progress: int):
        """Update challenge progress."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    UPDATE {cls.TABLE_NAME}
                    SET current = ?
                    WHERE id = ? AND status = 'active'
                """, (progress, challenge_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Could not update challenge: {e}")
    
    @classmethod
    def complete_challenge(cls, challenge_id: str):
        """Mark challenge as completed."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    UPDATE {cls.TABLE_NAME}
                    SET status = 'completed'
                    WHERE id = ?
                """, (challenge_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Could not complete challenge: {e}")


def check_challenges() -> list[Challenge]:
    """
    Check all challenges and update their status.
    Returns newly completed challenges.
    """
    manager = ChallengeManager()
    active = manager.get_active_challenges()
    completed = []
    
    for challenge in active:
        if challenge.current >= challenge.target:
            manager.complete_challenge(challenge.id)
            completed.append(challenge)
    
    return completed


def get_active_challenges() -> list[Challenge]:
    """Get all active challenges."""
    return ChallengeManager.get_active_challenges()


def render_challenges_widget():
    """Render active challenges in Streamlit."""
    challenges = get_active_challenges()
    
    if not challenges:
        st.info("Aucun challenge actif pour le moment")
        return
    
    st.subheader("🎯 Challenges actifs")
    
    for challenge in challenges:
        with st.container():
            cols = st.columns([0.1, 0.7, 0.2])
            
            cols[0].markdown(f"**{challenge.icon}**")
            
            with cols[1]:
                st.write(f"**{challenge.title}**")
                progress = min(challenge.current / challenge.target, 1.0)
                st.progress(progress, text=f"{challenge.current}/{challenge.target} {challenge.unit}")
            
            days_left = (challenge.deadline - datetime.now()).days
            cols[2].caption(f"{days_left}j restants")
        
        st.divider()
