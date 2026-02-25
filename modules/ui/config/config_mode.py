"""
Gestion du mode de configuration (Simple vs Avancé).
"""

import streamlit as st


def is_advanced_mode() -> bool:
    """Vérifie si l'utilisateur est en mode avancé."""
    return st.session_state.get("config_advanced_mode", False)


def render_mode_toggle():
    """Affiche le toggle pour switcher entre mode simple et avancé."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.caption("Mode d'affichage")
    
    with col2:
        current_mode = is_advanced_mode()
        new_mode = st.toggle(
            "Avancé",
            value=current_mode,
            key="config_advanced_mode_toggle",
            help="Activez pour voir toutes les options avancées"
        )
        
        if new_mode != current_mode:
            st.session_state["config_advanced_mode"] = new_mode
            st.rerun()


def render_simple_mode_help():
    """Affiche l'aide pour le mode simple."""
    with st.expander("❓ Mode Simple - Aide", expanded=False):
        st.markdown("""
        **Le mode simple affiche uniquement les options essentielles :**
        
        - Configuration de l'IA (clés API)
        - Gestion des membres
        - Sauvegarde et restauration
        - Export des données
        
        **Activez le mode avancé pour accéder à :**
        
        - Gestion des catégories personnalisées
        - Configuration ML local
        - Outils d'audit
        - Gestion des notifications
        - Logs système
        - Réglages techniques
        """)


def render_config_mode_section():
    """Section complète de gestion du mode de configuration."""
    st.subheader("🔧 Mode d'affichage")
    
    render_mode_toggle()
    
    if not is_advanced_mode():
        render_simple_mode_help()
    else:
        st.info("Mode avancé activé. Toutes les options sont disponibles ci-dessous.")
