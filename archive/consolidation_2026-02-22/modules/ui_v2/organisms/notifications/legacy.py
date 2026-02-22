"""
Module de compatibilité legacy pour le système de notifications UI v2.

Ré-exporte les fonctions depuis l'emplacement original avec des warnings
de déprécation pour faciliter la migration progressive du code.

Attention:
    Ce module est destiné à être utilisé temporairement pendant la migration.
    Les nouvelles implémentations devraient utiliser directement les modules
    sous modules.ui_v2.organisms.notifications.*
"""

import warnings
from collections.abc import Callable

import streamlit as st

from modules.ui.notifications.manager import get_notification_manager
from modules.ui_v2.organisms.notifications.types import (
    DEFAULT_ICONS,
    Notification,
    NotificationLevel,
)


def _emit_deprecation_warning(new_module: str, func_name: str):
    """Émet un warning de déprécation avec indication du nouveau module."""
    warnings.warn(
        f"{func_name} est déprécié. "
        f"Utilisez plutôt 'from {new_module} import {func_name}'",
        DeprecationWarning,
        stacklevel=3,
    )


def show_confirmation(
    title: str,
    message: str,
    on_confirm: Callable,
    on_cancel: Callable | None = None,
    confirm_label: str = "Confirmer",
    cancel_label: str = "Annuler",
    danger: bool = False,
    key: str = "confirm",
) -> bool:
    """
    Affiche une boîte de confirmation.

    .. deprecated::
        Utilisez modules.ui.components.confirm_dialog.confirm_dialog à la place.

    Returns:
        True si l'utilisateur a fait un choix
    """
    _emit_deprecation_warning(
        "modules.ui.components.confirm_dialog", "show_confirmation"
    )

    state_key = f"{key}_shown"
    result_key = f"{key}_result"

    if state_key not in st.session_state:
        st.session_state[state_key] = True
        st.session_state[result_key] = None

    if not st.session_state[state_key]:
        return True

    color = "#dc2626" if danger else "#f59e0b"
    icon = "⚠️" if danger else "🤔"

    with st.container():
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #fef2f2 0%, white 100%) if {danger} else linear-gradient(135deg, #fffbeb 0%, white 100%);
                border: 1px solid {color}40;
                border-left: 4px solid {color};
                border-radius: 12px;
                padding: 20px;
                margin: 16px 0;
            ">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                    <span style="font-size: 24px;">{icon}</span>
                    <span style="font-size: 18px; font-weight: 600; color: {color};">{title}</span>
                </div>
                <div style="color: #4b5563; margin-left: 36px;">{message}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns([1, 1, 3])

        with col1:
            btn_type = "primary" if not danger else "secondary"
            if st.button(
                cancel_label, key=f"{key}_cancel", type=btn_type, use_container_width=True
            ):
                st.session_state[state_key] = False
                st.session_state[result_key] = False
                if on_cancel:
                    on_cancel()
                st.rerun()

        with col2:
            btn_type = "primary" if danger else "secondary"
            if st.button(
                confirm_label, key=f"{key}_confirm", type=btn_type, use_container_width=True
            ):
                st.session_state[state_key] = False
                st.session_state[result_key] = True
                on_confirm()
                st.rerun()

    return False


def show_native_toast(notification: Notification):
    """
    Affiche une notification via le système natif de Streamlit (st.toast).
    Fallback quand les composants customs ne sont pas disponibles.

    .. deprecated::
        Cette fonction est conservée pour compatibilité. Préférez
        render_notification_toast pour un affichage riche.
    """
    _emit_deprecation_warning(
        "modules.ui_v2.organisms.notifications.toast", "show_native_toast"
    )

    icon = notification.icon or DEFAULT_ICONS.get(notification.level, "ℹ️")
    message = f"{icon} {notification.message}"

    if notification.level == NotificationLevel.SUCCESS:
        st.toast(message, icon="✅")
    elif notification.level == NotificationLevel.CRITICAL:
        st.error(message)
    elif notification.level == NotificationLevel.WARNING:
        st.warning(message)
    elif notification.level == NotificationLevel.ACHIEVEMENT:
        st.toast(message, icon="🏆")
    else:
        st.toast(message, icon="ℹ️")


def render_notifications_auto():
    """
    Fonction principale à appeler dans chaque page.
    Affiche automatiquement toutes les notifications actives.

    .. deprecated::
        Utilisez render_all_active_toasts à la place pour plus de contrôle.
    """
    _emit_deprecation_warning(
        "modules.ui_v2.organisms.notifications.toast", "render_notifications_auto"
    )

    manager = get_notification_manager()

    # Nettoyer les notifications expirées
    manager.cleanup_expired()

    # Afficher les notifications
    notifications = manager.active_notifications

    for notif in notifications:
        # Utiliser le système natif pour l'instant (plus stable)
        show_native_toast(notif)
