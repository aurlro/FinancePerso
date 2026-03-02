"""Tokens de border-radius et ombres - Source unique de vérité.

Tous les rayons de bordure et ombres doivent provenir de ce fichier.
PAS DE VALEURS HARDCODÉES dans les composants.
"""

from dataclasses import dataclass
from enum import StrEnum


class BorderRadius(StrEnum):
    """Rayons de bordure.

    Échelle: 0, 4, 8, 12, 16, 9999px
    """

    NONE = "0"
    SM = "4px"
    MD = "8px"
    LG = "12px"
    XL = "16px"
    FULL = "9999px"  # Pour badges/pills ronds
    ROUND = "50%"  # Pour cercles parfaits


@dataclass(frozen=True)
class Shadow:
    """Ombres prédéfinies.

    Usage:
        from modules.ui.tokens import Shadow

        box_shadow = Shadow.SM
    """

    # No shadow
    NONE: str = "none"

    # Small (subtle elevation)
    SM: str = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"

    # Medium (cards default)
    MD: str = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"

    # Large (modals, dropdowns)
    LG: str = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"

    # Extra large (high elevation)
    XL: str = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"

    # Inner (inset)
    INNER: str = "inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)"

    # Focus ring
    FOCUS: str = "0 0 0 3px rgba(59, 130, 246, 0.5)"


# Transitions standards
TRANSITIONS = {
    "fast": "all 150ms ease-in-out",
    "normal": "all 200ms ease-in-out",
    "slow": "all 300ms ease-in-out",
    "color": "color 150ms ease-in-out",
    "transform": "transform 200ms ease-in-out",
    "shadow": "box-shadow 200ms ease-in-out",
}


# Z-index scale
Z_INDEX = {
    "base": 0,
    "dropdown": 100,
    "sticky": 200,
    "fixed": 300,
    "modal_backdrop": 400,
    "modal": 500,
    "popover": 600,
    "tooltip": 700,
    "toast": 800,
}


# Breakpoints responsive
BREAKPOINTS = {
    "sm": "640px",
    "md": "768px",
    "lg": "1024px",
    "xl": "1280px",
    "2xl": "1536px",
}
