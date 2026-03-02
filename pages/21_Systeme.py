import subprocess

import pandas as pd
import streamlit as st

from modules.db.connection import get_db_connection
from modules.db.migrations import init_db
from modules.notifications import NotificationService
from modules.notifications.ui import (
    render_notification_center,
    render_notification_settings,
)
from modules.ui import load_css, render_scroll_to_top
from modules.ui.layout import render_app_info

# Page setup
st.set_page_config(page_title="Système", page_icon="⚙️", layout="wide")
load_css()
init_db()

st.title("🛠️ Système & Administration")

if "system_active_tab" not in st.session_state:
    st.session_state["system_active_tab"] = "🧪 Tests"

tabs_list = ["🧪 Tests", "🐞 Debug", "🔔 Notifications"]
selected_tab = st.segmented_control(
    "Navigation",
    tabs_list,
    default=st.session_state["system_active_tab"],
    key="system_nav",
    label_visibility="collapsed",
)

if selected_tab and selected_tab != st.session_state["system_active_tab"]:
    st.session_state["system_active_tab"] = selected_tab
    st.rerun()

st.divider()

active_tab = st.session_state["system_active_tab"]

# =============================================================================
# TAB: TESTS
# =============================================================================
if active_tab == "🧪 Tests":
    # Content extracted from 98_Tests.py
    st.header("Lancer les Tests Suite")

    col1, col2 = st.columns([2, 1])
    with col1:
        test_category = st.radio(
            "Sélectionnez les tests :",
            ["🌟 Tous", "🧪 Unitaires", "💾 DB", "🧠 AI", "🎨 UI", "🔄 Integration"],
            horizontal=True,
        )

    with col2:
        if st.button("▶️ Lancer la suite", type="primary", use_container_width=True):
            # Command construction logic (simplified for briefness but functional)
            cmd = ["python3", "-m", "pytest"]
            if "Unitaires" in test_category:
                cmd.append("tests/unit/")
            elif "DB" in test_category:
                cmd.append("tests/db/")
            elif "Integration" in test_category:
                cmd.append("tests/test_integration.py")

            with st.spinner("Exécution..."):
                try:
                    res = subprocess.run(cmd, capture_output=True, text=True)
                    st.session_state["sys_test_res"] = res.stdout + res.stderr
                    if res.returncode == 0:
                        st.success("✅ Succès !")
                    else:
                        st.error("❌ Échec")
                except Exception as e:
                    st.error(f"Erreur: {e}")

    if "sys_test_res" in st.session_state:
        with st.expander("Voir les logs de sortie", expanded=True):
            st.code(st.session_state["sys_test_res"])

# =============================================================================
# TAB: DEBUG
# =============================================================================
elif active_tab == "🐞 Debug":
    # Content extracted from 99_Debug.py
    st.header("État de santé de la base")
    from modules.db.stats import get_global_stats

    stats = get_global_stats()
    st.json(stats)

    if st.button("🔍 Chercher des doublons inter-comptes"):
        with get_db_connection() as conn:
            query = (
                "SELECT date, label, amount, COUNT(*) as c FROM transactions "
                "GROUP BY date, label, amount HAVING c > 1"
            )
            dupes = pd.read_sql(query, conn)
            if dupes.empty:
                st.success("Aucun doublon trouvé")
            else:
                st.dataframe(dupes)

# =============================================================================
# TAB: NOTIFICATIONS
# =============================================================================
elif active_tab == "🔔 Notifications":
    service = NotificationService()

    # Sous-onglets
    subtab_center, subtab_settings = st.tabs(["📬 Centre", "⚙️ Paramètres"])

    with subtab_center:
        render_notification_center(service)

    with subtab_settings:
        render_notification_settings(service)

st.divider()
render_scroll_to_top()
render_app_info()
