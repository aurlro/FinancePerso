"""
Composants Toast pour le système de notifications UI v2.

Affiche les notifications sous forme de toasts flottants avec animations
et barre de progression.
"""

from collections.abc import Callable

import streamlit as st

from modules.ui.notifications.manager import get_notification_manager
from modules.ui_v2.organisms.notifications.styles import render_toast_container
from modules.ui_v2.organisms.notifications.types import (
    DEFAULT_ICONS,
    LEVEL_BG_COLORS,
    LEVEL_COLORS,
    Notification,
)


def render_notification_toast(
    notification: Notification, on_dismiss: Callable | None = None
):
    """
    Rend une notification au format toast.

    Args:
        notification: La notification à afficher
        on_dismiss: Callback appelé lors de la fermeture
    """
    color = LEVEL_COLORS.get(notification.level, "#3b82f6")
    bg_color = LEVEL_BG_COLORS.get(notification.level, "#eff6ff")
    icon = notification.icon or DEFAULT_ICONS.get(notification.level, "ℹ️")

    # Calculer le temps restant
    progress = 100
    if notification.duration and notification.duration > 0:
        elapsed = notification.age_seconds
        remaining = max(0, notification.duration - elapsed)
        progress = (remaining / notification.duration) * 100

    # HTML du toast
    html = f"""
    <div class="fp-toast" id="toast-{notification.id}" style="
        border-left-color: {color};
        background: linear-gradient(to right, {bg_color} 0%, white 100%);
    ">
        <button class="fp-toast-close" onclick="dismissToast('{notification.id}')">×</button>
        
        <div class="fp-toast-header">
            <span class="fp-toast-icon">{icon}</span>
            <span class="fp-toast-title" style="color: {color};">
                {notification.title or notification.level.value.title()}
            </span>
        </div>
        
        <div class="fp-toast-message">{notification.message}</div>
    """

    # Ajouter les actions
    if notification.actions:
        html += '<div class="fp-toast-actions">'
        for action in notification.actions:
            btn_class = "primary" if action.primary else "secondary"
            icon_html = f"{action.icon} " if action.icon else ""
            html += f"""
                <button class="fp-toast-action {btn_class}" 
                        onclick="handleAction('{notification.id}', '{action.label}')">
                    {icon_html}{action.label}
                </button>
            """
        html += "</div>"

    # Ajouter la barre de progression
    if notification.show_progress and notification.duration and notification.duration > 0:
        html += f"""
            <div class="fp-toast-progress" style="
                width: {progress}%;
                color: {color};
            "></div>
        """

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)


def render_all_active_toasts():
    """Affiche toutes les notifications actives sous forme de toasts."""
    manager = get_notification_manager()
    notifications = manager.active_notifications

    if not notifications:
        return

    # Rendre le conteneur une seule fois
    render_toast_container()

    # Rendre chaque notification
    for notif in notifications:
        render_notification_toast(
            notif, on_dismiss=lambda nid=notif.id: manager.dismiss(nid)
        )
