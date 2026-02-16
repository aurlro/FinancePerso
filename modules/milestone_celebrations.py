"""
Milestone Celebrations - Système de célébrations pour les accomplissements.

Fournit des feedbacks positifs (balloons, badges, messages) lorsque
l'utilisateur atteint des milestones importants.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

import streamlit as st

from modules.logger import logger

CELEBRATIONS_FILE = Path("Data/celebrations.json")


class MilestoneType(Enum):
    """Types de milestones célébrables."""

    TRANSACTIONS_100 = "first_100_tx"
    TRANSACTIONS_500 = "first_500_tx"
    TRANSACTIONS_1000 = "first_1000_tx"
    STREAK_7 = "streak_7_days"
    STREAK_30 = "streak_30_days"
    STREAK_100 = "streak_100_days"
    FIRST_SAVING = "first_positive_month"
    BUDGET_MASTER = "budget_master"
    RULE_WIZARD = "rule_wizard"
    GOAL_ACHIEVED = "goal_achieved"


@dataclass
class Milestone:
    """Un milestone avec ses propriétés."""

    type: MilestoneType
    title: str
    message: str
    badge: str | None = None
    emoji: str = "🏆"

    def to_dict(self) -> dict:
        return {
            "type": self.type.value,
            "title": self.title,
            "message": self.message,
            "badge": self.badge,
            "emoji": self.emoji,
        }


# Définition des milestones
MILESTONES = {
    MilestoneType.TRANSACTIONS_100: Milestone(
        type=MilestoneType.TRANSACTIONS_100,
        title="💯 Première centaine !",
        message="100 transactions catégorisées. Vous êtes un pro de la gestion financière !",
        badge="centurion",
        emoji="💯",
    ),
    MilestoneType.TRANSACTIONS_500: Milestone(
        type=MilestoneType.TRANSACTIONS_500,
        title="🚀 500 transactions !",
        message="Une maîtrise exceptionnelle de vos finances. Bravo !",
        badge="master",
        emoji="🚀",
    ),
    MilestoneType.TRANSACTIONS_1000: Milestone(
        type=MilestoneType.TRANSACTIONS_1000,
        title="👑 1000 transactions !",
        message="Vous êtes un expert. Quel parcours !",
        badge="legend",
        emoji="👑",
    ),
    MilestoneType.STREAK_7: Milestone(
        type=MilestoneType.STREAK_7,
        title="🔥 Semaine parfaite !",
        message="7 jours consécutifs d'utilisation. L'habitude se forme !",
        badge="week_streak",
        emoji="🔥",
    ),
    MilestoneType.STREAK_30: Milestone(
        type=MilestoneType.STREAK_30,
        title="🌟 Mois complet !",
        message="30 jours de suivi financier sans interruption. Incroyable !",
        badge="month_streak",
        emoji="🌟",
    ),
    MilestoneType.STREAK_100: Milestone(
        type=MilestoneType.STREAK_100,
        title="💎 100 jours !",
        message="Une discipline de fer. Vous êtes un modèle !",
        badge="diamond_streak",
        emoji="💎",
    ),
    MilestoneType.FIRST_SAVING: Milestone(
        type=MilestoneType.FIRST_SAVING,
        title="🏆 Premier mois positif !",
        message="Vous avez économisé ce mois-ci. C'est un excellent début !",
        badge="saver",
        emoji="🏆",
    ),
    MilestoneType.BUDGET_MASTER: Milestone(
        type=MilestoneType.BUDGET_MASTER,
        title="🎯 Maître du budget !",
        message="Tous les budgets respectés ce mois. Un vrai pro !",
        badge="budget_master",
        emoji="🎯",
    ),
    MilestoneType.RULE_WIZARD: Milestone(
        type=MilestoneType.RULE_WIZARD,
        title="⚡ Magicien des règles !",
        message="10 règles de catégorisation créées. L'automatisation, c'est la vie !",
        badge="rule_wizard",
        emoji="⚡",
    ),
    MilestoneType.GOAL_ACHIEVED: Milestone(
        type=MilestoneType.GOAL_ACHIEVED,
        title="🎉 Objectif atteint !",
        message="Vous avez réalisé votre objectif d'épargne. Félicitations !",
        badge="goal_achiever",
        emoji="🎉",
    ),
}


class CelebrationManager:
    """Gestionnaire des célébrations de milestones."""

    def __init__(self):
        self._ensure_file_exists()
        self.celebrated = self._load_celebrated()

    def _ensure_file_exists(self):
        """Créer le fichier s'il n'existe pas."""
        CELEBRATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not CELEBRATIONS_FILE.exists():
            CELEBRATIONS_FILE.write_text("{}", encoding="utf-8")

    def _load_celebrated(self) -> dict[str, str]:
        """Charger les milestones déjà célébrés."""
        try:
            return json.loads(CELEBRATIONS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_celebrated(self):
        """Sauvegarder les milestones célébrés."""
        try:
            CELEBRATIONS_FILE.write_text(json.dumps(self.celebrated, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error(f"Error saving celebrations: {e}")

    def has_celebrated(self, milestone_type: MilestoneType) -> bool:
        """Vérifier si un milestone a déjà été célébré."""
        return milestone_type.value in self.celebrated

    def mark_celebrated(self, milestone_type: MilestoneType):
        """Marquer un milestone comme célébré."""
        self.celebrated[milestone_type.value] = datetime.now().isoformat()
        self._save_celebrated()

    def check_milestones(self) -> list[Milestone]:
        """Vérifier tous les milestones et retourner ceux à célébrer."""
        to_celebrate = []

        try:
            # Importer les stats nécessaires
            from modules.db.rules import get_learning_rules
            from modules.db.stats import get_global_stats
            from modules.gamification import GamificationManager
            from modules.savings_goals import get_achieved_goals

            stats = get_global_stats()

            # Vérifier les transactions
            if stats:
                tx_count = stats.get("total_transactions", 0)

                if tx_count >= 1000 and not self.has_celebrated(MilestoneType.TRANSACTIONS_1000):
                    to_celebrate.append(MILESTONES[MilestoneType.TRANSACTIONS_1000])
                elif tx_count >= 500 and not self.has_celebrated(MilestoneType.TRANSACTIONS_500):
                    to_celebrate.append(MILESTONES[MilestoneType.TRANSACTIONS_500])
                elif tx_count >= 100 and not self.has_celebrated(MilestoneType.TRANSACTIONS_100):
                    to_celebrate.append(MILESTONES[MilestoneType.TRANSACTIONS_100])

            # Vérifier le streak
            try:
                gamification = GamificationManager()
                streak_stats = gamification.get_stats_summary()
                streak = streak_stats.get("streak", 0)

                if streak >= 100 and not self.has_celebrated(MilestoneType.STREAK_100):
                    to_celebrate.append(MILESTONES[MilestoneType.STREAK_100])
                elif streak >= 30 and not self.has_celebrated(MilestoneType.STREAK_30):
                    to_celebrate.append(MILESTONES[MilestoneType.STREAK_30])
                elif streak >= 7 and not self.has_celebrated(MilestoneType.STREAK_7):
                    to_celebrate.append(MILESTONES[MilestoneType.STREAK_7])
            except Exception:
                pass

            # Vérifier les règles
            try:
                rules = get_learning_rules()
                if not rules.empty and len(rules) >= 10:
                    if not self.has_celebrated(MilestoneType.RULE_WIZARD):
                        to_celebrate.append(MILESTONES[MilestoneType.RULE_WIZARD])
            except Exception:
                pass

            # Vérifier les objectifs atteints
            try:
                achieved = get_achieved_goals()
                if achieved:
                    # Célébrer le dernier objectif atteint
                    if not self.has_celebrated(MilestoneType.GOAL_ACHIEVED):
                        # Vérifier si c'est un nouvel objectif atteint depuis la dernière visite
                        to_celebrate.append(MILESTONES[MilestoneType.GOAL_ACHIEVED])
            except Exception:
                pass

        except Exception as e:
            logger.error(f"Error checking milestones: {e}")

        return to_celebrate


# Singleton
_celebration_manager: CelebrationManager | None = None


def get_celebration_manager() -> CelebrationManager:
    """Get or create the celebration manager singleton."""
    global _celebration_manager
    if _celebration_manager is None:
        _celebration_manager = CelebrationManager()
    return _celebration_manager


def render_celebration(milestone: Milestone):
    """Afficher une célébration pour un milestone."""

    # Effet visuel
    st.balloons()

    # Message de succès
    st.success(f"## {milestone.emoji} {milestone.title}\n{milestone.message}")

    # Badge si applicable
    if milestone.badge:
        st.info(f"🏅 Badge débloqué: **{milestone.badge}**")

    # Marquer comme célébré
    get_celebration_manager().mark_celebrated(milestone.type)


def check_and_render_celebrations():
    """Vérifier et afficher les célébrations en attente."""

    manager = get_celebration_manager()
    milestones = manager.check_milestones()

    for milestone in milestones:
        render_celebration(milestone)


# Fonction utilitaire pour célébrer un objectif atteint spécifique
def celebrate_goal_achieved(goal_name: str, amount: float):
    """Célébrer l'atteinte d'un objectif d'épargne spécifique."""

    st.balloons()
    st.success(
        f"""
    ## 🎉 Félicitations !
    
    Vous avez atteint votre objectif **{goal_name}** !
    
    Montant épargné: **{amount:.0f}€**
    
    Quel accomplissement ! 🏆
    """
    )

    # Option de partage
    col1, col2 = st.columns(2)
    with col1:
        st.button("📱 Partager", key="share_goal_achieved")
    with col2:
        if st.button("🎯 Nouvel objectif", key="new_goal_after_achievement"):
            st.session_state["show_goal_form"] = True
            st.rerun()
