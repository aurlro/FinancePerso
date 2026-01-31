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
    
    # Inject PWA support and manifest
    _inject_pwa_support()


def _inject_pwa_support():
    """Inject PWA manifest and service worker registration."""
    import os
    
    # Manifest link
    st.markdown(
        '<link rel="manifest" href="/app/static/manifest.json">',
        unsafe_allow_html=True
    )
    
    # Theme color for mobile browsers
    st.markdown(
        '<meta name="theme-color" content="#0F172A">',
        unsafe_allow_html=True
    )
    
    # Apple touch icon
    st.markdown(
        '<link rel="apple-touch-icon" href="/app/static/favicon-192x192.png">',
        unsafe_allow_html=True
    )
    
    # Mobile viewport optimization
    st.markdown(
        '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">',
        unsafe_allow_html=True
    )
    
    # iOS standalone mode
    st.markdown(
        '<meta name="apple-mobile-web-app-capable" content="yes">',
        unsafe_allow_html=True
    )
    st.markdown(
        '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">',
        unsafe_allow_html=True
    )
    
    # Load PWA JavaScript
    try:
        pwa_js_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "pwa.js")
        if os.path.exists(pwa_js_path):
            with open(pwa_js_path) as f:
                pwa_js = f.read()
                st.markdown(f'<script>{pwa_js}</script>', unsafe_allow_html=True)
    except Exception:
        pass  # PWA JS is optional

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
