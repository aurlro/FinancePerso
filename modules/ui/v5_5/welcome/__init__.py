"""Welcome V5.5 - Écran d'accueil.

Usage:
    from modules.ui.v5_5.welcome import render_welcome_screen
    
    render_welcome_screen()
"""

from .welcome_screen import (
    render_welcome_screen,
    render_welcome_or_dashboard,
    has_transactions,
    get_user_name,
)

__all__ = [
    "render_welcome_screen",
    "render_welcome_or_dashboard",
    "has_transactions",
    "get_user_name",
]
