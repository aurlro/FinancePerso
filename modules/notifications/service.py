"""Service principal du système de notifications.

Point d'entrée unique pour toutes les opérations de notification.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any

from modules.logger import logger

from .models import (
    Notification,
    NotificationAction,
    NotificationLevel,
    NotificationPreferences,
    NotificationType,
)
from .repository import NotificationRepository


class NotificationService:
    """Service singleton pour la gestion des notifications.

    Usage:
        service = NotificationService()

        # Créer une notification simple
        service.notify(
            type=NotificationType.BUDGET_WARNING,
            title="Budget",
            message="Vous avez atteint 85%"
        )

        # Créer avec actions
        service.notify(
            type=NotificationType.VALIDATION_REMINDER,
            title="Transactions en attente",
            message="10 transactions à valider",
            actions=[
                NotificationAction("Valider", "navigate", "/operations"),
                NotificationAction("Ignorer", "dismiss")
            ]
        )

        # Récupérer et gérer
        unread = service.get_unread()
        service.mark_read(notification_id)
    """

    _instance = None

    def __new__(cls):
        """Pattern singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialise le service."""
        if self._initialized:
            return

        self._repo = NotificationRepository()
        self._prefs: NotificationPreferences | None = None
        self._initialized = True

    # ==================== Création ====================

    def notify(
        self,
        type: NotificationType,
        message: str,
        title: str | None = None,
        level: NotificationLevel | None = None,
        icon: str | None = None,
        category: str | None = None,
        source: str | None = None,
        actions: list[NotificationAction] | None = None,
        metadata: dict[str, Any] | None = None,
        dedup_key: str | None = None,
        dedup_hours: int = 24,
        expires_in_hours: int | None = None,
        pin: bool = False,
    ) -> Notification | None:
        """Crée et envoie une notification.

        Args:
            type: Type de notification
            message: Message principal
            title: Titre optionnel
            level: Niveau (déduit du type si non spécifié)
            icon: Icône emoji
            category: Catégorie pour regroupement
            source: Module source
            actions: Actions possibles
            metadata: Données additionnelles
            dedup_key: Clé pour déduplication
            dedup_hours: Fenêtre de déduplication
            expires_in_hours: Expiration après X heures
            pin: Épingler la notification

        Returns:
            La notification créée, ou None si dédupliquée ou désactivée
        """
        try:
            # Vérifier les préférences
            prefs = self.get_preferences()
            level = level or self._level_from_type(type)

            if not prefs.is_enabled(level, type):
                logger.debug(f"Notification {type.value} désactivée par l'utilisateur")
                return None

            # Vérifier déduplication
            if dedup_key and self._repo.dedup_exists(dedup_key, dedup_hours):
                logger.debug(f"Notification dédupliquée: {dedup_key}")
                return None

            # Créer la notification
            notification = Notification(
                id=str(uuid.uuid4())[:8],
                level=level,
                type=type,
                title=title,
                message=message,
                icon=icon or self._default_icon(type),
                category=category,
                source=source,
                actions=actions or [],
                metadata=metadata or {},
                dedup_key=dedup_key,
                is_pinned=pin,
                expires_at=(
                    (datetime.now() + timedelta(hours=expires_in_hours))
                    if expires_in_hours
                    else None
                ),
            )

            # Sauvegarder
            self._repo.create(notification)
            logger.info(f"Notification créée: {type.value} - {title or message[:50]}")

            return notification

        except Exception as e:
            logger.error(f"Erreur création notification: {e}")
            return None

    def notify_budget(
        self,
        category: str,
        spent: float,
        budget: float,
        percentage: float,
    ) -> Notification | None:
        """Crée une notification de budget."""
        prefs = self.get_preferences()

        # Déterminer le niveau
        if percentage >= prefs.budget_critical_threshold:
            level = NotificationLevel.CRITICAL
            type_ = NotificationType.BUDGET_CRITICAL
            message = (
                f"🚨 Budget {category} dépassé ! {spent:.0f}€ / {budget:.0f}€ ({percentage:.0f}%)"
            )
        elif percentage >= prefs.budget_warning_threshold:
            level = NotificationLevel.WARNING
            type_ = NotificationType.BUDGET_WARNING
            message = f"⚠️ Budget {category} à {percentage:.0f}% ({spent:.0f}€ / {budget:.0f}€)"
        else:
            return None  # Pas de notification si sous le seuil

        return self.notify(
            type=type_,
            title=f"Budget {category}",
            message=message,
            level=level,
            category="budget",
            dedup_key=f"budget_{category}_{datetime.now().strftime('%Y%m%d')}",
            actions=[
                NotificationAction("Voir", "navigate", "/budgets"),
                NotificationAction("Ignorer", "dismiss"),
            ],
        )

    def notify_validation_reminder(
        self,
        count: int,
        oldest_days: int,
    ) -> Notification | None:
        """Crée un rappel de validation."""
        if count == 0:
            return None

        return self.notify(
            type=NotificationType.VALIDATION_REMINDER,
            title=f"⏳ {count} transaction(s) en attente",
            message=f"Vous avez {count} transactions à valider. La plus ancienne date de {oldest_days} jours.",
            level=NotificationLevel.WARNING if oldest_days > 14 else NotificationLevel.INFO,
            category="validation",
            dedup_key=f"validation_reminder_{datetime.now().strftime('%Y%m%d')}",
            actions=[
                NotificationAction("Valider", "navigate", "/operations"),
            ],
        )

    def notify_duplicate(
        self,
        date: str,
        label: str,
        amount: float,
        count: int,
    ) -> Notification | None:
        """Crée une notification de doublon détecté."""
        return self.notify(
            type=NotificationType.DUPLICATE_DETECTED,
            title="♻️ Doublons détectés",
            message=f"{count} transactions similaires: {label} ({amount:.2f}€) le {date}",
            level=NotificationLevel.WARNING,
            category="duplicates",
            dedup_key=f"duplicate_{date}_{label}_{amount}",
            actions=[
                NotificationAction(
                    "Fusionner",
                    "action",
                    data={
                        "action": "merge_duplicates",
                        "date": date,
                        "label": label,
                        "amount": amount,
                    },
                ),
                NotificationAction("Voir", "navigate", "/operations"),
            ],
        )

    def notify_import_reminder(self, days_since_import: int) -> Notification | None:
        """Crée un rappel d'import."""
        if days_since_import < 7:
            return None

        return self.notify(
            type=NotificationType.IMPORT_REMINDER,
            title="📥 Il est temps d'importer",
            message=(
                f"Votre dernier import date de {days_since_import} jours. "
                f"Importez vos nouvelles transactions pour un suivi à jour."
            ),
            level=NotificationLevel.INFO if days_since_import < 14 else NotificationLevel.WARNING,
            category="import",
            dedup_key=f"import_reminder_{datetime.now().strftime('%Y%m%d')}",
            actions=[
                NotificationAction("Importer", "navigate", "/operations"),
            ],
        )

    def notify_achievement(
        self,
        badge_name: str,
        badge_icon: str,
    ) -> Notification | None:
        """Crée une notification de badge débloqué."""
        return self.notify(
            type=NotificationType.BADGE_EARNED,
            title="🎉 Nouveau badge débloqué !",
            message=f"Félicitations ! Vous avez obtenu le badge '{badge_name}'",
            level=NotificationLevel.ACHIEVEMENT,
            icon=badge_icon,
            category="gamification",
            actions=[
                NotificationAction("Voir mes badges", "navigate", "/badges"),
            ],
        )

    # ==================== Récupération ====================

    def get_unread(
        self,
        limit: int = 50,
        category: str | None = None,
    ) -> list[Notification]:
        """Récupère les notifications non lues."""
        return self._repo.get_unread(limit=limit, category=category)

    def get_all(
        self,
        limit: int = 50,
        include_dismissed: bool = False,
    ) -> list[Notification]:
        """Récupère toutes les notifications."""
        return self._repo.get_all(limit=limit, include_dismissed=include_dismissed)

    def count_unread(self) -> int:
        """Compte les notifications non lues."""
        return self._repo.count_unread()

    def get_by_id(self, notification_id: str) -> Notification | None:
        """Récupère une notification par ID."""
        return self._repo.get_by_id(notification_id)

    # ==================== Gestion ====================

    def mark_read(self, notification_id: str) -> bool:
        """Marque une notification comme lue."""
        return self._repo.mark_read(notification_id)

    def mark_all_read(self) -> int:
        """Marque toutes les notifications comme lues."""
        return self._repo.mark_all_read()

    def dismiss(self, notification_id: str) -> bool:
        """Marque une notification comme ignorée."""
        return self._repo.dismiss(notification_id)

    def delete(self, notification_id: str) -> bool:
        """Supprime définitivement une notification."""
        return self._repo.delete(notification_id)

    def cleanup(self, days: int = 30) -> int:
        """Nettoie les anciennes notifications."""
        return self._repo.cleanup_expired(days)

    # ==================== Préférences ====================

    def get_preferences(self) -> NotificationPreferences:
        """Récupère les préférences utilisateur."""
        if self._prefs is None:
            self._prefs = self._repo.get_preferences()
        return self._prefs

    def save_preferences(self, prefs: NotificationPreferences) -> None:
        """Sauvegarde les préférences utilisateur."""
        self._repo.save_preferences(prefs)
        self._prefs = prefs

    def is_enabled(self, type: NotificationType) -> bool:
        """Vérifie si un type de notification est activé."""
        prefs = self.get_preferences()
        level = self._level_from_type(type)
        return prefs.is_enabled(level, type)

    # ==================== Helpers ====================

    def _level_from_type(self, type: NotificationType) -> NotificationLevel:
        """Déduit le niveau du type."""
        mapping = {
            # Critical
            NotificationType.BUDGET_CRITICAL: NotificationLevel.CRITICAL,
            NotificationType.SECURITY_ALERT: NotificationLevel.CRITICAL,
            # Warning
            NotificationType.BUDGET_WARNING: NotificationLevel.WARNING,
            NotificationType.VALIDATION_REMINDER: NotificationLevel.WARNING,
            NotificationType.DUPLICATE_DETECTED: NotificationLevel.WARNING,
            NotificationType.ANOMALY_DETECTED: NotificationLevel.WARNING,
            NotificationType.RECURRING_MISSING: NotificationLevel.WARNING,
            NotificationType.PRICE_INCREASE: NotificationLevel.WARNING,
            # Success
            NotificationType.BUDGET_OVERRUN: NotificationLevel.SUCCESS,
            NotificationType.GOAL_ACHIEVED: NotificationLevel.SUCCESS,
            NotificationType.SAVINGS_MILESTONE: NotificationLevel.SUCCESS,
            # Achievement
            NotificationType.BADGE_EARNED: NotificationLevel.ACHIEVEMENT,
            NotificationType.STREAK_MILESTONE: NotificationLevel.ACHIEVEMENT,
            NotificationType.CHALLENGE_COMPLETED: NotificationLevel.ACHIEVEMENT,
            # Info (default)
        }
        return mapping.get(type, NotificationLevel.INFO)

    def _default_icon(self, type: NotificationType) -> str:
        """Retourne l'icône par défaut pour un type."""
        icons = {
            NotificationType.BUDGET_WARNING: "⚠️",
            NotificationType.BUDGET_CRITICAL: "🚨",
            NotificationType.BUDGET_OVERRUN: "💸",
            NotificationType.VALIDATION_REMINDER: "⏳",
            NotificationType.IMPORT_REMINDER: "📥",
            NotificationType.DUPLICATE_DETECTED: "♻️",
            NotificationType.LARGE_EXPENSE: "💰",
            NotificationType.UNUSUAL_PATTERN: "🔍",
            NotificationType.ANOMALY_DETECTED: "📊",
            NotificationType.RECURRING_MISSING: "🔔",
            NotificationType.NEW_MERCHANT: "🏪",
            NotificationType.PRICE_INCREASE: "📈",
            NotificationType.GOAL_ACHIEVED: "🎯",
            NotificationType.GOAL_PROGRESS: "📈",
            NotificationType.SAVINGS_MILESTONE: "🏆",
            NotificationType.BADGE_EARNED: "🏅",
            NotificationType.STREAK_MILESTONE: "🔥",
            NotificationType.CHALLENGE_COMPLETED: "🎉",
            NotificationType.SYSTEM_UPDATE: "🆕",
            NotificationType.BACKUP_REMINDER: "💾",
            NotificationType.SECURITY_ALERT: "🔒",
            NotificationType.WEEKLY_SUMMARY: "📅",
            NotificationType.MONTHLY_INSIGHT: "📊",
            NotificationType.SPENDING_INSIGHT: "💡",
        }
        return icons.get(type, "📌")
