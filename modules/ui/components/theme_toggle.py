"""Composant toggle pour changer le thème."""

import streamlit as st

from modules.ui.theme import ColorPalette, ThemeMode, theme_manager


def render_theme_toggle():
    """Affiche le toggle de thème dans la sidebar."""
    
    # Rafraîchir le thème pour avoir les valeurs à jour
    theme = theme_manager.refresh()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎨 Thème")
    
    # Toggle Light/Dark
    current_mode = theme.mode
    mode_col1, mode_col2 = st.sidebar.columns([1, 3])
    
    with mode_col1:
        icon = "🌙" if current_mode == ThemeMode.LIGHT else "🌞"
        if st.button(icon, key="theme_toggle_btn", help="Basculer mode clair/sombre"):
            theme_manager.toggle_mode()
            st.rerun()
    
    with mode_col2:
        st.write("Mode sombre" if current_mode == ThemeMode.DARK else "Mode clair")
    
    # Sélecteur de couleur
    current_palette = theme.palette
    palette_options = {
        ColorPalette.GREEN.value: "🟢 Vert (défaut)",
        ColorPalette.BLUE.value: "🔵 Bleu",
        ColorPalette.PURPLE.value: "🟣 Violet"
    }
    
    selected = st.sidebar.selectbox(
        "Couleur d'accent",
        options=list(palette_options.keys()),
        format_func=lambda x: palette_options[x],
        index=list(palette_options.keys()).index(current_palette.value),
        key="palette_select"
    )
    
    if selected != current_palette.value:
        theme_manager.set_palette(ColorPalette(selected))
        st.rerun()


def render_theme_selector_compact():
    """Version compacte du sélecteur de thème (pour header)."""
    
    theme = theme_manager.refresh()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Toggle mode
        icon = "🌙" if theme.mode == ThemeMode.LIGHT else "🌞"
        if st.button(icon, key="theme_toggle_compact", help="Mode clair/sombre"):
            theme_manager.toggle_mode()
            st.rerun()
    
    with col2:
        # Dropdown palette
        palette_emojis = {
            ColorPalette.GREEN.value: "🟢",
            ColorPalette.BLUE.value: "🔵",
            ColorPalette.PURPLE.value: "🟣"
        }
        
        selected = st.selectbox(
            "",
            options=list(palette_emojis.keys()),
            format_func=lambda x: palette_emojis[x],
            index=list(palette_emojis.keys()).index(theme.palette.value),
            key="palette_compact",
            label_visibility="collapsed"
        )
        
        if selected != theme.palette.value:
            theme_manager.set_palette(ColorPalette(selected))
            st.rerun()


def apply_theme_css():
    """Injecte les CSS du thème dans la page."""
    theme = theme_manager.current
    css = theme.get_css_variables()
    st.markdown(css, unsafe_allow_html=True)
    
    # CSS additionnel pour Streamlit
    additional_css = f"""
    <style>
    /* Fond de page */
    .stApp {{
        background-color: {theme.bg_page} !important;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {theme.bg_sidebar} !important;
    }}
    
    /* Textes */
    .stApp, .stMarkdown, p, h1, h2, h3, h4, h5, h6 {{
        color: {theme.text_primary} !important;
    }}
    
    /* Boutons primaires */
    .stButton > button[kind="primary"] {{
        background-color: {theme.primary} !important;
        border-color: {theme.primary} !important;
        color: {theme.text_on_primary} !important;
    }}
    
    .stButton > button[kind="primary"]:hover {{
        background-color: {theme.primary_hover} !important;
        border-color: {theme.primary_hover} !important;
    }}
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {{
        background-color: {theme.bg_input} !important;
        color: {theme.text_primary} !important;
        border-color: {theme.border} !important;
    }}
    
    /* Cards/conteneurs */
    [data-testid="stExpander"] {{
        background-color: {theme.bg_card} !important;
        border: 1px solid {theme.border} !important;
    }}
    
    /* Succès */
    .stSuccess {{
        background-color: {theme.primary_light} !important;
        color: {theme.text_primary} !important;
        border-left-color: {theme.success} !important;
    }}
    
    /* Erreur */
    .stError {{
        background-color: rgba(239, 68, 68, 0.1) !important;
        border-left-color: {theme.error} !important;
    }}
    
    /* Avertissement */
    .stWarning {{
        background-color: rgba(245, 158, 11, 0.1) !important;
        border-left-color: {theme.warning} !important;
    }}
    
    /* Info */
    .stInfo {{
        background-color: rgba(59, 130, 246, 0.1) !important;
        border-left-color: {theme.info} !important;
    }}
    </style>
    """
    st.markdown(additional_css, unsafe_allow_html=True)
