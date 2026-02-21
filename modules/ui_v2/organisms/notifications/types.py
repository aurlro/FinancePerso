"""
Types et classes de données pour le système de notifications UI v2.

Ce module ré-exporte tous les types depuis le module original pour maintenir
la compatibilité et permettre une évolution future du système de types.
"""

# Ré-export complet depuis le module original
# Le fichier original doit rester à modules/ui/notifications/types.py
from modules.ui.notifications.types import (
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

__all__ = [
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
]
