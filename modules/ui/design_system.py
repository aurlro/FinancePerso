"""
Design System Vibe - UI Premium pour FinancePerso
=================================================

Module d'injection CSS/JS personnalisé pour transformer l'UI Streamlit
en une expérience premium avec :
- Design System cohérent (Dark Mode optimisé)
- Micro-animations fluides
- Composants personnalisés
- Responsive mobile

Usage:
    from modules.ui.design_system import DesignSystem, apply_vibe_theme
    
    design = DesignSystem()
    design.apply_theme()  # Applique le thème complet
"""

from dataclasses import dataclass
from enum import Enum

import streamlit as st


class ColorScheme(Enum):
    """Palette de couleurs du Design System."""
    # Couleurs principales
    PRIMARY = "#6366F1"           # Indigo 500
    PRIMARY_LIGHT = "#818CF8"     # Indigo 400
    PRIMARY_DARK = "#4F46E5"      # Indigo 600
    
    # Couleurs secondaires
    SECONDARY = "#10B981"         # Emerald 500
    ACCENT = "#F59E0B"            # Amber 500
    DANGER = "#EF4444"            # Red 500
    WARNING = "#F59E0B"           # Amber 500
    INFO = "#3B82F6"              # Blue 500
    
    # Couleurs de fond (Dark Mode)
    BG_PRIMARY = "#0F172A"        # Slate 900
    BG_SECONDARY = "#1E293B"      # Slate 800
    BG_TERTIARY = "#334155"       # Slate 700
    BG_ELEVATED = "#1E293B"       # Slate 800 avec ombre
    
    # Couleurs de texte
    TEXT_PRIMARY = "#F8FAFC"      # Slate 50
    TEXT_SECONDARY = "#94A3B8"    # Slate 400
    TEXT_MUTED = "#64748B"        # Slate 500
    
    # Bordures
    BORDER = "#334155"            # Slate 700
    BORDER_LIGHT = "#475569"      # Slate 600
    
    # Élévations
    SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.3)"
    SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.4)"
    SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.5)"
    SHADOW_GLOW = "0 0 20px rgba(99, 102, 241, 0.3)"


@dataclass
class Typography:
    """Configuration typographique."""
    FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    FONT_MONO = "'JetBrains Mono', 'Fira Code', monospace"
    
    # Tailles
    SIZE_XS = "0.75rem"      # 12px
    SIZE_SM = "0.875rem"     # 14px
    SIZE_BASE = "1rem"       # 16px
    SIZE_LG = "1.125rem"     # 18px
    SIZE_XL = "1.25rem"      # 20px
    SIZE_2XL = "1.5rem"      # 24px
    SIZE_3XL = "1.875rem"    # 30px
    SIZE_4XL = "2.25rem"     # 36px
    
    # Poids
    WEIGHT_NORMAL = 400
    WEIGHT_MEDIUM = 500
    WEIGHT_SEMIBOLD = 600
    WEIGHT_BOLD = 700


@dataclass
class Spacing:
    """Espacements du Design System."""
    XS = "0.25rem"   # 4px
    SM = "0.5rem"    # 8px
    MD = "1rem"      # 16px
    LG = "1.5rem"    # 24px
    XL = "2rem"      # 32px
    XXL = "3rem"     # 48px


@dataclass
class Animation:
    """Configuration des animations."""
    DURATION_FAST = "150ms"
    DURATION_NORMAL = "300ms"
    DURATION_SLOW = "500ms"
    
    EASE_DEFAULT = "cubic-bezier(0.4, 0, 0.2, 1)"
    EASE_IN = "cubic-bezier(0.4, 0, 1, 1)"
    EASE_OUT = "cubic-bezier(0, 0, 0.2, 1)"
    EASE_BOUNCE = "cubic-bezier(0.68, -0.55, 0.265, 1.55)"


class DesignSystem:
    """
    Système de design complet pour FinancePerso.
    
    Cette classe génère et injecte du CSS/JS personnalisé dans Streamlit
    pour créer une expérience UI premium et cohérente.
    """
    
    def __init__(self):
        self.colors = ColorScheme
        self.typography = Typography()
        self.spacing = Spacing()
        self.animation = Animation()
        self._css_applied = False
    
    def get_css(self) -> str:
        """
        Génère le CSS complet du Design System.
        
        Returns:
            Chaîne CSS à injecter dans Streamlit
        """
        css = f"""
        <style>
        /* ========================================
           FINANCEPERSO DESIGN SYSTEM - VIBE THEME
           ======================================== */
        
        /* Import des polices */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
        
        /* Variables CSS globales */
        :root {{
            /* Couleurs */
            --fp-primary: {self.colors.PRIMARY.value};
            --fp-primary-light: {self.colors.PRIMARY_LIGHT.value};
            --fp-primary-dark: {self.colors.PRIMARY_DARK.value};
            --fp-secondary: {self.colors.SECONDARY.value};
            --fp-accent: {self.colors.ACCENT.value};
            --fp-danger: {self.colors.DANGER.value};
            --fp-warning: {self.colors.WARNING.value};
            --fp-info: {self.colors.INFO.value};
            
            /* Fonds */
            --fp-bg-primary: {self.colors.BG_PRIMARY.value};
            --fp-bg-secondary: {self.colors.BG_SECONDARY.value};
            --fp-bg-tertiary: {self.colors.BG_TERTIARY.value};
            --fp-bg-elevated: {self.colors.BG_ELEVATED.value};
            
            /* Texte */
            --fp-text-primary: {self.colors.TEXT_PRIMARY.value};
            --fp-text-secondary: {self.colors.TEXT_SECONDARY.value};
            --fp-text-muted: {self.colors.TEXT_MUTED.value};
            
            /* Bordures */
            --fp-border: {self.colors.BORDER.value};
            --fp-border-light: {self.colors.BORDER_LIGHT.value};
            
            /* Ombres */
            --fp-shadow-sm: {self.colors.SHADOW_SM.value};
            --fp-shadow-md: {self.colors.SHADOW_MD.value};
            --fp-shadow-lg: {self.colors.SHADOW_LG.value};
            --fp-shadow-glow: {self.colors.SHADOW_GLOW.value};
            
            /* Typographie */
            --fp-font-family: {self.typography.FONT_FAMILY};
            --fp-font-mono: {self.typography.FONT_MONO};
            
            /* Espacements */
            --fp-spacing-xs: {self.spacing.XS};
            --fp-spacing-sm: {self.spacing.SM};
            --fp-spacing-md: {self.spacing.MD};
            --fp-spacing-lg: {self.spacing.LG};
            --fp-spacing-xl: {self.spacing.XL};
            
            /* Animations */
            --fp-duration-fast: {self.animation.DURATION_FAST};
            --fp-duration-normal: {self.animation.DURATION_NORMAL};
            --fp-duration-slow: {self.animation.DURATION_SLOW};
            --fp-ease-default: {self.animation.EASE_DEFAULT};
            --fp-ease-bounce: {self.animation.EASE_BOUNCE};
        }}
        
        /* ========================================
           RESET & BASE
           ======================================== */
        
        .stApp {{
            background-color: var(--fp-bg-primary) !important;
            font-family: var(--fp-font-family) !important;
            color: var(--fp-text-primary) !important;
        }}
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {{
            font-family: var(--fp-font-family) !important;
            font-weight: 600 !important;
            color: var(--fp-text-primary) !important;
            letter-spacing: -0.025em !important;
        }}
        
        h1 {{
            font-size: 2.25rem !important;
            margin-bottom: 1.5rem !important;
            background: linear-gradient(135deg, var(--fp-text-primary) 0%, var(--fp-primary-light) 100%);
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            background-clip: text !important;
        }}
        
        h2 {{
            font-size: 1.5rem !important;
            margin-top: 2rem !important;
            margin-bottom: 1rem !important;
            border-bottom: 2px solid var(--fp-border);
            padding-bottom: 0.5rem;
        }}
        
        h3 {{
            font-size: 1.25rem !important;
            color: var(--fp-primary-light) !important;
        }}
        
        /* Texte */
        p, span, div {{
            color: var(--fp-text-primary) !important;
        }}
        
        .stMarkdown {{
            color: var(--fp-text-secondary) !important;
        }}
        
        /* ========================================
           COMPOSANTS - CARTES
           ======================================== */
        
        /* Conteneurs principaux */
        .stContainer, .stForm, [data-testid="stVerticalBlock"] {{
            background-color: var(--fp-bg-secondary) !important;
            border-radius: 12px !important;
            border: 1px solid var(--fp-border) !important;
            padding: var(--fp-spacing-lg) !important;
            box-shadow: var(--fp-shadow-md) !important;
            transition: all var(--fp-duration-normal) var(--fp-ease-default) !important;
        }}
        
        .stContainer:hover {{
            box-shadow: var(--fp-shadow-lg) !important;
            border-color: var(--fp-border-light) !important;
            transform: translateY(-2px);
        }}
        
        /* Métriques (KPIs) */
        [data-testid="stMetricValue"] {{
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: var(--fp-text-primary) !important;
            font-family: var(--fp-font-mono) !important;
        }}
        
        [data-testid="stMetricLabel"] {{
            font-size: 0.875rem !important;
            color: var(--fp-text-secondary) !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }}
        
        [data-testid="stMetricDelta"] {{
            font-size: 0.875rem !important;
            font-weight: 600 !important;
        }}
        
        /* Delta positif/négatif */
        [data-testid="stMetricDelta"] svg[data-testid="stMetricDeltaIcon-Up"] {{
            color: var(--fp-secondary) !important;
        }}
        
        [data-testid="stMetricDelta"] svg[data-testid="stMetricDeltaIcon-Down"] {{
            color: var(--fp-danger) !important;
        }}
        
        /* ========================================
           BOUTONS
           ======================================== */
        
        .stButton > button {{
            background: linear-gradient(135deg, var(--fp-primary) 0%, var(--fp-primary-dark) 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 600 !important;
            font-size: 0.875rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
            box-shadow: var(--fp-shadow-md) !important;
            transition: all var(--fp-duration-fast) var(--fp-ease-default) !important;
            position: relative !important;
            overflow: hidden !important;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: var(--fp-shadow-glow) !important;
        }}
        
        .stButton > button:active {{
            transform: translateY(0) !important;
        }}
        
        /* Effet ripple au clic */
        .stButton > button::after {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }}
        
        .stButton > button:active::after {{
            width: 300px;
            height: 300px;
        }}
        
        /* Bouton secondaire */
        .stButton > button[kind="secondary"] {{
            background: var(--fp-bg-tertiary) !important;
            color: var(--fp-text-primary) !important;
            border: 1px solid var(--fp-border) !important;
        }}
        
        /* ========================================
           INPUTS & FORMULAIRES
           ======================================== */
        
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > div,
        .stDateInput > div > div > input {{
            background-color: var(--fp-bg-tertiary) !important;
            border: 1px solid var(--fp-border) !important;
            border-radius: 8px !important;
            color: var(--fp-text-primary) !important;
            padding: 0.75rem 1rem !important;
            font-size: 0.875rem !important;
            transition: all var(--fp-duration-fast) var(--fp-ease-default) !important;
        }}
        
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stSelectbox > div > div > div:focus {{
            border-color: var(--fp-primary) !important;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
            outline: none !important;
        }}
        
        /* Labels */
        .stTextInput > label,
        .stNumberInput > label,
        .stSelectbox > label,
        .stDateInput > label {{
            color: var(--fp-text-secondary) !important;
            font-size: 0.875rem !important;
            font-weight: 500 !important;
            margin-bottom: 0.5rem !important;
        }}
        
        /* ========================================
           ONGLETS (Tabs)
           ======================================== */
        
        .stTabs [data-baseweb="tab-list"] {{
            background-color: var(--fp-bg-secondary) !important;
            border-radius: 8px !important;
            padding: 0.25rem !important;
            gap: 0.25rem !important;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: transparent !important;
            color: var(--fp-text-secondary) !important;
            border-radius: 6px !important;
            padding: 0.75rem 1.25rem !important;
            font-weight: 500 !important;
            transition: all var(--fp-duration-fast) var(--fp-ease-default) !important;
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            background-color: var(--fp-bg-tertiary) !important;
            color: var(--fp-text-primary) !important;
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: var(--fp-primary) !important;
            color: white !important;
            box-shadow: var(--fp-shadow-sm) !important;
        }}
        
        /* ========================================
           SIDEBAR
           ======================================== */
        
        .css-1cypcdb {{  /* Sélecteur de la sidebar */
            background-color: var(--fp-bg-secondary) !important;
            border-right: 1px solid var(--fp-border) !important;
        }}
        
        .sidebar .sidebar-content {{
            background-color: var(--fp-bg-secondary) !important;
        }}
        
        /* ========================================
           DATAFRAMES & TABLEAUX
           ======================================== */
        
        .stDataFrame {{
            border-radius: 8px !important;
            overflow: hidden !important;
        }}
        
        .stDataFrame [data-testid="stTable"] {{
            background-color: var(--fp-bg-secondary) !important;
        }}
        
        .stDataFrame th {{
            background-color: var(--fp-bg-tertiary) !important;
            color: var(--fp-text-primary) !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            font-size: 0.75rem !important;
            letter-spacing: 0.05em !important;
            padding: 1rem !important;
        }}
        
        .stDataFrame td {{
            color: var(--fp-text-secondary) !important;
            border-bottom: 1px solid var(--fp-border) !important;
            padding: 0.875rem 1rem !important;
        }}
        
        .stDataFrame tr:hover td {{
            background-color: var(--fp-bg-tertiary) !important;
            color: var(--fp-text-primary) !important;
        }}
        
        /* ========================================
           ALERTES & NOTIFICATIONS
           ======================================== */
        
        .stAlert {{
            border-radius: 8px !important;
            border: 1px solid !important;
            padding: 1rem 1.25rem !important;
        }}
        
        .stAlert [data-baseweb="notification"] {{
            background-color: transparent !important;
        }}
        
        /* Success */
        .element-container:has(.stAlert) [data-testid="stAlertContainer-success"] {{
            background-color: rgba(16, 185, 129, 0.1) !important;
            border-color: var(--fp-secondary) !important;
            color: var(--fp-secondary) !important;
        }}
        
        /* Error */
        .element-container:has(.stAlert) [data-testid="stAlertContainer-error"] {{
            background-color: rgba(239, 68, 68, 0.1) !important;
            border-color: var(--fp-danger) !important;
            color: var(--fp-danger) !important;
        }}
        
        /* Warning */
        .element-container:has(.stAlert) [data-testid="stAlertContainer-warning"] {{
            background-color: rgba(245, 158, 11, 0.1) !important;
            border-color: var(--fp-warning) !important;
            color: var(--fp-warning) !important;
        }}
        
        /* Info */
        .element-container:has(.stAlert) [data-testid="stAlertContainer-info"] {{
            background-color: rgba(59, 130, 246, 0.1) !important;
            border-color: var(--fp-info) !important;
            color: var(--fp-info) !important;
        }}
        
        /* ========================================
           EXPANDER
           ======================================== */
        
        .streamlit-expanderHeader {{
            background-color: var(--fp-bg-secondary) !important;
            border: 1px solid var(--fp-border) !important;
            border-radius: 8px !important;
            padding: 1rem 1.25rem !important;
            font-weight: 600 !important;
            color: var(--fp-text-primary) !important;
            transition: all var(--fp-duration-fast) var(--fp-ease-default) !important;
        }}
        
        .streamlit-expanderHeader:hover {{
            background-color: var(--fp-bg-tertiary) !important;
            border-color: var(--fp-border-light) !important;
        }}
        
        .streamlit-expanderContent {{
            background-color: var(--fp-bg-secondary) !important;
            border: 1px solid var(--fp-border) !important;
            border-top: none !important;
            border-radius: 0 0 8px 8px !important;
            padding: 1.25rem !important;
        }}
        
        /* ========================================
           SPINNER & LOADING
           ======================================== */
        
        .stSpinner > div {{
            border-top-color: var(--fp-primary) !important;
            border-right-color: var(--fp-primary) !important;
            border-bottom-color: transparent !important;
            border-left-color: transparent !important;
        }}
        
        /* ========================================
           SCROLLBAR
           ======================================== */
        
        ::-webkit-scrollbar {{
            width: 8px !important;
            height: 8px !important;
        }}
        
        ::-webkit-scrollbar-track {{
            background: var(--fp-bg-secondary) !important;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: var(--fp-border) !important;
            border-radius: 4px !important;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--fp-border-light) !important;
        }}
        
        /* ========================================
           UTILITAIRES
           ======================================== */
        
        /* Gradient text */
        .gradient-text {{
            background: linear-gradient(135deg, var(--fp-primary-light) 0%, var(--fp-accent) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        /* Glassmorphism */
        .glass {{
            background: rgba(30, 41, 59, 0.7) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }}
        
        /* Glow effect */
        .glow {{
            box-shadow: var(--fp-shadow-glow) !important;
        }}
        
        /* Hide default Streamlit elements */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* Custom footer */
        .custom-footer {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 1rem;
            background-color: var(--fp-bg-secondary);
            border-top: 1px solid var(--fp-border);
            text-align: center;
            font-size: 0.75rem;
            color: var(--fp-text-muted);
            z-index: 999;
        }}
        
        </style>
        """
        return css
    
    def get_js(self) -> str:
        """
        Génère le JavaScript pour les animations.
        
        Returns:
            Chaîne JS à injecter
        """
        js = """
        <script>
        // Animations et interactions
        document.addEventListener('DOMContentLoaded', function() {
            
            // Animation d'entrée pour les métriques
            const metrics = document.querySelectorAll('[data-testid="stMetricValue"]');
            metrics.forEach((metric, index) => {
                metric.style.opacity = '0';
                metric.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    metric.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
                    metric.style.opacity = '1';
                    metric.style.transform = 'translateY(0)';
                }, index * 100);
            });
            
            // Effet hover sur les cartes
            const cards = document.querySelectorAll('.stContainer');
            cards.forEach(card => {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-4px)';
                });
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0)';
                });
            });
            
            // Compteur animé pour les nombres
            function animateValue(element, start, end, duration) {
                let startTimestamp = null;
                const step = (timestamp) => {
                    if (!startTimestamp) startTimestamp = timestamp;
                    const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                    const easeProgress = 1 - Math.pow(1 - progress, 3); // Ease out cubic
                    element.textContent = Math.floor(easeProgress * (end - start) + start).toLocaleString();
                    if (progress < 1) {
                        window.requestAnimationFrame(step);
                    }
                };
                window.requestAnimationFrame(step);
            }
            
            // Observer pour déclencher les animations
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }
                });
            });
            
            document.querySelectorAll('.stContainer').forEach(el => {
                el.style.opacity = '0';
                el.style.transform = 'translateY(20px)';
                el.style.transition = 'all 0.5s ease-out';
                observer.observe(el);
            });
        });
        </script>
        """
        return js
    
    def apply_theme(self):
        """Applique le thème complet (CSS + JS)."""
        if self._css_applied:
            return
        
        # Injecter le CSS
        st.markdown(self.get_css(), unsafe_allow_html=True)
        
        # Injecter le JS
        st.components.v1.html(self.get_js(), height=0)
        
        self._css_applied = True
    
    def create_card(self, title: str, content: str, icon: str = "📊") -> str:
        """
        Crée une carte HTML stylisée.
        
        Args:
            title: Titre de la carte
            content: Contenu HTML
            icon: Icône emoji
            
        Returns:
            HTML de la carte
        """
        return f"""
        <div style="
            background-color: {self.colors.BG_SECONDARY.value};
            border: 1px solid {self.colors.BORDER.value};
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: {self.colors.SHADOW_MD.value};
            transition: all 0.3s ease;
        " onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='{self.colors.SHADOW_LG.value}'" 
           onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='{self.colors.SHADOW_MD.value}'">
            <h4 style="
                margin: 0 0 1rem 0;
                color: {self.colors.TEXT_PRIMARY.value};
                font-size: 1.125rem;
                font-weight: 600;
            ">{icon} {title}</h4>
            <div style="color: {self.colors.TEXT_SECONDARY.value};">
                {content}
            </div>
        </div>
        """
    
    def create_metric_card(self, label: str, value: str, delta: str | None = None, 
                          delta_positive: bool = True) -> str:
        """
        Crée une carte de métrique stylisée.
        
        Args:
            label: Label de la métrique
            value: Valeur à afficher
            delta: Variation (optionnel)
            delta_positive: Si la variation est positive
            
        Returns:
            HTML de la carte
        """
        delta_color = self.colors.SECONDARY.value if delta_positive else self.colors.DANGER.value
        delta_html = ""
        if delta:
            arrow = "↑" if delta_positive else "↓"
            delta_html = f'<div style="color: {delta_color}; font-size: 0.875rem; font-weight: 600; margin-top: 0.5rem;">{arrow} {delta}</div>'
        
        return f"""
        <div style="
            background: linear-gradient(135deg, {self.colors.BG_SECONDARY.value} 0%, {self.colors.BG_TERTIARY.value} 100%);
            border: 1px solid {self.colors.BORDER.value};
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
        ">
            <div style="
                font-size: 0.875rem;
                color: {self.colors.TEXT_SECONDARY.value};
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 0.5rem;
            ">{label}</div>
            <div style="
                font-size: 2rem;
                font-weight: 700;
                color: {self.colors.TEXT_PRIMARY.value};
                font-family: {self.typography.FONT_MONO};
            ">{value}</div>
            {delta_html}
        </div>
        """
    
    def create_badge(self, text: str, color: str = "primary") -> str:
        """
        Crée un badge stylisé.
        
        Args:
            text: Texte du badge
            color: Couleur (primary, secondary, success, danger, warning)
            
        Returns:
            HTML du badge
        """
        colors = {
            "primary": (self.colors.PRIMARY.value, "rgba(99, 102, 241, 0.2)"),
            "secondary": (self.colors.SECONDARY.value, "rgba(16, 185, 129, 0.2)"),
            "success": (self.colors.SECONDARY.value, "rgba(16, 185, 129, 0.2)"),
            "danger": (self.colors.DANGER.value, "rgba(239, 68, 68, 0.2)"),
            "warning": (self.colors.WARNING.value, "rgba(245, 158, 11, 0.2)"),
            "info": (self.colors.INFO.value, "rgba(59, 130, 246, 0.2)"),
        }
        
        text_color, bg_color = colors.get(color, colors["primary"])
        
        return f"""
        <span style="
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: {text_color};
            background-color: {bg_color};
            border: 1px solid {text_color};
        ">{text}</span>
        """


# Fonction d'aide pour appliquer rapidement le thème
def apply_vibe_theme():
    """Applique le thème Vibe à l'application Streamlit."""
    design = DesignSystem()
    design.apply_theme()


# Composants réutilisables
def vibe_container(title: str, content_func, icon: str = "📊"):
    """
    Crée un conteneur avec le style Vibe.
    
    Args:
        title: Titre du conteneur
        content_func: Fonction qui rend le contenu
        icon: Icône emoji
    """
    design = DesignSystem()
    
    st.markdown(design.create_card(title, "", icon), unsafe_allow_html=True)
    content_func()


def vibe_metric(label: str, value: str, delta: str | None = None, 
                delta_positive: bool = True):
    """
    Affiche une métrique avec le style Vibe.
    
    Args:
        label: Label de la métrique
        value: Valeur à afficher
        delta: Variation (optionnel)
        delta_positive: Si la variation est positive
    """
    design = DesignSystem()
    st.markdown(design.create_metric_card(label, value, delta, delta_positive), 
                unsafe_allow_html=True)


def vibe_badge(text: str, color: str = "primary"):
    """
    Affiche un badge avec le style Vibe.
    
    Args:
        text: Texte du badge
        color: Couleur du badge
    """
    design = DesignSystem()
    st.markdown(design.create_badge(text, color), unsafe_allow_html=True)


# ============================================================================
# ALIAS POUR COMPATIBILITÉ
# ============================================================================

# Alias pour faciliter l'import (utilisé par certaines pages)
Colors = ColorScheme

# ============================================================================
# FONCTIONS DE COMPATIBILITÉ
# ============================================================================

def load_css():
    """Charge les styles CSS personnalisés depuis assets/style.css.
    
    Cette fonction est utilisée par toutes les pages pour appliquer
    les styles personnalisés de l'application.
    
    Usage:
        from modules.ui import load_css
        load_css()
    """
    try:
        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # Si le fichier n'existe pas, on continue sans erreur
        pass


def card_kpi(title, value, trend=None, trend_color="positive"):
    """Rend une carte KPI avec style personnalisé.
    
    Args:
        title: Titre de la métrique
        value: Valeur à afficher
        trend: Tendance optionnelle (ex: "+12%")
        trend_color: "positive" (vert) ou "negative" (rouge)
    
    Usage:
        card_kpi("Total", "1 234 €", "+5%", "positive")
    """
    trend_html = ""
    if trend:
        color_class = "card-trend-positive" if trend_color == "positive" else "card-trend-negative"
        icon = "↗" if trend_color == "positive" else "↘"
        trend_html = f'<div class="{color_class}">{icon} {trend}</div>'
    
    html = f"""
    <div class="custom-card">
        <div class="card-title">{title}</div>
        <div class="card-value">{value}</div>
        {trend_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
