"""Composants UI pour la Couple Edition."""

from modules.ui.couple.dashboard import render_couple_dashboard, render_couple_summary_embedded
from modules.ui.couple.loans_view import render_loans_section, render_loans_tab
from modules.ui.couple.setup_wizard import render_couple_setup
from modules.ui.couple.widgets import (
    render_confidentiality_badge,
    render_personal_card,
    render_transfer_section,
)

__all__ = [
    "render_couple_setup",
    "render_couple_dashboard",
    "render_couple_summary_embedded",
    "render_loans_section",
    "render_loans_tab",
    "render_personal_card",
    "render_transfer_section",
    "render_confidentiality_badge",
]
