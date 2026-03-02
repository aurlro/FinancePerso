import streamlit as st

from modules.db.migrations import init_db
from modules.ui import load_css, render_scroll_to_top
from modules.ui.components.local_ml_manager import render_local_ml_section, render_ml_mode_selector
from modules.ui.config.api_settings import render_api_settings
from modules.ui.config.audit_tools import render_audit_tools
from modules.ui.config.backup_restore import render_backup_restore
from modules.ui.config.category_management import render_category_management
from modules.ui.config.recycle_bin import render_recycle_bin_manager
from modules.ui.config.config_dashboard import render_config_dashboard
from modules.ui.config.config_mode import (
    is_advanced_mode,
    render_mode_toggle,
    render_simple_mode_help,
)
from modules.ui.config.data_operations import render_export_section
from modules.ui.config.log_viewer import render_log_viewer
from modules.ui.config.member_management import render_member_management
from modules.ui.config.notifications import render_notification_settings
from modules.ui.couple.setup_wizard import render_couple_setup
from modules.ui.feedback import display_flash_messages, toast_info

# Page Setup
st.set_page_config(page_title="⚙️ Paramètres", page_icon="⚙️", layout="wide")
load_css()
init_db()  # Ensure tables exist

# Afficher les messages flash en attente
display_flash_messages()

st.title("⚙️ Paramètres")
toast_info("Page de configuration chargée", icon="⚙️")

# --- MODE TOGGLE (Simple vs Advanced) ---
render_mode_toggle()
render_simple_mode_help()
st.divider()

# Handle jump-to from dashboard
jump_to = st.session_state.get("config_jump_to", None)

# Create tabs based on mode
if is_advanced_mode():
    # Full tabs in advanced mode
    tab_labels = [
        "🏠 Vue d'ensemble",
        "👤 Profil",
        "💑 Couple",
        "🤖 IA & Services",
        "🔧 Maintenance",
    ]
else:
    # Simplified tabs in simple mode
    tab_labels = ["🏠 Vue d'ensemble", "👤 Profil", "💑 Couple", "🤖 IA & Services"]

# Set default tab if jump requested
default_index = 0
if jump_to:
    try:
        default_index = tab_labels.index(jump_to)
        del st.session_state["config_jump_to"]
    except ValueError:
        pass

tabs = st.tabs(tab_labels)

# --- TAB 1: DASHBOARD ---
with tabs[0]:
    render_config_dashboard()

# --- TAB 2: PROFILE (Members + Categories) ---
with tabs[1]:
    st.header("👤 Configuration du Profil")

    # Members Section
    st.subheader("Membres du foyer", divider="blue")
    render_member_management()

    st.divider()

    # Categories Section
    st.subheader("Catégories de dépenses", divider="blue")
    render_category_management()

# --- TAB 3: COUPLE ---
with tabs[2]:
    render_couple_setup()

# --- TAB 4: AI & SERVICES (API + ML Local + Notifications) ---
with tabs[3]:
    st.header("🤖 Intelligence Artificielle")
    st.markdown("Configurez les services de catégorisation et notifications.")

    # ML Mode Selector
    st.subheader("Mode de catégorisation", divider="blue")

    # Offline Mode Toggle
    from modules.feature_flags import get_feature_manager

    fm = get_feature_manager()
    is_offline = fm.is_enabled("FORCE_OFFLINE_MODE")

    col_off, col_help = st.columns([1, 2])
    with col_off:
        if st.checkbox(
            "🚫 Mode Hors-ligne Forcé",
            value=is_offline,
            help="Interdit tout appel aux APIs externes (IA Cloud). L'application utilisera uniquement les règles et le modèle local.",
        ):
            if not is_offline:
                fm.enable("FORCE_OFFLINE_MODE", "User forced offline mode")
                st.rerun()
        else:
            if is_offline:
                fm.disable("FORCE_OFFLINE_MODE")
                st.rerun()

    if is_offline:
        st.warning(
            "⚠️ Mode Hors-ligne activé : Aucune donnée ne sera envoyée vers les services d'IA externe."
        )

    ml_mode = render_ml_mode_selector()

    st.divider()

    # Local ML Section
    st.subheader("🧠 Modèle ML Local (Offline)", divider="blue")
    render_local_ml_section()

    st.divider()

    # API Settings (Cloud AI)
    st.subheader("☁️ IA Cloud (API Externe)", divider="blue")
    render_api_settings()

    st.divider()

    # Notifications
    st.header("🔔 Notifications")
    st.markdown("Recevez des alertes pour les dépassements de budget.")
    st.subheader("Paramètres des alertes", divider="blue")
    render_notification_settings()

# --- TAB 5: MAINTENANCE (Advanced only) ---
if is_advanced_mode():
    with tabs[4]:
        st.header("🔧 Maintenance et Outils")

        # Export Section (extracted from data_operations)
        st.subheader("📤 Export des données", divider="blue")
        render_export_section()

        st.divider()

        # Audit Tools
        st.subheader("🧹 Audit & Nettoyage", divider="blue")
        render_audit_tools()

        st.divider()

        # Backups
        col_back1, col_back2 = st.columns([1, 1])

        with col_back1:
            st.subheader("💾 Sauvegardes", divider="blue")
            render_backup_restore()

        with col_back2:
            st.subheader("📑 Logs système", divider="blue")
            render_log_viewer()

        # Recycle Bin
        st.divider()
        render_recycle_bin_manager()

render_scroll_to_top()
from modules.ui.layout import render_app_info

render_app_info()
