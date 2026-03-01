"""Vue Couple - Résumé pour le mode couple.

Usage:
    from modules.ui.v5_5.dashboard.couple_summary import render_couple_summary
    
    render_couple_summary()
"""

import streamlit as st
from modules.db.transactions import get_all_transactions


def render_couple_summary() -> None:
    """Affiche un résumé simplifié pour le couple."""
    try:
        import pandas as pd
        
        df = get_all_transactions()
        if df.empty:
            st.info("Aucune donnée à afficher")
            return
        
        # Récupérer les membres
        members = df['member'].unique() if 'member' in df.columns else ['Anonyme']
        
        if len(members) < 2:
            st.info("💡 Ajoutez un membre pour voir la répartition couple")
            return
        
        # Calculer les dépenses par membre
        expenses_by_member = {}
        for member in members:
            member_df = df[df['member'] == member] if 'member' in df.columns else df
            expenses = abs(member_df[member_df['amount'] < 0]['amount'].sum())
            expenses_by_member[member] = expenses
        
        # Afficher en colonnes
        cols = st.columns(len(members))
        
        for idx, (member, expenses) in enumerate(expenses_by_member.items()):
            with cols[idx]:
                with st.container(border=True):
                    st.markdown(f"**{member}**")
                    st.markdown(f"<div style='font-size: 1.5rem; font-weight: 600; color: #EF4444;'>{expenses:,.0f} €</div>", unsafe_allow_html=True)
                    st.caption("Dépenses ce mois")
        
        # Total
        total = sum(expenses_by_member.values())
        st.markdown(f"<div style='text-align: center; margin-top: 1rem;'><b>Total:</b> {total:,.0f} €</div>", unsafe_allow_html=True)
        
        # Bouton vers la vue couple complète
        if st.button("Voir le détail couple →", use_container_width=True):
            st.switch_page("pages/02_Dashboard.py")
            
    except Exception as e:
        st.error(f"Erreur lors du chargement de la vue couple: {str(e)}")
