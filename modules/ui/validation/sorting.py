"""
Transaction sorting logic.
Pure business logic for sorting transaction groups.
"""
import pandas as pd


class SortStrategy:
    """Sort strategies for transaction groups."""
    COUNT = "count"
    DATE_RECENT = "date_recent"
    DATE_OLD = "date_old"
    AMOUNT_DESC = "amount_desc"
    AMOUNT_ASC = "amount_asc"


def sort_groups(
    group_stats: pd.DataFrame,
    sort_key: str = SortStrategy.COUNT,
    max_groups: int = 40
) -> list[str]:
    """
    Sort and limit transaction groups based on strategy.
    
    Always prioritizes non-single transactions (groups) over single ones,
    then applies the selected sorting within each category.
    
    Args:
        group_stats: DataFrame with columns: clean_group, count, max_date, max_amount, is_single
        sort_key: Sorting strategy (use SortStrategy constants)
        max_groups: Maximum number of groups to return
        
    Returns:
        List of group names (clean_group values) in sorted order
        
    Example:
        >>> stats = calculate_group_stats(grouped_df)
        >>> top_groups = sort_groups(stats, SortStrategy.COUNT, max_groups=10)
        >>> # Returns top 10 groups sorted by count (largest first)
    """
    if sort_key == SortStrategy.COUNT:
        # Sort by count descending (largest groups first)
        sorted_stats = group_stats.sort_values(
            by=['is_single', 'count'], 
            ascending=[True, False]
        )
    elif sort_key == SortStrategy.DATE_RECENT:
        # Sort by date descending (most recent first)
        sorted_stats = group_stats.sort_values(
            by=['is_single', 'max_date'], 
            ascending=[True, False]
        )
    elif sort_key == SortStrategy.DATE_OLD:
        # Sort by date ascending (oldest first)
        sorted_stats = group_stats.sort_values(
            by=['is_single', 'max_date'], 
            ascending=[True, True]
        )
    elif sort_key == SortStrategy.AMOUNT_DESC:
        # Sort by amount descending (largest first)
        sorted_stats = group_stats.sort_values(
            by=['is_single', 'max_amount'], 
            ascending=[True, False]
        )
    elif sort_key == SortStrategy.AMOUNT_ASC:
        # Sort by amount ascending (smallest first)
        sorted_stats = group_stats.sort_values(
            by=['is_single', 'max_amount'], 
            ascending=[True, True]
        )
    else:
        # Default to count sorting
        sorted_stats = group_stats.sort_values(
            by=['is_single', 'count'], 
            ascending=[True, False]
        )
    
    # Limit to max_groups
    return sorted_stats['clean_group'].tolist()[:max_groups]


def get_sort_options() -> dict[str, str]:
    """
    Get human-readable sort options for UI display.
    
    Returns:
        Dict mapping display name to sort key
    """
    return {
        "Gros groupes (Défaut)": SortStrategy.COUNT,
        "Plus récentes": SortStrategy.DATE_RECENT,
        "Plus anciennes": SortStrategy.DATE_OLD,
        "Montant (Décroissant)": SortStrategy.AMOUNT_DESC,
        "Montant (Croissant)": SortStrategy.AMOUNT_ASC
    }
