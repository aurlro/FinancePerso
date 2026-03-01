"""
Prototype de refonte de la page Budgets
Ce fichier montre les améliorations concrètes suggérées.
À adapter et intégrer dans modules/ui/dashboard/budget/
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date
import calendar


# ============================================================================
# 1. COMPOSANT: Alertes Budgétaires Priorisées (remplace la liste brute)
# ============================================================================

def render_prioritized_alerts(predictions, df_month):
    """
    Affiche les alertes par ordre de priorité avec actions contextuelles.
    """
    if not predictions:
        st.success("✅ Tous vos budgets sont respectés ce mois-ci !")
        return
    
    # Trier par sévérité
    severity_order = {'overrun': 0, 'warning': 1, 'ok': 2}
    predictions_sorted = sorted(predictions, key=lambda x: severity_order.get(x['status'], 3))
    
    # Séparer en groupes
    critical = [p for p in predictions_sorted if p['status'] == 'overrun']
    warnings = [p for p in predictions_sorted if p['status'] == 'warning']
    ok = [p for p in predictions_sorted if p['status'] == 'ok']
    
    # Section 1: Alertes Critiques (🔴)
    if critical:
        st.error(f"🔴 **{len(critical)} Budget{'s' if len(critical) > 1 else ''} Critique{'s' if len(critical) > 1 else ''}**")
        for pred in critical:
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**{pred['category']}**")
                    st.caption(f"Projection: **{pred['projected_spent']:.0f}€** / {pred['budget']:.0f}€")
                    
                with col2:
                    overrun = pred['projected_spent'] - pred['budget']
                    st.markdown(f"📈 **+{pred['usage_percent']:.0f}%**")
                    st.caption(f"Dépassement: {overrun:.0f}€")
                    
                with col3:
                    # Actions contextuelles
                    if st.button("💡 Conseils", key=f"tips_{pred['category']}"):
                        st.toast(f"Analyse de {pred['category']}...")
                    if st.button("📊 Détails", key=f"details_{pred['category']}"):
                        st.session_state['show_budget_details'] = pred['category']
    
    # Section 2: Avertissements (🟠)
    if warnings:
        with st.expander(f"🟠 {len(warnings)} budget{'s' if len(warnings) > 1 else ''} à surveiller"):
            for pred in warnings:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{pred['category']}**: {pred['usage_percent']:.0f}% utilisé")
                with col2:
                    remaining = pred['budget'] - pred['current_spent']
                    days_left = calendar.monthrange(date.today().year, date.today().month)[1] - date.today().day
                    daily_allowance = remaining / days_left if days_left > 0 else 0
                    st.caption(f"{remaining:.0f}€ restant → {daily_allowance:.0f}€/jour")
    
    # Section 3: OK - Résumé compact
    if ok:
        with st.expander(f"🟢 {len(ok)} budget{'s' if len(ok) > 1 else ''} sous contrôle", expanded=False):
            cols = st.columns(min(len(ok), 4))
            for i, pred in enumerate(ok[:8]):  # Limiter à 8
                with cols[i % 4]:
                    st.caption(f"{pred['category']}")
                    st.progress(pred['usage_percent'] / 100)


# ============================================================================
# 2. COMPOSANT: Prévisions Scénarisées (remplace le calcul naïf)
# ============================================================================

def render_smart_forecast(df_month, fixed_categories, variable_categories):
    """
    Prévisions avec scénarios et recommandations actionnables.
    """
    if df_month.empty:
        st.info("Pas assez de données pour les prévisions.")
        return
    
    today = date.today()
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    days_passed = today.day
    days_remaining = days_in_month - days_passed
    
    # Calcul intelligent
    df_exp = df_month[df_month['amount'] < 0].copy()
    df_exp['amount'] = df_exp['amount'].abs()
    
    # 1. Dépenses fixes (déjà payées ce mois-ci)
    fixed_paid = df_exp[df_exp['category_validated'].isin(fixed_categories)]['amount'].sum()
    fixed_remaining = 0  # Estimation des fixes à venir
    
    # 2. Dépenses variables
    var_spent = df_exp[df_exp['category_validated'].isin(variable_categories)]['amount'].sum()
    
    # Calcul du rythme (seulement sur jours avec dépenses)
    days_with_expenses = len(df_exp['date'].dt.date.unique())
    if days_with_expenses > 0:
        avg_daily_var = var_spent / days_with_expenses
    else:
        avg_daily_var = 0
    
    # Scénarios
    income = df_month[df_month['amount'] > 0]['amount'].sum()
    
    scenarios = {
        'pessimiste': {
            'var_projection': avg_daily_var * days_remaining * 1.2,  # +20% marge
            'color': '🔴',
            'label': 'Si dépenses augmentent'
        },
        'réaliste': {
            'var_projection': avg_daily_var * days_remaining,
            'color': '🟡',
            'label': 'Tendance actuelle'
        },
        'optimiste': {
            'var_projection': avg_daily_var * days_remaining * 0.8,  # -20% économies
            'color': '🟢',
            'label': 'Si réduit de 20%'
        }
    }
    
    # Affichage
    st.subheader("🔮 Projections Fin de Mois")
    
    cols = st.columns(3)
    for i, (name, scenario) in enumerate(scenarios.items()):
        total_exp = fixed_paid + scenario['var_projection']
        balance = income - total_exp
        
        with cols[i]:
            st.markdown(f"{scenario['color']} **{scenario['label']}**")
            st.markdown(f"**{balance:+.0f}€**")
            st.caption(f"Dépenses: {total_exp:.0f}€")
            
            if name == 'optimiste' and balance > 0:
                st.success(f"+{balance:.0f}€ d'épargne !")
    
    # Recommandation personnalisée
    st.divider()
    current_var_daily = var_spent / days_passed if days_passed > 0 else 0
    remaining_daily_budget = (income - fixed_paid - var_spent) / days_remaining if days_remaining > 0 else 0
    
    if remaining_daily_budget < 0:
        st.error(f"💡 **Alerte**: Vous avez déjà dépassé votre capacité. Objectif: 0€/jour jusqu'à la fin du mois.")
    else:
        st.info(f"💡 **Conseil**: Pour tenir vos objectifs, ne dépassez pas **{remaining_daily_budget:.0f}€/jour** en variable.")


# ============================================================================
# 3. COMPOSANT: Suivi Budget avec Contexte Historique
# ============================================================================

def render_enhanced_budget_tracker(df_exp, cat_emoji_map, historical_data=None):
    """
    Budget tracker avec tendances et contexte.
    """
    from modules.db.budgets import get_budgets
    
    budgets = get_budgets()
    
    if budgets.empty:
        st.info("📝 **Aucun budget défini**")
        st.caption("Configurez vos budgets pour suivre vos dépenses")
        if st.button("➕ Créer mon premier budget", type="primary"):
            st.switch_page("pages/4_Intelligence.py")
        return
    
    # Calcul période
    num_months = 1
    if 'date_dt' in df_exp.columns and not df_exp.empty:
        num_months = max(1, len(df_exp['date_dt'].dt.strftime('%Y-%m').unique()))
    
    st.caption(f"Période: {num_months} mois")
    
    # Pour chaque budget
    for _, row in budgets.iterrows():
        cat_name = row['category']
        display_cat = f"{cat_emoji_map.get(cat_name, '🏷️')} {cat_name}"
        budget_amount = row['amount'] * num_months
        
        # Dépenses réelles
        spent = df_exp[df_exp['Catégorie'] == display_cat]['amount'].sum()
        percent = min(spent / budget_amount, 1.5) if budget_amount > 0 else 0
        
        # Comparaison historique (si données dispo)
        trend = None
        if historical_data and cat_name in historical_data:
            prev_spent = historical_data[cat_name]
            if prev_spent > 0:
                change = ((spent - prev_spent) / prev_spent) * 100
                trend = "↑" if change > 5 else "↓" if change < -5 else "→"
                trend_color = "red" if change > 5 else "green" if change < -5 else "gray"
        
        # Affichage carte
        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"**{display_cat}**")
                if trend:
                    st.caption(f"vs période précédente: {trend}")
            
            with col2:
                # Barre de progression colorée
                bar_color = "normal"
                if percent > 1.0:
                    bar_color = "red"
                elif percent > 0.8:
                    bar_color = "orange"
                
                st.progress(min(percent, 1.0), text=f"{percent*100:.0f}%")
                
                if percent > 1.0:
                    overrun = spent - budget_amount
                    st.error(f"Dépassé de {overrun:.0f}€")
                else:
                    remaining = budget_amount - spent
                    st.caption(f"Reste: {remaining:.0f}€ / {budget_amount:.0f}€")
            
            with col3:
                # Actions rapides
                if percent > 0.9:
                    if st.button("💡", key=f"tip_{cat_name}", help="Conseils"):
                        st.toast(f"Analyse de {cat_name}...")
                if st.button("📊", key=f"chart_{cat_name}", help="Historique"):
                    st.toast(f"Historique {cat_name}...")


# ============================================================================
# 4. DASHBOARD UNIFIÉ
# ============================================================================

def render_unified_budget_dashboard(df_current, df_full, selected_years, selected_months, cat_emoji_map):
    """
    Vue unifiée de tous les composants budget.
    """
    st.header("🎯 Suivi des Budgets", divider=True)
    
    # Section 1: Vue d'ensemble (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_budget = 0  # Calculer
        st.metric("Budgets actifs", "5")  # Exemple
    with col2:
        st.metric("Alertes", "2", delta="-1", delta_color="inverse")
    with col3:
        st.metric("Projection", "+350€", delta="Fin de mois")
    with col4:
        st.metric("Taux moyen", "78%", delta="-5%", delta_color="normal")
    
    st.divider()
    
    # Section 2: Alertes priorisées
    st.subheader("📈 Alertes & Recommandations")
    # render_prioritized_alerts(predictions, df_month)
    
    st.divider()
    
    # Section 3: Prévisions
    # render_smart_forecast(df_month, fixed_cats, variable_cats)
    
    st.divider()
    
    # Section 4: Suivi détaillé
    st.subheader("📋 Suivi par Catégorie")
    # render_enhanced_budget_tracker(df_exp, cat_emoji_map)


# ============================================================================
# EXEMPLE D'UTILISATION
# ============================================================================

if __name__ == "__main__":
    st.set_page_config(page_title="Budget Redesign Demo", layout="wide")
    
    st.title("🎨 Prototype: Refonte Page Budgets")
    st.caption("Ce fichier montre les améliorations proposées")
    
    st.markdown("---")
    st.markdown("### Exemple: Alertes Priorisées")
    
    # Données mock
    mock_predictions = [
        {'category': 'Courses', 'status': 'overrun', 'usage_percent': 120, 
         'current_spent': 600, 'projected_spent': 720, 'budget': 600, 'daily_avg': 24},
        {'category': 'Loisirs', 'status': 'warning', 'usage_percent': 85, 
         'current_spent': 170, 'projected_spent': 200, 'budget': 200, 'daily_avg': 6.8},
        {'category': 'Transport', 'status': 'ok', 'usage_percent': 45, 
         'current_spent': 45, 'projected_spent': 90, 'budget': 100, 'daily_avg': 3},
    ]
    
    # render_prioritized_alerts(mock_predictions, pd.DataFrame())
    
    st.markdown("---")
    st.markdown("### Exemple: Prévisions Scénarisées")
    # render_smart_forecast(pd.DataFrame(), [], [])
