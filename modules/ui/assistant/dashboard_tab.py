"""
Dashboard Tab - Vue d'accueil de l'Assistant IA.
"""

import streamlit as st
import pandas as pd
from typing import Callable
from modules.db.transactions import get_all_transactions
from modules.db.rules import get_learning_rules
from modules.db.budgets import get_budgets
from modules.db.stats import get_global_stats
from modules.ui.assistant.state import get_assistant_state, set_assistant_state
from modules.ui.assistant.components import (
    render_empty_state,
    render_metric_row,
    render_audit_summary_cards,
)


def get_dashboard_stats() -> dict:
    """Get statistics for the dashboard."""
    stats = {
        "tx_count": 0,
        "rules_count": 0,
        "budgets_count": 0,
        "last_import": None,
        "audit_pending": 0,
        "audit_total": 0,
    }

    try:
        # Get basic stats
        global_stats = get_global_stats()
        stats["tx_count"] = global_stats.get("total_transactions", 0)

        # Get rules
        rules_df = get_learning_rules()
        stats["rules_count"] = len(rules_df)

        # Get budgets
        budgets_df = get_budgets()
        stats["budgets_count"] = len(budgets_df)

        # Get audit status
        audit_results = get_assistant_state("audit_results") or []
        audit_corrected = get_assistant_state("audit_corrected") or []
        audit_hidden = get_assistant_state("audit_hidden") or []

        stats["audit_total"] = len(audit_results)
        stats["audit_pending"] = len(audit_results) - len(audit_corrected) - len(audit_hidden)

    except Exception:
        pass

    return stats


def render_dashboard_tab(
    on_launch_audit: Callable,
    on_view_analytics: Callable,
    on_open_chat: Callable,
    on_view_audit: Callable,
):
    """Render the main dashboard tab."""
    st.header("🏠 Tableau de bord")
    st.markdown("Vue d'ensemble de votre assistant financier.")

    stats = get_dashboard_stats()

    # If no data yet
    if stats["tx_count"] == 0:
        render_empty_state(
            icon="📊",
            title="Bienvenue dans l'Assistant IA",
            description="Commencez par importer vos transactions pour découvrir toutes les fonctionnalités.",
            actions=[
                (
                    "📥 Importer des données",
                    lambda: (
                        st.session_state.update({"active_op_tab": "📥 Importation"}),
                        st.switch_page("pages/1_Opérations.py"),
                    ),
                ),
            ],
        )
        return

    # Metrics row
    render_metric_row(
        [
            {"label": "Transactions", "value": stats["tx_count"]},
            {"label": "Règles actives", "value": stats["rules_count"]},
            {"label": "Budgets définis", "value": stats["budgets_count"]},
            {"label": "Anomalies en attente", "value": stats["audit_pending"]},
        ]
    )

    st.divider()

    # Quick Actions
    st.subheader("🎯 Actions rapides")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🔎 Lancer un audit", use_container_width=True, type="primary"):
            on_launch_audit()

    with col2:
        if st.button("📈 Voir les tendances", use_container_width=True):
            on_view_analytics()

    with col3:
        if st.button("💬 Poser une question", use_container_width=True):
            on_open_chat()

    with col4:
        if st.button("🎯 Voir les anomalies", use_container_width=True):
            on_view_audit()

    st.divider()

    # Audit Summary Section
    if stats["audit_total"] > 0:
        st.subheader("📋 Résumé de l'audit")

        audit_stats = {
            "total": stats["audit_total"],
            "pending": stats["audit_pending"],
            "corrected": len(get_assistant_state("audit_corrected") or []),
            "hidden": len(get_assistant_state("audit_hidden") or []),
        }

        render_audit_summary_cards(audit_stats)

        if audit_stats["pending"] > 0:
            st.warning(f"⚠️ {audit_stats['pending']} anomalies nécessitent votre attention.")
            if st.button("👉 Corriger les anomalies", type="primary"):
                on_view_audit()
        else:
            st.success("✅ Toutes les anomalies ont été traitées !")

    # Recent Activity / Insights
    st.divider()
    st.subheader("💡 Insight récent")

    # Placeholder for latest insight
    st.info(
        """
    **Analyse disponible**
    
    Lancez un audit ou une analyse de tendances pour obtenir des insights personnalisés sur vos finances.
    """
    )
