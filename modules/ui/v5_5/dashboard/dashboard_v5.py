"""Dashboard V5.5 - Dashboard complet style maquette FinCouple.

Usage:
    from modules.ui.v5_5.dashboard import render_dashboard_v5
    
    render_dashboard_v5()
"""

from typing import Optional
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from modules.ui.v5_5.theme import apply_light_theme, LightColors
from modules.ui.v5_5.components import KPICard, KPIData
from modules.ui.v5_5.components.dashboard_header import (
    DashboardHeader, 
    get_current_month_name,
    get_last_12_months
)
from modules.ui.v5_5.dashboard.kpi_grid import render_kpi_grid, calculate_kpis
from modules.ui.v5_5.welcome import has_transactions
from modules.db.transactions import get_all_transactions


def render_dashboard_v5(
    user_name: Optional[str] = None,
    default_month: Optional[str] = None,
) -> None:
    """Rend le dashboard complet V5.5.
    
    Affiche:
    - Header avec "Bonjour [Nom]" et sélecteur de mois
    - Grille de 4 KPIs (Reste à vivre, Dépenses, Revenus, Épargne)
    - Graphique de répartition des dépenses
    - Liste des transactions récentes
    
    Args:
        user_name: Nom de l'utilisateur
        default_month: Mois par défaut (sinon mois courant)
    """
    # Appliquer thème
    apply_light_theme()
    
    # Vérifier si données existent
    if not has_transactions():
        from modules.ui.v5_5.dashboard.empty_state import render_dashboard_empty
        render_dashboard_empty(user_name=user_name)
        return
    
    # Mois par défaut
    if default_month is None:
        default_month = get_current_month_name()
    
    available_months = get_last_12_months()
    
    # 1. Header
    selected_month = DashboardHeader.render(
        user_name=user_name,
        current_month=default_month,
        available_months=available_months,
        key="dashboard_v5"
    )
    
    # 2. Section Vue d'ensemble
    st.markdown("""
    <h2 style="
        font-size: 1.25rem;
        font-weight: 600;
        color: #1F2937;
        margin-top: 2rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    ">
        📊 Vue d'ensemble
    </h2>
    """, unsafe_allow_html=True)
    
    # 3. KPIs
    kpis = calculate_kpis(selected_month or default_month)
    render_kpi_grid(kpis)
    
    # 4. Deux colonnes: Graphique + Transactions
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        render_expenses_chart(selected_month or default_month)
    
    with col_right:
        render_recent_transactions(selected_month or default_month, limit=5)
    
    # Footer
    st.divider()
    st.caption("FinancePerso V5.5 - Dashboard")


def render_expenses_chart(month_str: str) -> None:
    """Affiche le graphique de répartition des dépenses.
    
    Args:
        month_str: Mois au format "Février 2026"
    """
    st.markdown("#### 📊 Répartition des dépenses")
    
    try:
        from modules.ui.v5_5.dashboard.kpi_grid import parse_month
        import pandas as pd
        
        year, month = parse_month(month_str)
        
        # Récupérer transactions
        df = get_all_transactions()
        if df.empty:
            st.info("Aucune donnée à afficher")
            return
        
        df['date'] = pd.to_datetime(df['date'])
        month_mask = (df['date'].dt.year == year) & (df['date'].dt.month == month)
        df_month = df[month_mask]
        
        # Filtrer dépenses uniquement
        expenses = df_month[df_month['amount'] < 0].copy()
        if expenses.empty:
            st.info("Aucune dépense ce mois-ci")
            return
        
        # Grouper par catégorie
        by_category = expenses.groupby('category_validated')['amount'].sum().abs().sort_values(ascending=False)
        
        if len(by_category) == 0:
            st.info("Aucune donnée à afficher")
            return
        
        # Prendre top 5 + autres
        if len(by_category) > 5:
            top5 = by_category.head(5)
            others = by_category[5:].sum()
            by_category = pd.concat([top5, pd.Series({'Autres': others})])
        
        # Couleurs
        colors = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6', '#6B7280']
        
        # Graphique donut
        fig = go.Figure(data=[go.Pie(
            labels=by_category.index,
            values=by_category.values,
            hole=0.5,
            marker_colors=colors[:len(by_category)],
            textinfo='label+percent',
            textposition='outside',
            textfont_size=11,
        )])
        
        fig.update_layout(
            showlegend=False,
            margin=dict(t=20, b=20, l=20, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=300,
        )
        
        st.plotly_chart(fig, use_container_width=True, key=f"expenses_chart_{month_str}")
        
    except Exception as e:
        st.error(f"Erreur lors du chargement du graphique: {str(e)}")


def render_recent_transactions(month_str: str, limit: int = 5) -> None:
    """Affiche les transactions récentes.
    
    Args:
        month_str: Mois au format "Février 2026"
        limit: Nombre de transactions à afficher
    """
    st.markdown("#### 📝 Transactions récentes")
    
    try:
        from modules.ui.v5_5.dashboard.kpi_grid import parse_month
        import pandas as pd
        from datetime import datetime
        
        year, month = parse_month(month_str)
        
        # Récupérer transactions
        df = get_all_transactions()
        if df.empty:
            st.info("Aucune transaction")
            return
        
        df['date'] = pd.to_datetime(df['date'])
        month_mask = (df['date'].dt.year == year) & (df['date'].dt.month == month)
        df_month = df[month_mask].sort_values('date', ascending=False).head(limit)
        
        if df_month.empty:
            st.info("Aucune transaction ce mois-ci")
            return
        
        # Afficher chaque transaction
        for _, tx in df_month.iterrows():
            amount = tx['amount']
            is_expense = amount < 0
            
            amount_str = f"{amount:,.2f} €".replace(",", " ").replace(".", ",")
            amount_color = "#EF4444" if is_expense else "#10B981"
            
            # Date relative
            tx_date = tx['date']
            today = datetime.now()
            delta = (today - tx_date).days
            
            if delta == 0:
                date_str = "Aujourd'hui"
            elif delta == 1:
                date_str = "Hier"
            else:
                date_str = tx_date.strftime("%d/%m")
            
            # HTML pour chaque transaction
            st.markdown(f"""
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.75rem 0;
                border-bottom: 1px solid #E5E7EB;
            ">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <span style="font-size: 1.25rem;">🛒</span>
                    <div>
                        <div style="font-weight: 500; color: #1F2937;">{tx['label'][:30]}{'...' if len(tx['label']) > 30 else ''}</div>
                        <div style="font-size: 0.875rem; color: #6B7280;">
                            {tx.get('category_validated', 'Non catégorisé')} • {date_str}
                        </div>
                    </div>
                </div>
                <div style="font-weight: 600; color: {amount_color};">
                    {amount_str}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Lien vers toutes les transactions
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        if st.button("Voir toutes les transactions →", key=f"see_all_tx_{month_str}"):
            st.switch_page("pages/1_Opérations.py")
            
    except Exception as e:
        st.error(f"Erreur lors du chargement des transactions: {str(e)}")


def render_dashboard_simple() -> None:
    """Version simplifiée pour test rapide."""
    render_dashboard_v5(
        user_name="Alex",
        default_month=get_current_month_name(),
    )
