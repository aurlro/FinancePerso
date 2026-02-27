"""Design Tokens pour FinancePerso.

Ce module fournit les tokens de design unifiés pour toute l'application.
À utiliser obligatoirement pour tout nouveau composant.

Usage:
    from modules.ui.tokens import Colors, Typography, Spacing, BorderRadius
    
    # Couleurs
    primary = Colors.PRIMARY
    danger = Colors.DANGER
    
    # Typographie
    font_size = Typography.SIZE_BASE
    
    # Espacements
    padding = Spacing.MD
    
    # Border radius
    radius = BorderRadius.LG
"""

from .colors import Colors, ColorPalette, SemanticColors, GRADIENTS, get_chart_colors, get_severity_color
from .typography import Typography, FontFamily, FontSize, FontWeight
from .spacing import Spacing, LayoutSpacing
from .radius import BorderRadius, Shadow

__all__ = [
    # Colors
    "Colors",
    "ColorPalette",
    "SemanticColors",
    # Typography
    "Typography",
    "FontFamily",
    "FontSize",
    "FontWeight",
    # Spacing
    "Spacing",
    "LayoutSpacing",
    # Radius & Shadow
    "BorderRadius",
    "Shadow",
]
