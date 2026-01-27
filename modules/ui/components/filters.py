"""
Filter Components
Reusable filter UI components for transaction filtering.
"""
import streamlit as st
import pandas as pd


def render_transaction_filters(
    df: pd.DataFrame,
    show_account: bool = True,
    show_member: bool = True,
    show_category: bool = False,
    show_tips: bool = True
) -> pd.DataFrame:
    """
    Render sidebar filters and return filtered DataFrame.
    
    Args:
        df: DataFrame to filter
        show_account: Show account filter
        show_member: Show member filter
        show_category: Show category filter
        show_tips: Show tip text at bottom
        
    Returns:
        Filtered DataFrame
        
    Example:
        >>> with st.sidebar:
        ...     filtered = render_transaction_filters(df)
    """
    st.header("🔍 Filtres")
    filtered_df = df.copy()
    
    # Account filter
    if show_account and 'account_label' in df.columns:
        accounts = sorted(df['account_label'].unique().tolist())
        if accounts:
            sel_accounts = st.multiselect(
                "Par Compte",
                accounts,
                key="filter_accounts"
            )
            if sel_accounts:
                filtered_df = filtered_df[filtered_df['account_label'].isin(sel_accounts)]
    
    # Member filter
    if show_member and 'member' in df.columns:
        members = sorted([m for m in df['member'].unique() if m])
        if members:
            sel_members = st.multiselect(
                "Par Membre",
                members,
                key="filter_members"
            )
            if sel_members:
                filtered_df = filtered_df[filtered_df['member'].isin(sel_members)]
    
    # Category filter
    if show_category and 'category_validated' in df.columns:
        categories = sorted([c for c in df['category_validated'].unique() if c])
        if categories:
            sel_categories = st.multiselect(
                "Par Catégorie",
                categories,
                key="filter_categories"
            )
            if sel_categories:
                filtered_df = filtered_df[filtered_df['category_validated'].isin(sel_categories)]
    
    # Tips
    if show_tips:
        st.divider()
        st.caption("💡 Astuce : Le regroupement intelligent fusionne les opérations identiques pour une validation plus rapide.")
    
    return filtered_df


def render_date_range_filter(
    df: pd.DataFrame,
    date_column: str = 'date'
) -> pd.DataFrame:
    """
    Render date range filter.
    
    Args:
        df: DataFrame with date column
        date_column: Name of the date column
        
    Returns:
        Filtered DataFrame
    """
    df_copy = df.copy()
    df_copy[date_column] = pd.to_datetime(df_copy[date_column])
    
    min_date = df_copy[date_column].min()
    max_date = df_copy[date_column].max()
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Du",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
            key="filter_start_date"
        )
    with col2:
        end_date = st.date_input(
            "Au",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            key="filter_end_date"
        )
    
    mask = (df_copy[date_column] >= pd.to_datetime(start_date)) & \
           (df_copy[date_column] <= pd.to_datetime(end_date))
    
    return df[mask]
