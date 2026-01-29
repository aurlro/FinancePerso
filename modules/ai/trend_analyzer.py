"""
Trend Analysis for Spending Patterns.

Identifies changes in financial behavior by comparing periods.
"""
import pandas as pd
from modules.logger import logger


def analyze_spending_trends(df_current: pd.DataFrame, df_previous: pd.DataFrame, 
                            threshold_pct: float = 30.0) -> list:
    """
    Analyze spending trends by comparing current and previous periods.
    
    Args:
        df_current: DataFrame with current period transactions
        df_previous: DataFrame with previous period transactions
        threshold_pct: Minimum percentage change to report (default: 30%)
        
    Returns:
        List of trend insight strings
        
    Example:
        trends = analyze_spending_trends(df_this_month, df_last_month)
        for trend in trends:
            print(trend)
        # "📈 Vos dépenses Restaurants ont augmenté de 45% ce mois-ci"
    """
    if df_current.empty:
        return ["Aucune donnée pour la période actuelle."]
    
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
        return df_exp.groupby('cat')['abs_amount'].sum().to_dict()
    
    current_by_cat = prepare_expenses(df_current)
    previous_by_cat = prepare_expenses(df_previous) if not df_previous.empty else {}
    
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
                    'previous': previous_amt
                })
        elif current_amt > 50:  # New category with significant spending
            changes.append({
                'category': cat,
                'change_pct': 999,  # Flag as new
                'change_abs': current_amt,
                'current': current_amt,
                'previous': 0
            })
    
    # Sort by absolute change
    changes.sort(key=lambda x: abs(x['change_abs']), reverse=True)
    
    # Generate insights
    for change in changes[:5]:  # Top 5 changes
        cat = change['category']
        pct = change['change_pct']
        amt = change['change_abs']
        
        if pct == 999:
            insights.append(f"🆕 Nouvelle catégorie de dépense : **{cat}** ({change['current']:.0f}€)")
        elif pct > 0:
            emoji = "📈" if pct > 50 else "↗️"
            insights.append(f"{emoji} Vos dépenses **{cat}** ont augmenté de **{pct:.0f}%** (+{amt:.0f}€)")
        else:
            emoji = "📉" if pct < -50 else "↘️"
            insights.append(f"{emoji} Vos dépenses **{cat}** ont diminué de **{abs(pct):.0f}%** ({amt:.0f}€)")
    
    if not insights:
        insights.append("✅ Vos dépenses sont stables par rapport à la période précédente.")
    
    logger.info(f"Generated {len(insights)} spending trend insights")
    return insights


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
