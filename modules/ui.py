import streamlit as st

def load_css():
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

def render_app_info():
    """
    Renders the application version and changelog link in the sidebar directly.
    Should be called at the end of every page.
    """
    from modules.constants import APP_VERSION
    
    with st.sidebar:
        st.divider()
        c1, c2 = st.columns([3, 1])
        c1.caption(f"v{APP_VERSION}")
        if c2.button("ℹ️", key="btn_changelog_sidebar", help="Nouveautés"):
            st.switch_page("pages/10_Nouveautés.py")
