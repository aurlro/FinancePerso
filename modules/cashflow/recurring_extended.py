# -*- coding: utf-8 -*-
"""
Extensions pour la gestion des dépenses récurrentes.
"""

from datetime import date
from typing import Any

import pandas as pd


def identify_recurring_expenses(history: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Identifie les dépenses récurrentes dans l'historique.
    
    Args:
        history: DataFrame avec 'date', 'label', 'amount'
    
    Returns:
        Liste des dépenses récurrentes détectées
    """
    if history.empty or len(history) < 3:
        return []
    
    recurring = []
    
    # Grouper par label similaire
    history['label_normalized'] = history['label'].str.upper().str.strip()
    grouped = history.groupby('label_normalized')
    
    for label, group in grouped:
        if len(group) >= 2:  # Au moins 2 occurrences
            # Vérifier si c'est mensuel
            dates = pd.to_datetime(group['date']).sort_values()
            if len(dates) >= 2:
                avg_days = (dates.diff().mean()).days
                if 25 <= avg_days <= 35:  # Environ mensuel
                    recurring.append({
                        "label": label,
                        "amount": group['amount'].mean(),
                        "frequency": "monthly",
                        "count": len(group),
                    })
    
    return recurring


def project_recurring_expenses(
    recurring: list[dict],
    start_date: date,
    months: int = 3,
) -> list[dict[str, Any]]:
    """
    Projette les dépenses récurrentes futures.
    
    Args:
        recurring: Liste des dépenses récurrentes
        start_date: Date de début
        months: Nombre de mois à projeter
    
    Returns:
        Liste des projections
    """
    projections = []
    
    for expense in recurring:
        for i in range(months):
            from datetime import timedelta
            
            month_date = date(
                start_date.year + (start_date.month + i - 1) // 12,
                (start_date.month + i - 1) % 12 + 1,
                min(start_date.day, 28)  # Éviter les problèmes de fin de mois
            )
            
            projections.append({
                "label": expense.get('label', 'Unknown'),
                "amount": expense.get('amount', 0),
                "date": month_date,
                "type": "recurring",
            })
    
    return projections


def analyze_expense_trends(
    history: pd.DataFrame,
    months: int = 6,
) -> dict[str, Any]:
    """
    Analyse les tendances des dépenses.
    
    Args:
        history: DataFrame avec 'date' et 'amount'
        months: Nombre de mois à analyser
    
    Returns:
        Dict avec tendances
    """
    if history.empty:
        return {"trend": "unknown", "change_percent": 0}
    
    history['date'] = pd.to_datetime(history['date'])
    history['month'] = history['date'].dt.to_period('M')
    
    monthly = history.groupby('month')['amount'].sum()
    
    if len(monthly) < 2:
        return {"trend": "stable", "change_percent": 0}
    
    # Calculer la tendance
    first_month = monthly.iloc[0]
    last_month = monthly.iloc[-1]
    
    if first_month == 0:
        change_percent = 0
    else:
        change_percent = ((last_month - first_month) / abs(first_month)) * 100
    
    if change_percent > 10:
        trend = "increasing"
    elif change_percent < -10:
        trend = "decreasing"
    else:
        trend = "stable"
    
    return {
        "trend": trend,
        "change_percent": round(change_percent, 2),
        "monthly_average": monthly.mean(),
    }
