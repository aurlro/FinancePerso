"""
Analytics V2 - Enhanced Recurrence Detection
Improved detection with better income handling and drill-down capabilities.
"""
import pandas as pd
import re
from typing import Tuple, List, Dict
from datetime import datetime
from modules.categorization import clean_label
from modules.analytics_constants import (
    MIN_OCCURRENCES_FOR_RECURRING,
    AMOUNT_TOLERANCE_ENERGY,
    AMOUNT_TOLERANCE_STANDARD,
    AMOUNT_TOLERANCE_FIXED_THRESHOLD,
    FREQUENCY_MONTHLY_MIN,
    FREQUENCY_MONTHLY_MAX,
    FREQUENCY_MONTHLY_LABEL,
    FREQUENCY_QUARTERLY_MIN,
    FREQUENCY_QUARTERLY_MAX,
    FREQUENCY_QUARTERLY_LABEL,
    FREQUENCY_ANNUAL_MIN,
    FREQUENCY_ANNUAL_MAX,
    FREQUENCY_ANNUAL_LABEL,
    ENERGY_KEYWORDS,
    SALARY_MIN_AMOUNT,
    HIGH_CONFIDENCE_MIN_COUNT,
)

# Income-specific patterns for better detection
INCOME_PATTERNS = {
    'salaire': ['SALAIRE', 'REMUNERATION', 'PAIEMENT SALAIRE', 'VIR SALAIRE'],
    'chomage': ['FRANCE TRAVAIL', 'POLE EMPLOI', 'ALLOCATION', 'ARE ', 'INDEMNITE'],
    'pension': ['PENSION', 'RETRAITE', 'CNAV', 'CARSAT', 'IRCEM'],
    'revenus_divers': ['VIREMENT', 'REMBOURSEMENT', 'PAIEMENT'],
}


def detect_frequency(avg_diff_days: float) -> Tuple[bool, str]:
    """Detect recurring frequency pattern."""
    if FREQUENCY_MONTHLY_MIN <= avg_diff_days <= FREQUENCY_MONTHLY_MAX:
        return True, FREQUENCY_MONTHLY_LABEL
    elif FREQUENCY_QUARTERLY_MIN <= avg_diff_days <= FREQUENCY_QUARTERLY_MAX:
        return True, FREQUENCY_QUARTERLY_LABEL
    elif FREQUENCY_ANNUAL_MIN <= avg_diff_days <= FREQUENCY_ANNUAL_MAX:
        return True, FREQUENCY_ANNUAL_LABEL
    return False, ""


def extract_base_label(label: str) -> str:
    """
    Extract a normalized base label for grouping similar transactions.
    More aggressive than clean_label to group variations.
    """
    # Upper case for consistency
    base = label.upper()
    
    # Remove dates (various formats)
    base = re.sub(r'\d{2}[/.]\d{2}[/.]\d{2,4}', '', base)
    base = re.sub(r'\d{2}/\d{2}', '', base)
    
    # Remove standalone numbers (references, amounts)
    base = re.sub(r'\b\d{3,}\b', '', base)
    
    # Remove common bank prefixes
    base = re.sub(r'\b(CARTE|CB|PRLV|SEPA|VIR|VIREMENT)\b\*?\s*', '', base)
    
    # Clean up
    base = re.sub(r'\s+', ' ', base).strip()
    
    return base


def detect_income_pattern(label: str) -> Tuple[bool, str]:
    """
    Check if label matches known income patterns.
    Returns (is_income, income_type)
    """
    label_upper = label.upper()
    
    for income_type, patterns in INCOME_PATTERNS.items():
        for pattern in patterns:
            if pattern in label_upper:
                return True, income_type
    
    return False, ""


def detect_recurring_payments_v2(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enhanced recurrence detection with:
    - Better income detection (salaries, unemployment benefits)
    - Transaction IDs for proper drill-down
    - Category grouping option
    """
    if df.empty:
        return pd.DataFrame()
    
    # Work on a copy and exclude internal transfers
    data = df[~df['category_validated'].isin(['Virement Interne', 'Hors Budget'])].copy()
    
    if data.empty:
        return pd.DataFrame()
    
    # Ensure date is datetime
    data['date'] = pd.to_datetime(data['date'])
    
    # Create grouping keys
    data['clean_label'] = data['label'].apply(clean_label)
    data['base_label'] = data['label'].apply(extract_base_label)
    
    # Check for income patterns
    data['income_check'] = data['label'].apply(lambda x: detect_income_pattern(x)[0])
    data['income_type'] = data['label'].apply(lambda x: detect_income_pattern(x)[1])
    
    recurring_items = []
    
    # Strategy 1: Group by clean_label (existing behavior)
    grouped = data.groupby('clean_label')
    
    for label, group in grouped:
        item = _analyze_group(label, group, grouping_key='clean_label')
        if item:
            recurring_items.append(item)
    
    # Strategy 2: For incomes, also try base_label grouping (more aggressive)
    income_data = data[data['income_check'] == True]
    if not income_data.empty:
        income_grouped = income_data.groupby('base_label')
        
        for label, group in income_grouped:
            # Skip if we already found this group
            if not any(item['label'] == label for item in recurring_items):
                item = _analyze_group(label, group, grouping_key='base_label', is_income=True)
                if item:
                    recurring_items.append(item)
    
    if not recurring_items:
        return pd.DataFrame(columns=[
            "label", "avg_amount", "frequency_days", "frequency_label", 
            "count", "last_date", "category", "is_subscription_candidate", 
            "variability", "transaction_ids", "grouping_key"
        ])
    
    result_df = pd.DataFrame(recurring_items)
    return result_df.sort_values(by='avg_amount', ascending=False)


def _analyze_group(label: str, group: pd.DataFrame, grouping_key: str, is_income: bool = False) -> Dict:
    """Analyze a group of transactions for recurrence patterns."""
    
    if len(group) < MIN_OCCURRENCES_FOR_RECURRING:
        return None
    
    # Check amounts consistency
    amounts = group['amount'].tolist()
    amounts_std = group['amount'].std()
    avg_amount = group['amount'].mean()
    
    # Skip if amounts vary too much (unless it's an income)
    if avg_amount != 0:
        variability_ratio = amounts_std / abs(avg_amount)
    else:
        variability_ratio = 0
    
    # For incomes, allow more variability
    tolerance = AMOUNT_TOLERANCE_STANDARD * 2 if is_income else AMOUNT_TOLERANCE_STANDARD
    is_consistent_amount = variability_ratio < tolerance
    
    # Check Periodicity
    dates = group['date'].sort_values()
    diffs = dates.diff().dropna()
    
    if len(diffs) == 0:
        return None
    
    avg_diff_days = diffs.dt.days.mean()
    
    # Detect frequency pattern
    is_recurring, freq_label = detect_frequency(avg_diff_days)
    
    # For incomes, also accept monthly patterns with more flexibility
    if is_income and not is_recurring:
        if 20 <= avg_diff_days <= 40:  # Broader range for incomes
            is_recurring = True
            freq_label = FREQUENCY_MONTHLY_LABEL
    
    if not is_recurring:
        return None
    
    # Determine category (use most common)
    current_cat = group['category_validated'].mode().iloc[0] if not group['category_validated'].empty else 'Non catégorisé'
    
    # Get transaction IDs for drill-down
    transaction_ids = group['id'].tolist()
    
    # Get sample labels (original variations)
    sample_labels = group['label'].unique()[:3].tolist()
    
    return {
        "label": label,
        "avg_amount": round(avg_amount, 2),
        "frequency_days": round(avg_diff_days, 1),
        "frequency_label": freq_label,
        "count": len(group),
        "last_date": group['date'].max().date(),
        "category": current_cat,
        "is_subscription_candidate": True,
        "variability": "Variable" if variability_ratio > AMOUNT_TOLERANCE_FIXED_THRESHOLD else "Fixe",
        "transaction_ids": transaction_ids,
        "grouping_key": grouping_key,
        "sample_labels": sample_labels,
        "is_income": is_income or avg_amount > 0
    }


def group_by_category(recurring_df: pd.DataFrame) -> pd.DataFrame:
    """
    Group recurring items by category with aggregation.
    """
    if recurring_df.empty:
        return pd.DataFrame()
    
    grouped = recurring_df.groupby('category').agg({
        'avg_amount': 'sum',
        'count': 'sum',
        'label': lambda x: list(x),
        'transaction_ids': lambda x: [item for sublist in x for item in sublist],
        'frequency_label': lambda x: x.mode().iloc[0] if not x.empty else 'Inconnu'
    }).reset_index()
    
    grouped.columns = ['category', 'total_amount', 'total_occurrences', 'labels', 'all_transaction_ids', 'dominant_frequency']
    
    return grouped


def get_recurring_by_tags(df: pd.DataFrame, recurring_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze recurring payments grouped by tags.
    """
    if recurring_df.empty or df.empty:
        return pd.DataFrame()
    
    # Get all transaction IDs from recurring items
    all_recurring_ids = []
    for ids in recurring_df['transaction_ids']:
        all_recurring_ids.extend(ids)
    
    # Filter transactions
    recurring_tx = df[df['id'].isin(all_recurring_ids)].copy()
    
    if recurring_tx.empty:
        return pd.DataFrame()
    
    # Extract tags
    recurring_tx['tag_list'] = recurring_tx['tags'].apply(
        lambda x: [t.strip() for t in str(x).split(',') if t.strip()] if pd.notna(x) else []
    )
    
    # Explode tags
    tags_exploded = recurring_tx.explode('tag_list')
    
    if tags_exploded.empty:
        return pd.DataFrame()
    
    # Group by tag
    grouped = tags_exploded.groupby('tag_list').agg({
        'amount': ['sum', 'mean', 'count'],
        'id': lambda x: list(x.unique())
    }).reset_index()
    
    grouped.columns = ['tag', 'total_amount', 'avg_amount', 'count', 'transaction_ids']
    
    return grouped.sort_values('total_amount', ascending=True)


def analyze_recurrence_summary(df: pd.DataFrame, recurring_df: pd.DataFrame) -> Dict:
    """
    Generate summary statistics for recurring payments.
    """
    if df.empty or recurring_df.empty:
        return {}
    
    total_recurring = len(recurring_df)
    expenses = recurring_df[recurring_df['avg_amount'] < 0]
    incomes = recurring_df[recurring_df['avg_amount'] > 0]
    
    summary = {
        'total_detected': total_recurring,
        'expense_count': len(expenses),
        'income_count': len(incomes),
        'monthly_expense_total': abs(expenses[expenses['frequency_label'] == FREQUENCY_MONTHLY_LABEL]['avg_amount'].sum()) if not expenses.empty else 0,
        'monthly_income_total': incomes[incomes['frequency_label'] == FREQUENCY_MONTHLY_LABEL]['avg_amount'].sum() if not incomes.empty else 0,
        'categories_covered': recurring_df['category'].nunique(),
        'fixed_count': len(recurring_df[recurring_df['variability'] == 'Fixe']),
        'variable_count': len(recurring_df[recurring_df['variability'] == 'Variable']),
    }
    
    return summary
