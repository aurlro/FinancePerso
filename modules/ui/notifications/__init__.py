"""Systeme de notifications modernise pour FinancePerso."""

import warnings

warnings.warn(
    "Notifications V2 is deprecated. Please migrate to V3.", DeprecationWarning, stacklevel=2
)

from .center import (
    render_notification_badge_sidebar,
    render_notification_center_compact,
    render_notification_center_full,
    render_notification_settings,
)
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
    "Notification",
    "NotificationLevel",
    "NotificationAction",
    "NotificationPosition",
    "NotificationPreferences",
    "NotificationSound",
    "NotificationManager",
    "get_notification_manager",
    "notify",
    "success",
    "warning",
    "error",
    "info",
    "achievement",
    "loading",
    "render_notifications_auto",
    "render_toast_container",
    "render_notification_toast",
    "render_inline_notification",
    "render_achievement_unlock",
    "render_loading_state",
    "render_empty_state",
    "show_confirmation",
    "show_native_toast",
    "render_notification_center_compact",
    "render_notification_center_full",
    "render_notification_settings",
    "render_notification_badge_sidebar",
]


def init_notification_system():
    """Initialise le systeme de notifications."""
    manager = get_notification_manager()
    manager.cleanup_expired()
    return manager
