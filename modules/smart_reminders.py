"""
Smart Reminders - Système de rappels intelligents et contextuels.

Rappelle l'utilisateur d'effectuer des actions importantes
basées sur son activité et ses habitudes.
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum

from modules.db.rules import get_learning_rules
from modules.db.transactions import get_all_transactions
from modules.logger import logger


class ReminderType(Enum):
    """Types de rappels disponibles."""

    IMPORT_REMINDER = "import_reminder"
    VALIDATION_REMINDER = "validation_reminder"
    BUDGET_ALERT = "budget_alert"
    GOAL_REMINDER = "goal_reminder"
    STREAK_WARNING = "streak_warning"
    NEW_FEATURE = "new_feature"


class Priority(Enum):
    """Niveaux de priorité des rappels."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class SmartReminder:
    """Un rappel intelligent avec contexte."""

    type: ReminderType
    title: str
    message: str
    priority: Priority
    action_type: str  # 'navigate', 'action', 'dismiss'
    action_target: str | None = None  # page path or action name
    action_label: str = "Voir"
    icon: str = "🔔"

    def to_dict(self) -> dict:
        """Convertir en dictionnaire."""
        return {
            "type": self.type.value,
            "title": self.title,
            "message": self.message,
            "priority": self.priority.value,
            "action_type": self.action_type,
            "action_target": self.action_target,
            "action_label": self.action_label,
            "icon": self.icon,
        }


class SmartReminderEngine:
    """Moteur de génération de rappels intelligents."""

    def __init__(self):
        self.reminders: list[SmartReminder] = []

    def check_all_reminders(self) -> list[SmartReminder]:
        """Vérifier et retourner tous les rappels pertinents."""
        self.reminders = []

        try:
            self._check_import_reminder()
            self._check_validation_reminder()
            self._check_budget_alerts()
            self._check_goal_reminders()
            self._check_streak_warning()
            self._check_rule_suggestions()
        except Exception as e:
            logger.error(f"Error checking reminders: {e}")

        # Trier par priorité
        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        self.reminders.sort(key=lambda r: priority_order.get(r.priority, 3))

        return self.reminders

    def _check_import_reminder(self):
        """Vérifier si un import est nécessaire."""
        try:
            df = get_all_transactions(limit=1)
            if df.empty:
                # Aucune transaction = premier usage
                self.reminders.append(
                    SmartReminder(
                        type=ReminderType.IMPORT_REMINDER,
                        title="🌱 Bienvenue ! Commencez votre suivi",
                        message="Importez votre premier relevé bancaire pour découvrir vos finances.",
                        priority=Priority.HIGH,
                        action_type="navigate",
                        action_target="pages/01_Import.py",
                        action_label="Importer",
                        icon="📥",
                    )
                )
                return

            # Vérifier la date de la dernière transaction
            last_date = pd.to_datetime(df["date"].max())
            days_since = (datetime.now() - last_date).days

            if days_since > 10:
                self.reminders.append(
                    SmartReminder(
                        type=ReminderType.IMPORT_REMINDER,
                        title="📥 Nouveau relevé à importer ?",
                        message=f"Dernière transaction il y a {days_since} jours. Mettez à jour vos données.",
                        priority=Priority.MEDIUM if days_since > 15 else Priority.LOW,
                        action_type="navigate",
                        action_target="pages/01_Import.py",
                        action_label="Importer",
                        icon="📥",
                    )
                )
        except Exception as e:
            logger.debug(f"Could not check import reminder: {e}")

    def _check_validation_reminder(self):
        """Vérifier s'il y a des transactions à valider."""
        try:

            df = get_all_transactions()

            if df.empty:
                return

            # Compter les transactions en attente
            pending = df[df["status"] == "pending"]
            pending_count = len(pending)

            if pending_count >= 10:
                self.reminders.append(
                    SmartReminder(
                        type=ReminderType.VALIDATION_REMINDER,
                        title=f"🏷️ {pending_count} transactions à catégoriser",
                        message="Validez-les pour améliorer la précision de vos statistiques.",
                        priority=Priority.HIGH if pending_count > 20 else Priority.MEDIUM,
                        action_type="navigate",
                        action_target="pages/01_Import.py",
                        action_label="Valider",
                        icon="🏷️",
                    )
                )
        except Exception as e:
            logger.debug(f"Could not check validation reminder: {e}")

    def _check_budget_alerts(self):
        """Vérifier les dépassements de budget."""
        try:
            from modules.analytics import get_category_spending
            from modules.db.budgets import get_budgets

            budgets = get_budgets()
            if budgets.empty:
                return

            # Récupérer les dépenses du mois en cours
            current_month = datetime.now().strftime("%Y-%m")

            overspent = []
            for _, budget in budgets.iterrows():
                category = budget["category"]
                budget_amount = budget["amount"]

                # Calculer les dépenses réelles
                actual = get_category_spending(category, current_month)

                if actual > budget_amount * 1.1:  # Dépassement de 10%
                    overspent.append(
                        {
                            "category": category,
                            "budget": budget_amount,
                            "actual": actual,
                            "overspend_pct": ((actual / budget_amount) - 1) * 100,
                        }
                    )

            if overspent:
                # Prendre le plus critique
                worst = max(overspent, key=lambda x: x["overspend_pct"])

                self.reminders.append(
                    SmartReminder(
                        type=ReminderType.BUDGET_ALERT,
                        title=f"🚨 Budget {worst['category']} dépassé",
                        message=f"Dépensé: {worst['actual']:.0f}€ / Budget: {worst['budget']:.0f}€ (+{worst['overspend_pct']:.0f}%)",
                        priority=Priority.HIGH,
                        action_type="navigate",
                        action_target="pages/02_Dashboard.py",
                        action_label="Voir budgets",
                        icon="🚨",
                    )
                )
        except Exception as e:
            logger.debug(f"Could not check budget alerts: {e}")

    def _check_goal_reminders(self):
        """Vérifier les objectifs d'épargne urgents."""
        try:
            from modules.savings_goals import get_active_savings_goals

            goals = get_active_savings_goals()
            if not goals:
                return

            # Trouver l'objectif le plus urgent
            urgent_goals = [g for g in goals if g.days_remaining and g.days_remaining <= 30]

            if urgent_goals:
                goal = urgent_goals[0]
                self.reminders.append(
                    SmartReminder(
                        type=ReminderType.GOAL_REMINDER,
                        title=f"🎯 {goal.name} - Échéance proche",
                        message=f"Plus que {goal.days_remaining} jours. Reste: {goal.remaining_amount:.0f}€ à atteindre.",
                        priority=Priority.MEDIUM,
                        action_type="navigate",
                        action_target="pages/02_Dashboard.py",
                        action_label="Contribuer",
                        icon=goal.emoji,
                    )
                )
        except Exception as e:
            logger.debug(f"Could not check goal reminders: {e}")

    def _check_streak_warning(self):
        """Vérifier si le streak est en danger."""
        try:
            from modules.gamification import GamificationManager

            manager = GamificationManager()
            stats = manager.get_stats_summary()

            if stats["streak"] > 0:
                # Vérifier si l'utilisateur s'est connecté aujourd'hui
                last_visit = manager._load_stats().get("last_visit", "")
                today = date.today().isoformat()

                if last_visit != today:
                    # Vérifier si hier il s'est connecté
                    yesterday = (date.today() - timedelta(days=1)).isoformat()
                    if last_visit == yesterday:
                        self.reminders.append(
                            SmartReminder(
                                type=ReminderType.STREAK_WARNING,
                                title=f"🔥 Série de {stats['streak']} jours en danger !",
                                message="Connectez-vous aujourd'hui pour maintenir votre streak.",
                                priority=Priority.MEDIUM,
                                action_type="dismiss",
                                action_label="J'ai compris",
                                icon="⚠️",
                            )
                        )
        except Exception as e:
            logger.debug(f"Could not check streak warning: {e}")

    def _check_rule_suggestions(self):
        """Suggérer de créer des règles si beaucoup de transactions similaires."""
        try:
            df = get_all_transactions()
            rules = get_learning_rules()

            if df.empty:
                return

            # Vérifier s'il y a des patterns fréquents sans règle
            from collections import Counter

            validated = df[df["status"] == "validated"]
            if validated.empty:
                return

            # Trouver les labels fréquents
            label_counts = Counter(validated["label"])
            frequent = [(label, count) for label, count in label_counts.items() if count >= 5]

            if not frequent:
                return

            # Vérifier s'ils ont déjà des règles
            existing_patterns = set(rules["pattern"].tolist()) if not rules.empty else set()

            missing_rules = [
                (label, count)
                for label, count in frequent
                if label not in existing_patterns and len(label) > 3
            ][
                :1
            ]  # Juste le premier

            if missing_rules:
                label, count = missing_rules[0]
                self.reminders.append(
                    SmartReminder(
                        type=ReminderType.NEW_FEATURE,
                        title="⚡ Suggestion de règle",
                        message=f"'{label[:30]}...' apparaît {count} fois. Créez une règle pour automatiser.",
                        priority=Priority.LOW,
                        action_type="navigate",
                        action_target="pages/03_Intelligence.py",
                        action_label="Créer",
                        icon="💡",
                    )
                )
        except Exception as e:
            logger.debug(f"Could not check rule suggestions: {e}")


# Fonctions utilitaires
def get_smart_reminders() -> list[SmartReminder]:
    """Récupérer tous les rappels intelligents."""
    engine = SmartReminderEngine()
    return engine.check_all_reminders()


def get_high_priority_reminders() -> list[SmartReminder]:
    """Récupérer uniquement les rappels haute priorité."""
    all_reminders = get_smart_reminders()
    return [r for r in all_reminders if r.priority == Priority.HIGH]


# Import pandas pour les fonctions qui en ont besoin
try:
    import pandas as pd
except ImportError:
    pd = None
