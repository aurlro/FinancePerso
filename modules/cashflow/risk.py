# -*- coding: utf-8 -*-
"""
Détection de risques de trésorerie.
"""

from datetime import date, datetime, timedelta
from typing import Any

import pandas as pd


def detect_overdraft_risk(
    current_balance: float,
    future_transactions: pd.DataFrame,
) -> dict[str, Any]:
    """
    Détecte un risque de découvert.
    
    Args:
        current_balance: Solde actuel
        future_transactions: DataFrame des transactions futures
    
    Returns:
        Dict avec has_risk, risk_date, recommended_action
    """
    if future_transactions.empty:
        return {
            "has_risk": False,
            "risk_date": None,
            "recommended_action": None,
        }
    
    # Calculer le solde cumulé
    balance = current_balance
    risk_date = None
    
    for _, tx in future_transactions.iterrows():
        balance += tx.get('amount', 0)
        if balance < 0 and risk_date is None:
            risk_date = tx.get('date')
    
    has_risk = balance < 0
    
    return {
        "has_risk": has_risk,
        "risk_date": risk_date,
        "recommended_action": "Réduire les dépenses" if has_risk else None,
    }


def calculate_overdraft_date(
    current_balance: float,
    daily_expense_rate: float,
    start_date: date | None = None,
) -> date | None:
    """
    Calcule la date de découvert potentielle.
    
    Args:
        current_balance: Solde actuel
        daily_expense_rate: Taux de dépenses quotidiennes
        start_date: Date de départ
    
    Returns:
        Date de découvert ou None si pas de risque
    """
    if daily_expense_rate <= 0 or current_balance <= 0:
        return None
    
    days_until_overdraft = int(current_balance / daily_expense_rate)
    start = start_date or date.today()
    
    return start + timedelta(days=days_until_overdraft)


def calculate_risk_score(
    current_balance: float,
    monthly_expenses: float,
) -> int:
    """
    Calcule un score de risque (0-100).
    
    Args:
        current_balance: Solde actuel
        monthly_expenses: Dépenses mensuelles
    
    Returns:
        Score de risque (0 = faible, 100 = élevé)
    """
    if monthly_expenses == 0:
        return 0
    
    months_of_expenses = current_balance / monthly_expenses
    
    if months_of_expenses >= 3:
        return 0
    elif months_of_expenses >= 1:
        return 30
    elif months_of_expenses >= 0.5:
        return 60
    else:
        return 100
