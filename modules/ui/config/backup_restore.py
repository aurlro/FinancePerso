"""
Backup & Restore module for Configuration page.

Provides data backup and restore functionality.
"""

import streamlit as st


def render_backup_restore():
    """Render the backup and restore section."""
    st.markdown("##### Sauvegarde")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Créer une sauvegarde", use_container_width=True):
            st.info("📦 Fonctionnalité de sauvegarde en développement")
            st.caption("La sauvegarde sera disponible prochainement.")

    with col2:
        if st.button("🔄 Restaurer", use_container_width=True):
            st.info("📦 Fonctionnalité de restauration en développement")
            st.caption("La restauration sera disponible prochainement.")

    st.divider()

    st.markdown("##### Export/Import")

    col3, col4 = st.columns(2)

    with col3:
        if st.button("📤 Exporter CSV", use_container_width=True):
            st.info("📦 Export CSV en développement")

    with col4:
        uploaded = st.file_uploader("📥 Importer des données", type=["csv", "json"])
        if uploaded:
            st.info(f"Fichier '{uploaded.name}' sélectionné (import non disponible)")
