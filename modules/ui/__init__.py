"""Modules UI - Interface utilisateur de FinancePerso.

Structure Atomic Design :
- tokens/ : Design tokens (couleurs, typographie, espacements)
- atoms/ : Éléments de base (Button, Badge, Icon)
- molecules/ : Compositions simples (Card, EmptyState, Metric)
- organisms/ : Sections complexes (Header, Sidebar, etc.)
- templates/ : Layouts de pages

Usage:
    # Design Tokens
    from modules.ui.tokens import Colors, Typography, Spacing
    
    # Atomes
    from modules.ui.atoms import Button, Badge, Icon
    
    # Molécules
    from modules.ui.molecules import Card, EmptyState, Metric
    
    # Templates
    from modules.ui.templates import PageLayout
"""

# Import pour compatibilité (anciens composants)
from .design_system import load_css, apply_vibe_theme, card_kpi, DesignSystem, ColorScheme
from .feedback import render_scroll_to_top, display_flash_messages
try:
    from .feedback import (
        toast_success,
        toast_error,
        toast_warning,
        toast_info,
        show_success,
        show_error,
        show_warning,
        show_info,
        confirm_dialog,
    )
except ImportError:
    # Fallback si fonctions non disponibles
    toast_success = toast_error = toast_warning = toast_info = lambda *a, **k: None
    show_success = show_error = show_warning = show_info = lambda *a, **k: None
    confirm_dialog = lambda *a, **k: False

# Version modernisée du feedback (avec fallback)
try:
    from .feedback_v2 import Feedback, Toast, Banner, ConfirmDialog
    FEEDBACK_V2_AVAILABLE = True
except ImportError:
    FEEDBACK_V2_AVAILABLE = False

__all__ = [
    # Design System
    "DesignSystem",
    "ColorScheme",
    "load_css",
    "apply_vibe_theme",
    "card_kpi",
    "render_scroll_to_top",
    
    # Feedback V2 (si disponible)
    "Feedback",
    "Toast",
    "Banner",
    "ConfirmDialog",
    "FEEDBACK_V2_AVAILABLE",
    
    # Feedback legacy compatibility
    "toast_success",
    "toast_error",
    "toast_warning",
    "toast_info",
    "show_success",
    "show_error",
    "show_warning",
    "show_info",
    "confirm_dialog",
    "display_flash_messages",
]
