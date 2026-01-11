import streamlit as st
from modules.data_manager import get_learning_rules, delete_learning_rule
import pandas as pd

st.set_page_config(page_title="Règles & Mémoire", page_icon="🧠", layout="wide")

st.title("🧠 Mémoire de l'assistant")
st.markdown("Ici, vous pouvez voir et gérer les règles apprises automatiquement lors de vos validations.")

rules_df = get_learning_rules()

if rules_df.empty:
    st.info("Aucune règle apprise pour le moment. Cochez 'Mém.' lors de la validation pour enseigner !")
else:
    st.markdown(f"**{len(rules_df)}** règles actives.")
    
    # Display as table with delete action
    for index, row in rules_df.iterrows():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        
        with col1:
            st.code(row['pattern'], language="text")
        with col2:
            st.markdown(f"**{row['category']}**")
        with col3:
            st.caption(f"Créé le {row['created_at']}")
        with col4:
            if st.button("🗑️", key=f"del_{row['id']}", help="Supprimer cette règle"):
                delete_learning_rule(row['id'])
                st.rerun()
        st.divider()
        st.divider()

st.header("🗑️ Zone de Danger")
with st.expander("Réinitialiser les données"):
    st.warning("Attention, ces actions sont irréversibles.")
    
    from modules.data_manager import get_available_months, delete_transactions_by_period
    
    months = get_available_months()
    if not months:
        st.write("Aucune donnée à supprimer.")
    else:
        selected_month = st.selectbox("Sélectionner un mois à supprimer", months)
        if st.button(f"Supprimer les transactions de {selected_month}", type="primary"):
            count = delete_transactions_by_period(selected_month)
            st.success(f"{count} transactions supprimées pour {selected_month}.")
            st.rerun()
