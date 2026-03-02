"""
Pagination Component - Composant de pagination réutilisable

Usage:
    from modules.ui.components.pagination import paginated_dataframe

    df = get_all_transactions()
    paginated_df = paginated_dataframe(df, page_size=50, key="tx_pagination")
    st.dataframe(paginated_df)
"""

import pandas as pd
import streamlit as st


def paginated_dataframe(
    df: pd.DataFrame, page_size: int = 50, key: str = "pagination", show_page_info: bool = True
) -> pd.DataFrame:
    """
    Returns a paginated slice of a DataFrame with UI controls.

    Args:
        df: DataFrame complet à paginer
        page_size: Nombre de lignes par page (défaut: 50)
        key: Clé unique pour le widget (important pour éviter les conflits)
        show_page_info: Afficher les informations de pagination

    Returns:
        DataFrame filtré pour la page courante
    """
    if df.empty:
        return df

    total_rows = len(df)
    total_pages = max(1, (total_rows - 1) // page_size + 1)

    # Session state pour persister la page
    session_key = f"{key}_current_page"
    if session_key not in st.session_state:
        st.session_state[session_key] = 1

    # UI de pagination
    col1, col2, col3, col4 = st.columns([2, 1, 1, 2])

    with col1:
        if show_page_info:
            st.caption(
                f"📊 {total_rows} résultats | Page {st.session_state[session_key]}/{total_pages}"
            )

    with col2:
        if st.button(
            "⏮️ Précédent", key=f"{key}_prev", disabled=st.session_state[session_key] <= 1
        ):
            st.session_state[session_key] -= 1
            st.rerun()

    with col3:
        if st.button(
            "Suivant ⏭️", key=f"{key}_next", disabled=st.session_state[session_key] >= total_pages
        ):
            st.session_state[session_key] += 1
            st.rerun()

    with col4:
        # Sélecteur de page direct
        if total_pages > 1:
            selected_page = st.number_input(
                "Page",
                min_value=1,
                max_value=total_pages,
                value=st.session_state[session_key],
                key=f"{key}_selector",
                label_visibility="collapsed",
            )
            if selected_page != st.session_state[session_key]:
                st.session_state[session_key] = selected_page
                st.rerun()

    # Calcul des indices
    current_page = st.session_state[session_key]
    start_idx = (current_page - 1) * page_size
    end_idx = min(start_idx + page_size, total_rows)

    return df.iloc[start_idx:end_idx]


def paginated_list(items: list, page_size: int = 10, key: str = "list_pagination") -> list:
    """
    Paginate a list with UI controls.

    Args:
        items: Liste complète à paginer
        page_size: Nombre d'éléments par page
        key: Clé unique pour le widget

    Returns:
        Sous-liste pour la page courante
    """
    if not items:
        return items

    total_items = len(items)
    total_pages = max(1, (total_items - 1) // page_size + 1)

    session_key = f"{key}_page"
    if session_key not in st.session_state:
        st.session_state[session_key] = 1

    current_page = st.session_state[session_key]

    # UI compacte
    cols = st.columns([1, 3, 1])
    with cols[0]:
        if st.button("◀", key=f"{key}_prev_btn", disabled=current_page <= 1):
            st.session_state[session_key] -= 1
            st.rerun()

    with cols[1]:
        st.caption(f"Page {current_page}/{total_pages} ({total_items} total)")

    with cols[2]:
        if st.button("▶", key=f"{key}_next_btn", disabled=current_page >= total_pages):
            st.session_state[session_key] += 1
            st.rerun()

    start_idx = (current_page - 1) * page_size
    end_idx = min(start_idx + page_size, total_items)

    return items[start_idx:end_idx]


def reset_pagination(key: str):
    """Reset pagination state for a given key."""
    session_key = f"{key}_current_page"
    list_key = f"{key}_page"

    if session_key in st.session_state:
        del st.session_state[session_key]
    if list_key in st.session_state:
        del st.session_state[list_key]


def calculate_total_pages(total_items: int, page_size: int) -> int:
    """
    Calculate the total number of pages needed.

    Args:
        total_items: Total number of items
        page_size: Number of items per page

    Returns:
        Total number of pages (minimum 1)
    """
    if total_items <= 0:
        return 1
    return max(1, (total_items - 1) // page_size + 1)
