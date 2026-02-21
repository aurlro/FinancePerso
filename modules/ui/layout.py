"""
UI Layout Components (Legacy wrapper).
This module is deprecated. Use modules.ui_v2.templates.app_layout instead.
"""

import streamlit as st
import warnings

def render_app_info():
    """
    Renders the application version and changelog link in the sidebar directly.
    Should be called at the end of every page.
    """
    st.warning("⚠️ L'utilisation de `modules.ui.layout.render_app_info` est dépréciée. Veuillez utiliser `modules.ui_v2.templates.app_layout.render_app_info`.", icon="🔄")
    warnings.warn("modules.ui.layout is deprecated. Use modules.ui_v2.templates.app_layout instead.", DeprecationWarning, stacklevel=2)
    
    from modules.ui_v2.templates.app_layout import render_app_info as new_render_app_info
    return new_render_app_info()

__all__ = ["render_app_info"]
