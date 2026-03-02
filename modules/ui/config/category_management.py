"""
Category Management module for Configuration page.

Provides category creation, editing, and deletion functionality.
"""

import streamlit as st


def render_category_management():
    """Render the category management section."""
    st.markdown("##### Gestion des catégories")

    st.info("🔧 Gestion des catégories en cours de développement.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("➕ Ajouter une catégorie", use_container_width=True):
            st.info("Fonctionnalité à venir : ajout de catégorie personnalisée")

    with col2:
        if st.button("🔄 Fusionner des catégories", use_container_width=True):
            st.info("Fonctionnalité à venir : fusion de catégories")

    st.caption("Les catégories par défaut couvrent la plupart des besoins.")
