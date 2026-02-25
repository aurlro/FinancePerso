"""Notification settings UI component - Simplified."""

import streamlit as st


def render_notification_settings() -> None:
    """Render notification settings section."""
    st.subheader("🔔 Paramètres des notifications")
    
    st.write("Configuration des alertes et notifications.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Alertes budget", value=True, key="notif_budget")
        st.checkbox("Nouvelles transactions", value=True, key="notif_new_tx")
    
    with col2:
        st.checkbox("Objectifs d'épargne", value=True, key="notif_goals")
        st.checkbox("Rapport hebdomadaire", value=False, key="notif_weekly")
    
    if st.button("Sauvegarder", key="save_notif"):
        st.success("Paramètres sauvegardés!")
