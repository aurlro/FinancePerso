"""
Quick Actions Component - Popup-based quick actions for the dashboard.

Provides inline actions without leaving the home page using Streamlit popovers.
"""

from datetime import datetime

import pandas as pd
import streamlit as st

from modules.ai_manager import is_ai_available
from modules.categorization import categorize_transaction
from modules.db.categories import add_category, get_categories
from modules.db.members import add_member, get_members
from modules.db.rules import add_learning_rule
from modules.db.transactions import (
    bulk_update_transaction_status,
    get_all_hashes,
    get_pending_transactions,
    save_transactions,
)
from modules.ingestion import load_transaction_file
from modules.transaction_types import filter_expense_transactions, filter_income_transactions
from modules.ui.feedback import (
    FeedbackType,
    set_flash_message,
    show_info,
    show_warning,
    toast_error,
)


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
            from modules.ui.components.empty_states import render_no_transactions_state

            render_no_transactions_state(key="quick_actions_no_pending")
            return

        # Show count
        pending_count = len(df)
        st.info(f"📋 {pending_count} transaction(s) en attente")

        # Get available options
        members = get_members()
        member_names = members["name"].tolist() if not members.empty else []
        categories = get_categories()

        # Show up to 5 transactions
        display_df = df.head(5)
        validated_count = 0

        for idx, row in display_df.iterrows():
            with st.container(border=True):
                cols = st.columns([2, 1, 1, 0.5])

                with cols[0]:
                    st.write(
                        f"**{row['label'][:40]}...**"
                        if len(row["label"]) > 40
                        else f"**{row['label']}**"
                    )
                    st.caption(f"{row['date']} • {row['amount']:.2f} €")

                with cols[1]:
                    cat_key = f"quick_cat_{row['id']}"
                    current_cat = (
                        row.get("category_validated")
                        if row.get("category_validated") != "Inconnu"
                        else categories[0] if categories else "Inconnu"
                    )
                    selected_cat = st.selectbox(
                        "Catégorie",
                        options=categories,
                        index=categories.index(current_cat) if current_cat in categories else 0,
                        key=cat_key,
                        label_visibility="collapsed",
                    )

                with cols[2]:
                    mem_key = f"quick_mem_{row['id']}"
                    member_options = [""] + member_names
                    selected_member = st.selectbox(
                        "Payeur", options=member_options, key=mem_key, label_visibility="collapsed"
                    )

                with cols[3]:
                    if st.button("✓", key=f"quick_val_{row['id']}", type="primary"):
                        tags = None
                        beneficiary = None
                        if selected_member:
                            # Use member as beneficiary if selected
                            beneficiary = selected_member

                        bulk_update_transaction_status(
                            [row["id"]], selected_cat, tags=tags, beneficiary=beneficiary
                        )
                        validated_count += 1
                        set_flash_message(
                            f"✅ Transaction validée : {row['label'][:30]}...", FeedbackType.SUCCESS
                        )
                        st.rerun()

        # Actions footer
        st.divider()
        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "Valider tout en masse...",
                use_container_width=True,
                type="secondary",
                key="button_110",
            ):
                st.session_state["active_op_tab"] = "✅ Validation"
                st.switch_page("pages/01_Import.py")

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
                new_name = st.text_input("Nom", placeholder="Ex: Jean", key="text_input_132")
                new_type = st.radio(
                    "Type",
                    ["HOUSEHOLD", "EXTERNAL"],
                    format_func=lambda x: "🏘️ Foyer" if x == "HOUSEHOLD" else "💼 Tiers",
                    horizontal=True,
                )

                submitted = st.form_submit_button(
                    "Ajouter", use_container_width=True, type="primary"
                )
                if submitted:
                    if new_name and new_name.strip():
                        cleaned_name = new_name.strip()
                        if add_member(cleaned_name, new_type):
                            type_label = "Foyer" if new_type == "HOUSEHOLD" else "Tiers"
                            set_flash_message(
                                f"✅ Membre '{cleaned_name}' ({type_label}) créé",
                                FeedbackType.SUCCESS,
                            )
                            st.rerun()
                        else:
                            set_flash_message(
                                f"⚠️ Le membre '{cleaned_name}' existe déjà", FeedbackType.WARNING
                            )
                    else:
                        set_flash_message("⚠️ Veuillez entrer un nom", FeedbackType.WARNING)

        # Tab 2: Add Category
        with tab_category:
            with st.form("quick_add_category", clear_on_submit=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    new_cat = st.text_input("Nom", placeholder="Ex: Sports", key="text_input_155")
                with col2:
                    emoji = st.text_input("Emoji", value="🏷️", key="text_input_157")

                is_fixed = st.checkbox("Dépense fixe (loyer, abonnement...)", key="checkbox_159")

                submitted = st.form_submit_button(
                    "Ajouter", use_container_width=True, type="primary"
                )
                if submitted:
                    if new_cat and new_cat.strip():
                        cleaned_cat = new_cat.strip()
                        if add_category(cleaned_cat, emoji, int(is_fixed)):
                            type_label = "fixe" if is_fixed else "variable"
                            set_flash_message(
                                f"✅ Catégorie '{cleaned_cat}' ({type_label}) créée",
                                FeedbackType.SUCCESS,
                            )
                            st.rerun()
                        else:
                            set_flash_message(
                                f"⚠️ La catégorie '{cleaned_cat}' existe déjà", FeedbackType.WARNING
                            )
                    else:
                        set_flash_message(
                            "⚠️ Veuillez entrer un nom de catégorie", FeedbackType.WARNING
                        )

        # Tab 3: Add Rule
        with tab_rule:
            with st.form("quick_add_rule", clear_on_submit=True):
                pattern = st.text_input(
                    "Mot-clé ou pattern", placeholder="Ex: UBER, AMAZON, NETFLIX..."
                )
                target_cat = st.selectbox(
                    "Catégorie cible", options=get_categories(), key="selectbox_181"
                )

                submitted = st.form_submit_button(
                    "Créer la règle", use_container_width=True, type="primary"
                )
                if submitted:
                    if pattern and pattern.strip():
                        clean_pattern = pattern.strip()
                        try:
                            if add_learning_rule(clean_pattern, target_cat):
                                set_flash_message(
                                    f"✅ Règle '{clean_pattern}' → '{target_cat}' créée",
                                    FeedbackType.SUCCESS,
                                )
                                st.rerun()
                            else:
                                set_flash_message(
                                    f"⚠️ La règle '{clean_pattern}' existe déjà",
                                    FeedbackType.WARNING,
                                )
                        except Exception as e:
                            set_flash_message(
                                f"❌ Erreur création règle : {str(e)[:50]}", FeedbackType.ERROR
                            )
                    else:
                        set_flash_message("⚠️ Veuillez entrer un mot-clé", FeedbackType.WARNING)

        # Shortcuts to other config pages
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🧠 Intelligence", use_container_width=True, key="jump_rules"):
                st.session_state["intel_active_tab"] = "📋 Règles"
                st.switch_page("pages/03_Intelligence.py")
        with col2:
            if st.button("💰 Budgets", use_container_width=True, key="jump_budgets"):
                st.session_state["intel_active_tab"] = "🎯 Budgets"
                st.switch_page("pages/03_Intelligence.py")
        with col3:
            if st.button("🔔 Alertes", use_container_width=True, key="jump_notifs"):
                st.session_state["config_jump_to"] = "🤖 IA & Services"
                st.switch_page("pages/08_Configuration.py")


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
            show_warning(
                "Mode hors ligne : seules les règles manuelles seront appliquées", icon="⚠️"
            )

        uploaded_file = st.file_uploader(
            "Fichier CSV BoursoBank",
            type=["csv"],
            help="Sélectionnez votre fichier de relevé bancaire",
        )

        if uploaded_file is not None:
            # Account selection
            from modules.db.transactions import get_all_account_labels

            existing_accounts = get_all_account_labels()

            if existing_accounts:
                account = st.selectbox("Compte", existing_accounts, key="selectbox_224")
            else:
                account = st.text_input(
                    "Nom du compte", value="Compte Principal", key="text_input_226"
                )

            # Preview and import
            try:
                df = load_transaction_file(uploaded_file, mode="bourso_preset")

                if isinstance(df, tuple):
                    toast_error(f"Erreur: {df[1]}")
                    return

                # Check for duplicates
                existing_hashes = get_all_hashes()
                if existing_hashes:
                    duplicates_mask = df["tx_hash"].isin(existing_hashes)
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
                    preview = df[["date", "label", "amount"]].head(3)
                    st.dataframe(preview, use_container_width=True, hide_index=True)

                # Import button
                if st.button(
                    "🚀 Importer maintenant",
                    type="primary",
                    use_container_width=True,
                    key="button_261",
                ):
                    with st.spinner("🔄 Import en cours..."):
                        # Categorize
                        results = []
                        for _, row in df.iterrows():
                            cat, source, conf = categorize_transaction(
                                row["label"], row["amount"], row["date"]
                            )
                            results.append(cat)

                        df["category_validated"] = results
                        df["account_label"] = account

                        # Save
                        count, skipped = save_transactions(df)

                    if count > 0:
                        msg = f"✅ {count} transaction(s) importée(s)"
                        if skipped > 0:
                            msg += f" ({skipped} doublons ignorés)"
                        set_flash_message(msg, FeedbackType.SUCCESS)
                    else:
                        set_flash_message(
                            "ℹ️ Aucune nouvelle transaction à importer", FeedbackType.INFO
                        )

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
        current_month = datetime.now().strftime("%Y-%m")
        df["date_dt"] = pd.to_datetime(df["date"])
        month_df = df[df["date_dt"].dt.strftime("%Y-%m") == current_month]

        if month_df.empty:
            show_info(f"Aucune transaction pour {current_month}")
            return

        # Calculate stats
        expenses = filter_expense_transactions(month_df)["amount"].sum()
        income = filter_income_transactions(month_df)["amount"].sum()
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

        expenses_df = filter_expense_transactions(month_df).copy()
        if not expenses_df.empty:
            expenses_df["amount_abs"] = expenses_df["amount"].abs()
            top_cats = (
                expenses_df.groupby("category_validated")["amount_abs"]
                .sum()
                .sort_values(ascending=False)
                .head(3)
            )

            for cat, amount in top_cats.items():
                st.progress(min(1.0, amount / abs(expenses)), text=f"{cat}: {amount:.0f} €")

        # Link to full stats
        st.divider()
        if st.button("Détails par catégorie →", use_container_width=True, key="jump_explorer"):
            st.session_state["research_active_tab"] = "📂 Explorateur"
            st.switch_page("pages/07_Recherche.py")


def render_quick_actions_grid():
    """
    Render the main quick actions grid with popovers.
    This replaces the simple buttons with interactive popovers.
    """
    # Afficher les messages flash en attente (pour les actions dans les popovers)
    from modules.ui.feedback import display_flash_toasts

    display_flash_toasts()

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


def render_projections_popover():
    """
    Render a popover for cashflow projections and financial forecasting.
    Quick access to projections from the dashboard.
    """
    with st.popover("🔮 Projections", use_container_width=True):
        st.markdown("#### 🔮 Projections financières")
        st.caption("Prévisions et simulations")
        
        try:
            from modules.cashflow.predictor import get_cashflow_insights
            
            insights = get_cashflow_insights()
            
            if "error" not in insights:
                cols = st.columns(2)
                
                with cols[0]:
                    st.metric(
                        "Solde actuel", 
                        f"{insights.get('current_balance', 0):,.0f}€"
                    )
                
                with cols[1]:
                    if "predicted_3m_balance" in insights:
                        st.metric(
                            "Projection 3 mois", 
                            f"{insights['predicted_3m_balance']:,.0f}€"
                        )
                
                # Warnings
                if insights.get('warnings'):
                    for warning in insights['warnings']:
                        st.warning(warning)
                
                # Moyennes
                st.divider()
                st.caption("Moyennes mensuelles")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        "Revenus", 
                        f"{insights.get('avg_monthly_income', 0):,.0f}€"
                    )
                with col2:
                    st.metric(
                        "Dépenses", 
                        f"{insights.get('avg_monthly_expense', 0):,.0f}€"
                    )
                
                st.divider()
                if st.button(
                    "📈 Voir les projections détaillées →", 
                    use_container_width=True, 
                    type="primary",
                    key="goto_projections_btn"
                ):
                    st.switch_page("pages/11_Projections.py")
            else:
                st.info("💡 Pas assez de données pour les projections (minimum 30 transactions)")
                
        except Exception as e:
            st.error(f"Erreur chargement projections: {e}")
        
        # Lien vers la page
        st.divider()
        if st.button(
            "🔮 Ouvrir les projections", 
            use_container_width=True,
            key="open_projections_btn"
        ):
            st.switch_page("pages/11_Projections.py")


def render_quick_actions_grid():
    """
    Render the main quick actions grid with popovers.
    This replaces the simple buttons with interactive popovers.
    """
    # Afficher les messages flash en attente (pour les actions dans les popovers)
    from modules.ui.feedback import display_flash_toasts

    display_flash_toasts()

    st.subheader("📌 Actions Rapides")

    col_a, col_b, col_c, col_d, col_e = st.columns(5)

    with col_a:
        render_quick_validation_popover()

    with col_b:
        render_quick_config_popover()

    with col_c:
        render_quick_import_popover()

    with col_d:
        render_quick_stats_popover()
    
    with col_e:
        render_projections_popover()
