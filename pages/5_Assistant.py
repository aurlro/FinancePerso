"""
🤖 Assistant IA - Votre conseiller financier intelligent.

Page refactorisée avec architecture propre :
- Dashboard : Vue d'accueil avec métriques et actions rapides
- Analytics : Analyse approfondie avec chat intégré
- Audit : Contrôle qualité des données
- Config : Paramétrage de l'IA
"""
import streamlit as st
from modules.ui import load_css, render_scroll_to_top
from modules.db.migrations import init_db
from modules.ui.assistant.state import init_assistant_state

# Page config
st.set_page_config(
    page_title="Assistant IA",
    page_icon="🤖",
    layout="wide"
)

# Initialize
load_css()
init_db()
init_assistant_state()

# Title
st.title("🤖 Assistant IA")
st.markdown("Votre conseiller financier intelligent.")

# Navigation tabs
tab_dashboard, tab_analytics, tab_audit, tab_config = st.tabs([
    "🏠 Tableau de bord",
    "📊 Analytics",
    "🎯 Audit",
    "⚙️ Configuration"
])

# Import tab renderers
from modules.ui.assistant.dashboard_tab import render_dashboard_tab
from modules.ui.assistant.analytics_tab import render_analytics_tab
from modules.ui.assistant.audit_tab import render_audit_tab
from modules.ui.assistant.config_tab import render_config_tab

# Render tabs
with tab_dashboard:
    render_dashboard_tab(
        on_launch_audit=lambda: switch_to_tab("audit"),
        on_view_analytics=lambda: switch_to_tab("analytics"),
        on_open_chat=lambda: switch_to_tab("analytics"),
        on_view_audit=lambda: switch_to_tab("audit")
    )

with tab_analytics:
    render_analytics_tab()

with tab_audit:
    render_audit_tab()

with tab_config:
    render_config_tab()

# Helper function for tab switching
def switch_to_tab(tab_name: str):
    """Switch to specified tab using query params or session state."""
    st.query_params['tab'] = tab_name
    st.rerun()

# Handle query params for tab switching
query_tab = st.query_params.get('tab')
if query_tab:
    # Clear param to avoid loops
    del st.query_params['tab']
    # Note: Actual tab switching in Streamlit requires JS or st.rerun with state

# Footer
st.divider()
from modules.ui.layout import render_app_info
render_app_info()

render_scroll_to_top()
