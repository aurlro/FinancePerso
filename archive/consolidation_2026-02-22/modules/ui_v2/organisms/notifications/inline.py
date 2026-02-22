"""
Composant de notification inline pour le système de notifications UI v2.

Affiche les notifications directement dans le flux de la page avec
style cohérent et actions interactives.
"""

import streamlit as st

from modules.ui_v2.organisms.notifications.types import (
    DEFAULT_ICONS,
    LEVEL_BG_COLORS,
    LEVEL_COLORS,
    NotificationAction,
    NotificationLevel,
)


def render_inline_notification(
    message: str,
    level: NotificationLevel = NotificationLevel.INFO,
    title: str | None = None,
    icon: str | None = None,
    actions: list[NotificationAction] | None = None,
    dismissible: bool = False,
    key: str | None = None,
) -> bool:
    """
    Affiche une notification inline dans le flux de la page.

    Args:
        message: Contenu du message
        level: Niveau de notification
        title: Titre optionnel
        icon: Icône personnalisée
        actions: Actions associées
        dismissible: Si True, affiche un bouton pour fermer
        key: Clé unique pour le composant

    Returns:
        True si fermé par l'utilisateur
    """
    color = LEVEL_COLORS.get(level, "#3b82f6")
    bg_color = LEVEL_BG_COLORS.get(level, "#eff6ff")
    icon = icon or DEFAULT_ICONS.get(level, "ℹ️")

    component_key = key or f"inline_notif_{hash(message)}"

    # Initialiser l'état de fermeture
    if f"{component_key}_dismissed" not in st.session_state:
        st.session_state[f"{component_key}_dismissed"] = False

    if st.session_state[f"{component_key}_dismissed"]:
        return True

    with st.container():
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, {bg_color} 0%, white 100%);
                border: 1px solid {color}30;
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 16px;
                margin: 8px 0;
            ">
                <div style="display: flex; align-items: flex-start; gap: 12px;">
                    <span style="font-size: 20px; flex-shrink: 0;">{icon}</span>
                    <div style="flex: 1;">
                        {f'<div style="font-weight: 600; color: {color}; margin-bottom: 4px;">{title}</div>' if title else ''}
                        <div style="color: #374151; line-height: 1.5;">{message}</div>
                    </div>
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

        # Actions
        if actions or dismissible:
            cols = st.columns([1] * (len(actions or [])) + ([1] if dismissible else []))

            for i, action in enumerate(actions or []):
                with cols[i]:
                    btn_type = "primary" if action.primary else "secondary"
                    if st.button(
                        f"{action.icon or ''} {action.label}".strip(),
                        key=f"{component_key}_action_{i}",
                        type=btn_type,
                        use_container_width=True,
                    ):
                        if action.callback:
                            action.callback()
                        if action.url:
                            st.switch_page(action.url)

            if dismissible:
                with cols[-1]:
                    if st.button(
                        "✕ Fermer", key=f"{component_key}_dismiss", type="secondary"
                    ):
                        st.session_state[f"{component_key}_dismissed"] = True
                        st.rerun()

    return False
