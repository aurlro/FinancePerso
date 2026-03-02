"""Tokens d'espacement - Source unique de vérité.

Tous les espacements (padding, margin, gap) doivent provenir de ce fichier.
PAS DE VALEURS HARDCODÉES dans les composants.
"""

from dataclasses import dataclass
from enum import Enum


class Spacing(str, Enum):
    """Espacements en rem.

    Échelle: 4, 8, 12, 16, 24, 32, 48, 64px
    """

    # Base scale
    XS = "0.25rem"  # 4px
    SM = "0.5rem"  # 8px
    MD = "1rem"  # 16px
    LG = "1.5rem"  # 24px
    XL = "2rem"  # 32px
    XL_2 = "3rem"  # 48px
    XL_3 = "4rem"  # 64px

    # Half-steps (rarement utilisés - préférer la base scale)
    XS_2 = "0.125rem"  # 2px
    SM_2 = "0.375rem"  # 6px
    MD_2 = "0.75rem"  # 12px
    LG_2 = "1.25rem"  # 20px

    # Zéro
    ZERO = "0"
    AUTO = "auto"


@dataclass(frozen=True)
class LayoutSpacing:
    """Espacements de layout complets.

    Usage:
        from modules.ui.tokens import Spacing, LayoutSpacing

        padding = Spacing.MD
        section_gap = LayoutSpacing.SECTION
    """

    # Section spacing (entre grandes sections)
    SECTION: str = Spacing.XL_2

    # Component spacing (entre composants)
    COMPONENT: str = Spacing.LG

    # Element spacing (entre éléments d'un composant)
    ELEMENT: str = Spacing.MD

    # Tight spacing (pour groupes serrés)
    TIGHT: str = Spacing.SM

    # Internal padding (à l'intérieur des composants)
    PADDING_XS: str = Spacing.XS
    PADDING_SM: str = Spacing.SM
    PADDING_MD: str = Spacing.MD
    PADDING_LG: str = Spacing.LG
    PADDING_XL: str = Spacing.XL


# Gap standards pour différents contextes
GAP_STANDARDS = {
    "none": Spacing.ZERO,
    "xs": Spacing.XS,
    "sm": Spacing.SM,
    "md": Spacing.MD,
    "lg": Spacing.LG,
    "xl": Spacing.XL,
}

# Container max-widths
CONTAINER_WIDTHS = {
    "sm": "640px",
    "md": "768px",
    "lg": "1024px",
    "xl": "1280px",
    "full": "100%",
}


def get_spacing_pair(vertical: str, horizontal: str) -> str:
    """Retourne un espacement pair (vertical horizontal).

    Args:
        vertical: Espacement vertical (Spacing.XXX)
        horizontal: Espacement horizontal (Spacing.XXX)

    Returns:
        Chaîne CSS "vertical horizontal"

    Usage:
        padding = get_spacing_pair(Spacing.MD, Spacing.LG)  # -> "1rem 1.5rem"
    """
    return f"{vertical} {horizontal}"
