# -*- coding: utf-8 -*-
"""
Alertes de trésorerie.
"""

from typing import Any


def generate_cashflow_alerts(
    current_balance: float,
    predicted_lowest_balance: float,
    overdraft_risk: bool = False,
) -> list[dict[str, Any]]:
    """
    Génère des alertes de trésorerie.
    
    Args:
        current_balance: Solde actuel
        predicted_lowest_balance: Solde le plus bas prédit
        overdraft_risk: Risque de découvert
    
    Returns:
        Liste des alertes
    """
    alerts = []
    
    if overdraft_risk or predicted_lowest_balance < 0:
        alerts.append({
            "level": "error",
            "message": "⚠️ Risque de découvert détecté !",
            "action": "Réduire les dépenses ou augmenter les revenus",
        })
    elif predicted_lowest_balance < 100:
        alerts.append({
            "level": "warning",
            "message": "⚠️ Solde très faible prévu (< 100€)",
            "action": "Surveiller les dépenses",
        })
    elif predicted_lowest_balance < 500:
        alerts.append({
            "level": "info",
            "message": "ℹ️ Solde faible prévu (< 500€)",
            "action": "Prévoir un revenu supplémentaire",
        })
    
    return alerts


def check_budget_alert(
    current_spending: float,
    budget_limit: float,
    alert_threshold: float = 0.8,
) -> dict[str, Any] | None:
    """
    Vérifie si une alerte de budget est nécessaire.
    
    Args:
        current_spending: Dépenses actuelles
        budget_limit: Limite du budget
        alert_threshold: Seuil d'alerte (0-1)
    
    Returns:
        Alerte ou None
    """
    if budget_limit <= 0:
        return None
    
    ratio = current_spending / budget_limit
    
    if ratio >= 1.0:
        return {
            "level": "error",
            "message": f"💸 Budget dépassé ({ratio*100:.0f}%)",
        }
    elif ratio >= alert_threshold:
        return {
            "level": "warning",
            "message": f"⚠️ Budget presque épuisé ({ratio*100:.0f}%)",
        }
    
    return None
