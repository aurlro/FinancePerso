"""Status badges - Indicateurs visuels d'état.

Les badges affichent des informations compactes comme le statut,
la priorité ou le nombre d'éléments.
"""

import streamlit as st

from modules.ui_v2.atoms.colors import PriorityColor
from modules.ui_v2.atoms.icons import IconSet


def status_badge(status: str, color: str = "blue") -> str:
    """Génère un badge de statut en HTML.

    Args:
        status: Texte du statut
        color: Couleur du badge (blue, green, red, yellow, gray)

    Returns:
        Code HTML du badge
    """
    color_map = {
        "blue": "#0066cc",
        "green": "#28a745",
        "red": "#dc3545",
        "yellow": "#ffc107",
        "gray": "#6c757d",
        "purple": "#6f42c1",
        "orange": "#fd7e14",
    }

    bg_color = color_map.get(color, "#6c757d")

    return f"""
    <span style="
        background-color: {bg_color}20;
        color: {bg_color};
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: 500;
        border: 1px solid {bg_color}40;
    ">{status}</span>
    """


def priority_badge(priority: str) -> str:
    """Génère un badge de priorité.

    Args:
        priority: Niveau de priorité ('high', 'medium', 'low')

    Returns:
        Code HTML du badge
    """
    config = {
        "high": ("High", PriorityColor.HIGH.value, IconSet.FIRE.value),
        "medium": ("Medium", PriorityColor.MEDIUM.value, IconSet.WARNING.value),
        "low": ("Low", PriorityColor.LOW.value, IconSet.INFO.value),
    }

    label, color, icon = config.get(priority.lower(), ("None", PriorityColor.NONE.value, "•"))

    return f"""
    <span style="
        background-color: {color}20;
        color: {color};
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: 500;
        border: 1px solid {color}40;
    ">{icon} {label}</span>
    """


def count_badge(count: int, label: str, color: str = "blue") -> str:
    """Génère un badge avec un nombre.

    Args:
        count: Nombre à afficher
        label: Label du badge
        color: Couleur du badge

    Returns:
        Code HTML du badge
    """
    color_map = {
        "blue": "#0066cc",
        "green": "#28a745",
        "red": "#dc3545",
        "yellow": "#ffc107",
        "gray": "#6c757d",
    }

    bg_color = color_map.get(color, "#6c757d")

    return f"""
    <div style="
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: {bg_color}15;
        color: {bg_color};
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.9em;
        font-weight: 500;
        border: 1px solid {bg_color}30;
    ">
        <span style="
            background-color: {bg_color};
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-weight: 700;
            font-size: 0.85em;
        ">{count}</span>
        <span>{label}</span>
    </div>
    """


def render_badge(html_badge: str):
    """Affiche un badge HTML dans Streamlit.

    Args:
        html_badge: Code HTML du badge
    """
    st.markdown(html_badge, unsafe_allow_html=True)


# Fonctions spécialisées pour les opérations courantes

def operation_status_badge(success: bool, operation: str = "Opération") -> str:
    """Badge de statut pour une opération (succès/échec).

    Args:
        success: Si l'opération a réussi
        operation: Nom de l'opération

    Returns:
        Code HTML du badge
    """
    if success:
        return status_badge(f"{IconSet.SUCCESS.value} {operation} réussie", "green")
    else:
        return status_badge(f"{IconSet.ERROR.value} {operation} échouée", "red")


def validation_badge(count: int, entity_name: str = "élément") -> str:
    """Badge pour le nombre d'éléments validés.

    Args:
        count: Nombre d'éléments
        entity_name: Nom de l'entité (singulier)

    Returns:
        Code HTML du badge
    """
    label = f"{entity_name}{'s' if count > 1 else ''} validé{'s' if count > 1 else ''}"
    return count_badge(count, label, "green")
