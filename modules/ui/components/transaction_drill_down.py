"""
Transaction Drill-Down Component (Legacy wrapper).
This module provides fallback implementations when ui_v2 is not available.
"""

import pandas as pd
import streamlit as st

from modules.db.transactions import get_transaction_by_id


def render_transaction_drill_down(
    category: str,
    transaction_ids: list,
    period_start: str = None,
    period_end: str = None,
    key_prefix: str = "drilldown",
    show_anomaly_management: bool = False,
    anomaly_index: int | None = None,
    anomaly_list_key: str | None = None,
):
    """
    Render an interactive drill-down view for transactions (fallback implementation).

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
        st.info("Aucune transaction trouvée.")
        return

    # Fetch transactions from database
    transactions = []
    for tx_id in transaction_ids:
        tx = get_transaction_by_id(tx_id)
        if tx:
            transactions.append(tx)

    if not transactions:
        st.warning("Les transactions n'ont pas pu être chargées.")
        return

    # Convert to DataFrame for display
    data = []
    for tx in transactions:
        data.append({
            "Date": tx.get("date"),
            "Description": tx.get("label"),
            "Montant": tx.get("amount"),
            "Catégorie": tx.get("category_validated") or tx.get("category") or "Non catégorisé",
            "Statut": "Validé" if tx.get("validated") else "En attente",
        })

    df = pd.DataFrame(data)

    # Display summary
    total = df["Montant"].sum()
    st.metric("Total", f"{total:,.2f} €")

    # Show corrected badge if applicable
    if anomaly_index is not None and anomaly_list_key:
        corrected_list = st.session_state.get(f"{anomaly_list_key}_corrected", [])
        if anomaly_index in corrected_list:
            st.success("✅ **Anomalie vérifiée et corrigée**")

    # Display transactions table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
            "Montant": st.column_config.NumberColumn("Montant", format="%.2f €"),
        },
    )

    # Simple edit form for first transaction (if needed)
    if len(transactions) > 0 and show_anomaly_management:
        with st.expander("Modifier la catégorie"):
            tx = transactions[0]
            new_category = st.text_input(
                "Nouvelle catégorie",
                value=tx.get("category_validated") or tx.get("category_suggested") or "",
                key=f"{key_prefix}_category",
            )
            if st.button("Sauvegarder", key=f"{key_prefix}_save"):
                from modules.db.transactions import update_transaction_category
                update_transaction_category(tx.get("id"), new_category)
                st.success("Catégorie mise à jour!")
                st.rerun()


def render_category_drill_down_expander(
    insight: dict, period_start: str = None, period_end: str = None, key_prefix: str = "insight"
):
    """Render expander for trend insights (fallback implementation)."""
    if not insight.get("category"):
        st.markdown(f"{insight.get('emoji', '💡')} {insight.get('message', '')}")
        return

    with st.expander(
        f"{insight.get('emoji', '💡')} {insight.get('message', '')}",
        expanded=False,
    ):
        render_transaction_drill_down(
            category=insight["category"],
            transaction_ids=insight.get("transaction_ids", []),
            period_start=period_start,
            period_end=period_end,
            key_prefix=f"{key_prefix}_{insight['category'].replace(' ', '_')}",
        )


__all__ = [
    "render_transaction_drill_down",
    "render_category_drill_down_expander",
]
