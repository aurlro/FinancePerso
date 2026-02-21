"""
Top Expenses Widget

Affiche le tableau des plus grosses dépenses.
"""

import pandas as pd
import streamlit as st

from modules.transaction_types import filter_expense_transactions


def render_top_expenses(df_current: pd.DataFrame, cat_emoji_map: dict, limit: int = 10):
    """
    Render table of top expenses.
    Filtre les dépenses en utilisant les catégories (pas le signe du montant).

    Args:
        df_current: Current period transactions
        cat_emoji_map: Category to emoji mapping
        limit: Number of top expenses to show (default: 10)
    """
    st.subheader("🔝 Top 10 Dépenses")

    # Filter expenses only using categories for "Top Expenses"
    df_exp = filter_expense_transactions(df_current).copy()

    if df_exp.empty:
        st.info("Aucune dépense sur cette période.")
        return

    df_exp["amount"] = df_exp["amount"].abs()

    # Add display category with emoji
    df_exp["raw_cat"] = df_exp.apply(
        lambda x: (
            x["category_validated"]
            if x["category_validated"] != "Inconnu"
            else (x["original_category"] or "Inconnu")
        ),
        axis=1,
    )
    df_exp["Catégorie"] = df_exp["raw_cat"].apply(lambda x: f"{cat_emoji_map.get(x, '🏷️')} {x}")

    # Get top N
    top_expenses = df_exp.sort_values("amount", ascending=False).head(limit)

    # Use drill-down instead of static dataframe
    from modules.ui.components.transaction_drill_down import render_transaction_drill_down

    # We pass 'Top 10' as a generic category name, but the component now handles
    # heterogeneous categories using the transaction's own category as default.
    render_transaction_drill_down(
        category="Top Expenses",
        transaction_ids=top_expenses["id"].tolist(),
        key_prefix="top_exp_drill",
    )
