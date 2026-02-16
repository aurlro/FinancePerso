"""
Savings Goals Module - Objectifs d'épargne visuels.

Crée une motivation émotionnelle forte pour économiser
en visualisant des objectifs concrets (vacances, voiture, etc.)
"""

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path

from modules.logger import logger

GOALS_FILE = Path("Data/savings_goals.json")


@dataclass
class SavingsGoal:
    """Un objectif d'épargne avec suivi de progression."""

    id: str
    name: str
    target_amount: float
    current_amount: float
    deadline: str | None  # ISO format YYYY-MM-DD
    emoji: str
    color: str  # hex color
    description: str
    created_at: str

    @property
    def progress_pct(self) -> float:
        """Pourcentage d'atteinte de l'objectif."""
        if self.target_amount <= 0:
            return 0.0
        return min(100.0, (self.current_amount / self.target_amount) * 100)

    @property
    def remaining_amount(self) -> float:
        """Montant restant à atteindre."""
        return max(0.0, self.target_amount - self.current_amount)

    @property
    def days_remaining(self) -> int | None:
        """Jours restants avant la deadline."""
        if not self.deadline:
            return None
        try:
            deadline_date = datetime.strptime(self.deadline, "%Y-%m-%d").date()
            return (deadline_date - date.today()).days
        except ValueError:
            return None

    @property
    def monthly_needed(self) -> float | None:
        """Montant mensuel nécessaire pour atteindre l'objectif à temps."""
        days = self.days_remaining
        if days is None or days <= 0:
            return None
        months = days / 30.44  # Average days per month
        if months <= 0:
            return None
        return self.remaining_amount / months

    def is_achieved(self) -> bool:
        """Vérifier si l'objectif est atteint."""
        return self.current_amount >= self.target_amount

    def to_dict(self) -> dict:
        """Convertir en dictionnaire pour JSON."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "SavingsGoal":
        """Créer depuis un dictionnaire."""
        return cls(**data)


class SavingsGoalsManager:
    """Gestionnaire des objectifs d'épargne."""

    def __init__(self):
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Créer le fichier s'il n'existe pas."""
        GOALS_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not GOALS_FILE.exists():
            GOALS_FILE.write_text("[]", encoding="utf-8")

    def _load_goals(self) -> list[SavingsGoal]:
        """Charger tous les objectifs."""
        try:
            data = json.loads(GOALS_FILE.read_text(encoding="utf-8"))
            return [SavingsGoal.from_dict(g) for g in data]
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading savings goals: {e}")
            return []

    def _save_goals(self, goals: list[SavingsGoal]):
        """Sauvegarder tous les objectifs."""
        try:
            data = [g.to_dict() for g in goals]
            GOALS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            logger.error(f"Error saving savings goals: {e}")

    def create_goal(
        self,
        name: str,
        target_amount: float,
        emoji: str = "🎯",
        color: str = "#1f77b4",
        deadline: str | None = None,
        description: str = "",
        initial_amount: float = 0.0,
    ) -> SavingsGoal:
        """Créer un nouvel objectif d'épargne."""
        goal = SavingsGoal(
            id=str(uuid.uuid4())[:8],
            name=name,
            target_amount=target_amount,
            current_amount=initial_amount,
            deadline=deadline,
            emoji=emoji,
            color=color,
            description=description,
            created_at=date.today().isoformat(),
        )

        goals = self._load_goals()
        goals.append(goal)
        self._save_goals(goals)

        logger.info(f"Created savings goal: {name} ({target_amount}€)")
        return goal

    def get_all_goals(self) -> list[SavingsGoal]:
        """Récupérer tous les objectifs."""
        return self._load_goals()

    def get_active_goals(self) -> list[SavingsGoal]:
        """Récupérer les objectifs non atteints."""
        return [g for g in self._load_goals() if not g.is_achieved()]

    def get_achieved_goals(self) -> list[SavingsGoal]:
        """Récupérer les objectifs atteints."""
        return [g for g in self._load_goals() if g.is_achieved()]

    def get_closest_goal(self) -> SavingsGoal | None:
        """Récupérer l'objectif le plus proche d'être atteint."""
        active = self.get_active_goals()
        if not active:
            return None
        return min(active, key=lambda g: g.remaining_amount)

    def get_urgent_goals(self, days_threshold: int = 30) -> list[SavingsGoal]:
        """Récupérer les objectifs urgents (deadline proche)."""
        active = self.get_active_goals()
        urgent = []
        for goal in active:
            days = goal.days_remaining
            if days is not None and days <= days_threshold:
                urgent.append(goal)
        return sorted(urgent, key=lambda g: g.days_remaining or 999)

    def update_goal(self, goal_id: str, **updates) -> bool:
        """Mettre à jour un objectif."""
        goals = self._load_goals()
        for goal in goals:
            if goal.id == goal_id:
                for key, value in updates.items():
                    if hasattr(goal, key):
                        setattr(goal, key, value)
                self._save_goals(goals)
                logger.info(f"Updated savings goal: {goal_id}")
                return True
        return False

    def contribute_to_goal(self, goal_id: str, amount: float) -> bool:
        """Ajouter un montant à un objectif."""
        goals = self._load_goals()
        for goal in goals:
            if goal.id == goal_id:
                goal.current_amount += amount
                self._save_goals(goals)
                logger.info(f"Added {amount}€ to goal {goal_id}")
                return True
        return False

    def delete_goal(self, goal_id: str) -> bool:
        """Supprimer un objectif."""
        goals = self._load_goals()
        goals = [g for g in goals if g.id != goal_id]
        self._save_goals(goals)
        logger.info(f"Deleted savings goal: {goal_id}")
        return True

    def get_total_saved(self) -> float:
        """Montant total épargné dans tous les objectifs."""
        return sum(g.current_amount for g in self._load_goals())

    def get_total_target(self) -> float:
        """Montant total ciblé."""
        return sum(g.target_amount for g in self._load_goals())


# Singleton instance
_goals_manager: SavingsGoalsManager | None = None


def get_goals_manager() -> SavingsGoalsManager:
    """Get or create the savings goals manager singleton."""
    global _goals_manager
    if _goals_manager is None:
        _goals_manager = SavingsGoalsManager()
    return _goals_manager


# Convenience functions
def create_savings_goal(name: str, target: float, emoji: str = "🎯", **kwargs) -> SavingsGoal:
    """Créer un objectif d'épargne."""
    return get_goals_manager().create_goal(name, target, emoji, **kwargs)


def get_active_savings_goals() -> list[SavingsGoal]:
    """Récupérer les objectifs actifs."""
    return get_goals_manager().get_active_goals()


def get_closest_savings_goal() -> SavingsGoal | None:
    """Récupérer l'objectif le plus proche."""
    return get_goals_manager().get_closest_goal()


def contribute_to_savings_goal(goal_id: str, amount: float) -> bool:
    """Contribuer à un objectif."""
    return get_goals_manager().contribute_to_goal(goal_id, amount)
