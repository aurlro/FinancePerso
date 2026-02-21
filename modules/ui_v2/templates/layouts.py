"""Layout Templates for Dashboard UI v2.

Définit les templates de layouts prédéfinis et les structures de données
pour les widgets du dashboard.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from modules.logger import logger
from modules.ui_v2.atoms.icons import IconSet


class WidgetType(Enum):
    """Types de widgets disponibles pour le dashboard."""

    # KPIs
    KPI_DEPENSES = "kpi_depenses"
    KPI_REVENUS = "kpi_revenus"
    KPI_SOLDE = "kpi_solde"
    KPI_EPARGNE = "kpi_epargne"

    # Charts
    EVOLUTION_CHART = "evolution_chart"
    SAVINGS_TREND = "savings_trend"
    CATEGORIES_CHART = "categories_chart"
    MONTHLY_STACKED = "monthly_stacked"

    # Lists & Tables
    TOP_EXPENSES = "top_expenses"

    # Budget
    BUDGET_TRACKER = "budget_tracker"
    BUDGET_ALERTS = "budget_alerts"

    # Intelligence
    SMART_RECOMMENDATIONS = "smart_recommendations"
    AI_INSIGHTS = "ai_insights"

    # Analyses avancées
    MEMBERS_ANALYSIS = "members_analysis"
    TIERS_ANALYSIS = "tiers_analysis"
    TAGS_ANALYSIS = "tags_analysis"


@dataclass
class DashboardWidget:
    """Représente un widget du dashboard.

    Attributes:
        id: Identifiant unique du widget
        type: Type de widget (WidgetType)
        title: Titre affiché du widget
        position: Position dans le layout (1-based)
        size: Taille du widget ('small', 'medium', 'large', 'full')
        visible: Si le widget est visible
        config: Configuration additionnelle (dict)
    """

    id: str
    type: WidgetType
    title: str
    position: int
    size: str
    visible: bool = True
    config: dict = field(default_factory=dict)

    def __post_init__(self):
        """Initialisation post-construction."""
        if self.config is None:
            self.config = {}

    def to_dict(self) -> dict[str, Any]:
        """Convertit le widget en dictionnaire pour JSON/DB.

        Returns:
            Dictionnaire représentant le widget
        """
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "position": self.position,
            "size": self.size,
            "visible": self.visible,
            "config": self.config,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DashboardWidget":
        """Crée un widget depuis un dictionnaire.

        Args:
            data: Dictionnaire contenant les données du widget

        Returns:
            Instance de DashboardWidget
        """
        type_val = data.get("type", "kpi_depenses")

        # Gérer différents types d'entrée pour le type
        if isinstance(type_val, WidgetType):
            widget_type = type_val
        elif isinstance(type_val, str):
            try:
                widget_type = WidgetType(type_val)
            except ValueError:
                logger.warning(f"Unknown widget type '{type_val}', using default")
                widget_type = WidgetType.KPI_DEPENSES
        else:
            logger.warning(f"Unexpected type '{type(type_val)}' for widget type, using default")
            widget_type = WidgetType.KPI_DEPENSES

        return cls(
            id=data.get("id", "unknown"),
            type=widget_type,
            title=data.get("title", "Widget"),
            position=data.get("position", 0),
            size=data.get("size", "small"),
            visible=data.get("visible", True),
            config=data.get("config", {}),
        )

    def copy(self) -> "DashboardWidget":
        """Crée une copie du widget.

        Returns:
            Nouvelle instance identique
        """
        return DashboardWidget(
            id=self.id,
            type=self.type,
            title=self.title,
            position=self.position,
            size=self.size,
            visible=self.visible,
            config=self.config.copy(),
        )


# ============================================================================
# TEMPLATES DE LAYOUTS PRÉDÉFINIS
# ============================================================================

LAYOUT_TEMPLATES: dict[str, dict[str, Any]] = {
    "essentiel": {
        "name": f"{IconSet.HOME.value} Essentiel",
        "description": "Les métriques clés uniquement - rapide et léger",
        "icon": IconSet.HOME,
        "widgets": [
            DashboardWidget("kpi_1", WidgetType.KPI_DEPENSES, f"{IconSet.MONEY.value} Dépenses", 1, "small"),
            DashboardWidget("kpi_2", WidgetType.KPI_REVENUS, f"{IconSet.CREDIT_CARD.value} Revenus", 2, "small"),
            DashboardWidget("kpi_3", WidgetType.KPI_SOLDE, f"{IconSet.CHART.value} Solde", 3, "small"),
            DashboardWidget("kpi_4", WidgetType.KPI_EPARGNE, f"{IconSet.TARGET.value} Taux d'épargne", 4, "small"),
            DashboardWidget("evol_1", WidgetType.EVOLUTION_CHART, f"{IconSet.TREND_UP.value} Évolution", 5, "large"),
            DashboardWidget("cat_1", WidgetType.CATEGORIES_CHART, f"{IconSet.PIE_CHART.value} Répartition", 6, "medium"),
        ],
    },
    "analytique": {
        "name": f"{IconSet.CHART.value} Analytique",
        "description": "Vue complète avec analyses détaillées",
        "icon": IconSet.CHART,
        "widgets": [
            DashboardWidget("kpi_1", WidgetType.KPI_DEPENSES, f"{IconSet.MONEY.value} Dépenses", 1, "small"),
            DashboardWidget("kpi_2", WidgetType.KPI_REVENUS, f"{IconSet.CREDIT_CARD.value} Revenus", 2, "small"),
            DashboardWidget("kpi_3", WidgetType.KPI_SOLDE, f"{IconSet.CHART.value} Solde", 3, "small"),
            DashboardWidget("kpi_4", WidgetType.KPI_EPARGNE, f"{IconSet.TARGET.value} Taux d'épargne", 4, "small"),
            DashboardWidget("evol_1", WidgetType.EVOLUTION_CHART, f"{IconSet.TREND_UP.value} Évolution", 5, "large"),
            DashboardWidget("sav_1", WidgetType.SAVINGS_TREND, f"{IconSet.TREND_UP.value} Tendance épargne", 6, "medium"),
            DashboardWidget("cat_1", WidgetType.CATEGORIES_CHART, f"{IconSet.PIE_CHART.value} Répartition", 7, "medium"),
            DashboardWidget("top_1", WidgetType.TOP_EXPENSES, f"{IconSet.FIRE.value} Top dépenses", 8, "medium"),
            DashboardWidget("month_1", WidgetType.MONTHLY_STACKED, f"{IconSet.CALENDAR.value} Évolution mensuelle", 9, "large"),
        ],
    },
    "budget": {
        "name": f"{IconSet.TARGET.value} Budget",
        "description": "Focus sur le suivi des budgets et alertes",
        "icon": IconSet.TARGET,
        "widgets": [
            DashboardWidget("kpi_1", WidgetType.KPI_DEPENSES, f"{IconSet.MONEY.value} Dépenses", 1, "small"),
            DashboardWidget("kpi_4", WidgetType.KPI_EPARGNE, f"{IconSet.TARGET.value} Taux d'épargne", 2, "small"),
            DashboardWidget("budget_1", WidgetType.BUDGET_TRACKER, f"{IconSet.CREDIT_CARD.value} Suivi budgets", 3, "large"),
            DashboardWidget("alert_1", WidgetType.BUDGET_ALERTS, f"{IconSet.ALERT.value} Alertes", 4, "medium"),
            DashboardWidget("rec_1", WidgetType.SMART_RECOMMENDATIONS, f"{IconSet.LIGHTBULB.value} Recommandations", 5, "medium"),
            DashboardWidget("cat_1", WidgetType.CATEGORIES_CHART, f"{IconSet.PIE_CHART.value} Répartition", 6, "medium"),
        ],
    },
    "complet": {
        "name": f"{IconSet.MAGIC.value} Complet",
        "description": "Tous les widgets disponibles",
        "icon": IconSet.MAGIC,
        "widgets": [
            DashboardWidget("kpi_1", WidgetType.KPI_DEPENSES, f"{IconSet.MONEY.value} Dépenses", 1, "small"),
            DashboardWidget("kpi_2", WidgetType.KPI_REVENUS, f"{IconSet.CREDIT_CARD.value} Revenus", 2, "small"),
            DashboardWidget("kpi_3", WidgetType.KPI_SOLDE, f"{IconSet.CHART.value} Solde", 3, "small"),
            DashboardWidget("kpi_4", WidgetType.KPI_EPARGNE, f"{IconSet.TARGET.value} Taux d'épargne", 4, "small"),
            DashboardWidget("evol_1", WidgetType.EVOLUTION_CHART, f"{IconSet.TREND_UP.value} Évolution", 5, "large"),
            DashboardWidget("sav_1", WidgetType.SAVINGS_TREND, f"{IconSet.TREND_UP.value} Tendance épargne", 6, "medium"),
            DashboardWidget("cat_1", WidgetType.CATEGORIES_CHART, f"{IconSet.PIE_CHART.value} Répartition", 7, "medium"),
            DashboardWidget("top_1", WidgetType.TOP_EXPENSES, f"{IconSet.FIRE.value} Top dépenses", 8, "medium"),
            DashboardWidget("month_1", WidgetType.MONTHLY_STACKED, f"{IconSet.CALENDAR.value} Évolution mensuelle", 9, "large"),
            DashboardWidget("budget_1", WidgetType.BUDGET_TRACKER, f"{IconSet.CREDIT_CARD.value} Suivi budgets", 10, "large"),
            DashboardWidget("alert_1", WidgetType.BUDGET_ALERTS, f"{IconSet.ALERT.value} Alertes", 11, "medium"),
            DashboardWidget("rec_1", WidgetType.SMART_RECOMMENDATIONS, f"{IconSet.LIGHTBULB.value} Recommandations", 12, "medium"),
        ],
    },
}

# Layout par défaut (template essentiel)
DEFAULT_LAYOUT: list[DashboardWidget] = LAYOUT_TEMPLATES["essentiel"]["widgets"]


__all__ = [
    "WidgetType",
    "DashboardWidget",
    "LAYOUT_TEMPLATES",
    "DEFAULT_LAYOUT",
]
