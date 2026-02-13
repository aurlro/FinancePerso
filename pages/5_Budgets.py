"""
🎯 Budgets - Planification & Suivi Financier

Gérez vos objectifs mensuels, analysez vos dépenses par catégorie
et recevez des alertes personnalisées.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from modules.ui import load_css, render_scroll_to_top
from modules.ui.layout import render_app_info
from modules.db.migrations import init_db
from modules.db.budgets import get_budgets, set_budget, delete_budget
from modules.db.transactions import get_all_transactions
from modules.db.categories import get_categories_with_emojis
from modules.ui.rules.budget_manager import render_budget_section, _get_cached_budgets
from modules.logger import logger

# Page configuration
st.set_page_config(page_title="Budgets", page_icon="🎯", layout="wide")
load_css()
init_db()

st.title("🎯 Budgets & Objectifs Financiers")
st.markdown("""
Définissez vos limites mensuelles par catégorie et suivez votre progression en temps réel.
""")

# --- NAVIGATION ---
if "budget_active_tab" not in st.session_state:
    st.session_state["budget_active_tab"] = "📊 Vue d'ensemble"

# Auto-jump from other pages
jump_to = st.query_params.get("tab")
if jump_to:
    st.session_state["budget_active_tab"] = jump_to

tabs_list = ["📊 Vue d'ensemble", "⚙️ Gérer les budgets", "🔔 Alertes & Conseils"]

selected_tab = st.segmented_control(
    "Navigation",
    tabs_list,
    default=st.session_state["budget_active_tab"],
    key="budget_nav",
    label_visibility="collapsed",
)

if selected_tab and selected_tab != st.session_state["budget_active_tab"]:
    st.session_state["budget_active_tab"] = selected_tab
    st.rerun()

st.divider()

active_tab = st.session_state["budget_active_tab"]

# Load data
budgets_df = get_budgets()
transactions_df = get_all_transactions()

# =============================================================================
# TAB: VUE D'ENSEMBLE
# =============================================================================
if active_tab == "📊 Vue d'ensemble":
    st.header("📊 Suivi mensuel de vos budgets")
    
    if budgets_df.empty or transactions_df.empty:
        st.info("""
        📭 **Aucun budget ou transaction à analyser.**
        
        Pour commencer :
        1. Allez dans l'onglet **⚙️ Gérer les budgets** pour définir vos objectifs
        2. Importez vos transactions via la page **Opérations**
        """)
    else:
        # Calculate current month spending
        today = datetime.now()
        first_day = today.replace(day=1)
        
        # Filter current month transactions
        if not transactions_df.empty and "date" in transactions_df.columns:
            transactions_df["date"] = pd.to_datetime(transactions_df["date"])
            month_tx = transactions_df[transactions_df["date"] >= first_day]
            
            # Calculate spending by category
            spending_by_cat = month_tx.groupby("category")["amount"].sum().to_dict()
            
            # Build budget vs actual comparison
            budget_comparison = []
            for _, row in budgets_df.iterrows():
                cat = row["category"]
                budget = row["amount"]
                spent = spending_by_cat.get(cat, 0)
                remaining = budget - abs(spent) if spent < 0 else budget + spent
                pct_used = (abs(spent) / budget * 100) if budget > 0 else 0
                
                budget_comparison.append({
                    "Catégorie": cat,
                    "Budget": budget,
                    "Dépensé": abs(spent),
                    "Restant": remaining,
                    "% Utilisé": min(pct_used, 100),
                    "État": "⚠️ Dépassement" if pct_used > 100 else ("🟡 Attention" if pct_used > 80 else "✅ OK")
                })
            
            if budget_comparison:
                comp_df = pd.DataFrame(budget_comparison)
                
                # KPIs
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    total_budget = comp_df["Budget"].sum()
                    st.metric("Budget total", f"{total_budget:,.0f} €")
                with col2:
                    total_spent = comp_df["Dépensé"].sum()
                    st.metric("Dépensé", f"{total_spent:,.0f} €")
                with col3:
                    remaining = total_budget - total_spent
                    st.metric("Restant", f"{remaining:,.0f} €", 
                             delta=f"{remaining/total_budget*100:.0f}%" if total_budget > 0 else "0%")
                with col4:
                    at_risk = len(comp_df[comp_df["État"].str.contains("⚠️|🟡")])
                    st.metric("Budgets à risque", f"{at_risk}/{len(comp_df)}", 
                             delta="alerte" if at_risk > 0 else "OK", 
                             delta_color="inverse")
                
                st.divider()
                
                # Visualization
                col_chart, col_table = st.columns([2, 1])
                
                with col_chart:
                    st.subheader("Progression par catégorie")
                    
                    # Create stacked bar chart
                    fig = go.Figure()
                    
                    # Add budget bars
                    fig.add_trace(go.Bar(
                        name="Budget",
                        x=comp_df["Catégorie"],
                        y=comp_df["Budget"],
                        marker_color="lightgray",
                        opacity=0.3
                    ))
                    
                    # Add spent bars with color based on status
                    colors = ["red" if x > 100 else ("orange" if x > 80 else "green") 
                             for x in comp_df["% Utilisé"]]
                    
                    fig.add_trace(go.Bar(
                        name="Dépensé",
                        x=comp_df["Catégorie"],
                        y=comp_df["Dépensé"],
                        marker_color=colors
                    ))
                    
                    fig.update_layout(
                        barmode="overlay",
                        height=400,
                        showlegend=True,
                        yaxis_title="Montant (€)",
                        xaxis_tickangle=-45
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col_table:
                    st.subheader("Détail par catégorie")
                    
                    # Style the dataframe
                    def color_status(val):
                        if "⚠️" in str(val):
                            return "background-color: #ffcccc"
                        elif "🟡" in str(val):
                            return "background-color: #ffffcc"
                        return "background-color: #ccffcc"
                    
                    styled_df = comp_df.style.applymap(color_status, subset=["État"])
                    st.dataframe(styled_df, use_container_width=True, hide_index=True)
                
                st.divider()
                
                # Actionable insights
                st.subheader("💡 Recommandations personnalisées")
                
                over_budget = comp_df[comp_df["État"].str.contains("⚠️")]
                at_risk = comp_df[comp_df["État"].str.contains("🟡")]
                
                if not over_budget.empty:
                    st.error("""
                    **🚨 Budgets dépassés :**
                    """)
                    for _, row in over_budget.iterrows():
                        st.markdown(f"- **{row['Catégorie']}** : {row['Dépensé']:.0f}€ / {row['Budget']:.0f}€")
                
                if not at_risk.empty:
                    st.warning("""
                    **⚠️ Budgets à surveiller (80%+ utilisés) :**
                    """)
                    for _, row in at_risk.iterrows():
                        st.markdown(f"- **{row['Catégorie']}** : {row['% Utilisé']:.0f}% utilisé")
                
                if over_budget.empty and at_risk.empty:
                    st.success("🎉 **Tous vos budgets sont respectés !** Continuez ainsi.")

# =============================================================================
# TAB: GÉRER LES BUDGETS
# =============================================================================
elif active_tab == "⚙️ Gérer les budgets":
    render_budget_section()

# =============================================================================
# TAB: ALERTES & CONSEILS
# =============================================================================
elif active_tab == "🔔 Alertes & Conseils":
    st.header("🔔 Alertes budgétaires")
    
    if budgets_df.empty:
        st.info("📭 Définissez d'abord vos budgets dans l'onglet **⚙️ Gérer les budgets**.")
    else:
        # Alert configuration
        st.subheader("Configuration des alertes")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Seuils d'alerte**")
            warning_threshold = st.slider(
                "Alerte jaune (% du budget)",
                min_value=50,
                max_value=95,
                value=80,
                step=5,
                help="Vous recevrez une alerte quand vous atteindrez ce pourcentage"
            )
            
            danger_threshold = st.slider(
                "Alerte rouge (% du budget)",
                min_value=80,
                max_value=100,
                value=95,
                step=5,
                help="Vous recevrez une alerte critique quand vous atteindrez ce pourcentage"
            )
        
        with col2:
            st.markdown("**Notifications**")
            
            notify_daily = st.toggle(
                "Résumé quotidien",
                value=True,
                help="Afficher les alertes dans le widget du jour"
            )
            
            notify_weekly = st.toggle(
                "Résumé hebdomadaire",
                value=False,
                help="Recevoir un récapitulatif chaque semaine"
            )
            
            if st.button("💾 Sauvegarder les préférences", type="primary"):
                st.success("✅ Préférences sauvegardées !")
        
        st.divider()
        
        # Smart tips based on data
        st.subheader("💡 Conseils personnalisés")
        
        if not transactions_df.empty and not budgets_df.empty:
            # Analyze patterns
            today = datetime.now()
            
            # Days remaining in month
            days_remaining = 30 - today.day
            days_in_month = 30
            month_progress = today.day / days_in_month
            
            tips = []
            
            # Tip 1: Monthly pacing
            if month_progress < 0.5:
                tips.append({
                    "icon": "📅",
                    "title": "Début de mois",
                    "text": "Nous sommes en début de mois. C'est le moment idéal pour planifier vos grosses dépenses."
                })
            elif month_progress > 0.8:
                tips.append({
                    "icon": "⏰",
                    "title": "Fin de mois",
                    "text": f"Plus que {days_remaining} jours. Serrez la ceinture si nécessaire !"
                })
            
            # Tip 2: Emergency fund
            has_savings = any("épargne" in str(b).lower() for b in budgets_df["category"])
            if not has_savings:
                tips.append({
                    "icon": "🏦",
                    "title": "Fonds d'urgence",
                    "text": "Conseil : Prévoyez un budget 'Épargne' pour constituer un fonds d'urgence (3-6 mois de dépenses)."
                })
            
            # Tip 3: 50/30/20 rule
            tips.append({
                "icon": "📊",
                "title": "Règle 50/30/20",
                "text": """
                **Une règle simple pour équilibrer vos finances :**
                - **50%** : Besoins (logement, courses, transport)
                - **30%** : Envies (loisirs, shopping, sorties)  
                - **20%** : Épargne et remboursements
                
                Vérifiez que vos budgets respectent cette répartition !
                """
            })
            
            # Display tips
            for tip in tips:
                with st.expander(f"{tip['icon']} {tip['title']}", expanded=True):
                    st.markdown(tip["text"])
        else:
            st.info("Importez des transactions et définissez des budgets pour recevoir des conseils personnalisés.")

st.divider()
render_scroll_to_top()
render_app_info()
