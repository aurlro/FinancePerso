"""
Transaction grouping logic.
Pure business logic for smart grouping of pending transactions.
"""
import re
import pandas as pd
from modules.utils import clean_label


def get_smart_groups(
    df: pd.DataFrame,
    excluded_ids: set[int] = None
) -> pd.DataFrame:
    """
    Apply smart grouping logic to transactions.
    
    Groups transactions by cleaned label with special handling for:
    - Cheques: Group by label + amount (to separate different cheques)
    - Manually ungrouped: Keep as individual transactions
    - Excluded IDs: Keep as individual transactions
    
    Args:
        df: DataFrame with pending transactions
        excluded_ids: Set of transaction IDs to keep ungrouped
        
    Returns:
        DataFrame with additional 'clean_group' column
        
    Example:
        >>> df = pd.DataFrame({
        ...     'id': [1, 2, 3],
        ...     'label': ['CARREFOUR CB*6759', 'CARREFOUR CB*6759', 'CHQ 12345'],
        ...     'amount': [-50.0, -50.0, -100.0],
        ...     'is_manually_ungrouped': [0, 0, 0]
        ... })
        >>> result = get_smart_groups(df)
        >>> result['clean_group'].unique()
        array(['CARREFOUR', 'CHQ 12345 | -100.00 €'])
    """
    if excluded_ids is None:
        excluded_ids = set()
    
    def get_group_key(row):
        # Check if ungrouped (DB flag or session state)
        is_ungrouped_db = row.get('is_manually_ungrouped', 0) == 1
        if is_ungrouped_db or row['id'] in excluded_ids:
            return f"single_{row['id']}"
        
        label_upper = str(row['label']).upper()
        
        # Special handling for cheques: group by label + amount
        if re.search(r'\b(CHQ|CHEQUE|REMISE\s+CHEQUE|REMISE\s+CHQ)\b', label_upper):
            return f"{clean_label(row['label'])} | {row['amount']:.2f} €"
        
        # Default: group by cleaned label
        return clean_label(row['label'])
    
    result = df.copy()
    result['id'] = result['id'].astype(int)
    result['clean_group'] = result.apply(get_group_key, axis=1)
    
    return result


def calculate_group_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate statistics for each transaction group.
    
    Args:
        df: DataFrame with 'clean_group' column
        
    Returns:
        DataFrame with columns: clean_group, count, max_date, max_amount, is_single
        
    Example:
        >>> grouped = get_smart_groups(df)
        >>> stats = calculate_group_stats(grouped)
        >>> stats[['clean_group', 'count', 'max_amount']]
    """
    stats = df.groupby('clean_group').agg({
        'id': 'size',
        'date': 'max',
        'amount': lambda x: x.abs().max()
    }).reset_index()
    
    stats.columns = ['clean_group', 'count', 'max_date', 'max_amount']
    
    # Mark single transactions (manually ungrouped)
    stats['is_single'] = stats['clean_group'].apply(
        lambda x: 1 if str(x).startswith("single_") else 0
    )
    
    return stats


def get_group_transactions(df: pd.DataFrame, group_name: str) -> pd.DataFrame:
    """
    Get all transactions belonging to a specific group.
    
    Args:
        df: DataFrame with 'clean_group' column
        group_name: Name of the group
        
    Returns:
        DataFrame containing only transactions from that group
    """
    return df[df['clean_group'] == group_name].copy()
