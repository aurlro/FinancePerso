# -*- coding: utf-8 -*-
"""
Préparation des données pour la visualisation de trésorerie.
"""

from datetime import date
from typing import Any


def prepare_timeline_data(
    current_balance: float,
    predictions: list[dict],
) -> dict[str, Any]:
    """
    Prépare les données pour une timeline.
    
    Args:
        current_balance: Solde actuel
        predictions: Liste des prédictions
    
    Returns:
        Dict avec dates et soldes
    """
    dates = []
    balances = []
    
    # Ajouter le point de départ
    dates.append(date.today().isoformat())
    balances.append(current_balance)
    
    # Ajouter les prédictions
    for pred in predictions:
        dates.append(pred.get('date', '').isoformat() if isinstance(pred.get('date'), date) else str(pred.get('date')))
        balances.append(pred.get('balance', 0))
    
    return {
        "dates": dates,
        "balances": balances,
    }


def identify_critical_points(
    predictions: list[dict],
) -> list[dict[str, Any]]:
    """
    Identifie les points critiques sur une timeline.
    
    Args:
        predictions: Liste des prédictions
    
    Returns:
        Liste des points critiques
    """
    critical = []
    
    for pred in predictions:
        balance = pred.get('balance', 0)
        pred_date = pred.get('date')
        
        if balance < 0:
            critical.append({
                "date": pred_date,
                "type": "overdraft",
                "balance": balance,
                "severity": "high",
            })
        elif balance < 100:
            critical.append({
                "date": pred_date,
                "type": "low_balance",
                "balance": balance,
                "severity": "medium",
            })
    
    return critical


def format_cashflow_for_chart(
    predictions: list[dict],
) -> dict[str, Any]:
    """
    Formate les prédictions pour un graphique.
    
    Args:
        predictions: Liste des prédictions
    
    Returns:
        Dict formaté pour charting
    """
    labels = []
    data = []
    
    for pred in predictions:
        date_val = pred.get('date')
        if isinstance(date_val, date):
            labels.append(date_val.strftime('%b %Y'))
        else:
            labels.append(str(date_val))
        
        data.append(pred.get('balance', 0))
    
    return {
        "labels": labels,
        "datasets": [{
            "label": "Solde prévisionnel",
            "data": data,
        }],
    }
