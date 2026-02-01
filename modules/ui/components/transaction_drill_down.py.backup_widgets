"""
Transaction Drill-Down Component.

Displays transactions for a category with validation capabilities.
"""
import streamlit as st
import pandas as pd
from typing import Tuple, Optional
from modules.db.transactions import get_all_transactions, update_transaction_category, add_tag_to_transactions
from modules.db.categories import get_categories
from modules.db.rules import add_learning_rule
from modules.utils import clean_label
from modules.logger import logger
from modules.ui.components.tag_selector_compact import render_cheque_nature_field
from modules.ui.components.tag_manager import (
    render_smart_tag_selector, 
    render_pill_tags,
    find_similar_transactions
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _fetch_and_filter_transactions(transaction_ids: list) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Fetch and filter transactions by IDs, returning validated and pending separately.

    Args:
        transaction_ids: List of transaction IDs to fetch

    Returns:
        Tuple of (df_validated, df_pending)
    """
    df_all = get_all_transactions()
    df_cat = df_all[df_all['id'].isin(transaction_ids)].copy()

    if df_cat.empty:
        return pd.DataFrame(), pd.DataFrame()

    df_validated = df_cat[df_cat['status'] == 'validated'].copy()
    df_pending = df_cat[df_cat['status'] == 'pending'].copy()

    return df_validated, df_pending


def _display_summary_metrics(df: pd.DataFrame):
    """
    Display summary metrics for a set of transactions.

    Args:
        df: DataFrame of transactions
    """
    total_amount = abs(df['amount'].sum())
    avg_amount = abs(df['amount'].mean())
    count = len(df)

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.metric("Total", f"{total_amount:.2f}€")
    with col_s2:
        st.metric("Moyenne", f"{avg_amount:.2f}€")
    with col_s3:
        st.metric("Transactions", count)

    st.divider()


def _is_cheque_transaction(label: str) -> bool:
    """Check if a transaction is a cheque based on label."""
    cheque_keywords = ['chq.', 'chèque', 'cheque', 'chq ', 'cheq ']
    label_lower = label.lower()
    return any(keyword in label_lower for keyword in cheque_keywords)


def _render_transaction_row_compact(
    row: pd.Series, 
    categories: list, 
    key_prefix: str,
    session_key: str, 
    current_category: str,
    is_header: bool = False
):
    """
    Render a compact transaction row optimized for space.
    
    Args:
        row: Transaction row data
        categories: List of available categories
        key_prefix: Unique key prefix
        session_key: Session state key
        current_category: Current category
        is_header: If True, render headers only
    """
    tx_id = row['id'] if not is_header else "header"
    
    # Check if this is a cheque
    is_cheque = _is_cheque_transaction(row.get('label', '')) if not is_header else False
    
    # Adjust layout based on whether it's a cheque (needs extra row for nature)
    if is_header:
        # Header row
        cols = st.columns([1.2, 2.5, 1, 1.8, 2.5, 2])
        with cols[0]:
            st.markdown("**📅 Date**")
        with cols[1]:
            st.markdown("**📝 Libellé**")
        with cols[2]:
            st.markdown("**💰 Montant**")
        with cols[3]:
            st.markdown("**📂 Catégorie**")
        with cols[4]:
            st.markdown("**🏷️ Tags**")
        with cols[5]:
            st.markdown("**📋 Contexte**")
        st.divider()
        return
    
    # Main transaction row
    cols = st.columns([1.2, 2.5, 1, 1.8, 2.5, 2])
    
    with cols[0]:
        st.text(row['date'])
    
    with cols[1]:
        label = row['label']
        label_display = label[:45] + "..." if len(label) > 45 else label
        st.text(label_display)
        if is_cheque:
            st.caption("🧾 Chèque détecté")
    
    with cols[2]:
        st.text(f"{row['amount']:.2f}€")
    
    with cols[3]:
        default_idx = categories.index(current_category) if current_category in categories else 0
        selected_cat = st.selectbox(
            "Catégorie",
            categories,
            index=default_idx,
            key=f"{key_prefix}_cat_{tx_id}",
            label_visibility="collapsed"
        )
        
        if session_key not in st.session_state:
            st.session_state[session_key] = {}
        if tx_id not in st.session_state[session_key]:
            st.session_state[session_key][tx_id] = {}
        st.session_state[session_key][tx_id]['category'] = selected_cat
    
    with cols[4]:
        current_tags_str = row.get('tags', '') if row.get('tags') else ""
        current_tags = [t.strip() for t in current_tags_str.split(',') if t.strip()]
        
        # Display current tags as pills (compact view)
        if current_tags:
            render_pill_tags(current_tags, size="small", removable=False)
        
        # Smart tag selector with propagation
        selected_tags = render_smart_tag_selector(
            transaction_id=tx_id,
            current_tags=current_tags,
            category=selected_cat,
            label=row.get('label', ''),
            key_suffix=f"{key_prefix}_tagsel_{tx_id}",
            max_quick_tags=3,
            enable_propagation=True
        )
        st.session_state[session_key][tx_id]['tags'] = selected_tags
    
    with cols[5]:
        notes_key = f"{key_prefix}_notes_{tx_id}"
        current_notes = row.get('notes', '') if pd.notna(row.get('notes')) else ""
        
        notes_value = st.text_input(
            "Notes",
            value=current_notes,
            key=notes_key,
            label_visibility="collapsed",
            placeholder="Contextualiser..."
        )
        st.session_state[session_key][tx_id]['notes'] = notes_value
    
    # Extra row for cheque nature
    if is_cheque:
        with st.container():
            nature_cols = st.columns([1.2, 8, 1])
            with nature_cols[1]:
                cheque_nature = render_cheque_nature_field(
                    transaction_id=tx_id,
                    current_nature="",
                    key_suffix=f"{key_prefix}_nature_{tx_id}"
                )
                if cheque_nature:
                    # Add nature as a tag
                    nature_tag = f"chèque-{cheque_nature.lower().replace(' ', '-')}"
                    if nature_tag not in st.session_state[session_key][tx_id].get('tags', []):
                        if 'tags' not in st.session_state[session_key][tx_id]:
                            st.session_state[session_key][tx_id]['tags'] = []
                        st.session_state[session_key][tx_id]['tags'].append(nature_tag)
        st.divider()


def _show_save_confirmation(msg: str, key_prefix: str, on_close_callback=None):
    """
    Show a confirmation toast and banner with auto-close and keep-open option.
    
    Args:
        msg: Success message to display
        key_prefix: Unique prefix for session state keys
        on_close_callback: Optional callback to execute on close
    """
    # Show toast
    st.toast(msg, icon="✅")
    
    # Show persistent banner with timer
    timer_key = f"{key_prefix}_close_timer"
    keep_open_key = f"{key_prefix}_keep_open"
    
    if keep_open_key not in st.session_state:
        st.session_state[keep_open_key] = False
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.success(msg)
    with col2:
        if st.button("📌 Garder ouvert", key=f"{key_prefix}_keep_btn"):
            st.session_state[keep_open_key] = True
            st.rerun()
    
    # Auto-close after 3 seconds if not kept open
    if not st.session_state.get(keep_open_key, False):
        st.markdown("""
            <script>
                setTimeout(function() {
                    window.parent.postMessage({type: 'streamlit:closeExpander'}, '*');
                }, 3000);
            </script>
        """, unsafe_allow_html=True)
        
        # For Streamlit, we'll use a different approach
        import time
        time.sleep(0.1)  # Small delay to let the UI render
        
        # Mark for auto-close
        if on_close_callback:
            on_close_callback()


def _handle_validated_transactions(
    df_validated: pd.DataFrame, 
    key_prefix: str,
    category: str, 
    show_anomaly_management: bool,
    anomaly_index: Optional[int] = None,
    anomaly_list_key: Optional[str] = None
):
    """
    Display and handle validated transactions with improved UX.
    """
    st.subheader(f"✅ Transactions Validées ({len(df_validated)})")
    
    # Info box
    st.info("""
    **📝 Modifiez vos transactions :**
    - **📂 Catégorie** : Corrigez si nécessaire
    - **🏷️ Tags** : Ajoutez des balises (cliquez sur les boutons rapides)
    - **📋 Contexte** : Notez des informations utiles
    - **🧾 Chèques** : Un champ "Nature" apparaît automatiquement
    
    💡 *Les tags vous permettent de suivre des dépenses spécifiques à travers différentes catégories*
    """)
    
    # Initialize session
    session_key = f'{key_prefix}_validated_edits'
    if session_key not in st.session_state:
        st.session_state[session_key] = {}
    
    categories = get_categories()
    
    # Header
    _render_transaction_row_compact(
        pd.Series({'id': 'header'}), categories, key_prefix, session_key, '', is_header=True
    )
    
    # Transaction rows
    for idx, row in df_validated.iterrows():
        current_edits = st.session_state.get(session_key, {})
        row_cat = row.get('category_validated', category)
        current_val = current_edits.get(row['id'], {}).get('category', row_cat)
        
        _render_transaction_row_compact(
            row, categories, f"{key_prefix}_validated", session_key, current_val
        )
    
    st.markdown("---")
    
    # Save section
    col_v1, col_v2 = st.columns([3, 1])
    
    with col_v1:
        st.markdown(f"**{len(df_validated)} transaction(s)** à modifier")
        
        auto_learn = st.checkbox(
            "🧠 Mémoriser pour le futur",
            value=True,
            key=f"{key_prefix}_learn_validated",
            help="Crée des règles pour l'IA"
        )
    
    with col_v2:
        if st.button(
            "💾 Sauvegarder",
            key=f"{key_prefix}_save_validated",
            type="primary",
            use_container_width=True
        ):
            edits = st.session_state.get(session_key, {})
            if not edits:
                st.warning("Aucune modification à sauvegarder.")
            else:
                rules_created = 0
                
                for tx_id, edit_data in edits.items():
                    selected_category = edit_data.get('category')
                    selected_tags = edit_data.get('tags', [])
                    selected_notes = edit_data.get('notes', '')
                    
                    # Prepare tags string
                    tags_str = ",".join(selected_tags) if selected_tags else None
                    notes_str = selected_notes if selected_notes else None
                    
                    update_transaction_category(tx_id, selected_category, tags=tags_str, notes=notes_str)
                    
                    if auto_learn:
                        tx_row = df_validated[df_validated['id'] == tx_id]
                        if not tx_row.empty:
                            label = tx_row.iloc[0]['label']
                            pattern = clean_label(label)
                            if add_learning_rule(pattern, selected_category, priority=5):
                                rules_created += 1
                
                # Invalidate caches
                from modules.cache_manager import invalidate_transaction_caches, invalidate_rule_caches
                invalidate_transaction_caches()
                if rules_created > 0:
                    invalidate_rule_caches()
                
                # Clear edits
                if session_key in st.session_state:
                    del st.session_state[session_key]
                
                # Build message
                msg = f"✅ {len(edits)} transactions mises à jour !"
                if rules_created > 0:
                    msg += f" \n🧠 {rules_created} règles créées."
                
                # Show confirmation
                st.session_state[f'{key_prefix}_success_msg'] = msg
                st.session_state[f'{key_prefix}_show_confetti'] = True
                
                # Mark anomaly as corrected if applicable
                if anomaly_index is not None and anomaly_list_key:
                    if f'{anomaly_list_key}_corrected' not in st.session_state:
                        st.session_state[f'{anomaly_list_key}_corrected'] = []
                    st.session_state[f'{anomaly_list_key}_corrected'].append(anomaly_index)
                
                st.rerun()


def _handle_pending_transactions(df_pending: pd.DataFrame, key_prefix: str, category: str):
    """Display pending transactions section."""
    st.subheader(f"⏳ Transactions en Attente ({len(df_pending)})")
    
    st.info("""
    **📝 Validez ces transactions :**
    Vérifiez la catégorie suggérée, ajoutez des tags si nécessaire, puis validez.
    """)
    
    session_key = f'{key_prefix}_edits'
    if session_key not in st.session_state:
        st.session_state[session_key] = {}
    
    categories = get_categories()
    
    # Header
    _render_transaction_row_compact(
        pd.Series({'id': 'header'}), categories, key_prefix, session_key, '', is_header=True
    )
    
    # Rows
    for idx, row in df_pending.iterrows():
        row_cat = row.get('original_category', category)
        current_val = st.session_state.get(session_key, {}).get(row['id'], {}).get('category', row_cat)
        
        _render_transaction_row_compact(
            row, categories, key_prefix, session_key, current_val
        )
    
    st.markdown("---")
    
    col_v1, col_v2 = st.columns([3, 1])
    
    with col_v1:
        st.markdown(f"**{len(df_pending)} transaction(s)** à valider")
        auto_learn = st.checkbox(
            "🧠 Mémoriser ces choix",
            value=True,
            key=f"{key_prefix}_learn_pending"
        )
    
    with col_v2:
        if st.button(
            "✅ Valider Tout",
            key=f"{key_prefix}_validate_bulk",
            type="primary",
            use_container_width=True
        ):
            edits = st.session_state.get(session_key, {})
            rules_created = 0
            
            for tx_id, edit_data in edits.items():
                selected_category = edit_data.get('category')
                selected_tags = edit_data.get('tags', [])
                selected_notes = edit_data.get('notes', '')
                
                tags_str = ",".join(selected_tags) if selected_tags else None
                notes_str = selected_notes if selected_notes else None
                
                update_transaction_category(tx_id, selected_category, tags=tags_str, notes=notes_str)
                
                if auto_learn:
                    tx_row = df_pending[df_pending['id'] == tx_id]
                    if not tx_row.empty:
                        label = tx_row.iloc[0]['label']
                        pattern = clean_label(label)
                        if add_learning_rule(pattern, selected_category, priority=5):
                            rules_created += 1
            
            from modules.cache_manager import invalidate_transaction_caches, invalidate_rule_caches
            invalidate_transaction_caches()
            if rules_created > 0:
                invalidate_rule_caches()
            
            if session_key in st.session_state:
                del st.session_state[session_key]
            
            msg = f"✅ {len(edits)} transactions validées !"
            if rules_created > 0:
                msg += f" \n🧠 {rules_created} règles créées."
            
            st.toast(msg, icon="✅")
            st.session_state[f'{key_prefix}_success_msg'] = msg
            st.rerun()


# ============================================================================
# MAIN RENDER FUNCTION
# ============================================================================

def render_transaction_drill_down(
    category: str, 
    transaction_ids: list,
    period_start: str = None, 
    period_end: str = None,
    key_prefix: str = "drilldown",
    show_anomaly_management: bool = False,
    anomaly_index: Optional[int] = None,
    anomaly_list_key: Optional[str] = None
):
    """
    Render an interactive drill-down view with improved UX.
    
    Args:
        category: Category name
        transaction_ids: List of transaction IDs
        period_start: Start date
        period_end: End date
        key_prefix: Unique key prefix
        show_anomaly_management: Show anomaly options
        anomaly_index: Index of anomaly in list (for marking corrected)
        anomaly_list_key: Session state key for anomaly list
    """
    if not transaction_ids:
        st.info(f"Aucune transaction trouvée.")
        return
    
    df_validated, df_pending = _fetch_and_filter_transactions(transaction_ids)
    
    if df_validated.empty and df_pending.empty:
        st.warning("Les transactions n'ont pas pu être chargées.")
        return
    
    # Show success message if exists
    if f'{key_prefix}_success_msg' in st.session_state:
        msg = st.session_state[f'{key_prefix}_success_msg']
        
        # Show confirmation with keep-open option
        col1, col2 = st.columns([4, 1])
        with col1:
            st.success(msg)
        with col2:
            if st.button("📌 Garder ouvert", key=f"{key_prefix}_keep_btn"):
                # Just clear the flag but don't auto-close
                del st.session_state[f'{key_prefix}_success_msg']
                st.rerun()
        
        # Auto-close the expander after delay (handled by parent)
        keep_open_key = f'{key_prefix}_keep_open'
        if keep_open_key not in st.session_state or not st.session_state[keep_open_key]:
            st.caption("✨ Cette anomalie sera fermée automatiquement dans 3 secondes...")
    
    # Summary
    df_all = pd.concat([df_validated, df_pending], ignore_index=True)
    _display_summary_metrics(df_all)
    
    # Show corrected badge
    if anomaly_index is not None and anomaly_list_key:
        corrected_list = st.session_state.get(f'{anomaly_list_key}_corrected', [])
        if anomaly_index in corrected_list:
            st.success("✅ **Anomalie vérifiée et corrigée** - Les modifications ont été sauvegardées.")
            st.caption("Vous pouvez continuer à modifier ou fermer cette section.")
    
    # Sections
    if not df_validated.empty:
        _handle_validated_transactions(
            df_validated, key_prefix, category, show_anomaly_management,
            anomaly_index, anomaly_list_key
        )
    
    if not df_pending.empty:
        _handle_pending_transactions(df_pending, key_prefix, category)


def render_category_drill_down_expander(
    insight: dict, 
    period_start: str = None, 
    period_end: str = None, 
    key_prefix: str = "insight"
):
    """Render expander for trend insights."""
    if not insight.get('category'):
        st.markdown(f"{insight['emoji']} {insight['message']}")
        return
    
    with st.expander(f"{insight['emoji']} {insight['message']}", expanded=False):
        render_transaction_drill_down(
            category=insight['category'],
            transaction_ids=insight.get('transaction_ids', []),
            period_start=period_start,
            period_end=period_end,
            key_prefix=f"{key_prefix}_{insight['category'].replace(' ', '_')}"
        )
