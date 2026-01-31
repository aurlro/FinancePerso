"""
Quick Actions Component - Popup-based quick actions for the dashboard.

Provides inline actions without leaving the home page using Streamlit popovers.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from modules.data_manager import (
    get_pending_transactions, bulk_update_transaction_status,
    get_members, get_categories, add_member, add_category, add_learning_rule
)
from modules.ui.feedback import (
    toast_success, toast_error, toast_warning,
    validation_feedback, save_feedback, show_info, show_warning
)
from modules.ingestion import load_transaction_file
from modules.data_manager import save_transactions
from modules.db.transactions import get_all_hashes
from modules.categorization import categorize_transaction
from modules.ai_manager import is_ai_available


def render_quick_validation_popover():
    """
    Render a popover for quick validation of pending transactions.
    Shows up to 5 transactions that can be validated inline.
    """
    with st.popover("🧠 Validation rapide", use_container_width=True):
        st.markdown("#### Validation rapide")
        st.caption("Validez vos transactions en attente sans quitter l'accueil")
        
        # Get pending transactions
        df = get_pending_transactions()
        
        if df.empty:
            st.success("✅ Toutes les transactions sont déjà validées !")
            if st.button("Aller à la validation complète →", use_container_width=True):
                st.switch_page("pages/2_Validation.py")
            return
        
        # Show count
        pending_count = len(df)
        st.info(f"📋 {pending_count} transaction(s) en attente")
        
        # Get available options
        members = get_members()
        member_names = members['name'].tolist() if not members.empty else []
        categories = get_categories()
        
        # Show up to 5 transactions
        display_df = df.head(5)
        validated_count = 0
        
        for idx, row in display_df.iterrows():
            with st.container(border=True):
                cols = st.columns([2, 1, 1, 0.5])
                
                with cols[0]:
                    st.write(f"**{row['label'][:40]}...**" if len(row['label']) > 40 else f"**{row['label']}**")
                    st.caption(f"{row['date']} • {row['amount']:.2f} €")
                
                with cols[1]:
                    cat_key = f"quick_cat_{row['id']}"
                    current_cat = row.get('category_validated') if row.get('category_validated') != 'Inconnu' else categories[0] if categories else "Inconnu"
                    selected_cat = st.selectbox(
                        "Catégorie",
                        options=categories,
                        index=categories.index(current_cat) if current_cat in categories else 0,
                        key=cat_key,
                        label_visibility="collapsed"
                    )
                
                with cols[2]:
                    mem_key = f"quick_mem_{row['id']}"
                    member_options = [""] + member_names
                    selected_member = st.selectbox(
                        "Payeur",
                        options=member_options,
                        key=mem_key,
                        label_visibility="collapsed"
                    )
                
                with cols[3]:
                    if st.button("✓", key=f"quick_val_{row['id']}", type="primary"):
                        tags = None
                        beneficiary = None
                        if selected_member:
                            # Use member as beneficiary if selected
                            beneficiary = selected_member
                        
                        bulk_update_transaction_status(
                            [row['id']], 
                            selected_cat, 
                            tags=tags, 
                            beneficiary=beneficiary
                        )
                        validated_count += 1
                        toast_success(f"Transaction validée", icon="✅")
                        st.rerun()
        
        # Actions footer
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Valider tout en masse...", use_container_width=True, type="secondary"):
                st.switch_page("pages/2_Validation.py")
        
        with col2:
            if pending_count > 5:
                st.caption(f"+ {pending_count - 5} autres transactions...")


def render_quick_config_popover():
    """
    Render a popover for quick configuration actions.
    Allows adding members, categories, or rules quickly.
    """
    with st.popover("⚙️ Configuration rapide", use_container_width=True):
        st.markdown("#### Configuration rapide")
        st.caption("Ajoutez membres, catégories ou règles rapidement")
        
        tab_member, tab_category, tab_rule = st.tabs(["👤 Membre", "🏷️ Catégorie", "🧠 Règle"])
        
        # Tab 1: Add Member
        with tab_member:
            with st.form("quick_add_member", clear_on_submit=True):
                new_name = st.text_input("Nom", placeholder="Ex: Jean")
                new_type = st.radio("Type", ["HOUSEHOLD", "EXTERNAL"], 
                                   format_func=lambda x: "🏘️ Foyer" if x == "HOUSEHOLD" else "💼 Tiers",
                                   horizontal=True)
                
                if st.form_submit_button("Ajouter", use_container_width=True, type="primary"):
                    if new_name:
                        if add_member(new_name, new_type):
                            type_label = "Foyer" if new_type == "HOUSEHOLD" else "Tiers"
                            save_feedback(f"Membre '{new_name}' ({type_label})", created=True)
                            st.rerun()
                        else:
                            toast_warning(f"Le membre '{new_name}' existe déjà", icon="⚠️")
                    else:
                        toast_warning("Veuillez entrer un nom", icon="⚠️")
        
        # Tab 2: Add Category
        with tab_category:
            with st.form("quick_add_category", clear_on_submit=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    new_cat = st.text_input("Nom", placeholder="Ex: Sports")
                with col2:
                    emoji = st.text_input("Emoji", value="🏷️")
                
                is_fixed = st.checkbox("Dépense fixe (loyer, abonnement...)")
                
                if st.form_submit_button("Ajouter", use_container_width=True, type="primary"):
                    if new_cat:
                        if add_category(new_cat, emoji, int(is_fixed)):
                            save_feedback(f"Catégorie '{new_cat}'", created=True)
                            st.rerun()
                        else:
                            toast_warning("Cette catégorie existe déjà", icon="⚠️")
                    else:
                        toast_warning("Veuillez entrer un nom", icon="⚠️")
        
        # Tab 3: Add Rule
        with tab_rule:
            with st.form("quick_add_rule", clear_on_submit=True):
                pattern = st.text_input(
                    "Mot-clé ou pattern",
                    placeholder="Ex: UBER, AMAZON, NETFLIX..."
                )
                target_cat = st.selectbox("Catégorie cible", options=get_categories())
                
                if st.form_submit_button("Créer la règle", use_container_width=True, type="primary"):
                    if pattern:
                        try:
                            if add_learning_rule(pattern.strip(), target_cat):
                                toast_success(f"Règle '{pattern}' → '{target_cat}' créée !", icon="🧠")
                                st.rerun()
                            else:
                                toast_warning("Cette règle existe peut-être déjà", icon="⚠️")
                        except Exception as e:
                            toast_error(f"Erreur: {e}", icon="❌")
                    else:
                        toast_warning("Veuillez entrer un mot-clé", icon="⚠️")


def render_quick_import_popover():
    """
    Render a popover for quick CSV import.
    Simplified import flow directly from the dashboard.
    """
    with st.popover("📥 Import rapide", use_container_width=True):
        st.markdown("#### Import rapide")
        st.caption("Importez un fichier CSV directement")
        
        # AI availability warning
        if not is_ai_available():
            show_warning("Mode hors ligne : seules les règles manuelles seront appliquées", icon="⚠️")
        
        uploaded_file = st.file_uploader(
            "Fichier CSV BoursoBank",
            type=['csv'],
            help="Sélectionnez votre fichier de relevé bancaire"
        )
        
        if uploaded_file is not None:
            # Account selection
            from modules.data_manager import get_all_account_labels
            existing_accounts = get_all_account_labels()
            
            if existing_accounts:
                account = st.selectbox("Compte", existing_accounts)
            else:
                account = st.text_input("Nom du compte", value="Compte Principal")
            
            # Preview and import
            try:
                df = load_transaction_file(uploaded_file, mode="bourso_preset")
                
                if isinstance(df, tuple):
                    toast_error(f"Erreur: {df[1]}")
                    return
                
                # Check for duplicates
                existing_hashes = get_all_hashes()
                if existing_hashes:
                    duplicates_mask = df['tx_hash'].isin(existing_hashes)
                    num_duplicates = duplicates_mask.sum()
                    num_new = len(df) - num_duplicates
                    
                    if num_duplicates > 0:
                        st.warning(f"⚠️ {num_duplicates} doublon(s) détecté(s)")
                        df = df[~duplicates_mask]  # Filter out duplicates
                else:
                    num_new = len(df)
                
                if num_new == 0:
                    show_info("Toutes ces transactions existent déjà")
                    return
                
                st.success(f"📊 {num_new} nouvelles transactions prêtes")
                
                # Preview
                with st.expander("Aperçu"):
                    preview = df[['date', 'label', 'amount']].head(3)
                    st.dataframe(preview, use_container_width=True, hide_index=True)
                
                # Import button
                if st.button("🚀 Importer maintenant", type="primary", use_container_width=True):
                    with st.spinner("Import en cours..."):
                        # Categorize
                        results = []
                        for _, row in df.iterrows():
                            cat, source, conf = categorize_transaction(row['label'], row['amount'], row['date'])
                            results.append(cat)
                        
                        df['category_validated'] = results
                        df['account_label'] = account
                        
                        # Save
                        count, skipped = save_transactions(df)
                    
                    toast_success(f"{count} transactions importées !", icon="🎉")
                    if count > 5:
                        st.balloons()
                    st.rerun()
                    
            except Exception as e:
                toast_error(f"Erreur lors de l'import: {e}", icon="❌")


def render_quick_stats_popover():
    """
    Render a popover showing quick stats about current month spending.
    """
    with st.popover("📊 Stats rapides", use_container_width=True):
        st.markdown("#### Ce mois-ci")
        
        # Get current month data
        df = get_pending_transactions()  # This gets all, not just pending
        # Actually get all transactions
        from modules.db.transactions import get_all_transactions
        df = get_all_transactions()
        
        if df.empty:
            show_info("Aucune donnée disponible")
            return
        
        # Filter current month
        current_month = datetime.now().strftime('%Y-%m')
        df['date_dt'] = pd.to_datetime(df['date'])
        month_df = df[df['date_dt'].dt.strftime('%Y-%m') == current_month]
        
        if month_df.empty:
            show_info(f"Aucune transaction pour {current_month}")
            return
        
        # Calculate stats
        expenses = month_df[month_df['amount'] < 0]['amount'].sum()
        income = month_df[month_df['amount'] > 0]['amount'].sum()
        balance = income + expenses
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Dépenses", f"{abs(expenses):.0f} €", delta_color="inverse")
        with col2:
            st.metric("Revenus", f"{income:.0f} €")
        with col3:
            delta_color = "normal" if balance >= 0 else "inverse"
            st.metric("Solde", f"{balance:.0f} €", delta_color=delta_color)
        
        # Top categories
        st.divider()
        st.caption("Top catégories de dépenses")
        
        expenses_df = month_df[month_df['amount'] < 0].copy()
        if not expenses_df.empty:
            expenses_df['amount_abs'] = expenses_df['amount'].abs()
            top_cats = expenses_df.groupby('category_validated')['amount_abs'].sum().sort_values(ascending=False).head(3)
            
            for cat, amount in top_cats.items():
                st.progress(min(1.0, amount / abs(expenses)), text=f"{cat}: {amount:.0f} €")
        
        # Link to full stats
        st.divider()
        if st.button("Voir la synthèse complète →", use_container_width=True):
            st.switch_page("pages/3_Synthese.py")


def render_quick_actions_grid():
    """
    Render the main quick actions grid with popovers.
    This replaces the simple buttons with interactive popovers.
    """
    st.subheader("📌 Actions Rapides")
    
    col_a, col_b, col_c, col_d = st.columns(4)
    
    with col_a:
        render_quick_validation_popover()
    
    with col_b:
        render_quick_config_popover()
    
    with col_c:
        render_quick_import_popover()
    
    with col_d:
        render_quick_stats_popover()
