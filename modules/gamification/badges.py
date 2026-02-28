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
from modules.ui.tokens import Colors, Spacing, Typography


class BadgeRarity(Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


# Color mapping for badge rarities using Design System
RARITY_COLORS = {
    BadgeRarity.COMMON: (Colors.TEXT_SECONDARY.value, Colors.BG_TERTIARY.value),
    BadgeRarity.RARE: (Colors.INFO.value, "rgba(59, 130, 246, 0.2)"),
    BadgeRarity.EPIC: (Colors.ACCENT.value, "rgba(245, 158, 11, 0.2)"),
    BadgeRarity.LEGENDARY: (Colors.PRIMARY_LIGHT.value, "rgba(99, 102, 241, 0.3)"),
}

RARITY_LABELS = {
    BadgeRarity.COMMON: "Commun",
    BadgeRarity.RARE: "Rare",
    BadgeRarity.EPIC: "Épique",
    BadgeRarity.LEGENDARY: "Légendaire",
}


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


def _create_badge_card(badge: Badge, earned: bool = True) -> str:
    """Create a styled badge card using Design System tokens."""
    if earned:
        text_color, bg_color = RARITY_COLORS.get(badge.rarity, RARITY_COLORS[BadgeRarity.COMMON])
        border_color = text_color
        opacity = "1"
        lock_icon = ""
    else:
        text_color = Colors.TEXT_MUTED.value
        bg_color = Colors.BG_SECONDARY.value
        border_color = Colors.BORDER.value
        opacity = "0.6"
        lock_icon = "🔒 "
    
    rarity_label = RARITY_LABELS.get(badge.rarity, "")
    
    return f"""
    <div style="
        background-color: {bg_color};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: {Spacing.LG};
        text-align: center;
        opacity: {opacity};
        transition: all 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    " onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='{Colors.SHADOW_LG.value}'" 
       onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='none'">
        <div>
            <div style="
                font-size: 3rem;
                margin-bottom: {Spacing.SM};
            ">{lock_icon}{badge.icon}</div>
            <div style="
                font-size: {Typography.SIZE_SM};
                font-weight: {Typography.WEIGHT_SEMIBOLD};
                color: {text_color};
                margin-bottom: {Spacing.XS};
            ">{badge.name}</div>
            <div style="
                font-size: {Typography.SIZE_XS};
                color: {Colors.TEXT_MUTED.value};
                margin-bottom: {Spacing.SM};
                min-height: 2.5em;
            ">{badge.description}</div>
        </div>
        <div>
            <span style="
                display: inline-block;
                padding: {Spacing.XS} {Spacing.SM};
                border-radius: 9999px;
                font-size: {Typography.SIZE_XS};
                font-weight: {Typography.WEIGHT_MEDIUM};
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: {text_color};
                background-color: {bg_color};
                border: 1px solid {border_color};
            ">{rarity_label}</span>
        </div>
    </div>
    """


def render_badges_collection():
    """Render badge collection in Streamlit using Design System."""
    earned = get_user_badges()
    total = len([b for b in BADGES.values() if not b.hidden])
    
    # Progress section with Design System styling
    progress_pct = len(earned) / total if total > 0 else 0
    
    st.markdown(f"""
    <div style="
        background-color: {Colors.BG_SECONDARY.value};
        border: 1px solid {Colors.BORDER.value};
        border-radius: 12px;
        padding: {Spacing.LG};
        margin-bottom: {Spacing.LG};
    ">
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: {Spacing.SM};
        ">
            <span style="
                font-size: {Typography.SIZE_SM};
                font-weight: {Typography.WEIGHT_MEDIUM};
                color: {Colors.TEXT_SECONDARY.value};
            ">Progression</span>
            <span style="
                font-size: {Typography.SIZE_LG};
                font-weight: {Typography.WEIGHT_BOLD};
                color: {Colors.TEXT_PRIMARY.value};
                font-family: {Typography.FONT_MONO};
            ">{len(earned)} / {total}</span>
        </div>
        <div style="
            width: 100%;
            height: 8px;
            background-color: {Colors.BG_TERTIARY.value};
            border-radius: 4px;
            overflow: hidden;
        ">
            <div style="
                width: {progress_pct * 100}%;
                height: 100%;
                background: linear-gradient(90deg, {Colors.PRIMARY.value} 0%, {Colors.PRIMARY_LIGHT.value} 100%);
                border-radius: 4px;
                transition: width 0.5s ease;
            "></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Earned badges section
    if earned:
        st.markdown(f"""
        <h3 style="
            font-size: {Typography.SIZE_XL};
            font-weight: {Typography.WEIGHT_SEMIBOLD};
            color: {Colors.TEXT_PRIMARY.value};
            margin-bottom: {Spacing.MD};
            margin-top: {Spacing.LG};
        ">🏆 Badges débloqués</h3>
        """, unsafe_allow_html=True)
        
        # Display badges in a grid
        cols_per_row = 4
        for i in range(0, len(earned), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, badge in enumerate(earned[i:i+cols_per_row]):
                with cols[j]:
                    st.markdown(_create_badge_card(badge, earned=True), unsafe_allow_html=True)
                    
                    # Info button using Design System button pattern
                    if st.button(
                        "ℹ️ Détails",
                        key=f"badge_info_{badge.id}",
                        use_container_width=True,
                        type="secondary"
                    ):
                        st.info(f"**{badge.name}**\n\n{badge.description}")
    else:
        st.markdown(f"""
        <div style="
            background-color: {Colors.BG_SECONDARY.value};
            border: 1px dashed {Colors.BORDER.value};
            border-radius: 12px;
            padding: {Spacing.XL};
            text-align: center;
            color: {Colors.TEXT_MUTED.value};
        ">
            <div style="font-size: 2rem; margin-bottom: {Spacing.SM};">🎯</div>
            <div style="font-size: {Typography.SIZE_BASE}; font-weight: {Typography.WEIGHT_MEDIUM};">
                Commencez à utiliser l'app pour gagner des badges!
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Locked badges section
    st.markdown(f"""
    <h3 style="
        font-size: {Typography.SIZE_XL};
        font-weight: {Typography.WEIGHT_SEMIBOLD};
        color: {Colors.TEXT_PRIMARY.value};
        margin-bottom: {Spacing.MD};
        margin-top: {Spacing.XL};
        padding-top: {Spacing.LG};
        border-top: 1px solid {Colors.BORDER.value};
    ">🔒 Badges à débloquer</h3>
    """, unsafe_allow_html=True)
    
    earned_ids = {b.id for b in earned}
    locked = [b for bid, b in BADGES.items() 
              if bid not in earned_ids and not b.hidden]
    
    if locked:
        # Show first 3 locked badges
        cols_per_row = 3
        display_locked = locked[:3]
        
        for i in range(0, len(display_locked), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, badge in enumerate(display_locked[i:i+cols_per_row]):
                with cols[j]:
                    st.markdown(_create_badge_card(badge, earned=False), unsafe_allow_html=True)
        
        # Show count of remaining badges
        if len(locked) > 3:
            remaining = len(locked) - 3
            st.markdown(f"""
            <div style="
                text-align: center;
                color: {Colors.TEXT_MUTED.value};
                font-size: {Typography.SIZE_SM};
                margin-top: {Spacing.MD};
                padding: {Spacing.MD};
                background-color: {Colors.BG_SECONDARY.value};
                border-radius: 8px;
            ">
                + {remaining} autre{'s' if remaining > 1 else ''} badge{'s' if remaining > 1 else ''} secret{'s' if remaining > 1 else ''} à découvrir...
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="
            background-color: rgba(16, 185, 129, 0.1);
            border: 1px solid {Colors.SECONDARY.value};
            border-radius: 12px;
            padding: {Spacing.LG};
            text-align: center;
        ">
            <div style="font-size: 2rem; margin-bottom: {Spacing.SM};">🎉</div>
            <div style="
                font-size: {Typography.SIZE_BASE};
                font-weight: {Typography.WEIGHT_SEMIBOLD};
                color: {Colors.SECONDARY.value};
            ">
                Félicitations! Vous avez débloqué tous les badges visibles!
            </div>
        </div>
        """, unsafe_allow_html=True)
