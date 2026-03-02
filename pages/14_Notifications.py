"""
🔔 Notifications V3 - Centre de notifications unifié

Nouveau système de notifications avec persistance DB.
"""

import streamlit as st

from modules.notifications import NotificationService, NotificationType
from modules.notifications.ui import (
    render_notification_center,
    render_notification_settings,
)
from modules.ui import load_css, render_scroll_to_top

# Configuration
st.set_page_config(
    page_title="Notifications V3",
    page_icon="🔔",
    layout="wide",
)

# Styles
load_css()

# Service
service = NotificationService()

# Titre
st.title("🔔 Centre de Notifications V3")

# Onglets
tab_center, tab_settings, tab_test = st.tabs(
    ["📬 Centre de notifications", "⚙️ Paramètres", "🧪 Test"]
)

with tab_center:
    render_notification_center(service)

with tab_settings:
    render_notification_settings(service)

with tab_test:
    st.header("🧪 Test du système de notifications")

    st.info("Utilisez ces boutons pour créer des notifications de test.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Budget")
        if st.button("🚨 Budget critique", use_container_width=True):
            service.notify(
                type=NotificationType.BUDGET_CRITICAL,
                title="Budget Alimentation dépassé",
                message="Vous avez dépensé 1,250€ sur un budget de 1,000€ (125%)",
                actions=[{"label": "Voir", "action": "navigate", "target": "04_Budgets"}],
            )
            st.success("Notification créée!")
            st.rerun()

        if st.button("⚠️ Budget warning", use_container_width=True):
            service.notify(
                type=NotificationType.BUDGET_WARNING,
                title="Budget Transport",
                message="Vous avez atteint 85% de votre budget (85€ / 100€)",
            )
            st.success("Notification créée!")
            st.rerun()

    with col2:
        st.subheader("Validation")
        if st.button("⏳ Rappel validation", use_container_width=True):
            service.notify_validation_reminder(count=12, oldest_days=18)
            st.success("Notification créée!")
            st.rerun()

        if st.button("📥 Rappel import", use_container_width=True):
            service.notify_import_reminder(days_since_import=15)
            st.success("Notification créée!")
            st.rerun()

    with col3:
        st.subheader("Gamification")
        if st.button("🏅 Nouveau badge", use_container_width=True):
            service.notify_achievement("Maître de l'épargne", "💰")
            st.success("Notification créée!")
            st.rerun()

        if st.button("♻️ Doublons", use_container_width=True):
            service.notify_duplicate("2024-02-15", "Supermarché Casino", 45.50, 2)
            st.success("Notification créée!")
            st.rerun()

    st.divider()

    # Stats
    st.subheader("📊 Statistiques")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Non lues", service.count_unread())
    with col2:
        all_notifs = service.get_all(limit=1000)
        st.metric("Total (30 jours)", len(all_notifs))
    with col3:
        service.cleanup(days=30)
        st.metric("Nettoyage", "OK")

# Scroll to top
render_scroll_to_top()
