"""Système de notifications unifié v3.0 - FinancePerso

API publique pour le système de notifications.

Usage:
    from modules.notifications import NotificationService, NotificationType
    
    service = NotificationService()
    
    # Créer une notification
    service.notify(
        type=NotificationType.BUDGET_WARNING,
        title="Budget Alimentation",
        message="Vous avez atteint 85% de votre budget",
        actions=[{"label": "Voir", "action": "navigate", "target": "/budgets"}]
    )
    
    # Récupérer les non-lues
    unread = service.get_unread(limit=10)
    
    # Marquer comme lue
    service.mark_read(notification_id)

Architecture:
    - models.py : Dataclasses Notification, NotificationLevel, NotificationType
    - service.py : NotificationService (singleton)
    - repository.py : Accès données DB
    - detectors.py : Détecteurs de notifications
    - ui.py : Composants d'interface
"""

from .models import (
    NotificationLevel,
    NotificationType,
    Notification,
    NotificationAction,
    NotificationPreferences,
)
from .service import NotificationService
from .repository import NotificationRepository
from .detectors import DetectorRegistry

__all__ = [
    # Enums
    "NotificationLevel",
    "NotificationType",
    # Models
    "Notification",
    "NotificationAction",
    "NotificationPreferences",
    # Service
    "NotificationService",
    "NotificationRepository",
    # Detectors
    "DetectorRegistry",
]

# Version du module
__version__ = "3.0.0"

# Version active du système de notifications
NOTIFICATION_SYSTEM_VERSION = "3.0"  # "3.0" pour V3, "2.0" pour rollback


def get_notification_service():
    """Retourne le service de notification actif.
    
    Returns:
        NotificationService: Instance du service de notifications V3
        ou NotificationManager: Instance du service V2 (legacy)
    """
    if NOTIFICATION_SYSTEM_VERSION == "3.0":
        return NotificationService()
    else:
        # Fallback V2
        from modules.ui.notifications import NotificationManager
        return NotificationManager()
