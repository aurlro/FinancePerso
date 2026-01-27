import streamlit as st
from modules.ui import load_css
from modules.data_manager import init_db
from modules.ui.config.api_settings import render_api_settings
from modules.ui.config.member_management import render_member_management
from modules.ui.config.category_management import render_category_management
from modules.ui.config.tags_rules import render_tags_rules
from modules.ui.config.audit_tools import render_audit_tools
from modules.ui.config.data_operations import render_data_operations
from modules.ui.config.backup_restore import render_backup_restore
from modules.ui.config.log_viewer import render_log_viewer

# Page Setup
st.set_page_config(page_title="Configuration", page_icon="⚙️")
load_css()
init_db()  # Ensure tables exist

st.title("⚙️ Configuration")

# Create tabs
tabs = st.tabs([
    "🔑 API & Services",
    "🏠 Foyer & Membres",
    "🏷️ Catégories",
    "🧠 Tags & Règles",
    "🧹 Audit & Nettoyage",
    "💾 Données & Danger",
    "💾 Sauvegardes",
    "📑 Logs"
])

# Render each tab with its component
with tabs[0]:
    render_api_settings()

with tabs[1]:
    render_member_management()

with tabs[2]:
    render_category_management()

with tabs[3]:
    render_tags_rules()

with tabs[4]:
    render_audit_tools()

with tabs[5]:
    render_data_operations()

with tabs[6]:
    render_backup_restore()

with tabs[7]:
    render_log_viewer()

from modules.ui import render_app_info
render_app_info()
