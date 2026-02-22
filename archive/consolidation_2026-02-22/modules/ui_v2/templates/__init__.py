"""Dashboard Templates for UI v2.

Système de templates pour le dashboard personnalisable avec widgets déplaçables.

Ce module fournit:
    - WidgetType: Enum des types de widgets disponibles
    - DashboardWidget: Dataclass représentant un widget
    - DashboardLayoutManager: Gestionnaire de layout avec mode Preview
    - LAYOUT_TEMPLATES: Templates prédéfinis (Essentiel, Analytique, Budget, Complet)
    - render_dashboard_configurator: Interface de configuration
    - render_customizable_overview: Rendu du dashboard

Examples:
    >>> from modules.ui_v2.templates import DashboardLayoutManager, WidgetType
    >>>
    >>> # Créer un manager
    >>> manager = DashboardLayoutManager()
    >>>
    >>> # Démarrer le mode preview
    >>> manager.start_preview()
    >>>
    >>> # Récupérer le layout actuel
    >>> widgets = manager.get_layout()
    >>>
    >>> # Déplacer un widget
    >>> manager.move_widget("kpi_1", 2)
    >>>
    >>> # Appliquer les changements
    >>> manager.apply_preview("mon_layout")
"""

from modules.ui_v2.templates.layouts import (
    WidgetType,
    DashboardWidget,
    LAYOUT_TEMPLATES,
    DEFAULT_LAYOUT,
)
from modules.ui_v2.templates.manager import DashboardLayoutManager
from modules.ui_v2.templates.renderer import (
    render_dashboard_configurator,
    render_customizable_overview,
)

# Version du module
__version__ = "2.0.0"

__all__ = [
    # Classes de données
    "WidgetType",
    "DashboardWidget",
    # Gestionnaire
    "DashboardLayoutManager",
    # Templates
    "LAYOUT_TEMPLATES",
    "DEFAULT_LAYOUT",
    # Fonctions de rendu
    "render_dashboard_configurator",
    "render_customizable_overview",
]
