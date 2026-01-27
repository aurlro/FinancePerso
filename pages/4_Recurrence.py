import streamlit as st
import pandas as pd
from modules.data_manager import get_all_transactions, get_categories_with_emojis
from modules.analytics import detect_recurring_payments
from modules.ui import load_css

st.set_page_config(page_title="Récurrence", page_icon="🔁", layout="wide")
load_css()

st.title("🔁 Analyse des Récurrences")
st.markdown("Détection automatique des abonnements, factures et revenus réguliers.")

df = get_all_transactions()

if df.empty:
    st.info("Aucune donnée disponible pour l'analyse.")
else:
    # We only analyze validated transactions for better accuracy
    validated_df = df[df['status'] == 'validated']
    
    if validated_df.empty:
        st.warning("Veuillez valider quelques transactions pour permettre l'analyse des récurrences.")
    else:
        with st.spinner("Analyse des tendances en cours..."):
            recurring_df = detect_recurring_payments(validated_df)
        
        if recurring_df.empty:
            st.info("Aucune récurrence claire détectée pour le moment. L'analyse nécessite au moins 2 occurrences d'un même type d'opération.")
        else:
            st.success(f"**{len(recurring_df)}** récurrences potentielles détectées.")
            
            cat_emoji_map = get_categories_with_emojis()
            
            # 1. Subscriptions & Bills (Expenses)
            st.subheader("💳 Abonnements & Charges")
            expenses = recurring_df[recurring_df['avg_amount'] < 0].copy()
            
            if expenses.empty:
                st.info("Aucun abonnement détecté.")
            else:
                for _, row in expenses.iterrows():
                    with st.container(border=True):
                        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                        
                        cat_name = row['category']
                        emoji = cat_emoji_map.get(cat_name, "🏷️")
                        
                        c1.markdown(f"**{row['label']}**")
                        c1.caption(f"{emoji} {cat_name}")
                        
                        c2.markdown(f"**{abs(row['avg_amount']):,.2f} €**")
                        c2.caption("Montant Moyen")
                        
                        c3.markdown(f"**{row['frequency_label']}**")
                        c3.caption(f"Tous les {row['frequency_days']}j")
                        
                        c4.markdown(f":grey[{row['last_date']}]")
                        c4.caption("Dernière occurrence")
            
            st.divider()
            
            # 2. Regular Incomes
            st.subheader("💰 Revenus Réguliers")
            incomes = recurring_df[recurring_df['avg_amount'] > 0].copy()
            
            if incomes.empty:
                st.info("Aucun revenu récurrent détecté.")
            else:
                for _, row in incomes.iterrows():
                    with st.container(border=True):
                        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                        
                        c1.markdown(f"**{row['label']}**")
                        c1.caption(f"✨ {row['category']}")
                        
                        c2.markdown(f"**{row['avg_amount']:,.2f} €**")
                        c2.caption("Montant Moyen")
                        
                        c3.markdown(f"**{row['frequency_label']}**")
                        c3.caption(f"Tous les {row['frequency_days']}j")
                        
                        c4.markdown(f":grey[{row['last_date']}]")
                        c4.caption("Dernière occurrence")

            st.info("💡 Cette analyse se base sur la similarité des libellés et la régularité des dates. Assurez-vous que vos transactions sont bien catégorisées pour une meilleure précision.")

from modules.ui.layout import render_app_info
render_app_info()
