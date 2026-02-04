"""
UI Package
User interface components and layouts for FinancePerso.
"""

import streamlit as st


# Load CSS helper (copied from ui.py for backward compatibility)
def load_css():
    """Load custom CSS from assets/style.css and global styles"""
    # Load main CSS
    with open("assets/style.css") as f:
        main_css = f.read()
        st.markdown(f"<style>{main_css}</style>", unsafe_allow_html=True)
    
    # Load global component styles
    try:
        import os
        global_css_path = os.path.join(os.path.dirname(__file__), "styles", "global.css")
        with open(global_css_path) as f:
            global_css = f.read()
            st.markdown(f"<style>{global_css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass  # Global CSS is optional
    
    # Inject PWA support and manifest
    _inject_pwa_support()


def _inject_pwa_support():
    """Inject PWA manifest and service worker registration."""
    pwa_meta = """
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#1a1a2e">
    <script>
    if ("serviceWorker" in navigator) {
        navigator.serviceWorker.register("service-worker.js")
            .then(reg => console.log("SW registered"))
            .catch(err => console.log("SW registration failed"));
    }
    </script>
    """
    st.markdown(pwa_meta, unsafe_allow_html=True)


# Import commonly used UI functions for convenience
from .feedback import (
    toast_success, toast_error, toast_warning, toast_info,
    show_success, show_error, show_warning, show_info,
    show_rich_success,
    validation_feedback,
    celebrate_all_done,
    confirm_dialog,
    render_scroll_to_top,
    display_flash_messages
)
from .layout import render_app_info

# Import from legacy ui.py module for backward compatibility
try:
    import importlib.util
    import sys
    import os
    
    # Load card_kpi from the legacy ui.py file (not the package)
    legacy_ui_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ui.py')
    if os.path.exists(legacy_ui_path):
        spec = importlib.util.spec_from_file_location("legacy_ui", legacy_ui_path)
        legacy_ui = importlib.util.module_from_spec(spec)
        sys.modules["legacy_ui"] = legacy_ui
        spec.loader.exec_module(legacy_ui)
        card_kpi = legacy_ui.card_kpi
    else:
        card_kpi = None
except Exception:
    card_kpi = None


# Export all for easy importing
__all__ = [
    # CSS
    "load_css",
    # Feedback
    "toast_success", "toast_error", "toast_warning", "toast_info",
    "show_success", "show_error", "show_warning", "show_info",
    "show_rich_success",
    "validation_feedback",
    "celebrate_all_done",
    "confirm_dialog",
    "render_scroll_to_top",
    "display_flash_messages",
    # Layout
    "render_app_info",
    # Components
    "card_kpi",
]
