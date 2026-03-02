"""
Explorer Main - Vue principale de l'explorateur.
"""

import pandas as pd
import streamlit as st

from modules.db.categories import get_categories_with_emojis
from modules.db.transactions import get_all_transactions

from .explorer_filters import render_explorer_filters
from .explorer_launcher import render_back_button
from .explorer_results import render_explorer_results


def load_data_for_explorer(explorer_type: str, value: str) -> pd.DataFrame:
    """
    Load transactions for the selected category or tag.

    Args:
        explorer_type: 'category' or 'tag'
        value: Category or tag value

    Returns:
        DataFrame with matching transactions
    """
    df = get_all_transactions()

    if df.empty:
        return df

    if explorer_type == "category":
        # Filter by category
        if "category_validated" in df.columns:
            return df[df["category_validated"].str.lower() == value.lower()]

    elif explorer_type == "tag":
        # Filter by tag
        if "tags" in df.columns:
            mask = df["tags"].apply(
                lambda x: value.lower() in str(x).lower().split(",") if pd.notna(x) else False
            )
            return df[mask]

    return df


def render_explorer_header(explorer_type: str, explorer_value: str, from_page: str):
    """Render the explorer header with title and back button."""
    # Get emoji
    cat_emojis = get_categories_with_emojis()

    if explorer_type == "category":
        icon = cat_emojis.get(explorer_value, "📂")
        label = "Catégorie"
    else:
        icon = "🏷️"
        label = "Tag"

    # Header row
    col1, col2 = st.columns([6, 1])

    with col1:
        st.header(f"{icon} {explorer_value}")
        st.caption(f"Exploration par {label}")

    with col2:
        render_back_button(from_page)

    st.divider()


def render_explorer_empty_state(explorer_type: str, explorer_value: str):
    """Render empty state when no data found."""
    icon = "📂" if explorer_type == "category" else "🏷️"

    st.markdown(
        f"""
    <div style='
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 16px;
        border: 2px dashed #cbd5e1;
        margin: 2rem 0;
    '>
        <div style='font-size: 4rem; margin-bottom: 1rem;'>{icon}</div>
        <h2 style='color: #475569; margin-bottom: 0.5rem;'>Aucune transaction trouvée</h2>
        <p style='color: #64748b; font-size: 1.1rem;'>
            Aucune transaction ne correspond à <strong>{explorer_value}</strong>
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.info(f"""
    **Conseils :**
    - Vérifiez que les transactions sont bien catégorisées comme "{explorer_value}"
    - Pour les tags, assurez-vous qu'ils sont séparés par des virgules
    - Importez de nouvelles données si nécessaire
    """)


def render_explorer_page(explorer_type: str, explorer_value: str, from_page: str):
    """
    Render the complete explorer page.

    Args:
        explorer_type: 'category' or 'tag'
        explorer_value: Value to explore
        from_page: Origin page for back navigation
    """
    # Load data
    df = load_data_for_explorer(explorer_type, explorer_value)

    # Render header
    render_explorer_header(explorer_type, explorer_value, from_page)

    # Handle empty state
    if df.empty:
        render_explorer_empty_state(explorer_type, explorer_value)
        return

    # Filters and results
    filtered_df = render_explorer_filters(df, key_prefix="explorer_main")

    st.divider()

    # Results
    render_explorer_results(filtered_df, explorer_type, explorer_value, key_prefix="explorer_main")


def render_quick_explorer(explorer_type: str, explorer_value: str, show_filters: bool = True):
    """
    Render a compact explorer view (for embedding in other pages).

    Args:
        explorer_type: 'category' or 'tag'
        explorer_value: Value to explore
        show_filters: Whether to show filters
    """
    df = load_data_for_explorer(explorer_type, explorer_value)

    if df.empty:
        st.info(f"Aucune transaction pour {explorer_value}")
        return

    if show_filters:
        filtered_df = render_explorer_filters(df, key_prefix="quick_explorer")
    else:
        filtered_df = df

    render_explorer_results(filtered_df, explorer_type, explorer_value, key_prefix="quick_explorer")
