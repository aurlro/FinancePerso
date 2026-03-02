"""Atoms - Éléments de base du Design System.

Les atomes sont les éléments UI les plus fondamentaux :
- Boutons
- Badges
- Inputs
- Icônes

Usage:
    from modules.ui.atoms import Button, Badge

    Button.primary("Valider", on_click=handler)
    Badge.success("Actif")
"""

from .badge import Badge, BadgeVariant
from .button import Button, ButtonVariant
from .icon import Icon, IconSize

__all__ = [
    "Button",
    "ButtonVariant",
    "Badge",
    "BadgeVariant",
    "Icon",
    "IconSize",
]
