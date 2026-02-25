"""
🧠 Automatisation - Centre de contrôle IA

Nouvelle architecture centrée sur les cas d'usage :
- 📥 INBOX : Tout ce qui demande votre attention (récurrences + suggestions + alertes)
- ⚙️ RÈGLES : Configuration de l'automatisation (catégorisation + abonnements)
- 📊 HISTORIQUE : Traçabilité et contrôle

Objectif : Une seule page pour tout ce qui concerne l'automatisation intelligente.
"""

import streamlit as st

from modules.db.migrations import init_db
from modules.db.recurrence_feedback import init_recurrence_feedback_table
from modules.ui import load_css, render_scroll_to_top
from modules.ui.automation import render_history_tab, render_inbox_tab, render_rules_tab
from modules.ui.layout import render_app_info

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Automatisation",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialisation
load_css()
init_db()
init_recurrence_feedback_table()

# =============================================================================
# HEADER
# =============================================================================

st.title("🧠 Automatisation")
st.markdown("""
Centre de contrôle pour l'automatisation de vos finances. 
L'IA analyse vos transactions et vous propose des actions.
""")

# =============================================================================
# NAVIGATION PRINCIPALE
# =============================================================================

# Handle query params pour navigation externe
query_tab = st.query_params.get("tab")
if query_tab:
    st.session_state["automation_tab"] = query_tab
    del st.query_params["tab"]

# Default tab
if "automation_tab" not in st.session_state:
    st.session_state["automation_tab"] = "📥 Inbox"

# Segmented control pour la navigation principale (plus moderne que tabs)
# Note: On garde les options fixes pour éviter les problèmes de synchro avec session_state
tabs_options = ["📥 Inbox", "⚙️ Règles", "📊 Historique"]

# S'assurer que la valeur par défaut est valide
current_tab = st.session_state.get("automation_tab", "📥 Inbox")
if current_tab not in tabs_options:
    current_tab = "📥 Inbox"
    st.session_state["automation_tab"] = current_tab

selected_tab = st.segmented_control(
    "Navigation",
    options=tabs_options,
    default=current_tab,
    key="automation_nav",
    label_visibility="collapsed",
)

if selected_tab:
    st.session_state["automation_tab"] = selected_tab

st.divider()

# =============================================================================
# RENDU DES ONGLETS
# =============================================================================

current_tab = st.session_state["automation_tab"]

if current_tab == "📥 Inbox":
    render_inbox_tab()

elif current_tab == "⚙️ Règles":
    render_rules_tab()

elif current_tab == "📊 Historique":
    render_history_tab()

# =============================================================================
# FOOTER
# =============================================================================

st.divider()
render_app_info()
render_scroll_to_top()
