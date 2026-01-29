"""
Trend Analysis for Spending Patterns.

Identifies changes in financial behavior by comparing periods.
"""
import pandas as pd
from modules.logger import logger


def analyze_spending_trends(df_current: pd.DataFrame, df_previous: pd.DataFrame, 
                            threshold_pct: float = 30.0) -> dict:
    """
    Analyze spending trends by comparing current and previous periods.
    
    Args:
        df_current: DataFrame with current period transactions
        df_previous: DataFrame with previous period transactions
        threshold_pct: Minimum percentage change to report (default: 30%)
        
    Returns:
        Dict with:
            - insights: List of insight dicts (category, message, emoji, change_pct, etc.)
            - period_current: Dict with start/end dates
            - period_previous: Dict with start/end dates
        
    Example:
        result = analyze_spending_trends(df_this_month, df_last_month)
        for insight in result['insights']:
            print(insight['message'])
    """
    if df_current.empty:
        return {
            'insights': [],
            'period_current': None,
            'period_previous': None,
            'message': "Aucune donnée pour la période actuelle."
        }
    
    # Extract period information
    period_current = None
    period_previous = None
    
    if 'date' in df_current.columns:
        df_current['date_dt'] = pd.to_datetime(df_current['date'])
        period_current = {
            'start': df_current['date_dt'].min().strftime('%Y-%m-%d'),
            'end': df_current['date_dt'].max().strftime('%Y-%m-%d'),
            'days': (df_current['date_dt'].max() - df_current['date_dt'].min()).days + 1
        }
    
    if not df_previous.empty and 'date' in df_previous.columns:
        df_previous['date_dt'] = pd.to_datetime(df_previous['date'])
        period_previous = {
            'start': df_previous['date_dt'].min().strftime('%Y-%m-%d'),
            'end': df_previous['date_dt'].max().strftime('%Y-%m-%d'),
            'days': (df_previous['date_dt'].max() - df_previous['date_dt'].min()).days + 1
        }
    
    insights = []
    
    # Prepare expense data
    def prepare_expenses(df):
        df_exp = df[df['amount'] < 0].copy()
        df_exp['abs_amount'] = df_exp['amount'].abs()
        df_exp['cat'] = df_exp.apply(
            lambda x: x['category_validated'] if x['category_validated'] != 'Inconnu' 
            else (x.get('original_category') or 'Inconnu'), 
            axis=1
        )
        return df_exp
    
    df_current_exp = prepare_expenses(df_current)
    df_previous_exp = prepare_expenses(df_previous) if not df_previous.empty else pd.DataFrame()
    
    current_by_cat = df_current_exp.groupby('cat')['abs_amount'].sum().to_dict()
    previous_by_cat = df_previous_exp.groupby('cat')['abs_amount'].sum().to_dict() if not df_previous_exp.empty else {}
    
    # Get transaction IDs by category
    current_ids_by_cat = df_current_exp.groupby('cat')['id'].apply(list).to_dict() if 'id' in df_current_exp.columns else {}
    
    # Analyze each category
    all_cats = set(current_by_cat.keys()) | set(previous_by_cat.keys())
    
    changes = []
    
    for cat in all_cats:
        # Skip internal transfers and excluded categories
        if cat in ['Virement Interne', 'Hors Budget', 'Inconnu']:
            continue
        
        current_amt = current_by_cat.get(cat, 0.0)
        previous_amt = previous_by_cat.get(cat, 0.0)
        
        # Calculate change
        if previous_amt > 0:
            change_pct = ((current_amt - previous_amt) / previous_amt) * 100
            change_abs = current_amt - previous_amt
            
            if abs(change_pct) >= threshold_pct:
                changes.append({
                    'category': cat,
                    'change_pct': change_pct,
                    'change_abs': change_abs,
                    'current': current_amt,
                    'previous': previous_amt,
                    'transaction_ids': current_ids_by_cat.get(cat, [])
                })
        elif current_amt > 50:  # New category with significant spending
            changes.append({
                'category': cat,
                'change_pct': 999,  # Flag as new
                'change_abs': current_amt,
                'current': current_amt,
                'previous': 0,
                'transaction_ids': current_ids_by_cat.get(cat, [])
            })
    
    # Sort by absolute change
    changes.sort(key=lambda x: abs(x['change_abs']), reverse=True)
    
    # Generate insights with structured data
    for change in changes[:5]:  # Top 5 changes
        cat = change['category']
        pct = change['change_pct']
        amt = change['change_abs']
        
        if pct == 999:
            emoji = "🆕"
            message = f"Nouvelle catégorie de dépense : **{cat}** ({change['current']:.0f}€)"
        elif pct > 0:
            emoji = "📈" if pct > 50 else "↗️"
            message = f"Vos dépenses **{cat}** ont augmenté de **{pct:.0f}%** (+{amt:.0f}€)"
        else:
            emoji = "📉" if pct < -50 else "↘️"
            message = f"Vos dépenses **{cat}** ont diminué de **{abs(pct):.0f}%** ({amt:.0f}€)"
        
        insights.append({
            'category': cat,
            'emoji': emoji,
            'message': message,
            'change_pct': pct,
            'change_abs': amt,
            'current': change['current'],
            'previous': change['previous'],
            'transaction_ids': change['transaction_ids']
        })
    
    if not insights:
        insights.append({
            'category': None,
            'emoji': "✅",
            'message': "Vos dépenses sont stables par rapport à la période précédente.",
            'change_pct': 0,
            'change_abs': 0,
            'current': 0,
            'previous': 0,
            'transaction_ids': []
        })
    
    logger.info(f"Generated {len(insights)} spending trend insights")
    
    return {
        'insights': insights,
        'period_current': period_current,
        'period_previous': period_previous
    }


def get_top_categories_comparison(df_current: pd.DataFrame, df_previous: pd.DataFrame, 
                                  top_n: int = 5) -> pd.DataFrame:
    """
    Get top spending categories with period-over-period comparison.
    
    Args:
        df_current: Current period transactions
        df_previous: Previous period transactions
        top_n: Number of top categories to return
        
    Returns:
        DataFrame with columns: category, current, previous, change_pct
    """
    def get_top_cats(df):
        df_exp = df[df['amount'] < 0].copy()
        df_exp['abs_amount'] = df_exp['amount'].abs()
        df_exp['cat'] = df_exp.apply(
            lambda x: x['category_validated'] if x['category_validated'] != 'Inconnu' 
            else (x.get('original_category') or 'Inconnu'), 
            axis=1
        )
        return df_exp.groupby('cat')['abs_amount'].sum().nlargest(top_n)
    
    current_top = get_top_cats(df_current)
    previous_top = get_top_cats(df_previous) if not df_previous.empty else pd.Series()
    
    # Merge
    comparison = pd.DataFrame({
        'current': current_top,
        'previous': previous_top
    }).fillna(0)
    
    comparison['change_pct'] = ((comparison['current'] - comparison['previous']) / 
                                comparison['previous'] * 100).fillna(0)
    
    return comparison.reset_index().rename(columns={'index': 'category'})
