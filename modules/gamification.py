"""
Système de gamification: challenges, badges, streaks.
Objectif: Créer l'habitude et l'engagement quotidien.
"""

import json
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from pathlib import Path

from modules.logger import logger
from modules.db.stats import get_global_stats
from modules.db.transactions import get_all_transactions
import pandas as pd


@dataclass
class Challenge:
    """Un challenge à accomplir."""

    id: str
    title: str
    description: str
    type: str  # 'daily', 'weekly', 'monthly', 'one_time'
    condition_type: str  # 'no_spend', 'budget_under', 'import_count', etc.
    condition_value: float
    reward_badge: str
    reward_points: int
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    completed: bool = False
    completed_at: Optional[str] = None
    progress: float = 0.0  # 0.0 to 1.0


@dataclass
class Badge:
    """Un badge débloqué."""

    id: str
    name: str
    description: str
    icon: str
    unlocked_at: str
    rarity: str  # 'common', 'rare', 'epic', 'legendary'


@dataclass
class UserStats:
    """Stats utilisateur pour gamification."""

    total_points: int
    current_streak: int  # jours consécutifs d'utilisation
    longest_streak: int
    last_visit: Optional[str]
    badges: List[Badge]
    completed_challenges: List[str]


class GamificationManager:
    """Gère toute la gamification."""

    # Challenges prédéfinis
    DEFAULT_CHALLENGES = [
        Challenge(
            id="no_spend_day",
            title="🛡️ Jour de résistance",
            description="Aucune dépense aujourd'hui",
            type="daily",
            condition_type="no_spend",
            condition_value=1,
            reward_badge="resistant",
            reward_points=50,
        ),
        Challenge(
            id="under_budget",
            title="📊 Dans le budget",
            description="Dépenses sous les 80% du budget du jour",
            type="daily",
            condition_type="budget_under",
            condition_value=0.8,
            reward_badge="planner",
            reward_points=30,
        ),
        Challenge(
            id="week_no_restaurant",
            title="🍳 Semaine maison",
            description="7 jours sans restaurant",
            type="weekly",
            condition_type="category_no_spend",
            condition_value=7,
            reward_badge="chef",
            reward_points=200,
        ),
        Challenge(
            id="import_streak_7",
            title="📥 Régulier",
            description="Importer des transactions 7 jours de suite",
            type="weekly",
            condition_type="import_streak",
            condition_value=7,
            reward_badge="organized",
            reward_points=100,
        ),
        Challenge(
            id="savings_20_percent",
            title="💰 Épargneur",
            description="Économiser 20% du revenu ce mois",
            type="monthly",
            condition_type="savings_rate",
            condition_value=0.20,
            reward_badge="saver",
            reward_points=500,
        ),
        Challenge(
            id="first_budget",
            title="🎯 Premier objectif",
            description="Créer votre premier budget",
            type="one_time",
            condition_type="create_budget",
            condition_value=1,
            reward_badge="starter",
            reward_points=100,
        ),
    ]

    def __init__(self):
        self.data_file = Path("Data/gamification.json")
        self.data_file.parent.mkdir(exist_ok=True)
        self.challenges: List[Challenge] = []
        self.badges: List[Badge] = []
        self.stats = UserStats(
            total_points=0,
            current_streak=0,
            longest_streak=0,
            last_visit=None,
            badges=[],
            completed_challenges=[],
        )
        self._load()
        self._check_daily_streak()

    def _load(self):
        """Charge les données de gamification."""
        if self.data_file.exists():
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.stats = UserStats(**data.get("stats", {}))
                    self.challenges = [Challenge(**c) for c in data.get("challenges", [])]
                    self.badges = [Badge(**b) for b in data.get("badges", [])]
            except Exception as e:
                logger.error(f"Error loading gamification data: {e}")

        # Initialiser les challenges par défaut si vide
        if not self.challenges:
            self.challenges = self.DEFAULT_CHALLENGES.copy()

    def _save(self):
        """Sauvegarde les données."""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "stats": asdict(self.stats),
                        "challenges": [asdict(c) for c in self.challenges],
                        "badges": [asdict(b) for b in self.badges],
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            logger.error(f"Error saving gamification data: {e}")

    def _check_daily_streak(self):
        """Vérifie et met à jour le streak quotidien."""
        today = datetime.now().date()

        if self.stats.last_visit:
            last = datetime.fromisoformat(self.stats.last_visit).date()
            diff = (today - last).days

            if diff == 0:
                # Déjà visité aujourd'hui
                pass
            elif diff == 1:
                # Jour consécutif
                self.stats.current_streak += 1
                self.stats.longest_streak = max(
                    self.stats.longest_streak, self.stats.current_streak
                )
                self.stats.last_visit = today.isoformat()
                self._save()
                logger.info(f"Streak continued: {self.stats.current_streak} days")
            else:
                # Streak cassé
                if self.stats.current_streak > 0:
                    logger.info(f"Streak broken! Was {self.stats.current_streak} days")
                self.stats.current_streak = 1
                self.stats.last_visit = today.isoformat()
                self._save()
        else:
            # Première visite
            self.stats.current_streak = 1
            self.stats.last_visit = today.isoformat()
            self._save()

    def get_active_challenges(self) -> List[Challenge]:
        """Retourne les challenges actifs et non complétés."""
        today = datetime.now()

        active = []
        for c in self.challenges:
            if c.completed:
                continue

            # Vérifier dates
            if c.type == "daily":
                # Reset daily challenges
                if c.start_date:
                    start = datetime.fromisoformat(c.start_date)
                    if start.date() != today.date():
                        c.start_date = today.isoformat()
                        c.progress = 0.0
                else:
                    c.start_date = today.isoformat()

            active.append(c)

        return active

    def check_challenges(self) -> List[Challenge]:
        """Vérifie si des challenges sont complétés. Retourne les nouveaux complétés."""
        completed = []
        today = datetime.now()

        for challenge in self.challenges:
            if challenge.completed:
                continue

            is_complete = False

            if challenge.condition_type == "no_spend":
                # Vérifier si aucune dépense aujourd'hui
                try:
                    all_tx = get_all_transactions()
                    today_str = today.strftime("%Y-%m-%d")
                    if not all_tx.empty and "date" in all_tx.columns:
                        all_tx["date"] = pd.to_datetime(all_tx["date"])
                        today_tx = all_tx[all_tx["date"].dt.strftime("%Y-%m-%d") == today_str]
                        spending = today_tx["amount"].sum() if not today_tx.empty else 0
                        if spending == 0:
                            is_complete = True
                except Exception:
                    pass

            elif challenge.condition_type == "create_budget":
                # Vérifié ailleurs quand un budget est créé
                pass

            elif challenge.condition_type == "savings_rate":
                # Vérifié mensuellement via global stats
                stats = get_global_stats()
                if stats:
                    savings_rate = abs(stats.get("current_month_rate", 0)) / 100
                    if savings_rate >= challenge.condition_value:
                        is_complete = True

            if is_complete:
                challenge.completed = True
                challenge.completed_at = today.isoformat()
                self.stats.total_points += challenge.reward_points
                self.stats.completed_challenges.append(challenge.id)
                completed.append(challenge)

                # Attribuer le badge
                self._award_badge(challenge.reward_badge)

        if completed:
            self._save()

        return completed

    def _award_badge(self, badge_id: str):
        """Attribue un badge à l'utilisateur."""
        # Badges définis
        BADGE_DEFINITIONS = {
            "resistant": ("🛡️", "Résistant", "Un jour sans dépense", "common"),
            "planner": ("📊", "Planificateur", "Dans le budget", "common"),
            "chef": ("🍳", "Chef", "Semaine sans restaurant", "rare"),
            "organized": ("📥", "Organisé", "Import régulier", "common"),
            "saver": ("💰", "Épargneur", "20% d'épargne", "epic"),
            "starter": ("🎯", "Débutant", "Premier budget créé", "common"),
        }

        if badge_id in BADGE_DEFINITIONS:
            icon, name, desc, rarity = BADGE_DEFINITIONS[badge_id]

            # Vérifier si pas déjà débloqué
            if not any(b.id == badge_id for b in self.badges):
                badge = Badge(
                    id=badge_id,
                    name=name,
                    description=desc,
                    icon=icon,
                    unlocked_at=datetime.now().isoformat(),
                    rarity=rarity,
                )
                self.badges.append(badge)
                logger.info(f"Badge awarded: {name}")

    def get_stats_summary(self) -> Dict:
        """Retourne un résumé des stats pour affichage."""
        return {
            "points": self.stats.total_points,
            "streak": self.stats.current_streak,
            "longest_streak": self.stats.longest_streak,
            "badges_count": len(self.badges),
            "challenges_completed": len(self.stats.completed_challenges),
        }


# Fonction utilitaire pour l'interface
def render_gamification_sidebar():
    """Affiche les stats de gamification dans la sidebar."""
    import streamlit as st

    manager = GamificationManager()
    stats = manager.get_stats_summary()

    with st.sidebar:
        st.divider()
        st.markdown("### 🏆 Progression")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("🔥 Streak", f"{stats['streak']}j")
        with col2:
            st.metric("⭐ Points", stats["points"])

        # Badges récents
        if manager.badges:
            st.caption("Derniers badges:")
            recent_badges = sorted(manager.badges, key=lambda b: b.unlocked_at, reverse=True)[:3]
            for badge in recent_badges:
                st.markdown(f"{badge.icon} {badge.name}")
