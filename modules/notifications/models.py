"""Modèles de données pour le système de notifications.

Définit les dataclasses et enums utilisés par tout le système.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class NotificationLevel(str, Enum):
    """Niveaux de priorité des notifications."""

    CRITICAL = "critical"  # 🚨 - Action immédiate requise
    WARNING = "warning"  # ⚠️ - Attention nécessaire
    INFO = "info"  # ℹ️ - Information
    SUCCESS = "success"  # ✅ - Confirmation
    ACHIEVEMENT = "achievement"  # 🏆 - Gamification


class NotificationType(str, Enum):
    """Types de notifications fonctionnels."""

    # Budget
    BUDGET_WARNING = "budget_warning"  # Approche du seuil
    BUDGET_CRITICAL = "budget_critical"  # Dépassement
    BUDGET_OVERRUN = "budget_overrun"  # Dépassement confirmé

    # Transactions
    VALIDATION_REMINDER = "validation_reminder"  # Transactions en attente
    IMPORT_REMINDER = "import_reminder"  # Pas importé depuis X jours
    DUPLICATE_DETECTED = "duplicate_detected"  # Doublons trouvés
    LARGE_EXPENSE = "large_expense"  # Dépense importante
    UNUSUAL_PATTERN = "unusual_pattern"  # Pattern anormal

    # Intelligence
    ANOMALY_DETECTED = "anomaly_detected"  # Anomalie statistique
    RECURRING_MISSING = "recurring_missing"  # Paiement récurrent absent
    NEW_MERCHANT = "new_merchant"  # Nouveau commerçant
    PRICE_INCREASE = "price_increase"  # Augmentation prix

    # Objectifs
    GOAL_ACHIEVED = "goal_achieved"  # Objectif atteint
    GOAL_PROGRESS = "goal_progress"  # Progression objectif
    SAVINGS_MILESTONE = "savings_milestone"  # Palier épargne

    # Gamification
    BADGE_EARNED = "badge_earned"  # Badge débloqué
    STREAK_MILESTONE = "streak_milestone"  # Streak atteint
    CHALLENGE_COMPLETED = "challenge_completed"  # Challenge terminé

    # Système
    SYSTEM_UPDATE = "system_update"  # Nouvelle fonctionnalité
    BACKUP_REMINDER = "backup_reminder"  # Rappel sauvegarde
    SECURITY_ALERT = "security_alert"  # Alerte sécurité

    # Insights
    WEEKLY_SUMMARY = "weekly_summary"  # Récap hebdomadaire
    MONTHLY_INSIGHT = "monthly_insight"  # Insight mensuel
    SPENDING_INSIGHT = "spending_insight"  # Insight dépenses


@dataclass
class NotificationAction:
    """Action possible sur une notification."""

    label: str  # Texte du bouton
    action: str  # Type d'action
    target: str | None = None  # Cible (URL, page, etc.)
    data: dict | None = None  # Données additionnelles

    def to_dict(self) -> dict:
        """Convertit en dictionnaire pour stockage JSON."""
        return {
            "label": self.label,
            "action": self.action,
            "target": self.target,
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NotificationAction":
        """Crée une instance depuis un dictionnaire."""
        return cls(
            label=data["label"],
            action=data["action"],
            target=data.get("target"),
            data=data.get("data"),
        )


@dataclass
class Notification:
    """Représente une notification."""

    id: str
    level: NotificationLevel
    type: NotificationType
    title: str | None
    message: str
    icon: str | None = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    read_at: datetime | None = None
    dismissed_at: datetime | None = None
    expires_at: datetime | None = None

    # Catégorisation
    category: str | None = None
    source: str | None = None

    # Actions
    actions: list[NotificationAction] = field(default_factory=list)

    # Métadonnées
    metadata: dict[str, Any] = field(default_factory=dict)

    # Déduplication
    dedup_key: str | None = None

    # Statut
    is_read: bool = False
    is_dismissed: bool = False
    is_pinned: bool = False

    def mark_read(self) -> None:
        """Marque la notification comme lue."""
        self.is_read = True
        self.read_at = datetime.now()

    def dismiss(self) -> None:
        """Marque la notification comme ignorée."""
        self.is_dismissed = True
        self.dismissed_at = datetime.now()

    def is_expired(self) -> bool:
        """Vérifie si la notification est expirée."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def is_active(self) -> bool:
        """Vérifie si la notification est active (non lue, non expirée)."""
        return not self.is_dismissed and not self.is_expired()

    def to_dict(self) -> dict:
        """Convertit en dictionnaire pour stockage."""
        return {
            "id": self.id,
            "level": self.level.value,
            "type": self.type.value,
            "title": self.title,
            "message": self.message,
            "icon": self.icon,
            "created_at": self.created_at.isoformat(),
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "dismissed_at": self.dismissed_at.isoformat() if self.dismissed_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "category": self.category,
            "source": self.source,
            "actions": [a.to_dict() for a in self.actions],
            "metadata": self.metadata,
            "dedup_key": self.dedup_key,
            "is_read": self.is_read,
            "is_dismissed": self.is_dismissed,
            "is_pinned": self.is_pinned,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Notification":
        """Crée une instance depuis un dictionnaire."""
        return cls(
            id=data["id"],
            level=NotificationLevel(data["level"]),
            type=NotificationType(data["type"]),
            title=data.get("title"),
            message=data["message"],
            icon=data.get("icon"),
            created_at=datetime.fromisoformat(data["created_at"]),
            read_at=datetime.fromisoformat(data["read_at"]) if data.get("read_at") else None,
            dismissed_at=(
                datetime.fromisoformat(data["dismissed_at"]) if data.get("dismissed_at") else None
            ),
            expires_at=(
                datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None
            ),
            category=data.get("category"),
            source=data.get("source"),
            actions=[NotificationAction.from_dict(a) for a in data.get("actions", [])],
            metadata=data.get("metadata", {}),
            dedup_key=data.get("dedup_key"),
            is_read=data.get("is_read", False),
            is_dismissed=data.get("is_dismissed", False),
            is_pinned=data.get("is_pinned", False),
        )


@dataclass
class NotificationPreferences:
    """Préférences de notification de l'utilisateur."""

    user_id: int = 1

    # Par niveau
    critical_enabled: bool = True
    warning_enabled: bool = True
    info_enabled: bool = True
    success_enabled: bool = True
    achievement_enabled: bool = True

    # Par type (dict type -> bool)
    type_preferences: dict[str, bool] = field(default_factory=dict)

    # Canaux
    desktop_enabled: bool = True
    email_enabled: bool = False
    sms_enabled: bool = False
    email_address: str | None = None

    # Seuils
    budget_warning_threshold: int = 80
    budget_critical_threshold: int = 100

    # Fréquences
    daily_digest_enabled: bool = True
    weekly_summary_enabled: bool = True

    def is_enabled(self, level: NotificationLevel, type_: NotificationType) -> bool:
        """Vérifie si une notification est activée."""
        # Vérifier le niveau
        level_enabled = getattr(self, f"{level.value}_enabled", True)
        if not level_enabled:
            return False

        # Vérifier le type
        type_pref = self.type_preferences.get(type_.value)
        if type_pref is not None:
            return type_pref

        return True
