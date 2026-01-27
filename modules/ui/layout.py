"""
UI Layout Components.
"""
import streamlit as st
def render_app_info():
    """
    Renders the application version and changelog link in the sidebar directly.
    Should be called at the end of every page.
    """
    try:
        from modules.constants import APP_VERSION
    except ImportError:
        # Fallback if the name is somehow missing during reload
        import modules.constants
        APP_VERSION = getattr(modules.constants, 'APP_VERSION', '0.x.x')
    
    with st.sidebar:
        st.divider()
        c1, c2 = st.columns([3, 1])
        c1.caption(f"v{APP_VERSION}")
        if c2.button("ℹ️", key="btn_changelog_sidebar", help="Nouveautés"):
            st.switch_page("pages/10_Nouveautés.py")
