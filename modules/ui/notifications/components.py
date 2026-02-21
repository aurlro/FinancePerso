"""
Composants visuels pour notifications - LEGACY WRAPPER
======================================================

⚠️ DEPRECATED: This module is kept for backward compatibility.

New location: modules.ui_v2.organisms.notifications

Migration guide:
    OLD: from modules.ui.notifications.components import render_notification_toast
    NEW: from modules.ui_v2.organisms.notifications import render_notification_toast
"""

import warnings

import streamlit as st

# Re-export everything from new location
from modules.ui_v2.organisms.notifications.inline import render_inline_notification
from modules.ui_v2.organisms.notifications.special import (
    render_achievement_unlock,
    render_empty_state,
    render_loading_state,
)
from modules.ui_v2.organisms.notifications.styles import render_toast_container
from modules.ui_v2.organisms.notifications.toast import (
    render_all_active_toasts,
    render_notification_toast,
)

# Import types for show_native_toast
from modules.ui.notifications.types import DEFAULT_ICONS, NotificationLevel


def render_notifications_auto():
    """
    Affiche automatiquement les notifications appropriées.
    
    ⚠️ DEPRECATED: Use render_all_active_toasts() instead.
    """
    warnings.warn(
        "render_notifications_auto() is deprecated. Use render_all_active_toasts() from modules.ui_v2.organisms.notifications",
        DeprecationWarning,
        stacklevel=2,
    )
    render_all_active_toasts()


def show_native_toast(
    message: str,
    level: NotificationLevel = NotificationLevel.INFO,
    duration: float = None,
):
    """
    Affiche un toast natif Streamlit.
    
    ⚠️ DEPRECATED: Use st.toast() directly or functions from modules.ui_v2.molecules.toasts
    """
    warnings.warn(
        "show_native_toast() is deprecated. Use modules.ui_v2.molecules.toasts instead",
        DeprecationWarning,
        stacklevel=2,
    )
    icon = DEFAULT_ICONS.get(level, "ℹ️")
    st.toast(message, icon=icon)


def show_confirmation(
    title: str,
    message: str,
    on_confirm=None,
    on_cancel=None,
):
    """
    Affiche une boîte de confirmation.
    
    ⚠️ DEPRECATED: Use confirm_dialog from modules.ui_v2.organisms.dialogs
    """
    warnings.warn(
        "show_confirmation() is deprecated. Use confirm_dialog from modules.ui_v2.organisms.dialogs",
        DeprecationWarning,
        stacklevel=2,
    )
    from modules.ui_v2.organisms.dialogs import confirm_dialog

    return confirm_dialog(title, message, "confirmer", on_confirm)


__all__ = [
    "render_toast_container",
    "render_notification_toast",
    "render_all_active_toasts",
    "render_inline_notification",
    "render_achievement_unlock",
    "render_loading_state",
    "render_empty_state",
    "render_notifications_auto",
    "show_native_toast",
    "show_confirmation",
]
