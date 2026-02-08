import streamlit as st
from modules.ui import load_css, render_scroll_to_top
from modules.db.migrations import init_db
from modules.ui.importing.main import render_import_tab
from modules.ui.validation.main import render_validation_tab
from modules.ui.components.tooltips import render_contextual_help, IMPORT_HELP, VALIDATION_HELP

st.set_page_config(page_title="Opérations", page_icon="🧾", layout="wide")
load_css()
init_db()

# --- CSS FOR TABS-LIKE RADIO ---
st.markdown("""
<style>
    div[data-testid="stHorizontalBlock"] {
        background-color: #f8fafc;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# State management for tab switching
if 'active_op_tab' not in st.session_state:
    st.session_state['active_op_tab'] = "📥 Importation"

# Auto-switch to Validation if just imported
if st.session_state.get('just_imported'):
    st.session_state['active_op_tab'] = "✅ Validation"
    st.session_state['just_imported'] = False

st.title("🧾 Opérations")

# Navigation
tabs = ["📥 Importation", "✅ Validation"]
idx = tabs.index(st.session_state['active_op_tab'])

selected_tab = st.segmented_control(
    "Flux de travail", 
    tabs, 
    default=st.session_state['active_op_tab'],
    key="ops_navigation",
    label_visibility="collapsed"
)

# Update state if changed
if selected_tab and selected_tab != st.session_state['active_op_tab']:
    st.session_state['active_op_tab'] = selected_tab
    st.rerun()

# Render selected content
if st.session_state['active_op_tab'] == "📥 Importation":
    render_import_tab()
    # Contextual help
    render_contextual_help({"📥 Guide d'importation": IMPORT_HELP})
else:
    render_validation_tab()
    # Contextual help
    render_contextual_help({"✅ Conseils de validation": VALIDATION_HELP})

render_scroll_to_top()

from modules.ui.layout import render_app_info
render_app_info()
