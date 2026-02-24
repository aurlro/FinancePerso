"""
Customizable Dashboard Components.

Provides configurable dashboard views.
"""

import streamlit as st
import pandas as pd


def render_dashboard_configurator():
    """Render the dashboard configuration panel."""
    st.markdown("### ⚙️ Configuration du Dashboard")
    
    # Widget visibility toggles
    st.markdown("#### Widgets visibles")
    
    col1, col2 = st.columns(2)
    with col1:
        st.checkbox("Cartes KPI", value=True, key="show_kpi")
        st.checkbox("Graphique d'évolution", value=True, key="show_evolution")
        st.checkbox("Répartition par catégorie", value=True, key="show_categories")
    
    with col2:
        st.checkbox("Top dépenses", value=True, key="show_top_expenses")
        st.checkbox("Suivi budgets", value=True, key="show_budgets")
        st.checkbox("Recommandations IA", value=True, key="show_ai")
    
    st.divider()
    
    # Period settings
    st.markdown("#### Période par défaut")
    st.selectbox(
        "Période affichée",
        ["Ce mois", "Mois dernier", "3 derniers mois", "Année en cours", "Tout"],
        key="default_period"
    )


def render_customizable_overview(
    df_current: pd.DataFrame,
    df_prev: pd.DataFrame,
    cat_emoji_map: dict,
    df_all: pd.DataFrame
):
    """
    Render the customizable overview section.
    
    Args:
        df_current: Current period transactions
        df_prev: Previous period transactions
        cat_emoji_map: Category to emoji mapping
        df_all: All transactions
    """
    # Default simple overview
    st.markdown("### 📊 Vue d'ensemble")
    
    # Calculate basic metrics
    if not df_current.empty:
        total_income = df_current[df_current['amount'] > 0]['amount'].sum()
        total_expense = abs(df_current[df_current['amount'] < 0]['amount'].sum())
        balance = total_income - total_expense
        
        # KPI cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Revenus",
                f"€{total_income:,.2f}",
                delta=None
            )
        with col2:
            st.metric(
                "Dépenses",
                f"€{total_expense:,.2f}",
                delta=None
            )
        with col3:
            st.metric(
                "Solde",
                f"€{balance:,.2f}",
                delta=None
            )
    else:
        st.info("💡 Aucune transaction pour la période sélectionnée.")
