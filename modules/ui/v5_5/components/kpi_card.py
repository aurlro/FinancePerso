"""KPI Card - Carte de métrique pour le dashboard.

Usage:
    from modules.ui.v5_5.components import KPICard, KPIData

    kpi = KPIData(
        label="Reste à vivre",
        value="1 847.52 €",
        value_color="positive",
        icon="💚",
        icon_bg="#DCFCE7",
        variation="+13.8%",
        variation_label="vs Janvier"
    )
    KPICard.render(kpi)
"""

from dataclasses import dataclass
from typing import Literal

import streamlit as st


@dataclass
class KPIData:
    """Données pour un KPI.

    Attributes:
        label: Nom du KPI (ex: "Reste à vivre")
        value: Valeur formatée (ex: "1 847.52 €")
        value_color: Couleur de la valeur
        icon: Emoji icône
        icon_bg: Couleur de fond de l'icône (hex)
        variation: Variation en pourcentage (ex: "+13.8%")
        variation_label: Label de la variation (ex: "vs Janvier")
    """

    label: str
    value: str
    value_color: Literal["positive", "negative", "neutral"] = "neutral"
    icon: str = "📊"
    icon_bg: str = "#F3F4F6"
    variation: str | None = None
    variation_label: str | None = None


class KPICard:
    """Carte KPI avec style maquette FinCouple."""

    @staticmethod
    def render(kpi: KPIData) -> None:
        """Affiche une carte KPI.

        Args:
            kpi: Données du KPI à afficher
        """
        # Couleurs selon le type
        value_colors = {
            "positive": "#059669",  # Emerald 600
            "negative": "#DC2626",  # Red 600
            "neutral": "#374151",  # Gray 700
        }
        value_color = value_colors.get(kpi.value_color, "#374151")

        border_color = (
            "#10B981"
            if kpi.value_color == "positive"
            else "#EF4444" if kpi.value_color == "negative" else "#E5E7EB"
        )

        # Flèche de variation
        variation_arrow = ""
        variation_color = "#6B7280"
        if kpi.variation:
            if kpi.variation.startswith("+"):
                variation_arrow = "↑"
                variation_color = "#059669"
            elif kpi.variation.startswith("-"):
                variation_arrow = "↓"
                variation_color = "#DC2626"

        # Construire le HTML sans sauts de ligne pour éviter les problèmes Streamlit
        bg_var = (
            "#DCFCE7"
            if kpi.value_color == "positive"
            else "#FEE2E2" if kpi.value_color == "negative" else "#F3F4F6"
        )

        if kpi.variation:
            variation_html = (
                f'<span style="color: {variation_color}; font-weight: 600; '
                f"background: {bg_var}; padding: 2px 8px; border-radius: 12px; "
                f'font-size: 0.75rem; white-space: nowrap;">'
                f"{variation_arrow} {kpi.variation}</span>"
                f'<span style="color: #9CA3AF; font-size: 0.75rem; margin-left: 6px;">'
                f'{kpi.variation_label or ""}</span>'
            )
        elif kpi.variation_label:
            variation_html = (
                f'<span style="color: #10B981; font-size: 0.75rem; '
                f'font-weight: 500;">{kpi.variation_label}</span>'
            )
        else:
            variation_html = ""

        # HTML sur une seule ligne pour éviter les problèmes de rendu
        html = (
            f'<div style="background: #FFFFFF; border: 1px solid {border_color}; '
            f"border-radius: 12px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); "
            f'height: 100%;">'
            f'<div style="display: flex; justify-content: space-between; align-items: flex-start; '
            f'margin-bottom: 10px;">'
            f'<span style="font-size: 14px; font-weight: 500; color: #6B7280; line-height: 1.4;">'
            f"{kpi.label}</span>"
            f'<div style="width: 36px; height: 36px; background: {kpi.icon_bg}; '
            f"border-radius: 8px; display: flex; align-items: center; justify-content: center; "
            f'font-size: 18px; flex-shrink: 0;">{kpi.icon}</div></div>'
            f'<div style="font-size: 24px; font-weight: 700; color: {value_color}; '
            f'margin-bottom: 8px; letter-spacing: -0.02em;">{kpi.value}</div>'
            f'<div style="display: flex; align-items: center; gap: 4px; flex-wrap: wrap;">'
            f"{variation_html}</div></div>"
        )

        st.markdown(html, unsafe_allow_html=True)

    @classmethod
    def render_mock(cls) -> None:
        """Affiche une carte KPI avec des données de démonstration."""
        mock_kpi = KPIData(
            label="Reste à vivre",
            value="1 847.52 €",
            value_color="positive",
            icon="💚",
            icon_bg="#DCFCE7",
            variation="+13.8%",
            variation_label="vs Janvier",
        )
        cls.render(mock_kpi)


def format_currency(amount: float, currency: str = "€") -> str:
    """Formate un montant en devise.

    Args:
        amount: Montant à formater
        currency: Symbole de la devise

    Returns:
        Chaîne formatée (ex: "1 847,52 €")
    """
    return f"{amount:,.2f} {currency}".replace(",", " ").replace(".", ",")


def create_kpi_variation(current: float, previous: float) -> tuple[str, str]:
    """Crée une variation de KPI.

    Args:
        current: Valeur actuelle
        previous: Valeur précédente

    Returns:
        Tuple (variation_formatée, label)
    """
    if previous == 0:
        return ("N/A", "Pas de données précédentes")

    change = ((current - previous) / abs(previous)) * 100
    sign = "+" if change >= 0 else ""
    return (f"{sign}{change:.1f}%", "vs période précédente")
