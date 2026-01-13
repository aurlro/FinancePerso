import pandas as pd
import re
from modules.categorization import clean_label

def detect_recurring_payments(df):
    """
    Analyze transactions to find recurring patterns (Subscriptions, Salaries, Bills).
    Returns a DataFrame of detected recurring items.
    """
    if df.empty:
        return pd.DataFrame()

    # Work on a copy
    data = df.copy()
    
    # 1. Clean labels for grouping
    # We use a stricter cleaning here to ensure slight variations (dates) don't break grouping
    data['clean_label_strict'] = data['label'].apply(clean_label)
    
    # 2. Group analysis
    recurring_items = []
    
    # Filter only relevant columns for speed
    # We need date, amount, clean_label_strict
    data['date'] = pd.to_datetime(data['date'])
    
    grouped = data.groupby('clean_label_strict')
    
    for label, group in grouped:
        if len(group) < 2:
            continue
            
        # Check amounts consistency
        # Subscriptions usually have exact same amount
        # Utilities might vary slightly
        amounts = group['amount'].tolist()
        amounts_std = group['amount'].std()
        avg_amount = group['amount'].mean()
        
        # If std is low relative to average (e.g. < 5%), we consider it consistent amount
        is_consistent_amount = (amounts_std / abs(avg_amount)) < 0.05 if avg_amount != 0 else (amounts_std == 0)
        
        # Check Periodicity
        dates = group['date'].sort_values()
        diffs = dates.diff().dropna()
        avg_diff_days = diffs.dt.days.mean()
        
        # We look for monthly (approx 28-31 days) or multiples
        is_monthly = 25 <= avg_diff_days <= 35
        
        # Frequency score (how many months present vs distinct months in dataset)
        # Not strictly needed for MVP, simplified logic:
        
        if is_consistent_amount and is_monthly:
            # It's a candidate
            # Determine category if known
            current_cat = group.iloc[0]['category_validated']
            
            recurring_items.append({
                "label": label,
                "avg_amount": round(avg_amount, 2),
                "frequency_days": round(avg_diff_days, 1),
                "count": len(group),
                "last_date": group['date'].max().date(),
                "category": current_cat,
                "is_subscription_candidate": True
            })
            
    return pd.DataFrame(recurring_items).sort_values(by='avg_amount')
