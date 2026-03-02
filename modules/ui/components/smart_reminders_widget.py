"""
Smart Reminders Widget - Affichage des rappels intelligents.

Intégré dans le dashboard pour guider l'utilisateur vers les actions importantes.
"""

import streamlit as st

from modules.smart_reminders import SmartReminder, get_smart_reminders
from modules.ui.feedback import toast_info


def render_reminder_card(reminder: SmartReminder, index: int = 0):
    """Afficher une carte de rappel."""

    # Couleur selon la priorité

    with st.container(border=True):
        col1, col2 = st.columns([4, 1])

        with col1:
            # Titre avec icône
            st.write(f"**{reminder.icon} {reminder.title}**")
            st.caption(reminder.message)

        with col2:
            # Action button
            if reminder.action_type == "navigate":
                if st.button(
                    reminder.action_label,
                    key=f"reminder_{reminder.type.value}_{index}",
                    use_container_width=True,
                    type="primary" if reminder.priority.value == "high" else "secondary",
                ):
                    if reminder.action_target:
                        st.switch_page(reminder.action_target)

            elif reminder.action_type == "dismiss":
                if st.button(
                    reminder.action_label, key=f"reminder_dismiss_{index}", use_container_width=True
                ):
                    # Juste disparaître (le composant sera re-render sans ce rappel)
                    toast_info("Rappel ignoré", icon="👍")
                    st.rerun()


def render_smart_reminders_widget(max_reminders: int = 3):
    """Widget principal des rappels intelligents."""

    reminders = get_smart_reminders()

    if not reminders:
        return

    # Ne garder que les plus importants
    display_reminders = reminders[:max_reminders]

    with st.expander(f"🔔 {len(reminders)} rappel(s) important(s)", expanded=True):
        st.caption("Actions recommandées basées sur votre activité")

        for i, reminder in enumerate(display_reminders):
            render_reminder_card(reminder, i)

        if len(reminders) > max_reminders:
            st.caption(f"... et {len(reminders) - max_reminders} autre(s)")


def render_compact_reminder():
    """Version compacte pour le header du dashboard."""

    reminders = get_smart_reminders()

    if not reminders:
        return

    # Prendre le plus important
    top = reminders[0]

    # Banner style
    priority_bg = {"high": "#ffcccc", "medium": "#ffffcc", "low": "#ccffcc"}

    bg_color = priority_bg.get(top.priority.value, "#f0f0f0")
    border_colors = {"high": "#ff0000", "medium": "#ffaa00", "low": "#00aa00"}
    border_color = border_colors.get(top.priority.value, "#00aa00")

    st.markdown(
        f"""
    <div style="
        background-color: {bg_color};
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        border-left: 4px solid {border_color};
    ">
        <strong>{top.icon} {top.title}</strong><br>
        <small>{top.message}</small>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Action buttons
    cols = st.columns([1, 1, 3])

    with cols[0]:
        if top.action_type == "navigate" and top.action_target:
            if st.button(top.action_label, key="top_reminder_action", type="primary"):
                st.switch_page(top.action_target)

    with cols[1]:
        if st.button("Ignorer", key="top_reminder_dismiss"):
            st.rerun()


def render_reminders_in_sidebar():
    """Afficher les rappels dans la sidebar."""

    reminders = get_smart_reminders()

    if not reminders:
        return

    with st.sidebar:
        st.divider()
        st.markdown("### 🔔 Rappels")

        for reminder in reminders[:2]:  # Max 2 dans la sidebar
            with st.container():
                st.write(f"**{reminder.icon} {reminder.title}**")
                st.caption(
                    reminder.message[:60] + "..."
                    if len(reminder.message) > 60
                    else reminder.message
                )

                if reminder.action_type == "navigate":
                    if st.button(
                        reminder.action_label,
                        key=f"sidebar_reminder_{reminder.type.value}",
                        use_container_width=True,
                    ):
                        st.switch_page(reminder.action_target)

                st.caption("")


# Helper pour vérifier s'il y a des rappels urgents
def has_urgent_reminders() -> bool:
    """Vérifier s'il y a des rappels haute priorité."""
    from modules.smart_reminders import get_high_priority_reminders

    return len(get_high_priority_reminders()) > 0


# Helper pour le daily widget
def get_reminder_insight_for_daily_widget() -> dict:
    """Génère un insight pour le daily widget basé sur les rappels."""

    reminders = get_smart_reminders()

    if not reminders:
        return None

    # Prendre le plus prioritaire
    top = reminders[0]

    return {
        "type": "reminder",
        "title": top.title,
        "message": top.message,
        "priority": top.priority.value,
        "action": top.action_target,
        "action_label": top.action_label,
        "icon": top.icon,
    }
