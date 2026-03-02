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
from modules.ui.tokens import ColorPalette, Colors, Spacing, Typography


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
        "reward": "🌟 Badge Validateur accéléré",
    },
    {
        "id": "categorize_week",
        "title": "Organisateur",
        "description": "Catégoriser 15 transactions en attente",
        "icon": "🏷️",
        "target": 15,
        "unit": "transactions",
        "reward": "🏷️ Points d'organisation",
    },
    {
        "id": "check_budget",
        "title": "Budget Watch",
        "description": "Consulter vos budgets 3 fois cette semaine",
        "icon": "👀",
        "target": 3,
        "unit": "vérifications",
        "reward": "📊 Alertes budget prioritaires",
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
        "reward": "🏆 Badge du mois complet",
    },
    {
        "id": "stay_under_budget",
        "title": "Dans les clous",
        "description": "Respecter tous vos budgets ce mois",
        "icon": "🎯",
        "target": 1,
        "unit": "objectif",
        "reward": "💰 Conseils épargne personnalisés",
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
                        challenges.append(
                            Challenge(
                                id=row[0],
                                title=challenge_def["title"],
                                description=challenge_def["description"],
                                icon=challenge_def["icon"],
                                target=row[2],
                                current=row[3],
                                unit=challenge_def["unit"],
                                deadline=datetime.fromisoformat(row[4]),
                                reward=challenge_def["reward"],
                                status=ChallengeStatus(row[5]),
                            )
                        )

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
                cursor.execute(
                    f"""
                    UPDATE {cls.TABLE_NAME}
                    SET current = ?
                    WHERE id = ? AND status = 'active'
                """,
                    (progress, challenge_id),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Could not update challenge: {e}")

    @classmethod
    def complete_challenge(cls, challenge_id: str):
        """Mark challenge as completed."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"""
                    UPDATE {cls.TABLE_NAME}
                    SET status = 'completed'
                    WHERE id = ?
                """,
                    (challenge_id,),
                )
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


def _create_challenge_card(challenge: Challenge) -> str:
    """Create a styled challenge card using Design System tokens."""
    progress = min(challenge.current / challenge.target, 1.0)
    progress_pct = int(progress * 100)

    days_left = (challenge.deadline - datetime.now()).days
    _palette = ColorPalette()
    days_color = (
        Colors.DANGER.value
        if days_left <= 2
        else (Colors.WARNING.value if days_left <= 5 else _palette.text_secondary)
    )

    # Progress bar color based on completion
    if progress >= 1.0:
        bar_color = Colors.SECONDARY.value
    elif progress >= 0.5:
        bar_color = Colors.INFO.value
    else:
        bar_color = Colors.PRIMARY.value

    return f"""
    <div style="
        background-color: {_palette.bg_secondary};
        border: 1px solid {_palette.border};
        border-radius: 12px;
        padding: {Spacing.LG};
        margin-bottom: {Spacing.MD};
        transition: all 0.3s ease;
    " onmouseover="this.style.borderColor='{_palette.border_light}';this.style.transform='translateY(-2px)'" 
       onmouseout="this.style.borderColor='{_palette.border}';this.style.transform='translateY(0)'">
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: {Spacing.MD};
        ">
            <div style="display: flex; align-items: center; gap: {Spacing.SM};">
                <span style="font-size: 1.75rem;">{challenge.icon}</span>
                <div>
                    <div style="
                        font-size: {Typography.SIZE_BASE};
                        font-weight: {Typography.WEIGHT_SEMIBOLD};
                        color: {_palette.text_primary};
                    ">{challenge.title}</div>
                    <div style="
                        font-size: {Typography.SIZE_SM};
                        color: {_palette.text_muted};
                    ">{challenge.description}</div>
                </div>
            </div>
            <span style="
                font-size: {Typography.SIZE_XS};
                color: {days_color};
                font-weight: {Typography.WEIGHT_MEDIUM};
                white-space: nowrap;
            ">{days_left}j restants</span>
        </div>
        
        <div style="margin-bottom: {Spacing.XS};">
            <div style="
                display: flex;
                justify-content: space-between;
                font-size: {Typography.SIZE_SM};
                color: {_palette.text_secondary};
                margin-bottom: {Spacing.XS};
            ">
                <span>Progression</span>
                <span style="font-weight: {Typography.WEIGHT_SEMIBOLD};">{challenge.current}/{challenge.target} {challenge.unit}</span>
            </div>
            <div style="
                width: 100%;
                height: 8px;
                background-color: {_palette.bg_tertiary};
                border-radius: 4px;
                overflow: hidden;
            ">
                <div style="
                    width: {progress_pct}%;
                    height: 100%;
                    background-color: {bar_color};
                    border-radius: 4px;
                    transition: width 0.5s ease;
                "></div>
            </div>
        </div>
        
        <div style="
            font-size: {Typography.SIZE_XS};
            color: {Colors.ACCENT.value};
            margin-top: {Spacing.SM};
            padding-top: {Spacing.SM};
            border-top: 1px solid {Colors.BORDER.value};
        ">
            🎁 Récompense: {challenge.reward}
        </div>
    </div>
    """


def render_challenges_widget():
    """Render active challenges in Streamlit using Design System."""
    _palette = ColorPalette()
    challenges = get_active_challenges()

    if not challenges:
        st.markdown(
            f"""
        <div style="
            background-color: {_palette.bg_secondary};
            border: 1px dashed {_palette.border};
            border-radius: 12px;
            padding: {Spacing.XL};
            text-align: center;
            color: {_palette.text_muted};
        ">
            <div style="font-size: 2rem; margin-bottom: {Spacing.SM};">🎯</div>
            <div style="font-size: {Typography.SIZE_BASE}; font-weight: {Typography.WEIGHT_MEDIUM};">
                Aucun challenge actif pour le moment
            </div>
            <div style="font-size: {Typography.SIZE_SM}; margin-top: {Spacing.XS};">
                Revenez bientôt pour de nouveaux défis!
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        return

    for challenge in challenges:
        st.markdown(_create_challenge_card(challenge), unsafe_allow_html=True)
