"""
🤖 Assistant IA - Votre conseiller financier intelligent.

Page refactorisée avec architecture propre :
- Dashboard : Vue d'accueil avec métriques et actions rapides
- Analytics : Analyse approfondie avec chat intégré
- Audit : Contrôle qualité des données
- Config : Paramétrage de l'IA
"""

import streamlit as st

from modules.db.migrations import init_db
from modules.ui import load_css, render_scroll_to_top
from modules.ui.assistant.state import init_assistant_state

# Page config
st.set_page_config(page_title="Assistant IA", page_icon="🤖", layout="wide")

# Initialize
load_css()
init_db()
init_assistant_state()

# Title
st.title("🤖 Assistant IA")
st.markdown("Votre conseiller financier intelligent.")

# Tab options
TAB_OPTIONS = ["🏠 Tableau de bord", "📊 Analytics", "🎯 Audit", "⚙️ Configuration"]
TAB_KEYS = ["dashboard", "analytics", "audit", "config"]
TAB_KEY_MAP = dict(zip(TAB_KEYS, TAB_OPTIONS))

# Handle query params for tab switching (before rendering)
query_tab = st.query_params.get("tab")
if query_tab and query_tab in TAB_KEYS:
    st.session_state["assistant_active_tab"] = TAB_KEY_MAP[query_tab]
    del st.query_params["tab"]

# Initialize active tab in session state
if "assistant_active_tab" not in st.session_state:
    st.session_state["assistant_active_tab"] = "🏠 Tableau de bord"

# Navigation with segmented control (allows programmatic switching)
selected_tab = st.segmented_control(
    "assistant_nav",
    options=TAB_OPTIONS,
    default=st.session_state["assistant_active_tab"],
    label_visibility="collapsed",
)

# Update session state when user clicks
if selected_tab != st.session_state["assistant_active_tab"]:
    st.session_state["assistant_active_tab"] = selected_tab
    st.rerun()

active_tab = st.session_state["assistant_active_tab"]

# Import tab renderers
from modules.ui.assistant.analytics_tab import render_analytics_tab
from modules.ui.assistant.audit_tab import render_audit_tab
from modules.ui.assistant.config_tab import render_config_tab
from modules.ui.assistant.dashboard_tab import render_dashboard_tab


def switch_to_tab(tab_key: str):
    """Switch to specified tab."""
    if tab_key in TAB_KEY_MAP:
        st.session_state["assistant_active_tab"] = TAB_KEY_MAP[tab_key]
        st.rerun()


# Render active tab content
if active_tab == "🏠 Tableau de bord":
    render_dashboard_tab(
        on_launch_audit=lambda: switch_to_tab("audit"),
        on_view_analytics=lambda: switch_to_tab("analytics"),
        on_open_chat=lambda: switch_to_tab("analytics"),
        on_view_audit=lambda: switch_to_tab("audit"),
    )
elif active_tab == "📊 Analytics":
    render_analytics_tab()
elif active_tab == "🎯 Audit":
    render_audit_tab()
elif active_tab == "⚙️ Configuration":
    render_config_tab()

# Footer
st.divider()
from modules.ui.layout import render_app_info

render_app_info()

render_scroll_to_top()
