"""Thème Light Mode V5.6 - Design System FinCouple.

Palette de couleurs et styles pour la nouvelle interface light mode,
inspirée des maquettes Figma FinCouple v5.6.

Usage:
    from modules.ui.v5_5.theme import LightColors, apply_light_theme

    # Appliquer le thème global
    apply_light_theme()

    # Utiliser les couleurs
    bg = LightColors.BG_PAGE
    primary = LightColors.PRIMARY
"""

import streamlit as st

from modules.ui.tokens import BorderRadius, Shadow, Spacing, Typography


class LightColors:
    """Palette de couleurs Light Mode - Maquette FinCouple V5.6.
    
    Design épuré avec fond très clair et cards blanches.
    """

    # ============================================================
    # COULEURS PRINCIPALES
    # ============================================================

    # Primary - Emerald (comme dans la maquette)
    PRIMARY = "#10B981"  # Vert émeraude
    PRIMARY_LIGHT = "#34D399"  # Vert clair
    PRIMARY_DARK = "#059669"  # Vert foncé
    PRIMARY_BG = "#D1FAE5"  # Vert très clair (fond icônes)

    # Secondary - Slate
    SECONDARY = "#64748B"
    SECONDARY_LIGHT = "#94A3B8"
    SECONDARY_DARK = "#475569"
    SECONDARY_BG = "#F1F5F9"

    # ============================================================
    # COULEURS SÉMANTIQUES
    # ============================================================

    # Success (vert)
    SUCCESS = "#10B981"
    SUCCESS_LIGHT = "#34D399"
    SUCCESS_DARK = "#059669"
    SUCCESS_BG = "#DCFCE7"

    # Danger (rouge)
    DANGER = "#EF4444"
    DANGER_LIGHT = "#F87171"
    DANGER_DARK = "#DC2626"
    DANGER_BG = "#FEE2E2"

    # Warning (orange)
    WARNING = "#F59E0B"
    WARNING_LIGHT = "#FBBF24"
    WARNING_DARK = "#D97706"
    WARNING_BG = "#FEF3C7"

    # Info (bleu)
    INFO = "#3B82F6"
    INFO_LIGHT = "#60A5FA"
    INFO_DARK = "#2563EB"
    INFO_BG = "#DBEAFE"

    # ============================================================
    # COULEURS DE FOND (Design FinCouple)
    # ============================================================

    BG_PAGE = "#F8FAFC"  # Gris très très clair (fond page)
    BG_SIDEBAR = "#FFFFFF"  # Blanc pur (sidebar)
    BG_CARD = "#FFFFFF"  # Blanc pur (cards)
    BG_SECONDARY = "#F1F5F9"  # Gris clair (fond secondaire)
    BG_TERTIARY = "#E2E8F0"  # Gris (fond tertiaire)
    BG_ELEVATED = "#FFFFFF"  # Blanc (éléments surélevés)
    BG_HOVER = "#F8FAFC"  # Hover très subtil

    # ============================================================
    # COULEURS DE TEXTE
    # ============================================================

    TEXT_PRIMARY = "#0F172A"  # Slate 900 (titres)
    TEXT_SECONDARY = "#475569"  # Slate 600 (sous-titres)
    TEXT_MUTED = "#64748B"  # Slate 500 (texte hint)
    TEXT_DISABLED = "#94A3B8"  # Slate 400 (désactivé)
    TEXT_ON_PRIMARY = "#FFFFFF"  # Blanc sur fond primary

    # ============================================================
    # COULEURS DE BORDURE
    # ============================================================

    BORDER = "#E2E8F0"  # Gris clair (bordures standard)
    BORDER_LIGHT = "#F1F5F9"  # Gris très clair (bordures subtiles)
    BORDER_FOCUS = "#10B981"  # Vert (bordure focus)
    BORDER_SIDEBAR = "#E2E8F0"  # Bordure sidebar

    # ============================================================
    # NUANCES DE GRIS
    # ============================================================

    SLATE_50 = "#F8FAFC"
    SLATE_100 = "#F1F5F9"
    SLATE_200 = "#E2E8F0"
    SLATE_300 = "#CBD5E1"
    SLATE_400 = "#94A3B8"
    SLATE_500 = "#64748B"
    SLATE_600 = "#475569"
    SLATE_700 = "#334155"
    SLATE_800 = "#1E293B"
    SLATE_900 = "#0F172A"


class ThemeV5:
    """Thème complet V5.6 - Light Mode FinCouple."""

    def __init__(self):
        self.colors = LightColors
        self.spacing = Spacing
        self.typography = Typography
        self.radius = BorderRadius
        self.shadow = Shadow

    def apply(self):
        """Applique le thème light mode à l'application."""
        st.markdown(get_light_theme_css(), unsafe_allow_html=True)


def apply_light_theme():
    """Applique le thème light mode V5.6 FinCouple."""
    theme = ThemeV5()
    theme.apply()


def get_light_theme_css() -> str:
    """Génère le CSS complet pour le thème FinCouple."""
    c = LightColors
    
    return f"""
    <style>
    /* ========================================
       FINCUPLE V5.6 - LIGHT THEME
       ======================================== */
    
    /* Import des polices */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Variables CSS globales */
    :root {{
        --fc-primary: {c.PRIMARY};
        --fc-primary-light: {c.PRIMARY_LIGHT};
        --fc-primary-dark: {c.PRIMARY_DARK};
        --fc-success: {c.SUCCESS};
        --fc-danger: {c.DANGER};
        --fc-warning: {c.WARNING};
        --fc-info: {c.INFO};
        
        --fc-bg-page: {c.BG_PAGE};
        --fc-bg-sidebar: {c.BG_SIDEBAR};
        --fc-bg-card: {c.BG_CARD};
        
        --fc-text-primary: {c.TEXT_PRIMARY};
        --fc-text-secondary: {c.TEXT_SECONDARY};
        --fc-text-muted: {c.TEXT_MUTED};
        
        --fc-border: {c.BORDER};
        --fc-border-light: {c.BORDER_LIGHT};
        
        --fc-font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    /* ========================================
       BASE
       ======================================== */
    
    .stApp {{
        background-color: var(--fc-bg-page) !important;
        font-family: var(--fc-font) !important;
    }}
    
    /* ========================================
       SIDEBAR (Style FinCouple)
       ======================================== */
    
    [data-testid="stSidebar"] {{
        background-color: var(--fc-bg-sidebar) !important;
        border-right: 1px solid var(--fc-border) !important;
    }}
    
    [data-testid="stSidebar"] .stMarkdown {{
        color: var(--fc-text-secondary) !important;
    }}
    
    /* Logo area */
    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 1rem !important;
    }}
    
    /* ========================================
       NAVIGATION (Sidebar items)
       ======================================== */
    
    /* Navigation items */
    .stSidebar .stButton > button {{
        background: transparent !important;
        border: none !important;
        color: var(--fc-text-secondary) !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        padding: 0.625rem 1rem !important;
        border-radius: 8px !important;
        text-align: left !important;
        width: 100% !important;
        transition: all 0.15s ease !important;
    }}
    
    .stSidebar .stButton > button:hover {{
        background: {c.BG_HOVER} !important;
        color: var(--fc-text-primary) !important;
    }}
    
    .stSidebar .stButton > button[data-active="true"],
    .stSidebar .stButton > button[aria-current="page"] {{
        background: {c.BG_SECONDARY} !important;
        color: var(--fc-text-primary) !important;
        font-weight: 600 !important;
    }}
    
    /* ========================================
       HEADERS
       ======================================== */
    
    h1 {{
        font-family: var(--fc-font) !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: var(--fc-text-primary) !important;
        letter-spacing: -0.025em !important;
        margin-bottom: 0.5rem !important;
    }}
    
    h2 {{
        font-family: var(--fc-font) !important;
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        color: var(--fc-text-primary) !important;
        letter-spacing: -0.025em !important;
    }}
    
    h3 {{
        font-family: var(--fc-font) !important;
        font-size: 1.125rem !important;
        font-weight: 600 !important;
        color: var(--fc-text-primary) !important;
    }}
    
    /* ========================================
       CARDS (Style FinCouple)
       ======================================== */
    
    /* Cards principales */
    .stContainer, div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {{
        background: var(--fc-bg-card) !important;
        border-radius: 12px !important;
        border: 1px solid var(--fc-border) !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
        padding: 1.5rem !important;
    }}
    
    /* ========================================
       BOUTONS
       ======================================== */
    
    /* Bouton primaire - Vert émeraude */
    .stButton > button[data-testid="baseButton-primary"] {{
        background: var(--fc-primary) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        transition: all 0.15s ease !important;
    }}
    
    .stButton > button[data-testid="baseButton-primary"]:hover {{
        background: var(--fc-primary-dark) !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25) !important;
    }}
    
    /* Bouton secondaire - Bordure */
    .stButton > button[data-testid="baseButton-secondary"] {{
        background: white !important;
        color: var(--fc-text-secondary) !important;
        border: 1px solid var(--fc-border) !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        transition: all 0.15s ease !important;
    }}
    
    .stButton > button[data-testid="baseButton-secondary"]:hover {{
        background: {c.BG_HOVER} !important;
        border-color: var(--fc-text-muted) !important;
    }}
    
    /* ========================================
       TABS (Style pills FinCouple)
       ======================================== */
    
    .stTabs [data-baseweb="tab-list"] {{
        background: {c.BG_SECONDARY} !important;
        border-radius: 8px !important;
        padding: 4px !important;
        gap: 4px !important;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: transparent !important;
        color: var(--fc-text-secondary) !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
    }}
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        background: white !important;
        color: var(--fc-text-primary) !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
    }}
    
    /* ========================================
       TABLEAUX (Style FinCouple)
       ======================================== */
    
    .stDataFrame {{
        border: 1px solid var(--fc-border) !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }}
    
    .stDataFrame thead tr {{
        background: {c.BG_SECONDARY} !important;
    }}
    
    .stDataFrame th {{
        background: transparent !important;
        color: var(--fc-text-secondary) !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        padding: 0.75rem 1rem !important;
        border-bottom: 1px solid var(--fc-border) !important;
    }}
    
    .stDataFrame td {{
        color: var(--fc-text-primary) !important;
        font-size: 0.875rem !important;
        padding: 0.875rem 1rem !important;
        border-bottom: 1px solid var(--fc-border-light) !important;
    }}
    
    .stDataFrame tr:last-child td {{
        border-bottom: none !important;
    }}
    
    .stDataFrame tr:hover td {{
        background: {c.BG_HOVER} !important;
    }}
    
    /* ========================================
       INPUTS
       ======================================== */
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {{
        background-color: white !important;
        border: 1px solid var(--fc-border) !important;
        border-radius: 8px !important;
        color: var(--fc-text-primary) !important;
        padding: 0.625rem 0.875rem !important;
        font-size: 0.875rem !important;
    }}
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {{
        border-color: var(--fc-primary) !important;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1) !important;
    }}
    
    /* ========================================
       METRICS (KPIs)
       ======================================== */
    
    [data-testid="stMetric"] {{
        background-color: var(--fc-bg-card) !important;
        border: 1px solid var(--fc-border) !important;
        border-radius: 12px !important;
        padding: 1.25rem !important;
    }}
    
    [data-testid="stMetricLabel"] {{
        font-size: 0.875rem !important;
        color: var(--fc-text-secondary) !important;
        font-weight: 500 !important;
    }}
    
    [data-testid="stMetricValue"] {{
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        color: var(--fc-text-primary) !important;
    }}
    
    /* ========================================
       ALERTES
       ======================================== */
    
    .stAlert {{
        border-radius: 8px !important;
        border: 1px solid !important;
        padding: 1rem !important;
    }}
    
    [data-testid="stAlertContainer-success"] {{
        background-color: {c.SUCCESS_BG} !important;
        border-color: {c.SUCCESS} !important;
        color: {c.SUCCESS_DARK} !important;
    }}
    
    [data-testid="stAlertContainer-error"] {{
        background-color: {c.DANGER_BG} !important;
        border-color: {c.DANGER} !important;
        color: {c.DANGER_DARK} !important;
    }}
    
    /* ========================================
       UTILITAIRES
       ======================================== */
    
    /* Card style */
    .fc-card {{
        background: var(--fc-bg-card);
        border: 1px solid var(--fc-border);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }}
    
    /* Header de page */
    .fc-page-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--fc-border);
    }}
    
    /* Badge */
    .fc-badge {{
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }}
    
    .fc-badge-primary {{
        background: {c.PRIMARY_BG};
        color: {c.PRIMARY_DARK};
    }}
    
    .fc-badge-secondary {{
        background: {c.SECONDARY_BG};
        color: {c.SECONDARY_DARK};
    }}
    
    /* Hide elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 6px !important;
        height: 6px !important;
    }}
    
    ::-webkit-scrollbar-track {{
        background: transparent !important;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {c.SLATE_300} !important;
        border-radius: 3px !important;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {c.SLATE_400} !important;
    }}
    
    </style>
    """


# Alias pour compatibilité
Colors = LightColors
