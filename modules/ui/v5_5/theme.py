"""Thème Light Mode V5.5 - Design System FinCouple.

Palette de couleurs et styles pour la nouvelle interface light mode,
inspirée des maquettes Figma.

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
    """Palette de couleurs Light Mode - Maquette V5.5.

    Couleurs principales:
    - Primary: Emerald (#10B981) - vert émeraude comme dans la maquette
    - Background: Gris très clair (#F9FAFB) - fond de page
    - Cards: Blanc pur (#FFFFFF) - fond des cartes
    - Text: Gris foncé (#1F2937) - texte principal
    """

    # ============================================================
    # COULEURS PRINCIPALES
    # ============================================================

    # Primary - Emerald (comme dans la maquette)
    PRIMARY = "#10B981"  # Vert émeraude
    PRIMARY_LIGHT = "#34D399"  # Vert clair
    PRIMARY_DARK = "#059669"  # Vert foncé
    PRIMARY_BG = "#D1FAE5"  # Vert très clair (fond icônes)

    # Secondary - Indigo (pour variante)
    SECONDARY = "#6366F1"
    SECONDARY_LIGHT = "#818CF8"
    SECONDARY_DARK = "#4F46E5"
    SECONDARY_BG = "#E0E7FF"

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
    # COULEURS DE FOND
    # ============================================================

    BG_PAGE = "#F9FAFB"  # Gris très clair (fond page)
    BG_CARD = "#FFFFFF"  # Blanc pur (fond cartes)
    BG_SECONDARY = "#F3F4F6"  # Gris clair (fond secondaire)
    BG_TERTIARY = "#E5E7EB"  # Gris (fond tertiaire)
    BG_ELEVATED = "#FFFFFF"  # Blanc (éléments surélevés)

    # ============================================================
    # COULEURS DE TEXTE
    # ============================================================

    TEXT_PRIMARY = "#1F2937"  # Gris foncé (titres)
    TEXT_SECONDARY = "#6B7280"  # Gris moyen (sous-titres)
    TEXT_MUTED = "#9CA3AF"  # Gris clair (texte hint)
    TEXT_DISABLED = "#D1D5DB"  # Gris très clair (désactivé)

    # ============================================================
    # COULEURS DE BORDURE
    # ============================================================

    BORDER = "#E5E7EB"  # Gris clair (bordures standard)
    BORDER_LIGHT = "#F3F4F6"  # Gris très clair (bordures subtiles)
    BORDER_FOCUS = "#10B981"  # Vert (bordure focus)

    # ============================================================
    # NUANCES DE GRIS (pour compatibilité)
    # ============================================================

    GRAY_50 = "#F9FAFB"
    GRAY_100 = "#F3F4F6"
    GRAY_200 = "#E5E7EB"
    GRAY_300 = "#D1D5DB"
    GRAY_400 = "#9CA3AF"
    GRAY_500 = "#6B7280"
    GRAY_600 = "#4B5563"
    GRAY_700 = "#374151"
    GRAY_800 = "#1F2937"
    GRAY_900 = "#111827"


class ThemeV5:
    """Thème complet V5.5 - Light Mode.

    Classe principale qui regroupe tous les tokens de design
    pour la nouvelle interface.

    Usage:
        theme = ThemeV5()
        bg_color = theme.colors.BG_PAGE
        padding = theme.spacing.MD
    """

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
    """Applique le thème light mode V5.5.

    Fonction utilitaire rapide pour appliquer le thème.

    Usage:
        import streamlit as st
        from modules.ui.v5_5 import apply_light_theme

        st.set_page_config(page_title="FinancePerso", layout="wide")
        apply_light_theme()
    """
    theme = ThemeV5()
    theme.apply()


def get_light_theme_css() -> str:
    """Génère le CSS complet pour le thème light mode.

    Returns:
        Chaîne CSS à injecter dans Streamlit
    """
    return f"""
    <style>
    /* ========================================
       FINANCEPERSO V5.5 - LIGHT THEME
       ======================================== */
    
    /* Import des polices */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Variables CSS globales */
    :root {{
        /* Primary */
        --v5-primary: {LightColors.PRIMARY};
        --v5-primary-light: {LightColors.PRIMARY_LIGHT};
        --v5-primary-dark: {LightColors.PRIMARY_DARK};
        --v5-primary-bg: {LightColors.PRIMARY_BG};
        
        /* Semantic */
        --v5-success: {LightColors.SUCCESS};
        --v5-success-bg: {LightColors.SUCCESS_BG};
        --v5-danger: {LightColors.DANGER};
        --v5-danger-bg: {LightColors.DANGER_BG};
        --v5-warning: {LightColors.WARNING};
        --v5-warning-bg: {LightColors.WARNING_BG};
        --v5-info: {LightColors.INFO};
        --v5-info-bg: {LightColors.INFO_BG};
        
        /* Backgrounds */
        --v5-bg-page: {LightColors.BG_PAGE};
        --v5-bg-card: {LightColors.BG_CARD};
        --v5-bg-secondary: {LightColors.BG_SECONDARY};
        --v5-bg-tertiary: {LightColors.BG_TERTIARY};
        
        /* Text */
        --v5-text-primary: {LightColors.TEXT_PRIMARY};
        --v5-text-secondary: {LightColors.TEXT_SECONDARY};
        --v5-text-muted: {LightColors.TEXT_MUTED};
        --v5-text-disabled: {LightColors.TEXT_DISABLED};
        
        /* Borders */
        --v5-border: {LightColors.BORDER};
        --v5-border-light: {LightColors.BORDER_LIGHT};
        --v5-border-focus: {LightColors.BORDER_FOCUS};
        
        /* Typography */
        --v5-font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        
        /* Espacements */
        --v5-spacing-xs: {Spacing.XS};
        --v5-spacing-sm: {Spacing.SM};
        --v5-spacing-md: {Spacing.MD};
        --v5-spacing-lg: {Spacing.LG};
        --v5-spacing-xl: {Spacing.XL};
    }}
    
    /* ========================================
       RESET & BASE
       ======================================== */
    
    .stApp {{
        background-color: var(--v5-bg-page) !important;
        font-family: var(--v5-font-family) !important;
    }}
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        font-family: var(--v5-font-family) !important;
        font-weight: 600 !important;
        color: var(--v5-text-primary) !important;
        letter-spacing: -0.025em !important;
    }}
    
    h1 {{
        font-size: 2rem !important;
        margin-bottom: 0.5rem !important;
    }}
    
    h2 {{
        font-size: 1.5rem !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
    }}
    
    h3 {{
        font-size: 1.25rem !important;
        color: var(--v5-text-primary) !important;
    }}
    
    /* Texte */
    p, span, div {{
        color: var(--v5-text-primary) !important;
    }}
    
    /* ========================================
       BOUTONS
       ======================================== */
    
    /* Bouton primaire - style maquette (fond foncé) */
    .stButton > button[data-testid="baseButton-primary"] {{
        background: #111827 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        transition: all 0.2s ease !important;
    }}
    
    .stButton > button[data-testid="baseButton-primary"]:hover {{
        background: #1F2937 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }}
    
    /* Bouton secondaire - style maquette (bordure) */
    .stButton > button[data-testid="baseButton-secondary"] {{
        background: white !important;
        color: #374151 !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        transition: all 0.2s ease !important;
    }}
    
    .stButton > button[data-testid="baseButton-secondary"]:hover {{
        background: #F9FAFB !important;
        border-color: #D1D5DB !important;
    }}
    
    /* ========================================
       INPUTS & FORMULAIRES
       ======================================== */
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div,
    .stDateInput > div > div > input {{
        background-color: white !important;
        border: 1px solid var(--v5-border) !important;
        border-radius: 8px !important;
        color: var(--v5-text-primary) !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.875rem !important;
        transition: all 0.2s ease !important;
    }}
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus {{
        border-color: var(--v5-primary) !important;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1) !important;
        outline: none !important;
    }}
    
    /* Labels */
    .stTextInput > label,
    .stNumberInput > label,
    .stSelectbox > label {{
        color: var(--v5-text-secondary) !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
    }}
    
    /* ========================================
       SIDEBAR
       ======================================== */
    
    [data-testid="stSidebar"] {{
        background-color: var(--v5-bg-card) !important;
        border-right: 1px solid var(--v5-border) !important;
    }}
    
    [data-testid="stSidebar"] .stMarkdown {{
        color: var(--v5-text-secondary) !important;
    }}
    
    /* ========================================
       MÉTRIQUES (KPIs)
       ======================================== */
    
    [data-testid="stMetric"] {{
        background-color: var(--v5-bg-card) !important;
        border: 1px solid var(--v5-border) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
    }}
    
    [data-testid="stMetricValue"] {{
        font-size: 1.875rem !important;
        font-weight: 700 !important;
        color: var(--v5-text-primary) !important;
    }}
    
    [data-testid="stMetricLabel"] {{
        font-size: 0.875rem !important;
        color: var(--v5-text-secondary) !important;
    }}
    
    /* ========================================
       DATAFRAMES & TABLEAUX
       ======================================== */
    
    .stDataFrame {{
        border-radius: 8px !important;
        overflow: hidden !important;
        border: 1px solid var(--v5-border) !important;
    }}
    
    .stDataFrame th {{
        background-color: var(--v5-bg-secondary) !important;
        color: var(--v5-text-primary) !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        padding: 1rem !important;
    }}
    
    .stDataFrame td {{
        color: var(--v5-text-secondary) !important;
        border-bottom: 1px solid var(--v5-border) !important;
        padding: 0.875rem 1rem !important;
    }}
    
    /* ========================================
       ALERTES
       ======================================== */
    
    .stAlert {{
        border-radius: 8px !important;
        border: 1px solid !important;
        padding: 1rem 1.25rem !important;
    }}
    
    /* Success */
    [data-testid="stAlertContainer-success"] {{
        background-color: {LightColors.SUCCESS_BG} !important;
        border-color: {LightColors.SUCCESS} !important;
        color: {LightColors.SUCCESS_DARK} !important;
    }}
    
    /* Error */
    [data-testid="stAlertContainer-error"] {{
        background-color: {LightColors.DANGER_BG} !important;
        border-color: {LightColors.DANGER} !important;
        color: {LightColors.DANGER_DARK} !important;
    }}
    
    /* Warning */
    [data-testid="stAlertContainer-warning"] {{
        background-color: {LightColors.WARNING_BG} !important;
        border-color: {LightColors.WARNING} !important;
        color: {LightColors.WARNING_DARK} !important;
    }}
    
    /* Info */
    [data-testid="stAlertContainer-info"] {{
        background-color: {LightColors.INFO_BG} !important;
        border-color: {LightColors.INFO} !important;
        color: {LightColors.INFO_DARK} !important;
    }}
    
    /* ========================================
       SCROLLBAR
       ======================================== */
    
    ::-webkit-scrollbar {{
        width: 8px !important;
        height: 8px !important;
    }}
    
    ::-webkit-scrollbar-track {{
        background: var(--v5-bg-secondary) !important;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: var(--v5-border) !important;
        border-radius: 4px !important;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--v5-text-muted) !important;
    }}
    
    /* ========================================
       UTILITAIRES V5.5
       ======================================== */
    
    /* Card style maquette */
    .v5-card {{
        background: var(--v5-bg-card);
        border: 1px solid var(--v5-border);
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease;
    }}
    
    .v5-card:hover {{
        border-color: var(--v5-primary);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.08);
        transform: translateY(-2px);
    }}
    
    /* Icône dans cercle */
    .v5-icon-circle {{
        width: 80px;
        height: 80px;
        background: var(--v5-primary-bg);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
    }}
    
    /* Texte gradient */
    .v5-gradient-text {{
        background: linear-gradient(135deg, var(--v5-primary) 0%, var(--v5-primary-light) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    /* Hide default Streamlit elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    </style>
    """


# Alias pour compatibilité
Colors = LightColors
