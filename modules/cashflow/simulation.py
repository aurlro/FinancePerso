# -*- coding: utf-8 -*-
"""
Simulation de scénarios de trésorerie.
"""

from typing import Any


def simulate_scenario(
    current_balance: float,
    daily_expenses_avg: float,
    days: int = 30,
    expense_reduction_percent: float = 0,
    extra_income: float = 0,
) -> dict[str, Any]:
    """
    Simule un scénario de trésorerie.
    
    Args:
        current_balance: Solde actuel
        daily_expenses_avg: Dépenses quotidiennes moyennes
        days: Nombre de jours
        expense_reduction_percent: Pourcentage de réduction des dépenses
        extra_income: Revenu supplémentaire
    
    Returns:
        Dict avec final_balance et autres métriques
    """
    # Appliquer la réduction de dépenses
    adjusted_daily_expenses = daily_expenses_avg * (1 - expense_reduction_percent / 100)
    
    # Calculer le solde final
    total_expenses = adjusted_daily_expenses * days
    final_balance = current_balance - total_expenses + extra_income
    
    return {
        "final_balance": final_balance,
        "total_expenses": total_expenses,
        "extra_income": extra_income,
        "savings": daily_expenses_avg * days - total_expenses,
    }


def compare_scenarios(
    current_balance: float,
    daily_expenses_avg: float,
    scenarios: list[dict],
    days: int = 30,
) -> list[dict[str, Any]]:
    """
    Compare plusieurs scénarios.
    
    Args:
        current_balance: Solde actuel
        daily_expenses_avg: Dépenses quotidiennes moyennes
        scenarios: Liste des scénarios à comparer
        days: Nombre de jours
    
    Returns:
        Liste des résultats de simulation
    """
    results = []
    
    for scenario in scenarios:
        result = simulate_scenario(
            current_balance=current_balance,
            daily_expenses_avg=daily_expenses_avg,
            days=days,
            expense_reduction_percent=scenario.get('expense_reduction', 0),
            extra_income=scenario.get('extra_income', 0),
        )
        result['name'] = scenario.get('name', 'Unnamed')
        results.append(result)
    
    return results
