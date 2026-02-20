"""Couleurs standardisées pour l'application.

Définit les palettes de couleurs utilisées dans l'interface.
"""

from enum import Enum


class FeedbackColor(Enum):
    """Couleurs pour les retours utilisateur."""

    SUCCESS = "#28a745"
    SUCCESS_BG = "#d4edda"
    SUCCESS_TEXT = "#155724"

    ERROR = "#dc3545"
    ERROR_BG = "#f8d7da"
    ERROR_TEXT = "#721c24"

    WARNING = "#ffc107"
    WARNING_BG = "#fff3cd"
    WARNING_TEXT = "#856404"

    INFO = "#17a2b8"
    INFO_BG = "#d1ecf1"
    INFO_TEXT = "#0c5460"


class PriorityColor(Enum):
    """Couleurs par niveau de priorité."""

    HIGH = "#dc3545"      # Rouge
    MEDIUM = "#ffc107"    # Jaune/Orange
    LOW = "#17a2b8"       # Bleu
    NONE = "#6c757d"      # Gris


class ColorScheme(Enum):
    """Schéma de couleurs principal."""

    # Primaires
    PRIMARY = "#0066cc"
    PRIMARY_LIGHT = "#4d94ff"
    PRIMARY_DARK = "#004c99"

    # Secondaires
    SECONDARY = "#6c757d"
    SECONDARY_LIGHT = "#adb5bd"
    SECONDARY_DARK = "#495057"

    # Neutres
    WHITE = "#ffffff"
    GRAY_100 = "#f8f9fa"
    GRAY_200 = "#e9ecef"
    GRAY_300 = "#dee2e6"
    GRAY_400 = "#ced4da"
    GRAY_500 = "#adb5bd"
    GRAY_600 = "#6c757d"
    GRAY_700 = "#495057"
    GRAY_800 = "#343a40"
    GRAY_900 = "#212529"
    BLACK = "#000000"

    # Catégories financières
    INCOME = "#28a745"      # Vert
    EXPENSE = "#dc3545"     # Rouge
    SAVINGS = "#17a2b8"     # Bleu
    INVESTMENT = "#6f42c1"  # Violet


# Mapping rapide pour Streamlit
def get_streamlit_color(color: FeedbackColor) -> str:
    """Convertit une couleur de feedback en nom Streamlit.

    Args:
        color: Couleur de feedback

    Returns:
        Nom de couleur Streamlit ('success', 'error', 'warning', 'info')
    """
    mapping = {
        FeedbackColor.SUCCESS: "success",
        FeedbackColor.ERROR: "error",
        FeedbackColor.WARNING: "warning",
        FeedbackColor.INFO: "info",
    }
    return mapping.get(color, "info")
