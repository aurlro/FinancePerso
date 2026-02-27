"""Tokens de typographie - Source unique de vérité.

Toutes les tailles de police et familles doivent provenir de ce fichier.
PAS DE TAILLES HARDCODÉES dans les composants.
"""

from enum import Enum
from dataclasses import dataclass


class FontFamily(str, Enum):
    """Familles de polices."""
    SANS = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    MONO = "'JetBrains Mono', 'Fira Code', 'Courier New', monospace"
    SERIF = "Georgia, 'Times New Roman', serif"


class FontSize(str, Enum):
    """Tailles de police en rem.
    
    Base: 16px (1rem)
    Échelle: 12, 14, 16, 18, 20, 24, 30, 36, 48px
    """
    XS = "0.75rem"      # 12px
    SM = "0.875rem"     # 14px
    BASE = "1rem"       # 16px
    LG = "1.125rem"     # 18px
    XL = "1.25rem"      # 20px
    XL_2 = "1.5rem"     # 24px
    XL_3 = "1.875rem"   # 30px
    XL_4 = "2.25rem"    # 36px
    XL_5 = "3rem"       # 48px (titres uniquement)


class FontWeight(str, Enum):
    """Graisses de police."""
    LIGHT = "300"
    NORMAL = "400"
    MEDIUM = "500"
    SEMIBOLD = "600"
    BOLD = "700"
    EXTRABOLD = "800"


class LineHeight(str, Enum):
    """Hauteurs de ligne."""
    TIGHT = "1.25"
    SNUG = "1.375"
    NORMAL = "1.5"
    RELAXED = "1.625"
    LOOSE = "2"


@dataclass(frozen=True)
class Typography:
    """Tokens de typographie complets.
    
    Usage:
        from modules.ui.tokens import Typography
        
        font_size = Typography.SIZE_LG
        font_family = Typography.FAMILY_SANS
    """
    # Familles
    FAMILY_SANS: str = FontFamily.SANS
    FAMILY_MONO: str = FontFamily.MONO
    
    # Tailles
    SIZE_XS: str = FontSize.XS
    SIZE_SM: str = FontSize.SM
    SIZE_BASE: str = FontSize.BASE
    SIZE_LG: str = FontSize.LG
    SIZE_XL: str = FontSize.XL
    SIZE_2XL: str = FontSize.XL_2
    SIZE_3XL: str = FontSize.XL_3
    SIZE_4XL: str = FontSize.XL_4
    SIZE_5XL: str = FontSize.XL_5
    
    # Graisses
    WEIGHT_LIGHT: str = FontWeight.LIGHT
    WEIGHT_NORMAL: str = FontWeight.NORMAL
    WEIGHT_MEDIUM: str = FontWeight.MEDIUM
    WEIGHT_SEMIBOLD: str = FontWeight.SEMIBOLD
    WEIGHT_BOLD: str = FontWeight.BOLD
    
    # Hauteurs de ligne
    LEADING_TIGHT: str = LineHeight.TIGHT
    LEADING_NORMAL: str = LineHeight.NORMAL
    LEADING_RELAXED: str = LineHeight.RELAXED
    
    @classmethod
    def get_size_for_heading(cls, level: int) -> str:
        """Retourne la taille appropriée pour un titre h1-h6.
        
        Args:
            level: Niveau de titre (1-6)
        
        Returns:
            Taille en rem
        
        Usage:
            size = Typography.get_size_for_heading(1)  # -> "2.25rem"
        """
        sizes = {
            1: cls.SIZE_4XL,  # h1: 36px
            2: cls.SIZE_3XL,  # h2: 30px
            3: cls.SIZE_2XL,  # h3: 24px
            4: cls.SIZE_XL,   # h4: 20px
            5: cls.SIZE_LG,   # h5: 18px
            6: cls.SIZE_BASE, # h6: 16px
        }
        return sizes.get(level, cls.SIZE_BASE)


# Styles prédéfinis pour référence (utilise les valeurs directes, pas Typography.XXX)
TEXT_STYLES = {
    "hero": {
        "font_size": FontSize.XL_4,
        "font_weight": FontWeight.BOLD,
        "line_height": LineHeight.TIGHT,
    },
    "h1": {
        "font_size": FontSize.XL_3,
        "font_weight": FontWeight.BOLD,
        "line_height": LineHeight.TIGHT,
    },
    "h2": {
        "font_size": FontSize.XL_2,
        "font_weight": FontWeight.SEMIBOLD,
        "line_height": LineHeight.TIGHT,
    },
    "h3": {
        "font_size": FontSize.XL,
        "font_weight": FontWeight.SEMIBOLD,
        "line_height": LineHeight.SNUG,
    },
    "h4": {
        "font_size": FontSize.LG,
        "font_weight": FontWeight.MEDIUM,
        "line_height": LineHeight.SNUG,
    },
    "body": {
        "font_size": FontSize.BASE,
        "font_weight": FontWeight.NORMAL,
        "line_height": LineHeight.NORMAL,
    },
    "body_small": {
        "font_size": FontSize.SM,
        "font_weight": FontWeight.NORMAL,
        "line_height": LineHeight.NORMAL,
    },
    "caption": {
        "font_size": FontSize.XS,
        "font_weight": FontWeight.NORMAL,
        "line_height": LineHeight.NORMAL,
    },
    "label": {
        "font_size": FontSize.SM,
        "font_weight": FontWeight.MEDIUM,
        "line_height": LineHeight.NORMAL,
    },
    "button": {
        "font_size": FontSize.SM,
        "font_weight": FontWeight.MEDIUM,
        "line_height": LineHeight.TIGHT,
    },
    "badge": {
        "font_size": FontSize.XS,
        "font_weight": FontWeight.SEMIBOLD,
        "line_height": LineHeight.TIGHT,
    },
}


def get_text_style(style_name: str) -> dict:
    """Retourne un style de texte complet.
    
    Args:
        style_name: Nom du style (hero, h1, h2, body, etc.)
    
    Returns:
        Dictionnaire avec font_size, font_weight, line_height
    
    Usage:
        style = get_text_style("h2")
        # -> {"font_size": "1.5rem", "font_weight": "600", "line_height": "1.25"}
    """
    return TEXT_STYLES.get(style_name, TEXT_STYLES["body"]).copy()
