"""
Système de notifications UI v2 - Organisme notifications.

Ce module fournit des composants modulaires pour afficher des notifications
dans l'application FinancePerso avec un design moderne et des animations.

Exports principaux:
    - Types: NotificationLevel, Notification, NotificationAction, etc.
    - Composants Toast: render_notification_toast, render_all_active_toasts
    - Composants Inline: render_inline_notification
    - Composants Spéciaux: render_achievement_unlock, render_loading_state, render_empty_state
    - Styles: render_toast_container
    - Compatibilité: Fonctions legacy avec warnings de déprécation

Usage:
    >>> from modules.ui_v2.organisms.notifications import (
    ...     render_all_active_toasts,
    ...     render_inline_notification,
    ...     NotificationLevel,
    ... )
    >>>
    >>> # Afficher tous les toasts actifs
    >>> render_all_active_toasts()
    >>>
    >>> # Notification inline
    >>> render_inline_notification(
    ...     message="Opération réussie !",
    ...     level=NotificationLevel.SUCCESS
    ... )
"""

# Types
from modules.ui_v2.organisms.notifications.types import (
    DEFAULT_DURATIONS,
    DEFAULT_ICONS,
    LEVEL_BG_COLORS,
    LEVEL_COLORS,
    Notification,
    NotificationAction,
    NotificationLevel,
    NotificationPosition,
    NotificationPreferences,
    NotificationSound,
)

# Composants Toast
from modules.ui_v2.organisms.notifications.toast import (
    render_all_active_toasts,
    render_notification_toast,
)

# Composants Inline
from modules.ui_v2.organisms.notifications.inline import render_inline_notification

# Composants Spéciaux
from modules.ui_v2.organisms.notifications.special import (
    render_achievement_unlock,
    render_empty_state,
    render_loading_state,
)

# Styles
from modules.ui_v2.organisms.notifications.styles import render_toast_container

# Compatibilité legacy (avec warnings)
from modules.ui_v2.organisms.notifications.legacy import (
    render_notifications_auto,
    show_confirmation,
    show_native_toast,
)

__all__ = [
    # Types
    "NotificationLevel",
    "NotificationPosition",
    "NotificationSound",
    "NotificationAction",
    "Notification",
    "NotificationPreferences",
    "DEFAULT_DURATIONS",
    "DEFAULT_ICONS",
    "LEVEL_COLORS",
    "LEVEL_BG_COLORS",
    # Toast
    "render_notification_toast",
    "render_all_active_toasts",
    # Inline
    "render_inline_notification",
    # Special
    "render_achievement_unlock",
    "render_loading_state",
    "render_empty_state",
    # Styles
    "render_toast_container",
    # Legacy
    "render_notifications_auto",
    "show_confirmation",
    "show_native_toast",
]
