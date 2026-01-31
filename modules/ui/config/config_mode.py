"""
Configuration Mode Manager - Simple vs Advanced mode.
Allows users to switch between simplified and full configuration views.
"""
import streamlit as st


def is_advanced_mode() -> bool:
    """Check if advanced mode is enabled."""
    return st.session_state.get('config_advanced_mode', False)


def toggle_config_mode():
    """Toggle between simple and advanced mode."""
    st.session_state['config_advanced_mode'] = not st.session_state.get('config_advanced_mode', False)


def render_mode_toggle():
    """Render the mode toggle button in the sidebar or header."""
    current_mode = "🔧 Avancé" if is_advanced_mode() else "🎯 Simple"
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption(f"Mode actuel : **{current_mode}**")
    with col2:
        if st.button(
            "Mode " + ("Simple" if is_advanced_mode() else "Avancé"),
            use_container_width=True,
            help="Basculer entre le mode simple (essentiels uniquement) et avancé (tous les paramètres)"
        ):
            toggle_config_mode()
            st.rerun()


def should_show_advanced_section(section_name: str) -> bool:
    """
    Determine if a section should be shown based on current mode.
    
    Args:
        section_name: Name of the configuration section
        
    Returns:
        True if the section should be shown
    """
    if is_advanced_mode():
        return True
    
    # In simple mode, only show essential sections
    essential_sections = {
        'members',           # Basic member management
        'categories',        # Basic category management
        'api_key',          # Just the API key, not advanced options
        'notifications_basic',  # Just enable/disable, not SMTP config
        'budgets',          # Budget creation
    }
    
    return section_name in essential_sections


def get_simplified_api_form():
    """
    Get simplified API configuration form fields.
    Returns only essential fields for simple mode.
    """
    return {
        'provider': 'Gemini',  # Default only
        'api_key': True,       # Show API key field
        'model_name': False,   # Hide model selection
        'advanced_options': False  # Hide advanced options
    }


def get_simplified_notification_form():
    """
    Get simplified notification configuration.
    Returns only on/off toggle for simple mode.
    """
    return {
        'enable_toggle': True,
        'desktop': True,       # Just enable/disable desktop
        'email': False,        # Hide email configuration in simple mode
        'thresholds': False,   # Use default thresholds
        'smtp_config': False   # Hide SMTP configuration
    }


def filter_categories_for_simple_mode(categories_df):
    """
    Filter categories to show only essential info in simple mode.
    Hides: suggested_tags, fixed flag editing
    """
    if is_advanced_mode():
        return categories_df
    
    # In simple mode, return only name and emoji
    return categories_df[['id', 'name', 'emoji']]


def render_simple_mode_help():
    """Render help text explaining simple mode."""
    with st.expander("ℹ️ À propos du mode Simple", expanded=False):
        st.markdown("""
        **Mode Simple** : Affiche uniquement les paramètres essentiels :
        - Ajout de membres et catégories
        - Configuration de base de l'IA (clé API)
        - Activation/désactivation des notifications
        - Création de budgets
        
        **Mode Avancé** : Accès à tous les paramètres :
        - Configuration SMTP détaillée
        - Seuils d'alerte personnalisés
        - Règles d'apprentissage et tags
        - Outils d'audit et nettoyage avancés
        - Export/Import de configuration
        
        💡 **Conseil** : Commencez par le mode Simple, passez en Avancé si vous avez besoin de fonctionnalités spécifiques.
        """)
