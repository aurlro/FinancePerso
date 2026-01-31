"""
UI Package
User interface components and layouts for Fin ancePerso.
"""

import streamlit as st

# Load CSS helper (copied from ui.py for backward compatibility)
def load_css():
    """Load custom CSS from assets/style.css and global styles"""
    # Load main CSS
    with open("assets/style.css") as f:
        main_css = f.read()
        st.markdown(f'<style>{main_css}</style>', unsafe_allow_html=True)
    
    # Load global component styles
    try:
        import os
        global_css_path = os.path.join(os.path.dirname(__file__), "styles", "global.css")
        with open(global_css_path) as f:
            global_css = f.read()
            st.markdown(f'<style>{global_css}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass  # Global CSS is optional

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
from .feedback import render_scroll_to_top

__all__ = [
    'components',
    'validation',
    'dashboard',
    'config',
    'load_css',
    'card_kpi',
    'render_app_info',
    'render_scroll_to_top',
]
