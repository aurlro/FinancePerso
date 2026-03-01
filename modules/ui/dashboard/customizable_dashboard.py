"""
Customizable Dashboard Components.

Provides configurable dashboard views.
"""

import pandas as pd
import streamlit as st


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
    from modules.ui.dashboard.kpi_cards import render_kpi_cards
    
    st.markdown("### 📊 Vue d'ensemble")
    
    if not df_current.empty:
        # Utiliser le composant KPI unifié (4 KPIs avec tendances)
        render_kpi_cards(df_current, df_prev)
    else:
        # Utiliser le composant EmptyState du design system
        from modules.ui.molecules.empty_state import EmptyState
        EmptyState.no_data(data_type="transaction")
