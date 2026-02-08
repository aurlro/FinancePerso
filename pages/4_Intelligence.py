import streamlit as st
import pandas as pd
from datetime import datetime

from modules.ui import load_css, render_scroll_to_top
from modules.ui.layout import render_app_info
from modules.db.migrations import init_db
from modules.logger import logger

# Rules module imports
from modules.ui.rules import (
    render_rule_list,
    render_add_rule_form,
    render_audit_section,
    render_budget_section,
)
from modules.ui.intelligence import render_smart_suggestions_panel
from modules.db.rules import get_learning_rules
from modules.db.audit import auto_fix_common_inconsistencies
from modules.ai.rules_auditor import analyze_rules_integrity
from modules.ui.feedback import (
    toast_success,
    toast_error,
    toast_warning,
    toast_info,
    show_success,
    show_error,
    show_warning,
    show_info,
)

# Recurrence module imports
from modules.db.transactions import get_all_transactions
from modules.db.categories import get_categories_with_emojis
from modules.db.recurrence_feedback import init_recurrence_feedback_table, get_all_feedback
from modules.analytics_v2 import detect_recurring_payments_v2
from modules.ui.recurrence_tabs import (
    render_dashboard_tab,
    render_validation_tab,
    render_subscriptions_tab,
    render_trash_tab,
)

# Page configuration
st.set_page_config(page_title="Intelligence", page_icon="🧠", layout="wide")
load_css()
init_db()
init_recurrence_feedback_table()

st.title("🧠 Intelligence & Automations")
st.markdown(
    "Centralisation de l'IA, des règles de catégorisation, des budgets et de la détection des récurrences."
)

# --- SHARED STATE & NAVIGATION ---
if "intel_active_tab" not in st.session_state:
    st.session_state["intel_active_tab"] = "📋 Règles"

# Auto-jump from other pages if needed
jump_to = st.query_params.get("tab")
if jump_to:
    st.session_state["intel_active_tab"] = jump_to

tabs_list = ["💡 Suggestions", "📋 Règles", "🔁 Récurrences", "🎯 Budgets", "🕵️ Audit IA"]

selected_tab = st.segmented_control(
    "Navigation",
    tabs_list,
    default=st.session_state["intel_active_tab"],
    key="intel_nav",
    label_visibility="collapsed",
)

if selected_tab and selected_tab != st.session_state["intel_active_tab"]:
    st.session_state["intel_active_tab"] = selected_tab
    st.rerun()

st.divider()

active_tab = st.session_state["intel_active_tab"]

# =============================================================================
# TAB: SUGGESTIONS
# =============================================================================
if active_tab == "💡 Suggestions":
    from modules.db.budgets import get_budgets
    from modules.db.members import get_members

    df_all = get_all_transactions()
    rules_df = get_learning_rules()
    budgets_df = get_budgets()
    members_df = get_members()

    render_smart_suggestions_panel(df_all, rules_df, budgets_df, members_df)

# =============================================================================
# TAB: RULES
# =============================================================================
elif active_tab == "📋 Règles":
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.subheader("Règles de catégorisation")
    with col_b:
        if st.button("🪄 Appliquer les règles", use_container_width=True, type="primary"):
            with st.spinner("Application..."):
                count = auto_fix_common_inconsistencies()
                if count > 0:
                    toast_success(f"✅ {count} transactions mises à jour !", icon="🪄")
                else:
                    toast_info("Toutes les transactions sont déjà à jour")

    st.markdown("### Ajouter une nouvelle règle")
    render_add_rule_form()
    st.divider()
    st.markdown("### Liste des règles")
    render_rule_list()

# =============================================================================
# TAB: RECURRENCES
# =============================================================================
elif active_tab == "🔁 Récurrences":
    df = get_all_transactions()
    if df.empty:
        st.info("Aucune donnée disponible pour l'analyse des récurrences.")
    else:
        validated_df = df[df["status"] == "validated"]
        if validated_df.empty:
            st.warning("Veuillez valider quelques transactions pour permettre l'analyse.")
        else:
            with st.spinner("Analyse des tendances..."):
                recurring_df = detect_recurring_payments_v2(validated_df)

                # Enrich with feedback (copying logic from original page)
                feedback = get_all_feedback()
                feedback_map = {
                    (f["label_pattern"], f["category"]): f["user_feedback"] for f in feedback
                }

                def get_status(row):
                    key = (row["label"], row.get("category", ""))
                    return feedback_map.get(key, None)

                recurring_df["user_feedback"] = recurring_df.apply(get_status, axis=1)

            rec_tabs = st.tabs(["📊 Synthèse", "✅ À Valider", "💳 Abonnements", "🗑️ Corbeille"])
            cat_emoji_map = get_categories_with_emojis()

            with rec_tabs[0]:
                render_dashboard_tab(recurring_df, validated_df)
            with rec_tabs[1]:
                render_validation_tab(recurring_df, cat_emoji_map)
            with rec_tabs[2]:
                render_subscriptions_tab(recurring_df, cat_emoji_map)
            with rec_tabs[3]:
                render_trash_tab()

# =============================================================================
# TAB: BUDGETS
# =============================================================================
elif active_tab == "🎯 Budgets":
    render_budget_section()

# =============================================================================
# TAB: AUDIT
# =============================================================================
elif active_tab == "🕵️ Audit IA":
    render_audit_section()

st.divider()
render_scroll_to_top()
render_app_info()
