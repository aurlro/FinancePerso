"""
Transaction Drill-Down Component.

Displays transactions for a category with validation capabilities.
"""
import streamlit as st
import pandas as pd
from modules.db.transactions import get_all_transactions, update_transaction_category, add_tag_to_transactions
from modules.db.categories import get_categories
from modules.db.rules import add_learning_rule
from modules.utils import clean_label
from modules.logger import logger


def render_transaction_drill_down(category: str, transaction_ids: list, 
                                  period_start: str = None, period_end: str = None,
                                  key_prefix: str = "drilldown",
                                  show_anomaly_management: bool = False):
    """
    Render an interactive drill-down view of transactions for a category.
    
    Args:
        category: Category name
        transaction_ids: List of transaction IDs to display
        period_start: Start date of period (YYYY-MM-DD)
        period_end: End date of period (YYYY-MM-DD)
        key_prefix: Unique key prefix for widgets
        
    Example:
        render_transaction_drill_down("Alimentation", [123, 456, 789], "2026-01-01", "2026-01-31")
    """
    if not transaction_ids:
        st.info(f"Aucune transaction trouvée pour la catégorie **{category}**.")
        return
    
    # Fetch all transactions
    df_all = get_all_transactions()
    
    # Filter to relevant transactions
    df_cat = df_all[df_all['id'].isin(transaction_ids)].copy()
    
    if df_cat.empty:
        st.warning("Les transactions n'ont pas pu être chargées.")
        return
    
    # Separate validated and pending
    df_validated = df_cat[df_cat['status'] == 'validated'].copy()
    df_pending = df_cat[df_cat['status'] == 'pending'].copy()
    
    # Display persistent success message if exists
    if f'{key_prefix}_success_msg' in st.session_state:
        st.success(st.session_state[f'{key_prefix}_success_msg'])
        # Clear it so it doesn't persist forever (optional, or keep it until next action)
        del st.session_state[f'{key_prefix}_success_msg']

    # Display summary
    total_amount = abs(df_cat['amount'].sum())
    avg_amount = abs(df_cat['amount'].mean())
    count = len(df_cat)
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.metric("Total", f"{total_amount:.2f}€")
    with col_s2:
        st.metric("Moyenne", f"{avg_amount:.2f}€")
    with col_s3:
        st.metric("Transactions", count)
    
    st.divider()
    
    # Display validated transactions with editing capability
    if not df_validated.empty:
        st.subheader(f"✅ Transactions Validées ({len(df_validated)})")
        st.markdown("### Modifier les Catégories")
        st.markdown("Vous pouvez modifier la catégorie de chaque transaction, puis sauvegarder toutes les modifications en une fois.")
        
        # Initialize session state for edits if not exists
        if f'{key_prefix}_validated_edits' not in st.session_state:
            st.session_state[f'{key_prefix}_validated_edits'] = {}
        
        categories = get_categories()
        
        # Display each validated transaction with category selector
        for idx, row in df_validated.iterrows():
            tx_id = row['id']
            
            col_tx1, col_tx2, col_tx3, col_tx4 = st.columns([2, 2, 1.5, 1.5])
            
            with col_tx1:
                st.text(row['date'])
            
            with col_tx2:
                st.text(row['label'][:40] + "..." if len(row['label']) > 40 else row['label'])
            
            with col_tx3:
                st.text(f"{row['amount']:.2f}€")
            
            with col_tx4:
                # Category selector for this transaction
                # Check for existing edit in session state
                current_edits = st.session_state.get(f'{key_prefix}_validated_edits', {})
                current_val = current_edits.get(tx_id, row.get('category_validated', category))
                
                # Determine index
                if current_val in categories:
                    default_idx = categories.index(current_val)
                else:
                    default_idx = 0
                
                selected_cat = st.selectbox(
                    "Catégorie",
                    categories,
                    index=default_idx,
                    key=f"{key_prefix}_validated_cat_{tx_id}",
                    label_visibility="collapsed"
                )
                
                # Store the selection
                st.session_state[f'{key_prefix}_validated_edits'][tx_id] = selected_cat
        
        st.markdown("---")
        
        # Save button with learning option
        col_v1, col_v2 = st.columns([3, 1])
        
        with col_v1:
            st.markdown(f"**{len(df_validated)} transaction(s)** prête(s) à être modifiée(s)")
            # Learning rule checkbox
            auto_learn = st.checkbox(
                "🧠 Mémoriser ces choix pour le futur (apprentissage automatique)",
                value=not show_anomaly_management, # Default to false if anomaly
                key=f"{key_prefix}_learn_validated",
                help="Crée automatiquement des règles pour que l'IA reconnaisse ces transactions la prochaine fois."
            )
            
            # Anomaly dismissal checkbox
            mark_normal = False
            if show_anomaly_management:
                mark_normal = st.checkbox(
                    "🎯 Ce montant est normal (ne plus signaler comme anomalie)",
                    value=True,
                    key=f"{key_prefix}_mark_normal",
                    help="Ajoute un tag pour que l'IA ignore ce montant à l'avenir."
                )


        with col_v2:
            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
            if st.button(
                "💾 Sauvegarder",
                key=f"{key_prefix}_save_validated",
                type="primary",
                use_container_width=True
            ):
                # Calculate effect
                edits = st.session_state.get(f'{key_prefix}_validated_edits', {})
                rules_created = 0
                
                # Calculate old total
                old_total = df_validated['amount'].abs().sum()
                
                # Apply edits
                for tx_id, selected_category in edits.items():
                    # Update transaction
                    update_transaction_category(tx_id, selected_category)
                    
                    # Create learning rule if requested
                    if auto_learn:
                        tx_row = df_validated[df_validated['id'] == tx_id]
                        if not tx_row.empty:
                            label = tx_row.iloc[0]['label']
                            pattern = clean_label(label)
                            if add_learning_rule(pattern, selected_category, priority=5):
                                rules_created += 1
                
                # Apply anomaly dismissal if requested
                anomalies_dismissed = 0
                if show_anomaly_management and mark_normal:
                    anomalies_dismissed = add_tag_to_transactions(list(edits.keys()), 'ignore_anomaly')
                
                st.cache_data.clear()
                
                # Clear edits
                if f'{key_prefix}_validated_edits' in st.session_state:
                    del st.session_state[f'{key_prefix}_validated_edits']
                
                # Prepare persistent message
                msg = f"✅ {len(edits)} transactions mises à jour !"
                if rules_created > 0:
                    msg += f" \n🧠 {rules_created} règles d'apprentissage créées."
                if anomalies_dismissed > 0:
                    msg += f" \n🎯 {anomalies_dismissed} montants marqués comme normaux."
                
                # Note: We can't easily calculate the NEW total here because we need to re-query DB
                # But we can say "Analysis will be updated."
                
                st.session_state[f'{key_prefix}_success_msg'] = msg
                # Trigger trend analysis refresh
                st.session_state['show_trends'] = True 
                
                # Clear anomaly results to force re-analysis
                if 'anomaly_results' in st.session_state:
                    del st.session_state['anomaly_results']
                
                st.rerun()

    
    # Display pending transactions with validation option
    if not df_pending.empty:
        st.subheader(f"⏳ Transactions en Attente ({len(df_pending)})")
        
        st.markdown("### Modifier les Catégories")
        st.markdown("Sélectionnez la catégorie pour chaque transaction, puis validez toutes les modifications en une fois.")
        
        # Initialize session state for edits if not exists
        if f'{key_prefix}_edits' not in st.session_state:
            st.session_state[f'{key_prefix}_edits'] = {}
        
        categories = get_categories()
        
        # Display each transaction with category selector
        for idx, row in df_pending.iterrows():
            tx_id = row['id']
            
            col_tx1, col_tx2, col_tx3, col_tx4 = st.columns([2, 2, 1.5, 1.5])
            
            with col_tx1:
                st.text(row['date'])
            
            with col_tx2:
                st.text(row['label'][:40] + "..." if len(row['label']) > 40 else row['label'])
            
            with col_tx3:
                st.text(f"{row['amount']:.2f}€")
            
            with col_tx4:
                # Category selector for this transaction
                default_cat = row.get('original_category', category)
                default_idx = categories.index(default_cat) if default_cat in categories else categories.index(category) if category in categories else 0
                
                selected_cat = st.selectbox(
                    "Catégorie",
                    categories,
                    index=default_idx,
                    key=f"{key_prefix}_cat_{tx_id}",
                    label_visibility="collapsed"
                )
                
                # Store the selection
                st.session_state[f'{key_prefix}_edits'][tx_id] = selected_cat
        
        st.markdown("---")
        
        # Bulk validation button with learning option
        col_v1, col_v2 = st.columns([3, 1])
        
        with col_v1:
            st.markdown(f"**{len(df_pending)} transaction(s)** prête(s) à être validée(s)")
            # Learning rule checkbox
            auto_learn_pending = st.checkbox(
                "🧠 Mémoriser ces choix pour le futur",
                value=True,
                key=f"{key_prefix}_learn_pending",
                help="Crée automatiquement des règles pour les futures importations."
            )
        
        with col_v2:
            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
            if st.button(
                "✅ Valider Tout",
                key=f"{key_prefix}_validate_bulk",
                type="primary",
                use_container_width=True
            ):
                # Apply all edits
                edits = st.session_state.get(f'{key_prefix}_edits', {})
                rules_created = 0
                
                for tx_id, selected_category in edits.items():
                    # Update transaction
                    update_transaction_category(tx_id, selected_category)
                    
                    # Create learning rule if requested
                    if auto_learn_pending:
                        # Find the transaction label
                        tx_row = df_pending[df_pending['id'] == tx_id]
                        if not tx_row.empty:
                            label = tx_row.iloc[0]['label']
                            pattern = clean_label(label)
                            
                            # Add rule with high priority (5)
                            if add_learning_rule(pattern, selected_category, priority=5):
                                rules_created += 1
                
                st.cache_data.clear()
                
                # Clear edits from session state
                if f'{key_prefix}_edits' in st.session_state:
                    del st.session_state[f'{key_prefix}_edits']
                
                msg = f"✅ {len(edits)} transactions validées !"
                if rules_created > 0:
                    msg += f" \n🧠 {rules_created} règles d'apprentissage créées."
                
                st.toast(msg, icon="✅")
                st.rerun()
    
    if df_validated.empty and df_pending.empty:
        st.info("Aucune transaction à afficher.")


def render_category_drill_down_expander(insight: dict, period_start: str = None, 
                                        period_end: str = None, key_prefix: str = "insight"):
    """
    Render an expander with drill-down for a trend insight.
    
    Args:
        insight: Insight dict from analyze_spending_trends()
        period_start: Start date of current period
        period_end: End date of current period
        key_prefix: Unique key prefix
        
    Example:
        for i, insight in enumerate(insights):
            render_category_drill_down_expander(insight, "2026-01-01", "2026-01-31", f"trend_{i}")
    """
    if not insight.get('category'):
        # Stable spending message, no drill-down
        st.markdown(f"{insight['emoji']} {insight['message']}")
        return
    
    # Create expander with insight message
    with st.expander(f"{insight['emoji']} {insight['message']}", expanded=False):
        render_transaction_drill_down(
            category=insight['category'],
            transaction_ids=insight.get('transaction_ids', []),
            period_start=period_start,
            period_end=period_end,
            key_prefix=f"{key_prefix}_{insight['category'].replace(' ', '_')}"
        )
