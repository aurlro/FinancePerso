"""
Système de notifications modernisé pour FinancePerso.

Ce module fournit une expérience de notification complète et cohérente :
- Types de notifications hiérarchisés (Critical, Warning, Success, Info, Achievement)
- Notification Center avec historique
- Préférences utilisateur personnalisables
- Design moderne avec animations

Usage basique:
    from modules.ui.notifications import notify, success, warning, error

    success("Opération réussie !")
    warning("Budget presque atteint")
    error("Une erreur est survenue", persistent=True)

Dans chaque page:
    from modules.ui.notifications import render_notifications_auto

    # En début de page
    render_notifications_auto()

Dans la sidebar:
    from modules.ui.notifications import render_notification_center_compact

    render_notification_center_compact()
"""

# Types et classes
# Centre de notifications
from .center import (
    render_notification_badge_sidebar,
    render_notification_center_compact,
    render_notification_center_full,
    render_notification_settings,
)

# Composants visuels
from .components import (
    render_achievement_unlock,
    render_empty_state,
    render_inline_notification,
    render_loading_state,
    render_notification_toast,
    render_notifications_auto,
    render_toast_container,
    show_confirmation,
    show_native_toast,
)

# Manager
from .manager import (
    NotificationManager,
    achievement,
    error,
    get_notification_manager,
    info,
    loading,
    notify,
    success,
    warning,
)
from .types import (
    Notification,
    NotificationAction,
    NotificationLevel,
    NotificationPosition,
    NotificationPreferences,
    NotificationSound,
)

__version__ = "2.0.0"

__all__ = [
    # Types
    "Notification",
    "NotificationLevel",
    "NotificationAction",
    "NotificationPosition",
    "NotificationPreferences",
    "NotificationSound",
    # Manager
    "NotificationManager",
    "get_notification_manager",
    "notify",
    "success",
    "warning",
    "error",
    "info",
    "achievement",
    "loading",
    # Composants
    "render_notifications_auto",
    "render_toast_container",
    "render_notification_toast",
    "render_inline_notification",
    "render_achievement_unlock",
    "render_loading_state",
    "render_empty_state",
    "show_confirmation",
    "show_native_toast",
    # Centre
    "render_notification_center_compact",
    "render_notification_center_full",
    "render_notification_settings",
    "render_notification_badge_sidebar",
]


def init_notification_system():
    """
    Initialise le système de notifications.
    À appeler au démarrage de l'application.
    """
    manager = get_notification_manager()

    # Nettoyer les notifications expirées au démarrage
    manager.cleanup_expired()

    return manager
