"""
Badge system for achievements.
"""

from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Callable

import streamlit as st

from modules.db.connection import get_db_connection
from modules.logger import logger


class BadgeRarity(Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class Badge:
    """A badge that can be earned."""
    id: str
    name: str
    description: str
    icon: str
    rarity: BadgeRarity
    condition: Callable[[], bool]
    hidden: bool = False  # Secret badges


# Define all badges
BADGES = {
    "first_transaction": Badge(
        id="first_transaction",
        name="Premier pas",
        description="Importer votre première transaction",
        icon="🌱",
        rarity=BadgeRarity.COMMON,
        condition=lambda: _count_transactions() >= 1
    ),
    "hundred_transactions": Badge(
        id="hundred_transactions",
        name="Centurion",
        description="Importer 100 transactions",
        icon="💯",
        rarity=BadgeRarity.RARE,
        condition=lambda: _count_transactions() >= 100
    ),
    "thousand_transactions": Badge(
        id="thousand_transactions",
        name="Collectionneur",
        description="Importer 1,000 transactions",
        icon="📊",
        rarity=BadgeRarity.EPIC,
        condition=lambda: _count_transactions() >= 1000
    ),
    "week_streak": Badge(
        id="week_streak",
        name="Régulier",
        description="7 jours de connexion consécutifs",
        icon="📅",
        rarity=BadgeRarity.COMMON,
        condition=lambda: _get_streak() >= 7
    ),
    "month_streak": Badge(
        id="month_streak",
        name="Marathonien",
        description="30 jours de connexion consécutifs",
        icon="🏃",
        rarity=BadgeRarity.RARE,
        condition=lambda: _get_streak() >= 30
    ),
    "budget_master": Badge(
        id="budget_master",
        name="Maître des budgets",
        description="Créer 5 budgets",
        icon="🎯",
        rarity=BadgeRarity.COMMON,
        condition=lambda: _count_budgets() >= 5
    ),
    "validator": Badge(
        id="validator",
        name="Validateur",
        description="Valider 50 transactions",
        icon="✅",
        rarity=BadgeRarity.COMMON,
        condition=lambda: _count_validated() >= 50
    ),
    "category_organizer": Badge(
        id="category_organizer",
        name="Organisateur",
        description="Créer 10 catégories personnalisées",
        icon="🏷️",
        rarity=BadgeRarity.RARE,
        condition=lambda: _count_categories() >= 10
    ),
    "saver": Badge(
        id="saver",
        name="Épargnant",
        description="3 mois avec épargne positive",
        icon="💰",
        rarity=BadgeRarity.RARE,
        condition=lambda: _check_saving_streak()
    ),
    "data_analyst": Badge(
        id="data_analyst",
        name="Analyste",
        description="Consulter le dashboard 20 fois",
        icon="📈",
        rarity=BadgeRarity.COMMON,
        condition=lambda: False  # Would need session tracking
    ),
    "midnight_owl": Badge(
        id="midnight_owl",
        name="Couche-tard",
        description="Se connecter après minuit",
        icon="🦉",
        rarity=BadgeRarity.EPIC,
        condition=lambda: False,  # Secret badge, checked differently
        hidden=True
    ),
}


# Helper functions for badge conditions
def _count_transactions() -> int:
    try:
        from modules.db.transactions import get_all_transactions
        df = get_all_transactions()
        return len(df)
    except Exception as e:
        logger.warning(f"Error counting transactions: {e}")
        return 0


def _get_streak() -> int:
    try:
        from modules.gamification.streaks import StreakManager
        return StreakManager.get_streak().current_streak
    except Exception as e:
        logger.warning(f"Error getting streak: {e}")
        return 0


def _count_budgets() -> int:
    try:
        from modules.db.budgets import get_budgets
        return len(get_budgets())
    except Exception as e:
        logger.warning(f"Error counting budgets: {e}")
        return 0


def _count_validated() -> int:
    try:
        from modules.db.transactions import get_all_transactions
        df = get_all_transactions()
        return len(df[df['status'] == 'validated'])
    except Exception as e:
        logger.warning(f"Error counting validated: {e}")
        return 0


def _count_categories() -> int:
    try:
        from modules.db.categories import get_categories
        cats = get_categories()
        # Exclude defaults
        defaults = {'Alimentation', 'Transport', 'Logement', 'Revenus', 
                   'Virement Interne', 'Hors Budget', 'Inconnu'}
        return len([c for c in cats if c not in defaults])
    except Exception as e:
        logger.warning(f"Error counting categories: {e}")
        return 0


def _check_saving_streak() -> bool:
    # Would need more complex logic for 3-month positive savings
    return False


class BadgeManager:
    """Manages earned badges."""
    
    TABLE_NAME = "user_badges"
    
    @classmethod
    def _ensure_table(cls):
        """Create badges table if not exists."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {cls.TABLE_NAME} (
                        badge_id TEXT PRIMARY KEY,
                        earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.warning(f"Could not create badges table: {e}")
    
    @classmethod
    def check_and_award_badges(cls) -> list[Badge]:
        """
        Check all badges and award new ones.
        
        Returns:
            List of newly earned badges
        """
        try:
            cls._ensure_table()
            earned_badges = cls._get_earned_badge_ids()
            new_badges = []
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                for badge_id, badge in BADGES.items():
                    if badge_id in earned_badges:
                        continue
                    
                    try:
                        if badge.condition():
                            cursor.execute(f"""
                                INSERT INTO {cls.TABLE_NAME} (badge_id)
                                VALUES (?)
                            """, (badge_id,))
                            new_badges.append(badge)
                    except Exception as e:
                        logger.debug(f"Badge check failed for {badge_id}: {e}")
                
                conn.commit()
            
            return new_badges
            
        except Exception as e:
            logger.error(f"Could not check badges: {e}")
            return []
    
    @classmethod
    def _get_earned_badge_ids(cls) -> set:
        """Get IDs of already earned badges."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT badge_id FROM {cls.TABLE_NAME}")
                return {row[0] for row in cursor.fetchall()}
        except Exception as e:
            logger.warning(f"Error getting earned badge IDs: {e}")
            return set()
    
    @classmethod
    def get_user_badges(cls) -> list[Badge]:
        """Get all earned badges."""
        earned_ids = cls._get_earned_badge_ids()
        return [BADGES[bid] for bid in earned_ids if bid in BADGES]


def get_user_badges() -> list[Badge]:
    """Get user's earned badges."""
    return BadgeManager.get_user_badges()


def has_badge(badge_id: str) -> bool:
    """Check if user has specific badge."""
    return badge_id in {b.id for b in get_user_badges()}


def render_badges_collection():
    """Render badge collection in Streamlit."""
    st.subheader("🏆 Collection de badges")
    
    earned = get_user_badges()
    total = len([b for b in BADGES.values() if not b.hidden])
    
    st.progress(len(earned) / total if total > 0 else 0)
    st.caption(f"{len(earned)} / {total} badges")
    
    if earned:
        cols = st.columns(4)
        for i, badge in enumerate(earned):
            with cols[i % 4]:
                st.markdown(f"**{badge.icon}**")
                st.caption(badge.name)
                if st.button("ℹ️", key=f"badge_info_{badge.id}"):
                    st.info(badge.description)
    else:
        st.info("Commencez à utiliser l'app pour gagner des badges!")
    
    # Show next possible badges
    st.divider()
    st.subheader("🔒 Badges à débloquer")
    
    locked = [b for bid, b in BADGES.items() if bid not in {eb.id for eb in earned} and not b.hidden][:3]
    for badge in locked:
        st.markdown(f"🔒 **{badge.name}** - {badge.description}")
