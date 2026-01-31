"""
Sections du tableau de bord organisées en fragments pour performance.
Chaque section peut se recharger indépendamment.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Dict, List

from modules.db.budgets import get_budgets
from modules.db.categories import get_categories_df
from modules.ui.dashboard.kpi_cards import render_kpi_cards
from modules.ui.dashboard.evolution_chart import render_evolution_chart, render_savings_trend_chart
from modules.ui.dashboard.category_charts import (
    render_category_bar_chart, render_monthly_stacked_chart, prepare_expense_dataframe
)
from modules.ui.dashboard.top_expenses import render_top_expenses
from modules.ui.dashboard.budget_tracker import render_budget_tracker
from modules.ui.dashboard.ai_insights import render_month_end_forecast, render_ai_financial_report
from modules.ui.components.transaction_drill_down import render_transaction_drill_down
from modules.ai import predict_budget_overruns, get_budget_alerts_summary


@st.cache_data(ttl=600)
def get_cached_budget_predictions(df_month: pd.DataFrame, budgets: pd.DataFrame) -> List[Dict]:
    """Cache les prédictions budgétaires (appel IA coûteux)."""
    if budgets.empty or df_month.empty:
        return []
    return predict_budget_overruns(df_month, budgets)


@st.fragment
def render_overview_tab(df_current: pd.DataFrame, df_prev: pd.DataFrame, cat_emoji_map: Dict):
    """
    Onglet Vue d'ensemble : KPIs, évolution, catégories, top dépenses.
    """
    # KPI Cards
    render_kpi_cards(df_current, df_prev)
    
    st.markdown("---")
    
    # Évolution
    col1, col2 = st.columns([3, 2])
    with col1:
        render_evolution_chart(df_current)
    with col2:
        render_savings_trend_chart()
    
    st.markdown("---")
    
    # Catégories et Top Dépenses
    col_cat, col_top = st.columns([1.2, 1])
    
    with col_cat:
        render_category_bar_chart(df_current, cat_emoji_map)
    
    with col_top:
        render_top_expenses(df_current, cat_emoji_map, limit=10)


@st.fragment
def render_budget_tab(df_current: pd.DataFrame, df_full: pd.DataFrame, 
                      selected_years: List[int], selected_months: List[int],
                      cat_emoji_map: Dict):
    """
    Onglet Budgets & Prévisions : Suivi budgets, alertes, prévisions fin de mois.
    """
    df_exp = prepare_expense_dataframe(df_current, cat_emoji_map)
    budgets = get_budgets()
    
    # Suivi des budgets
    render_budget_tracker(df_exp, cat_emoji_map)
    
    st.markdown("---")
    
    # Alertes budgétaires avec prédictions
    st.subheader("📈 Alertes Budgétaires")
    
    if budgets.empty:
        st.info("Définissez des budgets pour activer les alertes prédictives.")
    else:
        # Données du mois en cours
        import datetime
        today = datetime.date.today()
        current_month = today.strftime('%Y-%m')
        df_month = df_full[df_full['date_dt'].dt.strftime('%Y-%m') == current_month]
        
        predictions = get_cached_budget_predictions(df_month, budgets)
        
        if predictions:
            summary = get_budget_alerts_summary(predictions)
            
            # Métriques en colonnes
            cols = st.columns(4)
            with cols[0]:
                st.metric("✅ OK", summary['ok_count'])
            with cols[1]:
                st.metric("⚠️ Attention", summary['warning_count'])
            with cols[2]:
                st.metric("🚨 Dépassement", summary['overrun_count'])
            with cols[3]:
                total = summary['ok_count'] + summary['warning_count'] + summary['overrun_count']
                st.metric("📊 Total Budgets", total)
            
            # Détails des alertes
            alert_count = sum(1 for p in predictions if p['status'] != 'ok')
            if alert_count > 0:
                with st.expander(f"Voir les {alert_count} alertes", expanded=True):
                    for pred in predictions:
                        if pred['status'] != 'ok':
                            with st.container():
                                col_icon, col_info = st.columns([0.1, 0.9])
                                with col_icon:
                                    st.markdown(f"### {pred['alert_level']}")
                                with col_info:
                                    st.write(f"**{pred['category']}** - {pred['usage_percent']:.0f}% du budget")
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Dépensé", f"{pred['current_spent']:.0f}€")
                                    with col2:
                                        st.metric("Projection", f"{pred['projected_spent']:.0f}€")
                                    with col3:
                                        st.metric("Moy/jour", f"{pred['daily_avg']:.0f}€")
                                    
                                    # Drill-down des transactions
                                    tx_ids = df_month[
                                        df_month['category_validated'] == pred['category']
                                    ]['id'].tolist()
                                    if tx_ids:
                                        render_transaction_drill_down(
                                            category=pred['category'],
                                            transaction_ids=tx_ids,
                                            key_prefix=f"budget_alert_{pred['category']}"
                                        )
                                st.divider()
        else:
            st.info("Pas assez de données pour les prédictions ce mois-ci.")
    
    st.markdown("---")
    
    # Prévisions fin de mois
    cat_props = get_categories_df()
    fixed_categories = cat_props[cat_props['is_fixed'] == 1]['name'].tolist()
    render_month_end_forecast(df_full, selected_years, selected_months, fixed_categories)


@st.fragment
def render_analysis_tab(df_current: pd.DataFrame, df_full: pd.DataFrame, 
                        official_list: List[str], cat_emoji_map: Dict):
    """
    Onglet Analyses : Répartition par membre, bénéficiaires tiers, tags.
    """
    from modules.ui.dashboard.filters import normalize_name
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        # Analyse par membre du foyer
        st.subheader("👥 Par Membre du Foyer")
        
        if 'beneficiary_display' in df_current.columns:
            household_members = official_list + ['Famille', 'Maison']
            df_members = df_current[
                (df_current['amount'] < 0) &
                (df_current['beneficiary_display'].isin(household_members))
            ].copy()
            df_members['amount'] = df_members['amount'].abs()
            
            if not df_members.empty:
                df_members_sum = df_members.groupby('beneficiary_display')['amount'].sum().reset_index()
                df_members_sum.columns = ['Membre', 'Montant']
                
                fig = px.pie(
                    df_members_sum,
                    values='Montant',
                    names='Membre',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucune dépense affectée aux membres sur cette période.")
        
        st.markdown("---")
        
        # Analyse par bénéficiaires tiers
        st.subheader("🏢 Par Bénéficiaire (Tiers)")
        
        if 'beneficiary_display' in df_current.columns:
            household_exclude = official_list + ['Famille', 'Maison', 'Inconnu', 'Anonyme', '']
            df_tiers = df_current[
                (df_current['amount'] < 0) &
                (~df_current['beneficiary_display'].isin(household_exclude))
            ].copy()
            df_tiers['amount'] = df_tiers['amount'].abs()
            
            if not df_tiers.empty:
                df_tiers_sum = df_tiers.groupby('beneficiary_display')['amount'].sum().reset_index()
                df_tiers_sum.columns = ['Bénéficiaire', 'Montant']
                df_tiers_sum = df_tiers_sum.sort_values('Montant', ascending=False).head(15)
                
                fig = px.pie(
                    df_tiers_sum,
                    values='Montant',
                    names='Bénéficiaire',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.3))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucun bénéficiaire tiers détecté sur cette période.")
    
    with col_right:
        # Analyse par tags
        st.subheader("🏷️ Par Tags")
        
        if 'tags' in df_current.columns:
            tag_data = []
            for _, row in df_current[df_current['amount'] < 0].iterrows():
                if pd.notna(row['tags']):
                    tags = [t.strip() for t in str(row['tags']).split(',') if t.strip()]
                    for t in tags:
                        tag_data.append({"Tag": t, "Montant": abs(row['amount'])})
            
            if tag_data:
                df_tags = pd.DataFrame(tag_data).groupby('Tag')['Montant'].sum().reset_index()
                df_tags = df_tags.sort_values('Montant', ascending=True).tail(10)
                
                fig = px.bar(
                    df_tags,
                    x='Montant',
                    y='Tag',
                    orientation='h',
                    color='Tag',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig.update_layout(
                    showlegend=False,
                    xaxis_title="Montant (€)",
                    yaxis_title="",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucun tag sur cette période.")
    
    st.markdown("---")
    
    # Évolution mensuelle par catégorie (en bas, pleine largeur)
    st.subheader("📊 Évolution Mensuelle par Catégorie")
    render_monthly_stacked_chart(df_full, cat_emoji_map)


@st.fragment
def render_ai_tab(df_current: pd.DataFrame, df_prev: pd.DataFrame, 
                  df_full: pd.DataFrame, selected_years: List[int], 
                  selected_months: List[int]):
    """
    Onglet IA & Rapports : Rapport financier généré par IA.
    Fragment séparé pour ne pas recharger toute la page.
    """
    st.subheader("🔮 Analyse & Conseils IA")
    
    if df_current.empty:
        st.info("Sélectionnez une période avec des données pour générer un rapport.")
        return
    
    # Info sur les données analysées
    cur_inc = df_current[df_current['amount'] > 0]['amount'].sum()
    cur_exp = abs(df_current[df_current['amount'] < 0]['amount'].sum())
    tx_count = len(df_current)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Transactions analysées", tx_count)
    with col2:
        st.metric("Revenus", f"{cur_inc:,.0f}€")
    with col3:
        st.metric("Dépenses", f"{cur_exp:,.0f}€")
    
    st.markdown("---")
    
    # Bouton de génération
    if st.button("🪄 Générer le rapport & conseils", type="primary", use_container_width=True):
        with st.spinner("L'IA analyse vos finances sur cette période..."):
            render_ai_financial_report(df_current, df_prev, df_full, selected_years, selected_months)
        st.success("Rapport généré avec succès !")
    else:
        st.caption("Cliquez sur le bouton ci-dessus pour générer une analyse personnalisée.")
