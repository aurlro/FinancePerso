"""
Système de thème unifié pour FinancePerso v5.5
Supporte Light/Dark mode et personnalisation des couleurs
"""

from dataclasses import dataclass
from typing import Dict, Optional
import streamlit as st


@dataclass
class ThemeConfig:
    """Configuration complète d'un thème."""
    # Couleurs principales
    primary: str
    primary_light: str
    primary_dark: str
    
    # Couleurs de texte
    text_primary: str
    text_secondary: str
    text_muted: str
    
    # Couleurs de fond
    bg_page: str
    bg_card: str
    bg_hover: str
    
    # Couleurs d'état
    positive: str
    negative: str
    warning: str
    info: str
    
    # Bordures et ombres
    border: str
    shadow_sm: str
    shadow_md: str
    shadow_lg: str
    
    # Nom du thème
    name: str
    is_dark: bool = False


# Palettes prédéfinies
PALETTES = {
    "green": {
        "primary": "#10B981",
        "primary_light": "#D1FAE5",
        "primary_dark": "#059669",
    },
    "blue": {
        "primary": "#3B82F6",
        "primary_light": "#DBEAFE",
        "primary_dark": "#2563EB",
    },
    "purple": {
        "primary": "#8B5CF6",
        "primary_light": "#EDE9FE",
        "primary_dark": "#7C3AED",
    },
}


# Thèmes complets
THEMES: Dict[str, ThemeConfig] = {
    "light_green": ThemeConfig(
        name="light_green",
        is_dark=False,
        **PALETTES["green"],
        text_primary="#1F2937",
        text_secondary="#6B7280",
        text_muted="#9CA3AF",
        bg_page="#F9FAFB",
        bg_card="#FFFFFF",
        bg_hover="#F3F4F6",
        positive="#10B981",
        negative="#EF4444",
        warning="#F59E0B",
        info="#3B82F6",
        border="#E5E7EB",
        shadow_sm="0 1px 2px rgba(0,0,0,0.05)",
        shadow_md="0 4px 6px -1px rgba(0,0,0,0.1)",
        shadow_lg="0 10px 15px -3px rgba(0,0,0,0.1)",
    ),
    "light_blue": ThemeConfig(
        name="light_blue",
        is_dark=False,
        **PALETTES["blue"],
        text_primary="#1F2937",
        text_secondary="#6B7280",
        text_muted="#9CA3AF",
        bg_page="#F9FAFB",
        bg_card="#FFFFFF",
        bg_hover="#F3F4F6",
        positive="#10B981",
        negative="#EF4444",
        warning="#F59E0B",
        info="#3B82F6",
        border="#E5E7EB",
        shadow_sm="0 1px 2px rgba(0,0,0,0.05)",
        shadow_md="0 4px 6px -1px rgba(0,0,0,0.1)",
        shadow_lg="0 10px 15px -3px rgba(0,0,0,0.1)",
    ),
    "light_purple": ThemeConfig(
        name="light_purple",
        is_dark=False,
        **PALETTES["purple"],
        text_primary="#1F2937",
        text_secondary="#6B7280",
        text_muted="#9CA3AF",
        bg_page="#F9FAFB",
        bg_card="#FFFFFF",
        bg_hover="#F3F4F6",
        positive="#10B981",
        negative="#EF4444",
        warning="#F59E0B",
        info="#3B82F6",
        border="#E5E7EB",
        shadow_sm="0 1px 2px rgba(0,0,0,0.05)",
        shadow_md="0 4px 6px -1px rgba(0,0,0,0.1)",
        shadow_lg="0 10px 15px -3px rgba(0,0,0,0.1)",
    ),
    "dark_green": ThemeConfig(
        name="dark_green",
        is_dark=True,
        **PALETTES["green"],
        text_primary="#F9FAFB",
        text_secondary="#D1D5DB",
        text_muted="#9CA3AF",
        bg_page="#111827",
        bg_card="#1F2937",
        bg_hover="#374151",
        positive="#34D399",
        negative="#F87171",
        warning="#FBBF24",
        info="#60A5FA",
        border="#374151",
        shadow_sm="0 1px 2px rgba(0,0,0,0.3)",
        shadow_md="0 4px 6px -1px rgba(0,0,0,0.4)",
        shadow_lg="0 10px 15px -3px rgba(0,0,0,0.5)",
    ),
    "dark_blue": ThemeConfig(
        name="dark_blue",
        is_dark=True,
        **PALETTES["blue"],
        text_primary="#F9FAFB",
        text_secondary="#D1D5DB",
        text_muted="#9CA3AF",
        bg_page="#111827",
        bg_card="#1F2937",
        bg_hover="#374151",
        positive="#34D399",
        negative="#F87171",
        warning="#FBBF24",
        info="#60A5FA",
        border="#374151",
        shadow_sm="0 1px 2px rgba(0,0,0,0.3)",
        shadow_md="0 4px 6px -1px rgba(0,0,0,0.4)",
        shadow_lg="0 10px 15px -3px rgba(0,0,0,0.5)",
    ),
    "dark_purple": ThemeConfig(
        name="dark_purple",
        is_dark=True,
        **PALETTES["purple"],
        text_primary="#F9FAFB",
        text_secondary="#D1D5DB",
        text_muted="#9CA3AF",
        bg_page="#111827",
        bg_card="#1F2937",
        bg_hover="#374151",
        positive="#34D399",
        negative="#F87171",
        warning="#FBBF24",
        info="#60A5FA",
        border="#374151",
        shadow_sm="0 1px 2px rgba(0,0,0,0.3)",
        shadow_md="0 4px 6px -1px rgba(0,0,0,0.4)",
        shadow_lg="0 10px 15px -3px rgba(0,0,0,0.5)",
    ),
}


class ThemeManager:
    """Gestionnaire de thème pour l'application."""
    
    DEFAULT_THEME = "light_green"
    
    @classmethod
    def get_current_theme(cls) -> ThemeConfig:
        """Récupère le thème actuel depuis la session."""
        theme_name = st.session_state.get("theme_name", cls.DEFAULT_THEME)
        return THEMES.get(theme_name, THEMES[cls.DEFAULT_THEME])
    
    @classmethod
    def set_theme(cls, theme_name: str) -> None:
        """Change le thème actuel."""
        if theme_name in THEMES:
            st.session_state["theme_name"] = theme_name
    
    @classmethod
    def toggle_dark_mode(cls) -> None:
        """Bascule entre light et dark mode en gardant la palette."""
        current = cls.get_current_theme()
        
        # Extraire la palette (green, blue, purple)
        if "green" in current.name:
            palette = "green"
        elif "blue" in current.name:
            palette = "blue"
        else:
            palette = "purple"
        
        # Inverser le mode
        new_mode = "dark" if not current.is_dark else "light"
        new_theme = f"{new_mode}_{palette}"
        
        cls.set_theme(new_theme)
    
    @classmethod
    def set_palette(cls, palette: str) -> None:
        """Change la palette de couleurs en gardant le mode."""
        current = cls.get_current_theme()
        mode = "dark" if current.is_dark else "light"
        new_theme = f"{mode}_{palette}"
        
        if new_theme in THEMES:
            cls.set_theme(new_theme)
    
    @classmethod
    def apply_theme_css(cls) -> None:
        """Injecte les CSS du thème actuel dans la page."""
        theme = cls.get_current_theme()
        
        css = f"""
        <style>
        :root {{
            --primary: {theme.primary};
            --primary-light: {theme.primary_light};
            --primary-dark: {theme.primary_dark};
            --text-primary: {theme.text_primary};
            --text-secondary: {theme.text_secondary};
            --text-muted: {theme.text_muted};
            --bg-page: {theme.bg_page};
            --bg-card: {theme.bg_card};
            --bg-hover: {theme.bg_hover};
            --positive: {theme.positive};
            --negative: {theme.negative};
            --warning: {theme.warning};
            --info: {theme.info};
            --border: {theme.border};
            --shadow-sm: {theme.shadow_sm};
            --shadow-md: {theme.shadow_md};
            --shadow-lg: {theme.shadow_lg};
        }}
        
        .stApp {{
            background-color: {theme.bg_page};
            color: {theme.text_primary};
        }}
        
        /* Cards et containers */
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {{
            background-color: {theme.bg_card};
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)


def get_theme() -> ThemeConfig:
    """Raccourci pour récupérer le thème actuel."""
    return ThemeManager.get_current_theme()


def render_theme_toggle() -> None:
    """Affiche le toggle light/dark dans la sidebar."""
    theme = get_theme()
    
    with st.sidebar:
        st.divider()
        
        # Toggle Light/Dark
        col1, col2 = st.columns([1, 3])
        with col1:
            icon = "🌙" if not theme.is_dark else "🌞"
            if st.button(icon, key="theme_toggle", help="Basculer light/dark mode"):
                ThemeManager.toggle_dark_mode()
                st.rerun()
        
        with col2:
            st.caption("Mode " + ("sombre" if theme.is_dark else "clair"))
        
        # Sélecteur de palette
        palettes = {
            "green": "🟢 Vert",
            "blue": "🔵 Bleu", 
            "purple": "🟣 Violet"
        }
        
        current_palette = "green"
        if "blue" in theme.name:
            current_palette = "blue"
        elif "purple" in theme.name:
            current_palette = "purple"
        
        selected = st.selectbox(
            "Couleur d'accent",
            options=list(palettes.keys()),
            format_func=lambda x: palettes[x],
            index=list(palettes.keys()).index(current_palette),
            key="palette_selector"
        )
        
        if selected != current_palette:
            ThemeManager.set_palette(selected)
            st.rerun()


# Initialiser le thème au chargement
def init_theme():
    """Initialise le thème si pas déjà défini."""
    if "theme_name" not in st.session_state:
        st.session_state["theme_name"] = ThemeManager.DEFAULT_THEME
