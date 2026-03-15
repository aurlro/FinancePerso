# -*- coding: utf-8 -*-
"""
Calculateur de patrimoine.
"""

from typing import Any


def calculate_total_wealth(assets: list[dict]) -> float:
    """
    Calcule la valeur totale du patrimoine.
    
    Args:
        assets: Liste des actifs avec 'value'
    
    Returns:
        Valeur totale
    """
    return sum(asset.get('value', 0) for asset in assets)


def calculate_net_worth(assets: list[dict], liabilities: list[dict]) -> float:
    """
    Calcule le patrimoine net (actifs - dettes).
    
    Args:
        assets: Liste des actifs
        liabilities: Liste des dettes
    
    Returns:
        Patrimoine net
    """
    total_assets = calculate_total_wealth(assets)
    total_liabilities = sum(liability.get('value', 0) for liability in liabilities)
    return total_assets - total_liabilities


def calculate_wealth_by_category(assets: list[dict]) -> dict[str, float]:
    """
    Calcule la répartition par catégorie.
    
    Args:
        assets: Liste des actifs avec 'category' et 'value'
    
    Returns:
        Dict category -> value
    """
    by_category = {}
    
    for asset in assets:
        category = asset.get('category', 'Autre')
        value = asset.get('value', 0)
        by_category[category] = by_category.get(category, 0) + value
    
    return by_category


def calculate_wealth_distribution(assets: list[dict]) -> dict[str, float]:
    """
    Calcule la distribution en pourcentage.
    
    Args:
        assets: Liste des actifs
    
    Returns:
        Dict category -> percentage
    """
    by_category = calculate_wealth_by_category(assets)
    total = sum(by_category.values())
    
    if total == 0:
        return {cat: 0 for cat in by_category}
    
    return {
        cat: round(value / total * 100, 2)
        for cat, value in by_category.items()
    }
