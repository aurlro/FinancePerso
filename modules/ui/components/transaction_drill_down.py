"""
Transaction Drill-Down Component.

Displays transactions for a category with validation capabilities.
"""
import streamlit as st
import pandas as pd
from typing import Tuple
from modules.db.transactions import get_all_transactions, update_transaction_category, add_tag_to_transactions
from modules.db.categories import get_categories
from modules.db.rules import add_learning_rule
from modules.utils import clean_label
from modules.logger import logger


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


def _render_transaction_row(row: pd.Series, categories: list, key_prefix: str,
                            session_key: str, current_category: str, show_tags: bool = True,
                            show_notes: bool = True):
    """
    Render a single transaction row with category selector, tags, and notes.

    Args:
        row: Transaction row data
        categories: List of available categories
        key_prefix: Unique key prefix for widgets
        session_key: Session state key for storing edits
        current_category: Current category value
        show_tags: Whether to show tags column
        show_notes: Whether to show notes column
    """
    from modules.db.tags import get_all_tags
    from modules.ui.components.tag_manager import render_tag_selector

    tx_id = row['id']

    # Adjust columns based on what we show
    if show_tags and show_notes:
        col_tx1, col_tx2, col_tx3, col_tx4, col_tx5, col_tx6 = st.columns([1.5, 2, 1, 1.5, 2, 2])
    elif show_tags:
        col_tx1, col_tx2, col_tx3, col_tx4, col_tx5 = st.columns([2, 2, 1.5, 1.5, 2])
    else:
        col_tx1, col_tx2, col_tx3, col_tx4 = st.columns([2, 2, 1.5, 1.5])

    with col_tx1:
        st.text(row['date'])

    with col_tx2:
        label_display = row['label'][:35] + "..." if len(row['label']) > 35 else row['label']
        st.text(label_display)

    with col_tx3:
        st.text(f"{row['amount']:.2f}€")

    with col_tx4:
        # Determine default index
        if current_category in categories:
            default_idx = categories.index(current_category)
        else:
            default_idx = 0

        selected_cat = st.selectbox(
            "Catégorie",
            categories,
            index=default_idx,
            key=f"{key_prefix}_cat_{tx_id}",
            label_visibility="collapsed"
        )

        # Store the selection in session state
        if session_key not in st.session_state:
            st.session_state[session_key] = {}

        # Store as dict with all fields
        if tx_id not in st.session_state[session_key]:
            st.session_state[session_key][tx_id] = {}
        st.session_state[session_key][tx_id]['category'] = selected_cat

    if show_tags:
        with col_tx5:
            # Get current tags
            current_tags_str = row.get('tags', '') if row.get('tags') else ""
            current_tags = [t.strip() for t in current_tags_str.split(',') if t.strip()]

            # Use tag selector component
            selected_tags = render_tag_selector(
                transaction_id=tx_id,
                current_tags=current_tags,
                category=current_category,
                key_suffix=f"{key_prefix}_tagsel_{tx_id}",
                allow_create=True,
                strict_mode=False
            )

            # Store tags in session state
            st.session_state[session_key][tx_id]['tags'] = selected_tags

    if show_notes:
        with col_tx6:
            # Notes field (using session state for persistence)
            notes_key = f"{key_prefix}_notes_{tx_id}"
            current_notes = row.get('notes', '') if pd.notna(row.get('notes')) else ""

            notes_value = st.text_input(
                "Notes",
                value=current_notes,
                key=notes_key,
                label_visibility="collapsed",
                placeholder="Contexte, remarques..."
            )

            # Store notes in session state
            st.session_state[session_key][tx_id]['notes'] = notes_value


def _handle_validated_transactions(df_validated: pd.DataFrame, key_prefix: str,
                                   category: str, show_anomaly_management: bool):
    """
    Display and handle validated transactions editing section.

    Args:
        df_validated: DataFrame of validated transactions
        key_prefix: Unique key prefix for widgets
        category: Category name
        show_anomaly_management: Whether to show anomaly management options
    """
    st.subheader(f"✅ Transactions Validées ({len(df_validated)})")
    st.markdown("### Modifier les Catégories")
    st.markdown("Vous pouvez modifier la catégorie de chaque transaction, puis sauvegarder toutes les modifications en une fois.")

    # Initialize session state for edits
    session_key = f'{key_prefix}_validated_edits'
    if session_key not in st.session_state:
        st.session_state[session_key] = {}

    categories = get_categories()

    # Display each validated transaction with category selector
    for idx, row in df_validated.iterrows():
        current_edits = st.session_state.get(session_key, {})
        current_val = current_edits.get(row['id'], row.get('category_validated', category))

        _render_transaction_row(row, categories, f"{key_prefix}_validated",
                               session_key, current_val)

    st.markdown("---")

    # Save button with learning option
    col_v1, col_v2 = st.columns([3, 1])

    with col_v1:
        st.markdown(f"**{len(df_validated)} transaction(s)** prête(s) à être modifiée(s)")

        auto_learn = st.checkbox(
            "🧠 Mémoriser ces choix pour le futur (apprentissage automatique)",
            value=not show_anomaly_management,
            key=f"{key_prefix}_learn_validated",
            help="Crée automatiquement des règles pour que l'IA reconnaisse ces transactions la prochaine fois."
        )

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
            edits = st.session_state.get(session_key, {})
            rules_created = 0

            # Apply edits
            for tx_id, selected_category in edits.items():
                update_transaction_category(tx_id, selected_category)

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

            from modules.cache_manager import invalidate_transaction_caches, invalidate_rule_caches
            invalidate_transaction_caches()
            if rules_created > 0:
                invalidate_rule_caches()

            # Clear edits
            if session_key in st.session_state:
                del st.session_state[session_key]

            # Prepare persistent message
            msg = f"✅ {len(edits)} transactions mises à jour !"
            if rules_created > 0:
                msg += f" \n🧠 {rules_created} règles d'apprentissage créées."
            if anomalies_dismissed > 0:
                msg += f" \n🎯 {anomalies_dismissed} montants marqués comme normaux."

            st.session_state[f'{key_prefix}_success_msg'] = msg
            st.session_state['show_trends'] = True

            if 'anomaly_results' in st.session_state:
                del st.session_state['anomaly_results']

            st.rerun()


def _handle_pending_transactions(df_pending: pd.DataFrame, key_prefix: str, category: str):
    """
    Display and handle pending transactions validation section.

    Args:
        df_pending: DataFrame of pending transactions
        key_prefix: Unique key prefix for widgets
        category: Category name
    """
    st.subheader(f"⏳ Transactions en Attente ({len(df_pending)})")
    st.markdown("### Modifier les Catégories")
    st.markdown("Sélectionnez la catégorie pour chaque transaction, puis validez toutes les modifications en une fois.")

    # Initialize session state for edits
    session_key = f'{key_prefix}_edits'
    if session_key not in st.session_state:
        st.session_state[session_key] = {}

    categories = get_categories()

    # Display each transaction with category selector
    for idx, row in df_pending.iterrows():
        default_cat = row.get('original_category', category)
        current_val = st.session_state.get(session_key, {}).get(row['id'], default_cat)

        _render_transaction_row(row, categories, key_prefix, session_key, current_val)

    st.markdown("---")

    # Bulk validation button with learning option
    col_v1, col_v2 = st.columns([3, 1])

    with col_v1:
        st.markdown(f"**{len(df_pending)} transaction(s)** prête(s) à être validée(s)")

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
            edits = st.session_state.get(session_key, {})
            rules_created = 0

            for tx_id, selected_category in edits.items():
                update_transaction_category(tx_id, selected_category)

                if auto_learn_pending:
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

            # Clear edits from session state
            if session_key in st.session_state:
                del st.session_state[session_key]

            msg = f"✅ {len(edits)} transactions validées !"
            if rules_created > 0:
                msg += f" \n🧠 {rules_created} règles d'apprentissage créées."

            st.toast(msg, icon="✅")
            st.rerun()


# ============================================================================
# MAIN RENDER FUNCTION
# ============================================================================


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
        show_anomaly_management: Whether to show anomaly management options

    Example:
        render_transaction_drill_down("Alimentation", [123, 456, 789], "2026-01-01", "2026-01-31")
    """
    if not transaction_ids:
        st.info(f"Aucune transaction trouvée pour la catégorie **{category}**.")
        return

    # Fetch and filter transactions
    df_validated, df_pending = _fetch_and_filter_transactions(transaction_ids)

    if df_validated.empty and df_pending.empty:
        st.warning("Les transactions n'ont pas pu être chargées.")
        return

    # Display persistent success message if exists
    if f'{key_prefix}_success_msg' in st.session_state:
        st.success(st.session_state[f'{key_prefix}_success_msg'])
        del st.session_state[f'{key_prefix}_success_msg']

    # Display summary metrics for all transactions
    df_all = pd.concat([df_validated, df_pending], ignore_index=True)
    _display_summary_metrics(df_all)

    # Display validated transactions section
    if not df_validated.empty:
        _handle_validated_transactions(df_validated, key_prefix, category, show_anomaly_management)

    # Display pending transactions section
    if not df_pending.empty:
        _handle_pending_transactions(df_pending, key_prefix, category)

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
