# -*- coding: utf-8 -*-
"""
Extensions du module de prédiction de trésorerie.

Fonctions additionnelles pour les tests.
"""

from datetime import date, datetime, timedelta
from typing import Any

import pandas as pd

from modules.logger import logger


def predict_balance(
    current_balance: float,
    daily_expenses_avg: float,
    days: int = 30,
) -> dict[str, Any]:
    """
    Prédit le solde futur basique.
    
    Args:
        current_balance: Solde actuel
        daily_expenses_avg: Dépenses quotidiennes moyennes
        days: Nombre de jours à prédire
    
    Returns:
        Dict avec final_balance et trend
    """
    final_balance = current_balance - (daily_expenses_avg * days)
    
    trend = "stable"
    if final_balance > current_balance * 1.05:
        trend = "increasing"
    elif final_balance < current_balance * 0.95:
        trend = "decreasing"
    
    return {
        "final_balance": final_balance,
        "trend": trend,
        "days": days,
    }


def predict_balance_with_income(
    current_balance: float,
    daily_expenses_avg: float,
    monthly_income: float,
    days: int = 30,
) -> dict[str, Any]:
    """
    Prédit le solde avec revenus réguliers.
    
    Args:
        current_balance: Solde actuel
        daily_expenses_avg: Dépenses quotidiennes moyennes
        monthly_income: Revenus mensuels
        days: Nombre de jours à prédire
    
    Returns:
        Dict avec final_balance et trend
    """
    daily_income = monthly_income / 30
    daily_net = daily_income - daily_expenses_avg
    final_balance = current_balance + (daily_net * days)
    
    trend = "stable"
    if daily_net > 0:
        trend = "increasing"
    elif daily_net < 0:
        trend = "decreasing"
    
    return {
        "final_balance": final_balance,
        "trend": trend,
        "daily_net": daily_net,
    }


def predict_balance_from_history(
    current_balance: float,
    history: pd.DataFrame,
    days: int = 30,
) -> dict[str, Any]:
    """
    Prédit le solde basé sur l'historique.
    
    Args:
        current_balance: Solde actuel
        history: DataFrame avec colonnes 'date' et 'amount'
        days: Nombre de jours à prédire
    
    Returns:
        Dict avec final_balance
    """
    if history.empty:
        return {"final_balance": current_balance}
    
    # Calculer la moyenne quotidienne
    daily_avg = history['amount'].mean()
    final_balance = current_balance + (daily_avg * days)
    
    return {"final_balance": final_balance}


def predict_balance_with_recurring(
    current_balance: float,
    recurring_expenses: list[dict],
    days: int = 30,
) -> dict[str, Any]:
    """
    Prédit le solde avec dépenses récurrentes.
    
    Args:
        current_balance: Solde actuel
        recurring_expenses: Liste des dépenses récurrentes
        days: Nombre de jours à prédire
    
    Returns:
        Dict avec final_balance
    """
    total_recurring = sum(expense.get('amount', 0) for expense in recurring_expenses)
    final_balance = current_balance + total_recurring
    
    return {"final_balance": final_balance}
