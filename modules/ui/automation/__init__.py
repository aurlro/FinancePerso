"""
🧠 Automation UI Components

Nouvelle architecture centrée sur les cas d'usage :
- 📥 Inbox : Tout ce qui demande une action
- ⚙️ Règles : Configuration de l'automatisation
- 📊 Historique : Traçabilité et contrôle

Principes :
- Actions directes (pas de redirection)
- Langage utilisateur (pas de jargon)
- Progressive disclosure
"""

from .alerts_section import (
    detect_price_increases,
    detect_zombie_subscriptions,
    render_alerts_section,
    render_remaining_budget_calculator,
)
from .history_tab import render_history_tab
from .inbox_tab import get_inbox_count, render_inbox_tab
from .rules_tab import render_rules_tab

__all__ = [
    "render_inbox_tab",
    "render_rules_tab",
    "render_history_tab",
    "get_inbox_count",
    "render_alerts_section",
    "render_remaining_budget_calculator",
    "detect_zombie_subscriptions",
    "detect_price_increases",
]
