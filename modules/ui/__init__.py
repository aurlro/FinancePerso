
"""
UI Module - Design System et composants
========================================

Ce module contient le design system et les composants UI réutilisables.

Usage:
    from modules.ui import DesignSystem, apply_vibe_theme
    apply_vibe_theme()
"""

import streamlit as st

from modules.ui.design_system import (
    DesignSystem,
    ColorScheme,
    Typography,
    Spacing,
    Animation,
    apply_vibe_theme,
    vibe_container,
    vibe_metric,
    vibe_badge,
)
from modules.ui.feedback import (
    render_scroll_to_top,
    display_flash_messages,
    toast_success,
    toast_warning,
)


def load_css():
    """Charge le CSS personnalisé depuis assets/style.css"""
    try:
        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass


def card_kpi(title, value, trend=None, trend_color="positive"):
    """
    Renders a custom HTML card for key metrics.
    trend: str (e.g. "+12%")
    trend_color: "positive" (green) or "negative" (red)
    """
    trend_html = ""
    if trend:
        color_class = "card-trend-positive" if trend_color == "positive" else "card-trend-negative"
        icon = "↗" if trend_color == "positive" else "↘"
        trend_html = f'<div class="{color_class}">{icon} {trend}</div>'

    html = f"""
    <div class="custom-card">
        <div class="card-title">{title}</div>
        <div class="card-value">{value}</div>
        {trend_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


__all__ = [
    'DesignSystem',
    'ColorScheme',
    'Typography',
    'Spacing',
    'Animation',
    'apply_vibe_theme',
    'vibe_container',
    'vibe_metric',
    'vibe_badge',
    'load_css',
    'card_kpi',
    'render_scroll_to_top',
    'display_flash_messages',
    'toast_success',
    'toast_warning',
]
