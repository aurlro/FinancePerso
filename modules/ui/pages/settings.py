# -*- coding: utf-8 -*-
"""
Page de paramètres unifiée avec Design System V5.5.

Remplace: modules/ui/config/config_dashboard.py
"""

import streamlit as st

from modules.ui.molecules.toast import toast_error, toast_success
from modules.ui.tokens.colors import Colors
from modules.ui.tokens.spacing import Spacing


def render_settings_page() -> None:
    """
    Render the unified settings page.
    """
    # Header
    st.markdown(f"""
    <h1 style="color: {Colors.GRAY_900}; margin-bottom: {Spacing.SMALL}px;">
        ⚙️ Paramètres
    </h1>
    <p style="color: {Colors.GRAY_600}; margin-bottom: {Spacing.LARGE}px;">
        Configurez votre application FinancePerso
    </p>
    """, unsafe_allow_html=True)
    
    # Tabs for different settings categories
    tabs = st.tabs([
        "💾 Données",
        "🤖 Intelligence Artificielle",
        "👥 Membres",
        "🏷️ Catégories",
        "🔔 Notifications",
    ])
    
    with tabs[0]:
        render_data_settings()
    
    with tabs[1]:
        render_ai_settings()
    
    with tabs[2]:
        render_members_settings()
    
    with tabs[3]:
        render_categories_settings()
    
    with tabs[4]:
        render_notifications_settings()


def render_data_settings() -> None:
    """Render data management settings."""
    st.subheader("Gestion des données")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📥 Export")
        st.write("Exportez vos données au format CSV ou JSON.")
        
        if st.button("📄 Exporter CSV", use_container_width=True):
            try:
                # Export logic here
                toast_success("Export réussi !", "Vos données ont été exportées.")
            except Exception as e:
                toast_error("Erreur d'export", str(e))
        
        if st.button("📄 Exporter JSON", use_container_width=True):
            try:
                toast_success("Export réussi !")
            except Exception as e:
                toast_error("Erreur d'export", str(e))
    
    with col2:
        st.markdown("#### 📤 Import")
        st.write("Importez des données depuis un fichier.")
        
        uploaded_file = st.file_uploader(
            "Choisir un fichier",
            type=["csv", "json"],
            key="settings_import",
        )
        
        if uploaded_file is not None:
            if st.button("📥 Importer", type="primary", use_container_width=True):
                try:
                    # Import logic here
                    toast_success("Import réussi !")
                except Exception as e:
                    toast_error("Erreur d'import", str(e))
    
    st.divider()
    
    # Danger zone
    st.markdown(f"""
    <div style="
        background: {Colors.RED_50};
        border: 1px solid {Colors.RED_200};
        border-radius: {Spacing.RADIUS_MEDIUM}px;
        padding: {Spacing.MEDIUM}px;
    ">
        <h4 style="color: {Colors.RED_700}; margin-top: 0;">⚠️ Zone de danger</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(
            "🗑️ Vider le cache",
            use_container_width=True,
        ):
            if st.checkbox("Confirmer le vidage du cache", key="confirm_clear"):
                st.cache_data.clear()
                toast_success("Cache vidé !")
    
    with col2:
        if st.button(
            "💥 Réinitialiser toutes les données",
            type="secondary",
            use_container_width=True,
        ):
            st.error("⚠️ Cette action est irréversible !")
            if st.checkbox("Je confirme vouloir tout supprimer", key="confirm_reset"):
                # Reset logic here
                toast_success("Données réinitialisées")


def render_ai_settings() -> None:
    """Render AI settings."""
    st.subheader("Configuration de l'IA")
    
    # Provider selection
    st.markdown("#### 🤖 Provider IA")
    
    provider = st.selectbox(
        "Provider IA",
        options=["Gemini (Google)", "OpenAI", "Ollama (Local)", "ML Local"],
        help="Choisissez le service d'IA pour la catégorisation",
    )
    
    # API Key (if needed)
    if provider in ["Gemini (Google)", "OpenAI"]:
        api_key = st.text_input(
            "Clé API",
            type="password",
            help="Votre clé API pour le service sélectionné",
        )
    
    # Cache settings
    st.markdown("#### 💾 Cache IA")
    
    use_cache = st.toggle(
        "Activer le cache IA",
        value=True,
        help="Mise en cache des résultats pour réduire les appels API",
    )
    
    if use_cache:
        cache_ttl = st.slider(
            "Durée de vie du cache (heures)",
            min_value=1,
            max_value=72,
            value=24,
        )
    
    if st.button("💾 Sauvegarder", type="primary"):
        toast_success("Configuration sauvegardée !")


def render_members_settings() -> None:
    """Render members settings."""
    st.subheader("Gestion des membres")
    
    # Current members
    st.markdown("#### 👥 Membres actuels")
    
    # Mock data - replace with actual data
    members = [
        {"name": "Maison", "type": "HOUSEHOLD", "color": "🟢"},
        {"name": "Famille", "type": "HOUSEHOLD", "color": "🔵"},
    ]
    
    for member in members:
        with st.container():
            cols = st.columns([3, 2, 1])
            with cols[0]:
                st.write(f"{member['color']} **{member['name']}**")
            with cols[1]:
                st.caption(member['type'])
            with cols[2]:
                if st.button("✏️", key=f"edit_{member['name']}"):
                    st.session_state[f"editing_{member['name']}"] = True
        
        st.divider()
    
    # Add new member
    st.markdown("#### ➕ Ajouter un membre")
    
    new_member_name = st.text_input("Nom du membre")
    new_member_type = st.selectbox(
        "Type",
        options=["HOUSEHOLD", "EXTERNAL"],
    )
    
    if st.button("Ajouter", type="primary"):
        if new_member_name:
            toast_success(f"Membre '{new_member_name}' ajouté !")
        else:
            toast_error("Erreur", "Veuillez entrer un nom")


def render_categories_settings() -> None:
    """Render categories settings."""
    st.subheader("Gestion des catégories")
    
    # Current categories
    st.markdown("#### 🏷️ Catégories actuelles")
    
    categories = [
        {"name": "Alimentation", "emoji": "🛒", "is_fixed": False},
        {"name": "Transport", "emoji": "🚗", "is_fixed": False},
        {"name": "Logement", "emoji": "🏠", "is_fixed": True},
    ]
    
    for cat in categories:
        with st.container():
            cols = st.columns([1, 3, 2, 1])
            with cols[0]:
                st.write(cat['emoji'])
            with cols[1]:
                st.write(f"**{cat['name']}**")
            with cols[2]:
                if cat['is_fixed']:
                    st.badge("Fixe")
            with cols[3]:
                if st.button("✏️", key=f"edit_cat_{cat['name']}"):
                    pass
        
        st.divider()
    
    # Add new category
    st.markdown("#### ➕ Ajouter une catégorie")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        new_cat_name = st.text_input("Nom de la catégorie")
    with col2:
        new_cat_emoji = st.text_input("Emoji", value="🏷️")
    
    new_cat_fixed = st.checkbox("Catégorie fixe")
    
    if st.button("Ajouter la catégorie", type="primary"):
        if new_cat_name:
            toast_success(f"Catégorie '{new_cat_name}' ajoutée !")
        else:
            toast_error("Erreur", "Veuillez entrer un nom")


def render_notifications_settings() -> None:
    """Render notifications settings."""
    st.subheader("Paramètres de notifications")
    
    st.markdown("#### 🔔 Notifications")
    
    # Enable/disable notifications
    enable_notifications = st.toggle(
        "Activer les notifications",
        value=True,
    )
    
    if enable_notifications:
        st.markdown("#### 📧 Alertes email")
        
        email = st.text_input(
            "Adresse email",
            help="Pour recevoir les alertes",
        )
        
        st.markdown("#### 🔔 Types d'alertes")
        
        st.checkbox("Alertes de budget", value=True)
        st.checkbox("Alertes de découvert", value=True)
        st.checkbox("Résumé hebdomadaire", value=False)
        st.checkbox("Résumé mensuel", value=True)
        
        st.markdown("#### ⏰ Horaires")
        
        st.time_input(
            "Heure du résumé quotidien",
            value=None,
        )
    
    if st.button("Sauvegarder les préférences", type="primary"):
        toast_success("Préférences sauvegardées !")


# Pour compatibilité avec l'ancien système
def render() -> None:
    """Alias for render_settings_page."""
    render_settings_page()
