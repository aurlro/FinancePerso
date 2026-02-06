"""
Smart Recommendations Component for Budget Dashboard
Affiche les recommandations intelligentes par catégorie.
"""

import streamlit as st
import pandas as pd
from typing import List, Optional
from modules.transaction_types import filter_expense_transactions
from modules.ai.category_insights import (
    CategoryInsightsEngine, 
    CategoryInsight,
    render_category_insights_card,
    get_smart_recommendations
)


def render_smart_recommendations_section(df_full: pd.DataFrame, df_current: pd.DataFrame):
    """
    Section complète de recommandations intelligentes.
    À intégrer dans l'onglet Budgets.
    
    Args:
        df_full: Historique complet des transactions
        df_current: Transactions du mois en cours
    """
    st.subheader("💡 Recommandations Intelligentes")
    st.caption("Analyse personnalisée basée sur vos habitudes de dépenses")
    
    if df_current.empty or df_full.empty:
        st.info("📊 Importez des transactions pour recevoir des recommandations personnalisées.")
        return
    
    # Initialiser le moteur
    engine = CategoryInsightsEngine(df_full)
    insights = engine.get_top_insights(df_current, max_insights=5)
    
    if not insights:
        st.success("✅ Tout semble normal ! Aucune anomalie détectée ce mois-ci.")
        return
    
    # Résumé des opportunités
    total_savings = sum(i.savings_potential for i in insights if i.savings_potential)
    high_priority = sum(1 for i in insights if i.severity == 'high')
    
    if total_savings > 0 or high_priority > 0:
        cols = st.columns(2)
        with cols[0]:
            if high_priority > 0:
                st.error(f"🚨 **{high_priority}** problème{'s' if high_priority > 1 else ''} nécessite{'nt' if high_priority == 1 else ''} votre attention")
        with cols[1]:
            if total_savings > 0:
                st.success(f"💰 **{total_savings:.0f}€** d'économies potentielles ce mois-ci")
    
    st.divider()
    
    # Grouper par type d'insight
    anomalies = [i for i in insights if i.insight_type == 'anomaly']
    trends = [i for i in insights if i.insight_type == 'trend']
    suggestions = [i for i in insights if i.insight_type == 'suggestion']
    
    # Section 1: Anomalies (haute priorité)
    if anomalies:
        st.markdown("### 🚨 Dépenses à Vérifier")
        for insight in anomalies:
            _render_anomaly_card(insight, df_current)
        st.divider()
    
    # Section 2: Tendances
    if trends:
        st.markdown("### 📈 Tendances Détectées")
        for insight in trends:
            _render_trend_card(insight)
        st.divider()
    
    # Section 3: Suggestions d'économies
    if suggestions:
        st.markdown("### 💡 Opportunités d'Économies")
        for insight in suggestions:
            _render_suggestion_card(insight)


def _render_anomaly_card(insight: CategoryInsight, df_current: pd.DataFrame):
    """Rendu spécifique pour les anomalies."""
    with st.container(border=True):
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            st.markdown(f"**{insight.title}**")
            st.write(insight.description)
            
            if insight.amount:
                st.caption(f"Montant: **{insight.amount:.0f}€**")
        
        with col2:
            if insight.savings_potential and insight.savings_potential > 0:
                st.markdown(f"💰 **{insight.savings_potential:.0f}€** potentiel")
                st.caption("Si corrigé rapidement")
        
        with col3:
            st.markdown("### 🔴")
            
            # Boutons d'action
            action_cols = st.columns(1)
            with action_cols[0]:
                if st.button("🔍 Vérifier", key=f"check_{insight.category}_{insight.insight_type}", 
                           use_container_width=True, type="primary"):
                    # Afficher les transactions concernées
                    st.session_state[f"show_anomaly_{insight.category}"] = True
            
            if insight.action:
                if st.button("✏️ Modifier", key=f"edit_{insight.category}", 
                           use_container_width=True):
                    st.toast(f"Modification de la catégorie...", icon="✏️")
        
        # Détail des transactions si demandé
        if st.session_state.get(f"show_anomaly_{insight.category}", False):
            with st.expander(f"Transactions suspectes dans {insight.category}", expanded=True):
                # Récupérer les transactions anormales
                engine = CategoryInsightsEngine(df_current)  # Simplifié
                tx_anomalies = engine.get_anomalous_transactions(insight.category, df_current)
                
                if tx_anomalies:
                    for anomaly in tx_anomalies[:3]:  # Limiter à 3
                        with st.container():
                            cols = st.columns([2, 1, 1])
                            with cols[0]:
                                st.write(f"**{anomaly.label}**")
                                st.caption(f"{anomaly.date}")
                            with cols[1]:
                                st.write(f"{anomaly.amount:.0f}€")
                                if anomaly.expected_amount:
                                    st.caption(f"habituellement: {anomaly.expected_amount:.0f}€")
                            with cols[2]:
                                if anomaly.deviation_percent:
                                    st.error(f"+{anomaly.deviation_percent:.0f}%")
                else:
                    st.info("Aucune transaction spécifique à afficher.")


def _render_trend_card(insight: CategoryInsight):
    """Rendu spécifique pour les tendances."""
    is_positive = "Réussite" in insight.title or "réduit" in insight.description.lower()
    
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**{insight.title}** — *{insight.category}*")
            st.write(insight.description)
        
        with col2:
            icon = "📈" if "augmenté" in insight.description else "📉" if "réduit" in insight.description else "📊"
            st.markdown(f"### {icon}")
            
            if insight.action:
                if st.button(insight.action, key=f"trend_{insight.category}", 
                           use_container_width=True):
                    st.toast(f"Ouverture du détail...", icon="📊")


def _render_suggestion_card(insight: CategoryInsight):
    """Rendu spécifique pour les suggestions d'économies."""
    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"**{insight.title}** — *{insight.category}*")
            st.write(insight.description)
        
        with col2:
            if insight.savings_potential:
                st.success(f"💰 **{insight.savings_potential:.0f}€/mois**")
        
        with col3:
            st.markdown("### 💡")
            if st.button("En savoir +", key=f"sugg_{insight.category}", 
                       use_container_width=True):
                st.toast(f"Conseils pour {insight.category}...", icon="💡")


def render_quick_actions_banner(df_current: pd.DataFrame, budgets_df: pd.DataFrame) -> Optional[str]:
    """
    Bannière d'actions rapides basées sur l'état actuel.
    Retourne l'action recommandée principale.
    
    Args:
        df_current: Données du mois courant
        budgets_df: DataFrame des budgets
        
    Returns:
        Message de l'action recommandée ou None
    """
    if df_current.empty:
        return None
    
    # Détecter l'état
    uncategorized = df_current[
        (df_current['category_validated'].isna()) | 
        (df_current['category_validated'] == 'Non catégorisé')
    ]
    
    if len(uncategorized) > 5:
        return f"📝 **{len(uncategorized)} transactions non catégorisées** — Passez à la validation"
    
    # Vérifier les budgets en dépassement
    if not budgets_df.empty:
        # Calcul simplifié
        expenses = filter_expense_transactions(df_current).groupby('category_validated')['amount'].sum().abs()
        
        for _, budget in budgets_df.iterrows():
            cat = budget['category']
            spent = expenses.get(cat, 0)
            if spent > budget['amount'] * 1.1:  # +10%
                overrun = spent - budget['amount']
                return f"🚨 **Budget {cat} dépassé** de {overrun:.0f}€ — Voir les recommandations"
    
    return None


# Export pour utilisation dans sections.py
__all__ = [
    'render_smart_recommendations_section',
    'render_quick_actions_banner',
    'get_smart_recommendations'
]