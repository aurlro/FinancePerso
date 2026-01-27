import streamlit as st
from modules.data_manager import (
    get_available_months, delete_transactions_by_period,
    get_transactions_by_criteria, delete_transaction_by_id
)

def render_data_operations():
    """
    Render the Données & Danger tab content.
    Dangerous operations: delete by period, search and delete specific transactions.
    """
    st.header("💾 Gestion des Données")
    st.warning("⚠️ **Zone de Danger**  \nLes opérations ci-dessous sont irréversibles. Assurez-vous d'avoir une sauvegarde avant de supprimer des données.")
    
    # --- DELETE BY PERIOD ---
    st.subheader("🗑️ Supprimer par Période")
    st.markdown("Supprimez toutes les transactions d'un mois donné (utile pour nettoyer un import incorrect).")
    
    available_months = get_available_months()
    if not available_months:
        st.info("Aucune.transaction dans la base.")
    else:
        col_d1, col_d2 = st.columns([2, 1])
        with col_d1:
            selected_month = st.selectbox(
                "Mois à supprimer",
                available_months,
                format_func=lambda x: f"{x} ({len(get_transactions_by_criteria(period=x))} tx)",
                key="month_to_delete"
            )
        
        with col_d2:
            st.markdown("<div style='height: 0.1rem;'></div>", unsafe_allow_html=True)
            if st.button("🗑️ Supprimer", type="primary", use_container_width=True, key="btn_delete_month"):
                if selected_month:
                    # Confirmation via checkbox
                    if 'confirm_delete_month' not in st.session_state:
                        st.session_state['confirm_delete_month'] = False
                    
                    if not st.session_state['confirm_delete_month']:
                        st.session_state['confirm_delete_month'] = True
                        st.warning(f"⚠️ Confirmer la suppression de **{selected_month}** ?")
                        st.rerun()
                    else:
                        count = delete_transactions_by_period(selected_month)
                        st.success(f"✅ {count} transactions supprimées pour {selected_month}.")
                        st.session_state['confirm_delete_month'] = False
                        st.rerun()
    
    # Reset confirmation if month changed
    if 'confirm_delete_month' in st.session_state and st.session_state.get('month_to_delete') != st.session_state.get('last_selected_month'):
        st.session_state['confirm_delete_month'] = False
        st.session_state['last_selected_month'] = st.session_state.get('month_to_delete')
    
    # --- TRANSACTION SEARCH & DELETE ---
    st.divider()
    st.subheader("🔍 Rechercher et Supprimer")
    st.markdown("Trouvez et supprimez des transactions spécifiques.")
    
    search_label = st.text_input("Rechercher par libellé", placeholder="Ex: AMAZON, SNCF...")
    
    if search_label:
        results = get_transactions_by_criteria(label_contains=search_label)
        if results.empty:
            st.info(f"Aucune transaction trouvée pour '{search_label}'.")
        else:
            st.success(f"**{len(results)}** transaction(s) trouvée(s).")
            
            for _, row in results.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    c1.markdown(f"**{row['date']}** • {row['label']} • **{row['amount']:.2f}€** • {row['category']}")
                    if c2.button("🗑️", key=f"del_tx_{row['id']}"):
                        delete_transaction_by_id(row['id'])
                        st.success("Transaction supprimée !")
                        st.rerun()
