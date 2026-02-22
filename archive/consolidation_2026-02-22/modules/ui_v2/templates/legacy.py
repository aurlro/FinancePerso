"""Legacy compatibility wrapper for customizable dashboard.

Ce module fournit une couche de compatibilité arrière pour le code
utilisant l'ancien module customizable_dashboard.py.

Tous les imports depuis modules.ui.dashboard.customizable_dashboard
devraient être migrés vers modules.ui_v2.templates.

Deprecated:
    Ce module sera supprimé dans une future version (v6.0+).
    Utilisez directement modules.ui_v2.templates à la place.

Examples:
    # Ancien import (déprécié)
    from modules.ui.dashboard.customizable_dashboard import DashboardLayoutManager

    # Nouvel import (recommandé)
    from modules.ui_v2.templates import DashboardLayoutManager
"""

import warnings
from typing import Any

# Import et ré-export depuis les nouveaux emplacements
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
    _get_column_width,
)

# Émettre un avertissement de dépréciation
warnings.warn(
    "modules.ui_v2.templates.legacy is deprecated. "
    "Import directly from modules.ui_v2.templates instead. "
    "This module will be removed in v6.0+",
    DeprecationWarning,
    stacklevel=2,
)

# ============================================================================
# Classes et fonctions pour compatibilité exacte
# ============================================================================


class LegacyDashboardLayoutManager(DashboardLayoutManager):
    """Version legacy du manager avec warnings supplémentaires.

    Cette classe étend DashboardLayoutManager pour ajouter des warnings
    lors de l'utilisation de méthodes dépréciées.
    """

    def __init__(self, layout_key: str = "dashboard_layout"):
        """Initialize avec warning de dépréciation."""
        warnings.warn(
            "LegacyDashboardLayoutManager is deprecated. "
            "Use DashboardLayoutManager from modules.ui_v2.templates.manager instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(layout_key)


def _deprecated_render_dashboard_configurator() -> Any:
    """Wrapper avec warning de dépréciation."""
    warnings.warn(
        "render_dashboard_configurator from legacy module is deprecated. "
        "Import from modules.ui_v2.templates.renderer instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return render_dashboard_configurator()


def _deprecated_render_customizable_overview(*args, **kwargs) -> Any:
    """Wrapper avec warning de dépréciation."""
    warnings.warn(
        "render_customizable_overview from legacy module is deprecated. "
        "Import from modules.ui_v2.templates.renderer instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return render_customizable_overview(*args, **kwargs)


# ============================================================================
# Exports pour compatibilité exacte avec l'ancien module
# ============================================================================

__all__ = [
    # Classes principales
    "DashboardLayoutManager",
    "DashboardWidget",
    "WidgetType",
    # Constantes
    "LAYOUT_TEMPLATES",
    "DEFAULT_LAYOUT",
    # Fonctions de rendu
    "render_dashboard_configurator",
    "render_customizable_overview",
    "_get_column_width",
    # Legacy spécifique
    "LegacyDashboardLayoutManager",
]
