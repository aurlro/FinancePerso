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
    
    # Suivi des budgets (avec données historiques pour les tendances)
    render_budget_tracker(df_exp, cat_emoji_map, df_full)
    
    st.markdown("---")
    
    # Alertes budgétaires avec prédictions - VERSION AMÉLIORÉE
    st.subheader("📈 Alertes & Recommandations")
    
    if budgets.empty:
        st.info("📝 **Aucun budget défini**")
        st.caption("Configurez vos budgets pour recevoir des alertes intelligentes")
        if st.button("➕ Créer un budget", type="primary", key="btn_create_budget"):
            st.switch_page("pages/4_Regles.py")
    else:
        # Données du mois en cours
        import datetime
        import calendar
        today = datetime.date.today()
        current_month = today.strftime('%Y-%m')
        df_month = df_full[df_full['date_dt'].dt.strftime('%Y-%m') == current_month]
        
        predictions = get_cached_budget_predictions(df_month, budgets)
        
        if predictions:
            # Trier par sévérité: overrun > warning > ok
            severity_order = {'overrun': 0, 'warning': 1, 'ok': 2}
            predictions_sorted = sorted(predictions, key=lambda x: severity_order.get(x['status'], 3))
            
            summary = get_budget_alerts_summary(predictions)
            
            # KPIs en colonnes avec couleurs
            cols = st.columns(4)
            with cols[0]:
                st.metric("✅ Sur la bonne voie", summary['ok_count'])
            with cols[1]:
                if summary['warning_count'] > 0:
                    st.metric("⚠️ À surveiller", summary['warning_count'], delta="Attention")
                else:
                    st.metric("⚠️ À surveiller", 0)
            with cols[2]:
                if summary['overrun_count'] > 0:
                    st.metric("🚨 Critique", summary['overrun_count'], delta="Action requise", delta_color="inverse")
                else:
                    st.metric("🚨 Critique", 0)
            with cols[3]:
                total = summary['ok_count'] + summary['warning_count'] + summary['overrun_count']
                st.metric("📊 Total Budgets", total)
            
            # Section 1: Alertes CRITIQUES (🔴)
            critical_preds = [p for p in predictions_sorted if p['status'] == 'overrun']
            if critical_preds:
                st.error(f"🔴 **{len(critical_preds)} budget{'s' if len(critical_preds) > 1 else ''} en dépassement**")
                for pred in critical_preds:
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([2, 2, 1])
                        
                        with col1:
                            st.markdown(f"**{pred['category']}**")
                            overrun = pred['projected_spent'] - pred['budget']
                            st.caption(f"Projection: **{pred['projected_spent']:.0f}€** / {pred['budget']:.0f}€ budget")
                            st.markdown(f"📈 **+{pred['usage_percent']:.0f}%** — Dépassé de **{overrun:.0f}€**")
                        
                        with col2:
                            # Conseil contextuel
                            st.caption("💡 **Conseil**")
                            days_left = calendar.monthrange(today.year, today.month)[1] - today.day
                            if days_left > 0:
                                daily_max = max(0, (pred['budget'] - pred['current_spent']) / days_left)
                                st.markdown(f"Max {daily_max:.0f}€/jour jusqu'à la fin du mois")
                        
                        with col3:
                            # Actions rapides
                            if st.button("💡 Conseils", key=f"tips_{pred['category']}", use_container_width=True):
                                st.toast(f"Analyse de {pred['category']}...", icon="💡")
                            
                            # Limiter à 5 dernières transactions pour le drill-down
                            tx_ids = df_month[
                                df_month['category_validated'] == pred['category']
                            ]['id'].tolist()[:5]  # Limiter à 5
                            
                            if tx_ids and len(tx_ids) > 0:
                                if st.button(f"📊 Voir ({len(tx_ids)}+)", key=f"details_{pred['category']}", use_container_width=True):
                                    st.session_state[f"show_budget_drill_{pred['category']}"] = True
                                
                                if st.session_state.get(f"show_budget_drill_{pred['category']}", False):
                                    with st.expander(f"Transactions {pred['category']}", expanded=True):
                                        render_transaction_drill_down(
                                            category=pred['category'],
                                            transaction_ids=tx_ids,
                                            key_prefix=f"budget_alert_{pred['category']}"
                                        )
            
            # Section 2: Avertissements (🟠)
            warning_preds = [p for p in predictions_sorted if p['status'] == 'warning']
            if warning_preds:
                with st.expander(f"🟠 {len(warning_preds)} budget{'s' if len(warning_preds) > 1 else ''} à surveiller", expanded=False):
                    for pred in warning_preds:
                        col1, col2 = st.columns([3, 2])
                        with col1:
                            st.markdown(f"**{pred['category']}**: {pred['usage_percent']:.0f}% utilisé")
                            remaining = pred['budget'] - pred['current_spent']
                            st.caption(f"Reste: {remaining:.0f}€ sur {pred['budget']:.0f}€")
                        
                        with col2:
                            days_left = calendar.monthrange(today.year, today.month)[1] - today.day
                            if days_left > 0:
                                daily_allowance = remaining / days_left
                                st.caption(f"💡 **{daily_allowance:.0f}€/jour max** pour tenir")
            
            # Section 3: Budgets OK - Résumé compact
            ok_preds = [p for p in predictions_sorted if p['status'] == 'ok']
            if ok_preds:
                with st.expander(f"🟢 {len(ok_preds)} budget{'s' if len(ok_preds) > 1 else ''} sous contrôle", expanded=False):
                    cols_ok = st.columns(min(len(ok_preds), 4))
                    for i, pred in enumerate(ok_preds[:8]):  # Limiter à 8
                        with cols_ok[i % 4]:
                            st.caption(f"{pred['category']}")
                            st.progress(min(pred['usage_percent'] / 100, 1.0), 
                                       text=f"{pred['usage_percent']:.0f}%")
                            st.caption(f"{pred['current_spent']:.0f}€ / {pred['budget']:.0f}€")
        else:
            st.info("📊 Pas assez de données ce mois-ci pour les prédictions. Importez des transactions pour activer les alertes.")
    
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
    if st.button("🪄 Générer le rapport & conseils", type="primary", use_container_width=True, key='button_287'):
        with st.spinner("L'IA analyse vos finances sur cette période..."):
            render_ai_financial_report(df_current, df_prev, df_full, selected_years, selected_months)
        st.success("Rapport généré avec succès !")
    else:
        st.caption("Cliquez sur le bouton ci-dessus pour générer une analyse personnalisée.")
