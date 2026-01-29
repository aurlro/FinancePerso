"""
Budget Prediction and Overrun Detection.

Projects monthly spending and alerts on potential budget overruns.
"""
import pandas as pd
import datetime
import calendar
from modules.logger import logger


def predict_budget_overruns(df_month: pd.DataFrame, budgets: pd.DataFrame) -> list:
    """
    Predict which budgets are likely to be exceeded by month end.
    
    Args:
        df_month: DataFrame with current month's transactions
        budgets: DataFrame with budget definitions (columns: category, amount)
        
    Returns:
        List of prediction dictionaries with keys:
            - category: Category name
            - budget: Budget amount
            - current_spent: Amount spent so far
            - projected_spent: Projected total for month
            - status: 'ok', 'warning', 'overrun'
            - alert_level: '🟢', '🟠', '🔴'
            - days_remaining: Days left in month
            
    Example:
        predictions = predict_budget_overruns(df_current_month, budgets_df)
        for pred in predictions:
            print(f"{pred['category']}: {pred['status']} - {pred['projected_spent']:.2f}€")
    """
    if df_month.empty or budgets.empty:
        return []
    
    today = datetime.date.today()
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    days_passed = today.day
    days_remaining = days_in_month - days_passed
    
    # Avoid division by zero
    if days_passed == 0:
        return []
    
    # Prepare expense data
    df_exp = df_month[df_month['amount'] < 0].copy()
    df_exp['abs_amount'] = df_exp['amount'].abs()
    
    # Get category from validated or original
    df_exp['cat'] = df_exp.apply(
        lambda x: x['category_validated'] if x['category_validated'] != 'Inconnu' 
        else (x.get('original_category') or 'Inconnu'), 
        axis=1
    )
    
    # Group by category
    spent_by_cat = df_exp.groupby('cat')['abs_amount'].sum().to_dict()
    
    predictions = []
    
    for _, budget_row in budgets.iterrows():
        category = budget_row['category']
        budget_amt = budget_row['amount']
        
        # Get current spending
        current_spent = spent_by_cat.get(category, 0.0)
        
        # Project to end of month (linear)
        daily_avg = current_spent / days_passed
        projected_spent = daily_avg * days_in_month
        
        # Determine status
        usage_pct = (projected_spent / budget_amt * 100) if budget_amt > 0 else 0
        
        if usage_pct < 80:
            status = 'ok'
            alert_level = '🟢'
        elif usage_pct < 100:
            status = 'warning'
            alert_level = '🟠'
        else:
            status = 'overrun'
            alert_level = '🔴'
        
        predictions.append({
            'category': category,
            'budget': budget_amt,
            'current_spent': current_spent,
            'projected_spent': projected_spent,
            'usage_percent': usage_pct,
            'status': status,
            'alert_level': alert_level,
            'days_remaining': days_remaining,
            'daily_avg': daily_avg
        })
    
    # Sort by severity (overrun first)
    status_order = {'overrun': 0, 'warning': 1, 'ok': 2}
    predictions.sort(key=lambda x: (status_order[x['status']], -x['usage_percent']))
    
    logger.info(f"Generated {len(predictions)} budget predictions")
    return predictions


def get_budget_alerts_summary(predictions: list) -> dict:
    """
    Get a summary of budget alerts.
    
    Args:
        predictions: List of predictions from predict_budget_overruns()
        
    Returns:
        Dict with summary stats:
            - total_budgets: Total number of budgets
            - ok_count: Number of budgets on track
            - warning_count: Number of budgets at risk
            - overrun_count: Number of budgets projected to overrun
    """
    return {
        'total_budgets': len(predictions),
        'ok_count': sum(1 for p in predictions if p['status'] == 'ok'),
        'warning_count': sum(1 for p in predictions if p['status'] == 'warning'),
        'overrun_count': sum(1 for p in predictions if p['status'] == 'overrun')
    }
