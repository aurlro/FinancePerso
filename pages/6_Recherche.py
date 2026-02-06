import streamlit as st
from modules.ui import load_css, render_scroll_to_top
from modules.ui.layout import render_app_info
from modules.db.migrations import init_db
from modules.ui.global_search import render_global_search_full
from modules.ui.explorer import render_explorer_page

# Page config
st.set_page_config(
    page_title="Recherche & Exploration",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load styles
load_css()
init_db()

st.title("🔍 Recherche & Exploration")

# Get parameters from session state or URL (for Explorer)
explorer_type = st.session_state.get('_explorer_type') or st.query_params.get('type')
explorer_value = st.session_state.get('_explorer_value') or st.query_params.get('value')

# Determine starting tab
default_tab = "🔍 Recherche Globale"
if explorer_value:
    default_tab = "📂 Explorateur"

if 'research_active_tab' not in st.session_state:
    st.session_state['research_active_tab'] = default_tab

# Navigation
tabs_list = ["🔍 Recherche Globale", "📂 Explorateur"]
selected_tab = st.segmented_control(
    "Navigation",
    tabs_list,
    default=st.session_state['research_active_tab'],
    key="research_nav",
    label_visibility="collapsed"
)

if selected_tab and selected_tab != st.session_state['research_active_tab']:
    st.session_state['research_active_tab'] = selected_tab
    st.rerun()

st.divider()

active_tab = st.session_state['research_active_tab']

if active_tab == "🔍 Recherche Globale":
    render_global_search_full()

elif active_tab == "📂 Explorateur":
    # Explorer handling (from original 6_Explorer.py)
    explorer_type = st.session_state.pop('_explorer_type', None) or st.query_params.get('type', 'category')
    explorer_value = st.session_state.pop('_explorer_value', None) or st.query_params.get('value', '')
    from_page = st.session_state.pop('_explorer_from', None) or st.query_params.get('from', '6_Explorer')

    if not explorer_value:
        st.warning("⚠️ Aucune catégorie ou tag spécifié.")
        st.info("Utilisez le moteur de recherche ou cliquez sur 'Explorer' depuis vos graphiques.")
        
        # Quick links
        from modules.db.categories import get_categories
        categories = get_categories()[:6]
        cols = st.columns(3)
        for i, cat in enumerate(categories):
            with cols[i % 3]:
                if st.button(f"📂 {cat}", key=f"recherche_quick_cat_{i}", use_container_width=True):
                    st.query_params['type'] = 'category'
                    st.query_params['value'] = cat
                    st.rerun()
    else:
        render_explorer_page(
            explorer_type=explorer_type,
            explorer_value=explorer_value,
            from_page=from_page
        )

render_scroll_to_top()
render_app_info()
