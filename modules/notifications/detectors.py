"""Détecteurs de notifications.

Analysent les données et créent des notifications pertinentes.
"""

from abc import ABC, abstractmethod
from datetime import datetime

from modules.db.budgets import get_budget_spending, get_budgets
from modules.db.connection import get_db_connection
from modules.db.transactions import get_pending_transactions
from modules.logger import logger

from .models import NotificationAction, NotificationType
from .service import NotificationService


class NotificationDetector(ABC):
    """Classe de base pour les détecteurs de notifications."""

    def __init__(self, service: NotificationService):
        self.service = service

    @abstractmethod
    def detect(self) -> None:
        """Détecte et crée les notifications pertinentes."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Nom du détecteur."""
        pass


class BudgetAlertDetector(NotificationDetector):
    """Détecte les dépassements de budget."""

    @property
    def name(self) -> str:
        return "budget_alerts"

    def detect(self) -> None:
        """Vérifie les budgets et crée des alertes si nécessaire."""
        try:
            prefs = self.service.get_preferences()
            budgets = get_budgets()

            for budget in budgets:
                category = budget.get("category")
                budget_amount = budget.get("amount", 0)

                if budget_amount <= 0:
                    continue

                # Calculer les dépenses
                spent = get_budget_spending(category)
                percentage = (spent / budget_amount) * 100

                # Créer notification si seuil dépassé
                if percentage >= prefs.budget_critical_threshold:
                    self.service.notify_budget(category, spent, budget_amount, percentage)
                elif percentage >= prefs.budget_warning_threshold:
                    self.service.notify_budget(category, spent, budget_amount, percentage)

        except Exception as e:
            logger.error(f"Erreur détection budget: {e}")


class ValidationReminderDetector(NotificationDetector):
    """Détecte les transactions en attente de validation."""

    @property
    def name(self) -> str:
        return "validation_reminder"

    def detect(self) -> None:
        """Vérifie s'il y a des transactions en attente."""
        try:
            count = len(get_pending_transactions())
            if count == 0:
                return

            # Trouver l'âge de la plus ancienne
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT MIN(date) FROM transactions 
                    WHERE status = 'pending' OR category_validated = 0
                """)
                oldest_date = cursor.fetchone()[0]

                if oldest_date:
                    oldest = datetime.strptime(oldest_date, "%Y-%m-%d")
                    days = (datetime.now() - oldest).days

                    self.service.notify_validation_reminder(count, days)

        except Exception as e:
            logger.error(f"Erreur détection validation: {e}")


class ImportReminderDetector(NotificationDetector):
    """Détecte si l'utilisateur n'a pas importé depuis longtemps."""

    @property
    def name(self) -> str:
        return "import_reminder"

    def detect(self) -> None:
        """Vérifie la date du dernier import."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT MAX(created_at) FROM transactions
                """)
                last_import = cursor.fetchone()[0]

                if last_import:
                    last_date = datetime.fromisoformat(last_import)
                    days = (datetime.now() - last_date).days

                    if days >= 7:
                        self.service.notify_import_reminder(days)

        except Exception as e:
            logger.error(f"Erreur détection import: {e}")


class DuplicateDetector(NotificationDetector):
    """Détecte les doublons de transactions."""

    @property
    def name(self) -> str:
        return "duplicates"

    def detect(self) -> None:
        """Recherche les transactions en double."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT date, label, amount, COUNT(*) as cnt
                    FROM transactions
                    WHERE status != 'deleted'
                    GROUP BY date, label, amount
                    HAVING cnt > 1
                    LIMIT 5
                """)

                for row in cursor.fetchall():
                    date, label, amount, count = row
                    self.service.notify_duplicate(date, label, amount, count)

        except Exception as e:
            logger.error(f"Erreur détection doublons: {e}")


class AnomalyDetector(NotificationDetector):
    """Détecte les anomalies statistiques dans les dépenses."""

    @property
    def name(self) -> str:
        return "anomalies"

    def detect(self) -> None:
        """Analyse les variations de dépenses."""
        try:
            # Calculer la moyenne mobile des 3 derniers mois
            with get_db_connection() as conn:
                cursor = conn.cursor()

                # Dépenses ce mois vs moyenne
                cursor.execute("""
                    SELECT 
                        strftime('%Y-%m', date) as month,
                        SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as total
                    FROM transactions
                    WHERE date >= date('now', '-3 months')
                    GROUP BY month
                    ORDER BY month DESC
                    LIMIT 3
                """)

                rows = cursor.fetchall()
                if len(rows) >= 2:
                    current_month, current_total = rows[0]
                    prev_months = [r[1] for r in rows[1:]]
                    avg_prev = sum(prev_months) / len(prev_months)

                    if avg_prev > 0:
                        variation = ((current_total - avg_prev) / avg_prev) * 100

                        if variation > 30:
                            self.service.notify(
                                type=NotificationType.UNUSUAL_PATTERN,
                                title="📈 Hausse des dépenses",
                                message=(
                                    f"Vos dépenses ont augmenté de {variation:.0f}% "
                                    f"ce mois par rapport à la moyenne."
                                ),
                                level="warning",
                                category="spending",
                                dedup_key=f"spike_{current_month}",
                                actions=[
                                    NotificationAction("Analyser", "navigate", "/synthese"),
                                ],
                            )
                        elif variation < -20:
                            self.service.notify(
                                type=NotificationType.SPENDING_INSIGHT,
                                title="📉 Baisse des dépenses",
                                message=f"Bonne nouvelle ! Vos dépenses ont diminué de {abs(variation):.0f}% ce mois.",
                                level="success",
                                category="spending",
                                dedup_key=f"drop_{current_month}",
                            )

        except Exception as e:
            logger.error(f"Erreur détection anomalies: {e}")


class RecurringMissingDetector(NotificationDetector):
    """Détecte les paiements récurrents manquants."""

    @property
    def name(self) -> str:
        return "recurring_missing"

    def detect(self) -> None:
        """Vérifie les paiements récurrents attendus."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                # Chercher les patterns récurrents (même label, montant similaire, intervalle régulier)
                cursor.execute("""
                    SELECT 
                        label,
                        amount,
                        COUNT(*) as count,
                        MAX(date) as last_date,
                        AVG(julianday(date) - julianday(lag(date) 
                             OVER (PARTITION BY label ORDER BY date))) as avg_interval
                    FROM (
                        SELECT label, amount, date,
                               LAG(date) OVER (PARTITION BY label ORDER BY date) as lag_date
                        FROM transactions
                        WHERE status = 'validated'
                    )
                    GROUP BY label, amount
                    HAVING count >= 3
                """)

                for row in cursor.fetchall():
                    label, amount, count, last_date, avg_interval = row

                    if last_date and avg_interval:
                        last = datetime.strptime(last_date, "%Y-%m-%d")
                        days_since = (datetime.now() - last).days
                        expected_interval = int(avg_interval)

                        # Si dépassé de 7 jours l'intervalle attendu
                        if days_since > expected_interval + 7:
                            self.service.notify(
                                type=NotificationType.RECURRING_MISSING,
                                title="🔔 Paiement attendu",
                                message=(
                                    f"'{label}' ({amount:.2f}€) n'a pas été détecté depuis {days_since} jours "
                                    f"(intervalle habituel: {expected_interval} jours)."
                                ),
                                category="recurring",
                                dedup_key=f"recurring_{label}_{datetime.now().strftime('%Y%m')}",
                            )

        except Exception as e:
            logger.error(f"Erreur détection récurrents: {e}")


# ==================== Registry ====================


class DetectorRegistry:
    """Registre de tous les détecteurs."""

    def __init__(self, service: NotificationService):
        self.service = service
        self._detectors: list[NotificationDetector] = []
        self._register_default_detectors()

    def _register_default_detectors(self) -> None:
        """Enregistre les détecteurs par défaut."""
        self._detectors = [
            BudgetAlertDetector(self.service),
            ValidationReminderDetector(self.service),
            ImportReminderDetector(self.service),
            DuplicateDetector(self.service),
            AnomalyDetector(self.service),
            RecurringMissingDetector(self.service),
        ]

    def run_all(self) -> dict[str, int]:
        """Exécute tous les détecteurs et retourne les stats."""
        stats = {}

        for detector in self._detectors:
            try:
                count_before = self.service.count_unread()
                detector.detect()
                count_after = self.service.count_unread()
                stats[detector.name] = count_after - count_before
            except Exception as e:
                logger.error(f"Erreur détecteur {detector.name}: {e}")
                stats[detector.name] = -1

        return stats

    def run(self, name: str) -> bool:
        """Exécute un détecteur spécifique."""
        for detector in self._detectors:
            if detector.name == name:
                detector.detect()
                return True
        return False

    def list_detectors(self) -> list[str]:
        """Liste les noms des détecteurs."""
        return [d.name for d in self._detectors]
