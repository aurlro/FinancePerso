# -*- coding: utf-8 -*-
"""
Dashboard unifié avec Design System V5.5.

Remplace: pages/02_Dashboard.py (legacy)
"""

from datetime import date, timedelta
from typing import Any

import pandas as pd
import streamlit as st

from modules.db.transactions import get_all_transactions
from modules.logger import logger
from modules.ui.molecules.toast import toast_error, toast_info, toast_success
from modules.ui.tokens.colors import Colors
from modules.ui.tokens.spacing import Spacing


def render_dashboard_page() -> None:
    """
    Render the unified dashboard page with Design System V5.5.
    """
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <h1 style="color: {Colors.GRAY_900}; margin-bottom: {Spacing.SMALL}px;">
            📊 Tableau de bord
        </h1>
        <p style="color: {Colors.GRAY_600};">
            Vue d'ensemble de vos finances
        </p>
        """, unsafe_allow_html=True)
    
    with col2:
        # Période
        period = st.selectbox(
            "Période",
            options=[
                "Ce mois",
                "Mois dernier",
                "3 derniers mois",
                "Cette année",
                "Année dernière",
            ],
            key="dashboard_period",
        )
    
    # Récupérer les transactions
    try:
        df = get_all_transactions()
        if df.empty:
            render_empty_state()
            return
    except Exception as e:
        logger.error(f"Error loading transactions: {e}")
        toast_error("Erreur de chargement", "Impossible de charger les transactions")
        return
    
    # KPI Cards
    render_kpi_section(df)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        render_expense_chart(df)
    
    with col2:
        render_category_chart(df)
    
    # Recent transactions
    st.divider()
    render_recent_transactions(df)
    
    # Alerts
    render_alerts_section(df)


def render_empty_state() -> None:
    """Render empty state when no transactions."""
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: {Spacing.XXXLARGE}px;
        background: {Colors.SLATE_50};
        border-radius: {Spacing.RADIUS_LARGE}px;
        margin-top: {Spacing.LARGE}px;
    ">
        <div style="font-size: 4rem; margin-bottom: {Spacing.MEDIUM}px;">📊</div>
        <h2 style="color: {Colors.GRAY_700};">Aucune transaction</h2>
        <p style="color: {Colors.GRAY_500};">
            Importez vos premières transactions pour voir votre tableau de bord.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📥 Importer des transactions", type="primary"):
        st.switch_page("pages/01_Import.py")


def render_kpi_section(df: pd.DataFrame) -> None:
    """Render KPI cards section."""
    st.markdown("#### 📈 Indicateurs clés")
    
    # Calculate KPIs
    total_income = df[df['amount'] > 0]['amount'].sum()
    total_expenses = abs(df[df['amount'] < 0]['amount'].sum())
    balance = total_income - total_expenses
    transaction_count = len(df)
    
    cols = st.columns(4)
    
    with cols[0]:
        render_kpi_card(
            title="Revenus",
            value=f"+{total_income:,.2f} €",
            icon="💰",
            color=Colors.SUCCESS,
            bg_color=Colors.SUCCESS_BG,
        )
    
    with cols[1]:
        render_kpi_card(
            title="Dépenses",
            value=f"-{total_expenses:,.2f} €",
            icon="💸",
            color=Colors.DANGER,
            bg_color=Colors.DANGER_BG,
        )
    
    with cols[2]:
        balance_color = Colors.SUCCESS if balance >= 0 else Colors.DANGER
        balance_bg = Colors.SUCCESS_BG if balance >= 0 else Colors.DANGER_BG
        render_kpi_card(
            title="Solde",
            value=f"{balance:,.2f} €",
            icon="💵",
            color=balance_color,
            bg_color=balance_bg,
        )
    
    with cols[3]:
        render_kpi_card(
            title="Transactions",
            value=f"{transaction_count}",
            icon="📄",
            color=Colors.INFO,
            bg_color=Colors.INFO_BG,
        )


def render_kpi_card(
    title: str,
    value: str,
    icon: str,
    color: str,
    bg_color: str,
) -> None:
    """Render a single KPI card."""
    st.markdown(f"""
    <div style="
        background: white;
        border-radius: {Spacing.RADIUS_MEDIUM}px;
        padding: {Spacing.LARGE}px;
        border-left: 4px solid {color};
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    ">
        <div style="display: flex; align-items: center; gap: {Spacing.SMALL}px; margin-bottom: {Spacing.SMALL}px;">
            <span style="font-size: 1.5rem;">{icon}</span>
            <span style="color: {Colors.GRAY_500}; font-size: 0.875rem; font-weight: 500;">
                {title}
            </span>
        </div>
        <div style="font-size: 1.5rem; font-weight: 700; color: {Colors.GRAY_900};">
            {value}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_expense_chart(df: pd.DataFrame) -> None:
    """Render expense evolution chart."""
    st.markdown("#### 📊 Évolution des dépenses")
    
    # Prepare data
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    
    monthly = df.groupby('month')['amount'].sum().reset_index()
    monthly['month_str'] = monthly['month'].astype(str)
    
    # Simple bar chart using Streamlit
    chart_data = monthly.set_index('month_str')['amount']
    st.bar_chart(chart_data, use_container_width=True)


def render_category_chart(df: pd.DataFrame) -> None:
    """Render category breakdown chart."""
    st.markdown("#### 🏷️ Répartition par catégorie")
    
    # Get expenses by category
    expenses = df[df['amount'] < 0].copy()
    expenses['amount'] = abs(expenses['amount'])
    
    by_category = expenses.groupby('category')['amount'].sum().sort_values(ascending=False).head(10)
    
    if not by_category.empty:
        st.bar_chart(by_category, use_container_width=True)
    else:
        st.info("Pas assez de données pour afficher le graphique")


def render_recent_transactions(df: pd.DataFrame) -> None:
    """Render recent transactions table."""
    st.markdown("#### 📝 Transactions récentes")
    
    # Get last 10 transactions
    recent = df.sort_values('date', ascending=False).head(10)
    
    if not recent.empty:
        # Format for display
        display_df = recent[['date', 'label', 'category', 'amount']].copy()
        display_df['amount'] = display_df['amount'].apply(lambda x: f"{x:,.2f} €")
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Aucune transaction récente")
    
    if st.button("Voir toutes les transactions"):
        st.switch_page("pages/07_Recherche.py")


def render_alerts_section(df: pd.DataFrame) -> None:
    """Render alerts and recommendations."""
    st.divider()
    st.markdown("#### 🔔 Alertes et recommandations")
    
    alerts = []
    
    # Check for uncategorized transactions
    uncategorized = df[df['category'] == 'Inconnu']
    if len(uncategorized) > 0:
        alerts.append({
            "type": "warning",
            "message": f"{len(uncategorized)} transactions non catégorisées",
            "action": "Catégoriser",
            "page": "pages/05_Audit.py",
        })
    
    # Check for large expenses
    large_expenses = df[df['amount'] < -500]
    if len(large_expenses) > 0:
        alerts.append({
            "type": "info",
            "message": f"{len(large_expenses)} dépenses importantes ce mois",
            "action": "Voir",
            "page": "pages/07_Recherche.py",
        })
    
    if not alerts:
        st.success("✅ Tout va bien ! Aucune alerte à signaler.")
    else:
        for alert in alerts:
            col1, col2 = st.columns([4, 1])
            with col1:
                if alert["type"] == "warning":
                    st.warning(alert["message"])
                else:
                    st.info(alert["message"])
            with col2:
                if st.button(alert["action"], key=f"alert_{alert['message'][:20]}"):
                    st.switch_page(alert["page"])


def render() -> None:
    """Alias for render_dashboard_page."""
    render_dashboard_page()
