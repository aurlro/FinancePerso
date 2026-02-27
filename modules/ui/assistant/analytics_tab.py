"""
Analytics & Trends Tab - Analyse approfondie avec chat intégré.
"""

import datetime

import pandas as pd
import streamlit as st

from modules.analytics import exclude_internal_transfers
from modules.db.transactions import get_all_transactions
from modules.ui.assistant.components import render_chat_interface
from modules.ui.assistant.state import add_chat_message, get_assistant_state, set_assistant_state


def render_analytics_tab():
    """Render the analytics and trends tab."""
    st.header("📊 Analytics & Trends")
    st.markdown("Analysez vos habitudes de dépenses et discutez avec l'IA.")

    # Filters
    st.subheader("Filtres")

    col1, col2, col3 = st.columns(3)

    with col1:
        exclude_transfers = st.checkbox(
            "🔄 Exclure virements internes",
            value=True,
            help="Exclut les virements entre vos comptes",
        )

    with col2:
        exclude_savings = st.checkbox(
            "🏦 Exclure épargne", value=True, help="Exclut les transferts vers l'épargne"
        )

    with col3:
        if st.button("🔄 Analyser", type="primary", use_container_width=True):
            run_trend_analysis(exclude_transfers, exclude_savings)

    st.divider()

    # Trend Results
    trend_results = get_assistant_state("trend_results")
    if trend_results:
        render_trend_results(trend_results)

    st.divider()

    # Chat Section
    st.subheader("💬 Assistant Conversationnel")

    suggestions = [
        "Quelles sont mes plus grosses dépenses ce mois ?",
        "Compare mes dépenses janvier et février",
        "Quels abonnements me coûtent le plus cher ?",
        "Où puis-je économiser de l'argent ?",
    ]

    def on_send(message: str):
        add_chat_message("user", message)

        # Get AI response
        from modules.ai import chat_with_assistant
        from modules.ai_manager_v2 import get_ai_error_message, is_ai_available

        # Check if chat is available
        if chat_with_assistant is None:
            add_chat_message(
                "assistant",
                "⚠️ L'assistant conversationnel n'est pas disponible. "
                "Erreur d'initialisation du module IA. Vérifiez les logs.",
            )
            st.rerun()
            return

        # Check if AI provider is properly configured
        if not is_ai_available():
            error_msg = get_ai_error_message()
            add_chat_message(
                "assistant",
                f"⚠️ **Service IA non disponible**\n\n{error_msg}\n\n"
                "_Rendez-vous dans l'onglet **Configuration** pour vérifier vos paramètres IA._",
            )
            st.rerun()
            return

        with st.spinner("L'assistant réfléchit..."):
            try:
                history = get_assistant_state("chat_history")
                response = chat_with_assistant(message, history)
                add_chat_message("assistant", response)
            except Exception as e:
                add_chat_message("assistant", f"Désolé, une erreur est survenue : {str(e)}")

        st.rerun()

    render_chat_interface(
        history=get_assistant_state("chat_history") or [],
        on_send=on_send,
        suggestions=suggestions if not get_assistant_state("chat_history") else None,
    )

    # Clear chat button
    if get_assistant_state("chat_history"):
        if st.button("🗑️ Effacer la conversation", key="clear_chat"):
            set_assistant_state("chat_history", [])
            st.rerun()


def run_trend_analysis(exclude_transfers: bool, exclude_savings: bool):
    """Run trend analysis with current filters."""
    df = get_all_transactions()

    if df.empty:
        st.warning("Pas de transactions à analyser.")
        return

    with st.spinner("Analyse en cours..."):
        # Apply filters
        if exclude_transfers:
            df = exclude_internal_transfers(df)

        df["date_dt"] = pd.to_datetime(df["date"])

        # Current month
        today = datetime.date.today()
        current_month = today.strftime("%Y-%m")
        df_current = df[df["date_dt"].dt.strftime("%Y-%m") == current_month]

        # Previous month
        prev_month_date = today.replace(day=1) - datetime.timedelta(days=1)
        prev_month = prev_month_date.strftime("%Y-%m")
        df_prev = df[df["date_dt"].dt.strftime("%Y-%m") == prev_month]

        # Run analysis
        from modules.ai import analyze_spending_trends

        result = analyze_spending_trends(df_current, df_prev)

        set_assistant_state("trend_results", result)
        st.rerun()


def render_trend_results(result: dict):
    """Render trend analysis results."""
    insights = result.get("insights", [])
    period_current = result.get("period_current")
    period_previous = result.get("period_previous")

    if period_current and period_previous:
        st.info(
            f"📅 **Comparaison** : {period_current['start']} → {period_current['end']} "
            f"vs {period_previous['start']} → {period_previous['end']}"
        )

    if not insights:
        st.success("✅ Aucune tendance significative détectée.")
        return

    st.subheader(f"🎯 {len(insights)} insights détectés")

    from modules.ui.components.transaction_drill_down import render_category_drill_down_expander

    for i, insight in enumerate(insights):
        period_start = period_current["start"] if period_current else None
        period_end = period_current["end"] if period_current else None
        render_category_drill_down_expander(
            insight, period_start, period_end, key_prefix=f"trend_{i}"
        )
