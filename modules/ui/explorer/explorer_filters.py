"""
Explorer Filters - Filtres avancés pour l'explorateur.
"""
import streamlit as st
import pandas as pd
from datetime import date, datetime
from typing import Tuple, Optional, List
from modules.transaction_types import (
    is_expense_category, is_income_category, is_excluded_category
)


def render_date_filter(df: pd.DataFrame, key_prefix: str = "explorer") -> Tuple[Optional[date], Optional[date]]:
    """Render date range filter."""
    if df.empty or 'date' not in df.columns:
        return None, None
    
    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df_copy['date'])
    
    min_date = df_copy['date'].min().date()
    max_date = df_copy['date'].max().date()
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "📅 Du",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
            key=f"{key_prefix}_start_date"
        )
    with col2:
        end_date = st.date_input(
            "📅 Au",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            key=f"{key_prefix}_end_date"
        )
    
    return start_date, end_date


def render_amount_filter(df: pd.DataFrame, key_prefix: str = "explorer") -> Tuple[float, float]:
    """Render amount range filter."""
    if df.empty or 'amount' not in df.columns:
        return 0.0, 0.0
    
    amounts = df['amount'].astype(float)
    min_val = abs(amounts.min()) if amounts.min() < 0 else 0.0
    max_val = abs(amounts.max()) if amounts.max() > 0 else 1000.0
    
    col1, col2 = st.columns(2)
    with col1:
        min_amount = st.number_input(
            "💰 Montant min (€)",
            value=0.0,
            min_value=0.0,
            max_value=float(max_val),
            step=10.0,
            key=f"{key_prefix}_min_amount"
        )
    with col2:
        max_amount = st.number_input(
            "💰 Montant max (€)",
            value=float(max_val),
            min_value=0.0,
            max_value=float(max_val) * 2,
            step=10.0,
            key=f"{key_prefix}_max_amount"
        )
    
    return min_amount, max_amount


def render_type_filter(key_prefix: str = "explorer") -> str:
    """Render transaction type filter."""
    return st.selectbox(
        "📊 Type",
        options=["Tous", "Dépenses", "Revenus"],
        index=0,
        key=f"{key_prefix}_type"
    )


def render_account_filter(df: pd.DataFrame, key_prefix: str = "explorer") -> List[str]:
    """Render account multi-select filter."""
    if df.empty or 'account_label' not in df.columns:
        return []
    
    accounts = sorted([a for a in df['account_label'].unique() if a])
    if not accounts:
        return []
    
    return st.multiselect(
        "🏦 Comptes",
        options=accounts,
        default=[],
        placeholder="Tous les comptes",
        key=f"{key_prefix}_accounts"
    )


def render_member_filter(df: pd.DataFrame, key_prefix: str = "explorer") -> List[str]:
    """Render member multi-select filter."""
    if df.empty or 'member' not in df.columns:
        return []
    
    members = sorted([m for m in df['member'].unique() if m])
    if not members:
        return []
    
    return st.multiselect(
        "👤 Membres",
        options=members,
        default=[],
        placeholder="Tous les membres",
        key=f"{key_prefix}_members"
    )


def render_status_filter(key_prefix: str = "explorer") -> List[str]:
    """Render status filter."""
    return st.multiselect(
        "📋 Statut",
        options=["validated", "pending"],
        default=["validated"],
        format_func=lambda x: "✅ Validé" if x == "validated" else "⏳ En attente",
        key=f"{key_prefix}_status"
    )


def render_tag_filter(available_tags: List[str], key_prefix: str = "explorer") -> List[str]:
    """Render tag filter."""
    if not available_tags:
        return []
    
    return st.multiselect(
        "🏷️ Tags",
        options=sorted(available_tags),
        default=[],
        placeholder="Filtrer par tags",
        key=f"{key_prefix}_tags"
    )


def render_search_filter(key_prefix: str = "explorer") -> str:
    """Render text search filter."""
    return st.text_input(
        "🔍 Recherche",
        placeholder="Rechercher dans les libellés...",
        key=f"{key_prefix}_search"
    )


def apply_filters(
    df: pd.DataFrame,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    min_amount: float = 0.0,
    max_amount: float = float('inf'),
    tx_type: str = "Tous",
    accounts: List[str] = None,
    members: List[str] = None,
    statuses: List[str] = None,
    tags: List[str] = None,
    search: str = ""
) -> pd.DataFrame:
    """
    Apply all filters to DataFrame.
    
    Returns:
        Filtered DataFrame
    """
    if df.empty:
        return df
    
    filtered = df.copy()
    
    # Date filter
    if start_date is not None and end_date is not None and 'date' in filtered.columns:
        filtered['date'] = pd.to_datetime(filtered['date'])
        mask = (filtered['date'].dt.date >= start_date) & (filtered['date'].dt.date <= end_date)
        filtered = filtered[mask]
    
    # Amount filter (comparing absolute values for expenses)
    if 'amount' in filtered.columns and (min_amount > 0 or max_amount < float('inf')):
        amounts = filtered['amount'].astype(float).abs()
        mask = (amounts >= min_amount) & (amounts <= max_amount)
        filtered = filtered[mask]
    
    # Type filter
    if tx_type != "Tous" and 'category_validated' in filtered.columns:
        if tx_type == "Dépenses":
            filtered = filtered[filtered['category_validated'].apply(is_expense_category)]
        elif tx_type == "Revenus":
            filtered = filtered[filtered['category_validated'].apply(is_income_category)]
        elif tx_type == "Exclus":
            filtered = filtered[filtered['category_validated'].apply(is_excluded_category)]
    
    # Account filter
    if accounts and 'account_label' in filtered.columns:
        filtered = filtered[filtered['account_label'].isin(accounts)]
    
    # Member filter
    if members and 'member' in filtered.columns:
        filtered = filtered[filtered['member'].isin(members)]
    
    # Status filter
    if statuses and 'status' in filtered.columns:
        filtered = filtered[filtered['status'].isin(statuses)]
    
    # Tags filter
    if tags and 'tags' in filtered.columns:
        # Check if any of the selected tags is in the transaction's tags
        mask = filtered['tags'].apply(
            lambda x: any(tag in str(x).split(',') for tag in tags) if pd.notna(x) else False
        )
        filtered = filtered[mask]
    
    # Search filter
    if search and 'label' in filtered.columns:
        search_lower = search.lower()
        filtered = filtered[filtered['label'].str.lower().str.contains(search_lower, na=False)]
    
    return filtered


@st.fragment
def render_explorer_filters(df: pd.DataFrame, key_prefix: str = "explorer") -> pd.DataFrame:
    """
    Render all filters and return filtered DataFrame.
    Uses @st.fragment to avoid full page reruns.
    """
    if df.empty:
        return df
    
    with st.container(border=True):
        st.subheader("🎛️ Filtres")
        
        # Row 1: Date, Amount
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            start_date, end_date = render_date_filter(df, f"{key_prefix}_date")
        with col2:
            st.empty()  # Placeholder for alignment
        with col3:
            min_amount, max_amount = render_amount_filter(df, f"{key_prefix}_amount")
        with col4:
            st.empty()  # Placeholder for alignment
        
        # Row 2: Type, Account, Member
        col5, col6, col7 = st.columns(3)
        with col5:
            tx_type = render_type_filter(key_prefix)
        with col6:
            accounts = render_account_filter(df, key_prefix)
        with col7:
            members = render_member_filter(df, key_prefix)
        
        # Row 3: Status, Tags, Search
        col8, col9, col10 = st.columns(3)
        with col8:
            statuses = render_status_filter(key_prefix)
        with col9:
            # Get available tags from data
            available_tags = []
            if 'tags' in df.columns:
                all_tags = df['tags'].dropna().str.split(',').explode().unique()
                available_tags = [t.strip() for t in all_tags if t.strip()]
            tags = render_tag_filter(available_tags, key_prefix)
        with col10:
            search = render_search_filter(key_prefix)
        
        # Quick stats
        filtered = apply_filters(
            df, start_date, end_date, min_amount, max_amount,
            tx_type, accounts, members, statuses, tags, search
        )
        
        col_stats, col_reset = st.columns([4, 1])
        with col_stats:
            total = len(filtered)
            total_amount = filtered['amount'].sum() if 'amount' in filtered.columns else 0
            st.caption(f"📊 {total} transaction(s) • Total: {total_amount:,.2f} €")
        
        with col_reset:
            if st.button("🔄 Réinitialiser", key=f"{key_prefix}_reset"):
                st.rerun()
        
        return filtered
