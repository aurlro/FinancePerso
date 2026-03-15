# -*- coding: utf-8 -*-
"""
Projections de patrimoine.
"""

from typing import Any


def project_wealth(
    current_wealth: float,
    monthly_savings: float,
    annual_return_rate: float,
    years: int = 10,
) -> list[dict[str, Any]]:
    """
    Projette l'évolution du patrimoine.
    
    Args:
        current_wealth: Patrimoine actuel
        monthly_savings: Épargne mensuelle
        annual_return_rate: Taux de rendement annuel (ex: 0.05 pour 5%)
        years: Nombre d'années
    
    Returns:
        Liste des projections annuelles
    """
    projections = []
    balance = current_wealth
    
    for year in range(years + 1):
        projections.append({
            "year": year,
            "total": round(balance, 2),
            "contributions": monthly_savings * 12 * year,
            "returns": round(balance - current_wealth - monthly_savings * 12 * year, 2),
        })
        
        # Appliquer le rendement et ajouter l'épargne
        balance = balance * (1 + annual_return_rate) + monthly_savings * 12
    
    return projections


def calculate_compound_growth(
    principal: float,
    monthly_contribution: float,
    annual_rate: float,
    years: int,
) -> float:
    """
    Calcule la croissance composée.
    
    Args:
        principal: Capital initial
        monthly_contribution: Contribution mensuelle
        annual_rate: Taux annuel
        years: Années
    
    Returns:
        Valeur finale
    """
    monthly_rate = annual_rate / 12
    months = years * 12
    
    # Formule du compound interest avec contributions
    if monthly_rate == 0:
        return principal + monthly_contribution * months
    
    future_value = principal * (1 + monthly_rate) ** months
    future_value += monthly_contribution * (((1 + monthly_rate) ** months - 1) / monthly_rate)
    
    return round(future_value, 2)


def project_wealth_breakdown(
    assets: dict[str, dict],
    monthly_savings: float,
    years: int = 5,
) -> list[dict[str, Any]]:
    """
    Projette avec détail par type d'actif.
    
    Args:
        assets: Dict avec type -> {value, growth_rate}
        monthly_savings: Épargne mensuelle
        years: Années
    
    Returns:
        Liste des projections
    """
    projections = []
    
    # Initialiser les soldes par type
    balances = {
        asset_type: info.get('value', 0)
        for asset_type, info in assets.items()
    }
    
    for year in range(years + 1):
        year_data = {"year": year}
        total = 0
        
        for asset_type, balance in balances.items():
            year_data[asset_type] = round(balance, 2)
            total += balance
        
        year_data["total"] = round(total, 2)
        projections.append(year_data)
        
        # Mettre à jour les soldes pour l'année suivante
        for asset_type in balances:
            growth_rate = assets.get(asset_type, {}).get('growth_rate', 0)
            balances[asset_type] = balances[asset_type] * (1 + growth_rate)
        
        # Distribuer l'épargne mensuelle (simplifié)
        if assets:
            savings_per_asset = monthly_savings * 12 / len(assets)
            for asset_type in balances:
                balances[asset_type] += savings_per_asset
    
    return projections


def calculate_fire_number(
    annual_expenses: float,
    withdrawal_rate: float = 0.04,
) -> float:
    """
    Calcule le nombre FIRE (Financial Independence Retire Early).
    
    Args:
        annual_expenses: Dépenses annuelles
        withdrawal_rate: Taux de retrait sécurisé (4% par défaut)
    
    Returns:
        Montant nécessaire pour la retraite
    """
    return annual_expenses / withdrawal_rate
