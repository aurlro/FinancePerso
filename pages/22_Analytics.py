"""
Page Analytics - Dashboard des métriques internes
Accessible uniquement aux administrateurs ou via le menu Système
"""

import streamlit as st
from modules.analytics.metrics import MetricsCollector, get_metrics_dashboard
from modules.analytics.events import get_analytics_summary

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")

st.title("📊 Analytics FinancePerso")

# Tabs pour organiser les données
tab_overview, tab_metrics, tab_events = st.tabs(
    ["Vue d'ensemble", "Métriques métier", "Événements bruts"]
)

with tab_overview:
    st.header("Résumé des 30 derniers jours")

    # Métriques clés
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        import_30d = MetricsCollector.get_import_conversion_rate(days=30)
        st.metric(
            "Taux d'import J+30",
            f"{import_30d['conversion_rate']}%",
            f"{import_30d['imported_users']}/{import_30d['total_new_users']}",
        )

    with col2:
        retention_7d = MetricsCollector.get_retention_rate(days=7)
        st.metric(
            "Rétention J+7",
            f"{retention_7d['retention_rate']}%",
            f"{retention_7d['retained_users']}/{retention_7d['cohort_size']}",
        )

    with col3:
        events_30d = get_analytics_summary(days=30)
        st.metric("Événements totaux", f"{events_30d.get('total_events', 0)}")

    with col4:
        sessions_30d = events_30d.get("total_sessions", 0)
        avg_duration = events_30d.get("avg_session_duration", 0)
        st.metric("Sessions", f"{sessions_30d}", f"{avg_duration/60:.1f}min avg")

with tab_metrics:
    get_metrics_dashboard()

with tab_events:
    st.header("Événements des 7 derniers jours")

    events_data = get_analytics_summary(days=7)

    if events_data.get("events_by_type"):
        st.bar_chart(events_data["events_by_type"])
    else:
        st.info("Pas encore de données d'événements")

st.divider()
st.caption("Données stockées localement dans Data/analytics.db - Pas de données externes")
