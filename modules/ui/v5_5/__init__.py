"""Modules UI V5.5 - Interface moderne type FinCouple.

Nouvelle interface light mode avec design épuré.

Usage:
    from modules.ui.v5_5 import ThemeV5, apply_light_theme
    from modules.ui.v5_5.components import WelcomeCard
    from modules.ui.v5_5.welcome import render_welcome_screen
    
    # Appliquer le thème
    apply_light_theme()
    
    # Afficher l'écran d'accueil
    render_welcome_screen()
"""

from .theme import (
    LightColors,
    ThemeV5,
    apply_light_theme,
    get_light_theme_css,
)

# Composants
from .components import WelcomeCard

# Welcome screen
from .welcome import (
    render_welcome_screen,
    render_welcome_or_dashboard,
    has_transactions,
    get_user_name,
)

__all__ = [
    # Theme
    "LightColors",
    "ThemeV5",
    "apply_light_theme",
    "get_light_theme_css",
    # Components
    "WelcomeCard",
    # Welcome
    "render_welcome_screen",
    "render_welcome_or_dashboard",
    "has_transactions",
    "get_user_name",
]
