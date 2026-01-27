"""
UI Package
User interface components and layouts for Fin ancePerso.
"""

import streamlit as st

# Load CSS helper (copied from ui.py for backward compatibility)
def load_css():
    """Load custom CSS from assets/style.css"""
    with open("assets/style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

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

from .layout import render_app_info

__all__ = [
    'components',
    'validation',
    'dashboard',
    'config',
    'load_css',
    'card_kpi',
    'render_app_info',
]
