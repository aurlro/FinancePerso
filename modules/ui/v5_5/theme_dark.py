"""Dark Mode Theme - FinCouple Design System.

Thème sombre pour l'interface V5.5
"""

import streamlit as st


class DarkColors:
    """Palette Dark Mode."""
    
    # Primary - Emerald
    PRIMARY = "#10B981"
    PRIMARY_LIGHT = "#34D399"
    PRIMARY_DARK = "#059669"
    PRIMARY_BG = "#064E3B"
    
    # Backgrounds
    BG_PAGE = "#111827"  # Gris très foncé
    BG_CARD = "#1F2937"  # Gris foncé
    BG_SECONDARY = "#374151"  # Gris moyen
    BG_TERTIARY = "#4B5563"  # Gris clair
    BG_ELEVATED = "#1F2937"
    
    # Text
    TEXT_PRIMARY = "#F9FAFB"  # Blanc cassé
    TEXT_SECONDARY = "#D1D5DB"  # Gris clair
    TEXT_MUTED = "#9CA3AF"  # Gris moyen
    TEXT_DISABLED = "#6B7280"
    
    # Borders
    BORDER = "#374151"
    BORDER_LIGHT = "#4B5563"
    BORDER_FOCUS = "#10B981"
    
    # Semantic
    SUCCESS = "#10B981"
    SUCCESS_BG = "#064E3B"
    DANGER = "#EF4444"
    DANGER_BG = "#7F1D1D"
    WARNING = "#F59E0B"
    WARNING_BG = "#78350F"
    INFO = "#3B82F6"
    INFO_BG = "#1E3A8A"


def get_dark_theme_css() -> str:
    """Génère le CSS pour le thème sombre."""
    c = DarkColors
    
    return f"""
    <style>
    :root {{
        --v5-primary: {c.PRIMARY};
        --v5-primary-light: {c.PRIMARY_LIGHT};
        --v5-bg-page: {c.BG_PAGE};
        --v5-bg-card: {c.BG_CARD};
        --v5-text-primary: {c.TEXT_PRIMARY};
        --v5-text-secondary: {c.TEXT_SECONDARY};
        --v5-border: {c.BORDER};
    }}
    
    .stApp {{
        background-color: {c.BG_PAGE} !important;
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        color: {c.TEXT_PRIMARY} !important;
    }}
    
    p, span, div {{
        color: {c.TEXT_PRIMARY} !important;
    }}
    
    /* Cards */
    [data-testid="stMetric"],
    .stDataFrame {{
        background-color: {c.BG_CARD} !important;
        border-color: {c.BORDER} !important;
    }}
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {{
        background-color: {c.BG_CARD} !important;
        border-color: {c.BORDER} !important;
        color: {c.TEXT_PRIMARY} !important;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {c.BG_CARD} !important;
        border-color: {c.BORDER} !important;
    }}
    
    /* Buttons */
    .stButton > button[data-testid="baseButton-secondary"] {{
        background: {c.BG_CARD} !important;
        color: {c.TEXT_PRIMARY} !important;
        border-color: {c.BORDER} !important;
    }}
    
    /* Scrollbar */
    ::-webkit-scrollbar-track {{
        background: {c.BG_SECONDARY} !important;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {c.BORDER} !important;
    }}
    </style>
    """


def apply_dark_theme():
    """Applique le thème sombre."""
    st.markdown(get_dark_theme_css(), unsafe_allow_html=True)


def render_theme_toggle():
    """Rend le toggle pour changer de thème."""
    from modules.ui.v5_5.theme import get_light_theme_css
    
    # Récupérer le thème actuel
    if "theme" not in st.session_state:
        st.session_state.theme = "light"
    
    # Toggle
    cols = st.columns([1, 3])
    with cols[0]:
        new_theme = st.toggle(
            "🌙",
            value=st.session_state.theme == "dark",
            key="theme_toggle",
            help="Basculer entre le mode clair et sombre"
        )
    
    # Mettre à jour
    if new_theme and st.session_state.theme != "dark":
        st.session_state.theme = "dark"
        apply_dark_theme()
    elif not new_theme and st.session_state.theme != "light":
        st.session_state.theme = "light"
        st.markdown(get_light_theme_css(), unsafe_allow_html=True)
    
    return st.session_state.theme
