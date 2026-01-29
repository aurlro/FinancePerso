"""
Anomaly Detection for Transaction Amounts.

Identifies transactions with unusual amounts compared to historical patterns.
"""
import pandas as pd
import numpy as np
from modules.utils import clean_label
from modules.logger import logger


def detect_amount_anomalies(df: pd.DataFrame, threshold_sigma: float = 2.0) -> list:
    """
    Detect transactions with anomalous amounts based on historical patterns.
    
    Args:
        df: DataFrame with transactions (must have 'label', 'amount', 'id', 'date', 'category_validated')
        threshold_sigma: Number of standard deviations to consider anomalous (default: 2.0)
        
    Returns:
        List of anomaly dictionaries with keys:
            - type: "Anomalie Montant"
            - label: Clean label
            - details: Description of the anomaly
            - rows: DataFrame of anomalous transactions
            - expected_range: Tuple (mean, std)
            
    Example:
        anomalies = detect_amount_anomalies(df)
        for anomaly in anomalies:
            print(f"{anomaly['label']}: {anomaly['details']}")
    """
    if df.empty:
        return []
    
    # Work only with expenses (negative amounts) and non-ignored ones
    df_exp = df[df['amount'] < 0].copy()
    
    # Exclude transactions with 'ignore_anomaly' tag
    if 'tags' in df_exp.columns:
        df_exp = df_exp[~df_exp['tags'].fillna('').str.contains('ignore_anomaly')]
        
    if df_exp.empty:
        return []
    
    # Use absolute values for analysis
    df_exp['abs_amount'] = df_exp['amount'].abs()
    df_exp['clean'] = df_exp['label'].apply(clean_label)
    
    # Group by clean label and calculate statistics
    stats = df_exp.groupby('clean')['abs_amount'].agg(['mean', 'std', 'count']).reset_index()
    
    # Only consider labels with at least 3 occurrences
    stats = stats[stats['count'] >= 3]
    
    anomalies = []
    
    for _, stat_row in stats.iterrows():
        label_clean = stat_row['clean']
        mean_amt = stat_row['mean']
        std_amt = stat_row['std']
        
        # Skip if std is too small or NaN (constant amounts)
        if pd.isna(std_amt) or std_amt < 1.0:
            continue
        
        # Find transactions for this label
        label_txs = df_exp[df_exp['clean'] == label_clean].copy()
        
        # Calculate z-score for each transaction
        label_txs['z_score'] = (label_txs['abs_amount'] - mean_amt) / std_amt
        
        # Identify anomalies (|z| > threshold)
        anomalous_txs = label_txs[label_txs['z_score'].abs() > threshold_sigma]
        
        if not anomalous_txs.empty:
            # Prepare output
            anomaly_rows = anomalous_txs[['id', 'date', 'label', 'amount', 'category_validated']].copy()
            
            anomalies.append({
                "type": "Anomalie Montant",
                "label": label_clean,
                "details": f"Montant inhabituel détecté. Moyenne: {mean_amt:.2f}€ (±{std_amt:.2f}€)",
                "rows": anomaly_rows,
                "expected_range": (mean_amt, std_amt),
                "severity": "high" if anomalous_txs['z_score'].abs().max() > 3.0 else "medium"
            })
    
    # Sort by severity
    anomalies.sort(key=lambda x: x['severity'], reverse=True)
    
    logger.info(f"Detected {len(anomalies)} amount anomalies")
    return anomalies
