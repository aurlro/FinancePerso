"""KPI Card - Carte de métrique style maquette V5.5.

Affiche une métrique avec label, valeur, icône et variation,
dans le style épuré des maquettes FinCouple.

Usage:
    from modules.ui.v5_5.components import KPICard, KPIData
    
    kpi = KPIData(
        label="Reste à vivre",
        value="1 847.52 €",
        value_color="positive",
        icon="💚",
        icon_bg="#DCFCE7",
        variation="+13.8%",
        variation_label="vs Janvier 2026"
    )
    KPICard.render(kpi)
"""

from dataclasses import dataclass
from typing import Optional
import streamlit as st

from modules.ui.v5_5.theme import LightColors


@dataclass
class KPIData:
    """Données d'une métrique KPI.
    
    Attributes:
        label: Label de la métrique (ex: "Reste à vivre")
        value: Valeur formatée (ex: "1 847.52 €")
        value_color: Couleur de la valeur ("positive", "negative", "neutral")
        icon: Emoji icône (ex: "💚")
        icon_bg: Couleur de fond de l'icône (ex: "#DCFCE7")
        variation: Variation en pourcentage (ex: "+13.8%")
        variation_label: Label de la variation (ex: "vs Janvier 2026")
        highlight: Si True, ajoute une bordure d'accent
    """
    label: str
    value: str
    value_color: str = "neutral"  # "positive", "negative", "neutral"
    icon: str = "📊"
    icon_bg: str = "#F3F4F6"
    variation: Optional[str] = None
    variation_label: Optional[str] = None
    highlight: bool = False


class KPICard:
    """Carte KPI style maquette V5.5.
    
    Style:
    - Fond blanc
    - Bordure légère
    - Icône dans coin supérieur droit avec fond coloré
    - Label en haut à gauche
    - Valeur en gros au centre
    - Variation en dessous avec flèche
    
    Usage:
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
    
    # Mapping des couleurs
    VALUE_COLORS = {
        "positive": "#10B981",  # Vert
        "negative": "#EF4444",  # Rouge
        "neutral": "#1F2937",   # Gris foncé
    }
    
    @classmethod
    def render(cls, kpi: KPIData) -> None:
        """Rend une carte KPI.
        
        Args:
            kpi: Données de la métrique (KPIData)
        """
        # Couleur de la valeur
        value_color = cls.VALUE_COLORS.get(kpi.value_color, cls.VALUE_COLORS["neutral"])
        
        # Flèche de variation
        variation_arrow = ""
        if kpi.variation:
            if kpi.value_color == "positive":
                variation_arrow = "↑"
            elif kpi.value_color == "negative":
                variation_arrow = "↓"
            else:
                variation_arrow = "→"
        
        # Bordure highlight
        border_color = LightColors.PRIMARY if kpi.highlight else LightColors.BORDER
        
        # Couleur de variation
        if kpi.value_color == "positive":
            variation_color = "#059669"  # Vert plus foncé pour meilleur contraste
        elif kpi.value_color == "negative":
            variation_color = "#DC2626"  # Rouge plus foncé
        else:
            variation_color = "#6B7280"  # Gris
        
        # Construire le HTML sans sauts de ligne pour éviter les problèmes Streamlit
        bg_var = "#DCFCE7" if kpi.value_color == "positive" else "#FEE2E2" if kpi.value_color == "negative" else "#F3F4F6"
        
        if kpi.variation:
            variation_html = f'<span style="color: {variation_color}; font-weight: 600; background: {bg_var}; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; white-space: nowrap;">{variation_arrow} {kpi.variation}</span><span style="color: #9CA3AF; font-size: 0.75rem; margin-left: 6px;">{kpi.variation_label or ""}</span>'
        elif kpi.variation_label:
            variation_html = f'<span style="color: #10B981; font-size: 0.75rem; font-weight: 500;">{kpi.variation_label}</span>'
        else:
            variation_html = ""
        
        # HTML sur une seule ligne pour éviter les problèmes de rendu
        html = f'<div style="background: #FFFFFF; border: 1px solid {border_color}; border-radius: 12px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); height: 100%;"><div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;"><span style="font-size: 14px; font-weight: 500; color: #6B7280; line-height: 1.4;">{kpi.label}</span><div style="width: 36px; height: 36px; background: {kpi.icon_bg}; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0;">{kpi.icon}</div></div><div style="font-size: 24px; font-weight: 700; color: {value_color}; margin-bottom: 8px; letter-spacing: -0.02em;">{kpi.value}</div><div style="display: flex; align-items: center; gap: 4px; flex-wrap: wrap;">{variation_html}</div></div>'
        
        st.markdown(html, unsafe_allow_html=True)
    
    @classmethod
    def render_many(cls, kpis: list[KPIData], columns: int = 4) -> None:
        """Rend plusieurs KPIs dans une grille.
        
        Args:
            kpis: Liste des données KPI
            columns: Nombre de colonnes (2, 3 ou 4)
        """
        # Créer les colonnes
        cols = st.columns(columns)
        
        # Répartir les KPIs dans les colonnes
        for idx, kpi in enumerate(kpis):
            with cols[idx % columns]:
                cls.render(kpi)


def create_kpi_variation(current: float, previous: float) -> tuple[str, str]:
    """Calcule la variation entre deux valeurs.
    
    Args:
        current: Valeur actuelle
        previous: Valeur précédente
    
    Returns:
        Tuple (variation_formatted, color)
        Ex: ("+13.8%", "positive")
    """
    if previous == 0:
        return ("N/A", "neutral")
    
    variation = ((current - previous) / abs(previous)) * 100
    variation_str = f"{variation:+.1f}%"
    
    # Pour les finances, une augmentation de "restant" est positive
    # mais une augmentation de "dépenses" est négative
    # Le contexte d'utilisation détermine la couleur
    if variation > 0:
        return (variation_str, "positive")
    elif variation < 0:
        return (variation_str, "negative")
    else:
        return ("0%", "neutral")


def format_currency(amount: float, currency: str = "€") -> str:
    """Formate un montant en devise.
    
    Args:
        amount: Montant à formater
        currency: Symbole de la devise
    
    Returns:
        Chaîne formatée (ex: "1 847.52 €")
    """
    # Format avec espace comme séparateur de milliers
    formatted = f"{amount:,.2f}".replace(",", " ").replace(".", ",")
    return f"{formatted} {currency}"


# KPIs prédéfinis pour le dashboard
def get_default_kpis() -> list[KPIData]:
    """Retourne les 4 KPIs par défaut pour le dashboard.
    
    Returns:
        Liste des 4 KPIs standard
    """
    return [
        KPIData(
            label="Reste à vivre",
            value="1 847.52 €",
            value_color="positive",
            icon="💚",
            icon_bg="#DCFCE7",
            variation="+13.8%",
            variation_label="vs Janvier 2026"
        ),
        KPIData(
            label="Dépenses",
            value="-2 152.48 €",
            value_color="negative",
            icon="💳",
            icon_bg="#FEE2E2",
            variation="-9.4%",
            variation_label="vs Janvier 2026"
        ),
        KPIData(
            label="Revenus",
            value="4 200.00 €",
            value_color="positive",
            icon="📈",
            icon_bg="#DBEAFE",
            variation="+5.0%",
            variation_label="vs Janvier 2026"
        ),
        KPIData(
            label="Épargne",
            value="200.00 €",
            value_color="positive",
            icon="🎯",
            icon_bg="#F3E8FF",
            variation=None,
            variation_label="🎉 Premier versement !"
        ),
    ]
