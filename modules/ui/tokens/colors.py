"""Tokens de couleurs - Source unique de vérité.

Toutes les couleurs de l'application doivent provenir de ce fichier.
PAS DE COULEURS HARDCODÉES dans les composants.
"""

from dataclasses import dataclass
from enum import StrEnum


class Colors(StrEnum):
    """Palette de couleurs principale - Light Mode (actuel).

    Usage:
        background = Colors.PRIMARY  # -> "#0F172A"
        success_bg = Colors.SUCCESS_LIGHT  # -> "#DCFCE7"
    """

    # Primary (Slate - pour le Light Mode actuel)
    PRIMARY = "#0F172A"
    PRIMARY_LIGHT = "#334155"
    PRIMARY_DARK = "#020617"

    # Secondary (Emerald)
    SECONDARY = "#10B981"
    SECONDARY_LIGHT = "#34D399"
    SECONDARY_DARK = "#059669"
    SECONDARY_BG = "#DCFCE7"

    # Accent (Amber)
    ACCENT = "#F59E0B"
    ACCENT_LIGHT = "#FBBF24"
    ACCENT_DARK = "#D97706"
    ACCENT_BG = "#FEF3C7"

    # Semantic - Danger
    DANGER = "#EF4444"
    DANGER_LIGHT = "#F87171"
    DANGER_DARK = "#DC2626"
    DANGER_BG = "#FEE2E2"

    # Semantic - Warning
    WARNING = "#F59E0B"
    WARNING_LIGHT = "#FBBF24"
    WARNING_DARK = "#D97706"
    WARNING_BG = "#FEF3C7"

    # Semantic - Info
    INFO = "#3B82F6"
    INFO_LIGHT = "#60A5FA"
    INFO_DARK = "#2563EB"
    INFO_BG = "#DBEAFE"

    # Semantic - Success
    SUCCESS = "#10B981"
    SUCCESS_LIGHT = "#34D399"
    SUCCESS_DARK = "#059669"
    SUCCESS_BG = "#DCFCE7"

    # Neutrals - Slate scale
    SLATE_50 = "#F8FAFC"
    SLATE_100 = "#F1F5F9"
    SLATE_200 = "#E2E8F0"
    SLATE_300 = "#CBD5E1"
    SLATE_400 = "#94A3B8"
    SLATE_500 = "#64748B"
    SLATE_600 = "#475569"
    SLATE_700 = "#334155"
    SLATE_800 = "#1E293B"
    SLATE_900 = "#0F172A"

    # Neutrals - Gray scale
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

    # White & Black
    WHITE = "#FFFFFF"
    BLACK = "#000000"
    TRANSPARENT = "transparent"


@dataclass(frozen=True)
class ColorPalette:
    """Palette complète pour référence.

    Usage:
        palette = ColorPalette()
        primary = palette.primary
    """

    # Brand
    primary: str = Colors.PRIMARY
    primary_light: str = Colors.PRIMARY_LIGHT
    primary_dark: str = Colors.PRIMARY_DARK

    secondary: str = Colors.SECONDARY
    secondary_light: str = Colors.SECONDARY_LIGHT
    secondary_dark: str = Colors.SECONDARY_DARK

    accent: str = Colors.ACCENT
    accent_light: str = Colors.ACCENT_LIGHT
    accent_dark: str = Colors.ACCENT_DARK

    # Semantic
    danger: str = Colors.DANGER
    danger_light: str = Colors.DANGER_LIGHT
    danger_dark: str = Colors.DANGER_DARK
    danger_bg: str = Colors.DANGER_BG

    warning: str = Colors.WARNING
    warning_light: str = Colors.WARNING_LIGHT
    warning_dark: str = Colors.WARNING_DARK
    warning_bg: str = Colors.WARNING_BG

    info: str = Colors.INFO
    info_light: str = Colors.INFO_LIGHT
    info_dark: str = Colors.INFO_DARK
    info_bg: str = Colors.INFO_BG

    success: str = Colors.SUCCESS
    success_light: str = Colors.SUCCESS_LIGHT
    success_dark: str = Colors.SUCCESS_DARK
    success_bg: str = Colors.SUCCESS_BG

    # Backgrounds
    bg_primary: str = Colors.SLATE_50
    bg_secondary: str = Colors.SLATE_100
    bg_tertiary: str = Colors.WHITE
    bg_card: str = Colors.WHITE

    # Text
    text_primary: str = Colors.SLATE_900
    text_secondary: str = Colors.SLATE_500
    text_muted: str = Colors.SLATE_400
    text_inverse: str = Colors.WHITE

    # Borders
    border_light: str = Colors.SLATE_200
    border: str = Colors.SLATE_300
    border_dark: str = Colors.SLATE_400


@dataclass(frozen=True)
class SemanticColors:
    """Couleurs sémantiques avec leurs combinaisons (text + bg).

    Usage:
        colors = SemanticColors()
        danger_text, danger_bg, danger_border = colors.danger
    """

    # Tuple: (text_color, bg_color, border_color)
    danger: tuple[str, str, str] = (Colors.DANGER_DARK, Colors.DANGER_BG, Colors.DANGER)
    warning: tuple[str, str, str] = (Colors.WARNING_DARK, Colors.WARNING_BG, Colors.WARNING)
    success: tuple[str, str, str] = (Colors.SUCCESS_DARK, Colors.SUCCESS_BG, Colors.SUCCESS)
    info: tuple[str, str, str] = (Colors.INFO_DARK, Colors.INFO_BG, Colors.INFO)

    # Muted versions (for subtle badges, etc.)
    danger_muted: tuple[str, str, str] = (Colors.DANGER, Colors.DANGER_BG, Colors.DANGER_LIGHT)
    warning_muted: tuple[str, str, str] = (Colors.WARNING, Colors.WARNING_BG, Colors.WARNING_LIGHT)
    success_muted: tuple[str, str, str] = (Colors.SUCCESS, Colors.SUCCESS_BG, Colors.SUCCESS_LIGHT)
    info_muted: tuple[str, str, str] = (Colors.INFO, Colors.INFO_BG, Colors.INFO_LIGHT)


# Gradients prédéfinis
GRADIENTS = {
    "primary": f"linear-gradient(135deg, {Colors.PRIMARY} 0%, {Colors.PRIMARY_LIGHT} 100%)",
    "secondary": f"linear-gradient(135deg, {Colors.SECONDARY} 0%, {Colors.SECONDARY_LIGHT} 100%)",
    "accent": f"linear-gradient(135deg, {Colors.ACCENT} 0%, {Colors.ACCENT_LIGHT} 100%)",
    "card": f"linear-gradient(135deg, {Colors.WHITE} 0%, {Colors.SLATE_50} 100%)",
    "skeleton": f"linear-gradient(90deg, {Colors.SLATE_100} 25%, {Colors.SLATE_200} 50%, {Colors.SLATE_100} 75%)",
}


def get_chart_colors() -> list[str]:
    """Retourne la palette de couleurs pour les graphiques.

    Usage:
        colors = get_chart_colors()
        fig.update_traces(marker_color=colors[0])
    """
    return [
        Colors.PRIMARY,
        Colors.SECONDARY,
        Colors.ACCENT,
        Colors.INFO,
        Colors.DANGER,
        Colors.SLATE_500,
        Colors.SLATE_400,
        Colors.SECONDARY_DARK,
        Colors.ACCENT_DARK,
        Colors.INFO_DARK,
    ]


def get_severity_color(severity: str) -> str:
    """Retourne la couleur associée à un niveau de sévérité.

    Args:
        severity: "low", "medium", "high", "critical", "info", "success", "warning", "error"

    Returns:
        Code couleur hex

    Usage:
        color = get_severity_color("high")  # -> "#EF4444"
    """
    mapping = {
        "low": Colors.INFO,
        "medium": Colors.WARNING,
        "high": Colors.DANGER,
        "critical": Colors.DANGER_DARK,
        "info": Colors.INFO,
        "success": Colors.SUCCESS,
        "warning": Colors.WARNING,
        "error": Colors.DANGER,
    }
    return mapping.get(severity.lower(), Colors.SLATE_500)
