"""
Composants visuels pour notifications - LEGACY WRAPPER
======================================================

⚠️ DEPRECATED: This module is kept for backward compatibility.

New location: modules.ui_v2.organisms.notifications (ARCHIVED)

Migration guide:
    OLD: from modules.ui.notifications.components import render_notification_toast
    NEW: Use st.toast() directly or functions from modules.ui.notifications.manager
"""

import warnings

import streamlit as st

# Import types for show_native_toast
from modules.ui.notifications.types import DEFAULT_ICONS, NotificationLevel

# Native implementations (formerly fallbacks)
def render_toast_container():
    """Container for toasts - fallback implementation."""
    pass

def render_notification_toast(message, level="info", title=None, duration=None):
    """Render a notification toast - fallback to st.toast."""
    icon = DEFAULT_ICONS.get(level, "ℹ️")
    st.toast(f"{title + ': ' if title else ''}{message}", icon=icon)

def render_all_active_toasts():
    """Render all active toasts - fallback implementation."""
    pass

def render_inline_notification(message, level="info"):
    """Render an inline notification - fallback implementation."""
    icon = DEFAULT_ICONS.get(level, "ℹ️")
    st.info(f"{icon} {message}")

def render_achievement_unlock(title, description, icon="🏆"):
    """Render achievement unlock notification."""
    st.success(f"{icon} **{title}**: {description}")

def render_loading_state(message="Chargement..."):
    """Render loading state."""
    st.spinner(message)

def render_empty_state(title, message, icon="📭"):
    """Render empty state."""
    st.info(f"{icon} **{title}**: {message}")


def render_notifications_auto():
    """
    Affiche automatiquement les notifications appropriées.
    
    ⚠️ DEPRECATED: Use render_all_active_toasts() instead.
    """
    warnings.warn(
        "render_notifications_auto() is deprecated.",
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
    
    ⚠️ DEPRECATED: Use st.toast() directly
    """
    warnings.warn(
        "show_native_toast() is deprecated. Use st.toast() instead",
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
    
    ⚠️ DEPRECATED: Use native Streamlit dialogs
    """
    warnings.warn(
        "show_confirmation() is deprecated.",
        DeprecationWarning,
        stacklevel=2,
    )
    # Fallback: simple dialog using st.dialog if available
    import streamlit as st
    
    @st.dialog(title)
    def _confirm():
        st.write(message)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirmer", type="primary"):
                if on_confirm:
                    on_confirm()
                st.rerun()
        with col2:
            if st.button("Annuler"):
                if on_cancel:
                    on_cancel()
                st.rerun()
    
    _confirm()


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
