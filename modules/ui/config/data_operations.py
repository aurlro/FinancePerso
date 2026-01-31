import streamlit as st
import pandas as pd
from io import BytesIO
from modules.db.transactions import (
    delete_transactions_by_period,
    get_transactions_by_criteria, delete_transaction_by_id,
    get_all_transactions
)
from modules.db.stats import get_available_months
from modules.ui.feedback import toast_success, toast_error, show_success, show_warning, show_info


def render_export_section():
    """
    Render only the export section.
    Can be used standalone or within render_data_operations.
    """
    df_all = get_all_transactions()
    if df_all.empty:
        st.info("Aucune transaction à exporter.")
        return
    
    col_ex1, col_ex2, col_ex3 = st.columns([2, 1, 1])
    
    with col_ex1:
        # Period filter for export
        available_months = get_available_months()
        export_period = st.selectbox(
            "Période à exporter",
            options=["Toutes"] + available_months,
            index=0,
            key="export_period"
        )
    
    # Filter data if needed
    if export_period != "Toutes":
        df_export = df_all[df_all['date'].str.startswith(export_period)].copy()
    else:
        df_export = df_all.copy()
    
    with col_ex2:
        st.markdown(f"<p style='margin-top:28px; font-size:0.9em; color:#666;'>{len(df_export)} transactions</p>", unsafe_allow_html=True)
    
    with col_ex3:
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        # CSV Export
        csv = df_export.to_csv(index=False, sep=';', encoding='utf-8-sig')
        st.download_button(
            label="📄 CSV",
            data=csv,
            file_name=f"financeperso_export_{export_period.replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Excel Export (if openpyxl is available)
    try:
        import openpyxl
        excel_buffer = BytesIO()
        df_export.to_excel(excel_buffer, index=False, sheet_name='Transactions')
        excel_buffer.seek(0)
        
        col_ex4, col_ex5 = st.columns([3, 1])
        with col_ex5:
            st.download_button(
                label="📊 Excel",
                data=excel_buffer,
                file_name=f"financeperso_export_{export_period.replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    except ImportError:
        st.caption("💡 Installez `openpyxl` pour l'export Excel : `pip install openpyxl`")


def render_data_operations():
    """
    Render the Données & Danger tab content.
    Dangerous operations: delete by period, search and delete specific transactions.
    """
    st.header("💾 Gestion des Données")
    
    # --- EXPORT SECTION ---
    st.subheader("📤 Exporter les données")
    st.markdown("Téléchargez vos transactions au format CSV ou Excel pour une sauvegarde externe ou une analyse dans un tableur.")
    
    render_export_section()
    
    st.divider()
    st.warning("⚠️ **Zone de Danger**  \nLes opérations ci-dessous sont irréversibles. Assurez-vous d'avoir une sauvegarde avant de supprimer des données.")
    
    # --- DELETE BY PERIOD ---
    st.subheader("🗑️ Supprimer par Période")
    st.markdown("Supprimez toutes les transactions d'un mois donné (utile pour nettoyer un import incorrect).")
    
    available_months = get_available_months()
    if not available_months:
        st.info("Aucune transaction dans la base.")
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
                        show_warning(f"⚠️ Confirmer la suppression de **{selected_month}** ? Cliquez à nouveau pour confirmer.", icon="⚠️")
                        st.rerun()
                    else:
                        with st.spinner(f"Suppression des transactions de {selected_month}..."):
                            count = delete_transactions_by_period(selected_month)
                        if count > 0:
                            toast_success(f"✅ {count} transactions supprimées ({selected_month})", icon="🗑️")
                            show_success(f"{count} transactions de {selected_month} ont été supprimées")
                        else:
                            show_info("Aucune transaction à supprimer pour cette période")
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
            show_info(f"Aucune transaction trouvée pour '{search_label}'", icon="🔍")
        else:
            show_success(f"**{len(results)}** transaction(s) trouvée(s)", icon="🔍")
            
            for _, row in results.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    c1.markdown(f"**{row['date']}** • {row['label']} • **{row['amount']:.2f}€** • {row['category']}")
                    if c2.button("🗑️", key=f"del_tx_{row['id']}"):
                        try:
                            delete_transaction_by_id(row['id'])
                            toast_success("Transaction supprimée", icon="🗑️")
                            st.rerun()
                        except Exception as e:
                            toast_error(f"Erreur : {e}", icon="❌")

    # --- VERSIONING ---
    st.divider()
    st.subheader("🚀 Mise à jour de Version")
    st.markdown("Analyse les derniers commits Git pour mettre à jour la version de l'application et générer le Changelog.")
    
    if st.button("🔄 Lancer la mise à jour (Git commits)", use_container_width=True):
        import subprocess
        with st.spinner("Analyse des commits Git..."):
            try:
                # Run the versioning script
                result = subprocess.run(["python3", "scripts/versioning.py"], capture_output=True, text=True)
                if result.returncode == 0:
                    toast_success("Version mise à jour", icon="🚀")
                    show_success(f"**Mise à jour réussie**")
                    with st.expander("📋 Détails des changements", expanded=False):
                        st.code(result.stdout)
                else:
                    toast_error("Échec de la mise à jour", icon="❌")
                    show_error(f"**Erreur :**\n\n{result.stderr}")
            except Exception as e:
                toast_error("Impossible de lancer le script", icon="❌")
                show_error(f"Impossible de lancer le script de versioning : {str(e)}")
