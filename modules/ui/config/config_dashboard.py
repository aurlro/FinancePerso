"""
Configuration Dashboard module.

Provides the main configuration dashboard overview.
"""

import streamlit as st


def render_config_dashboard():
    """Render the configuration dashboard section."""
    st.markdown("### Tableau de bord de configuration")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Catégories", "12")
    with col2:
        st.metric("Membres", "3")
    with col3:
        st.metric("Règles actives", "8")

    st.divider()

    st.info("🔧 Dashboard de configuration complet en cours de développement.")
    st.caption("Cette section affichera des statistiques et rapports sur la configuration.")
