"""Controllers de pages V5.5.

Ce module contient les controllers pour les pages de l'application V5.5.
Les controllers gèrent la logique métier et la coordination entre les vues.

Usage:
    from modules.ui.v5_5.pages import DashboardController

    controller = DashboardController()
    controller.render()
"""

from .dashboard_controller import DashboardController

__all__ = ["DashboardController"]
