"""
Intégration Patrimoine × Monte Carlo - Projections Patrimoniales
=================================================================

Ce module intègre le WealthManager (Phase 5) avec le moteur Monte Carlo (Phase 4)
pour projeter l'évolution du patrimoine net total.

Au lieu de projeter uniquement le cash, cette intégration :
1. Agrège tous les actifs (cash, immo, financier, crypto)
2. Applique des rendements différenciés par classe d'actif
3. Projette la dette (amortissement des crédits)
4. Calcule le patrimoine net futur

Usage:
    from modules.wealth.wealth_projection import project_wealth_evolution
    from src import WealthManager
    
    manager = WealthManager()
    # ... ajouter actifs ...
    
    projection = project_wealth_evolution(
        wealth_manager=manager,
        years=20,
        monthly_contribution=500,
    )
    
    print(f"Patrimoine dans 20 ans: €{projection['median']:,.2f}")
"""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import pandas as pd

from modules.wealth.wealth_manager import (
    WealthManager, AssetType, RealEstateAsset, FinancialAsset, 
    CryptoAsset, Liability, AssetLiquidity,
)
from modules.wealth.math_engine import MonteCarloSimulator, ScenarioType


# Paramètres de rendement par défaut pour chaque classe d'actif
DEFAULT_ASSET_RETURNS = {
    AssetType.CASH: {'mu': 0.025, 'sigma': 0.005},           # Livret ~2.5%
    AssetType.REAL_ESTATE: {'mu': 0.035, 'sigma': 0.08},     # Immo ~3.5%
    AssetType.SECURITIES: {'mu': 0.07, 'sigma': 0.15},       # Actions ~7%
    AssetType.LIFE_INSURANCE: {'mu': 0.04, 'sigma': 0.05},   # Assurance vie ~4%
    AssetType.CRYPTO: {'mu': 0.15, 'sigma': 0.60},           # Crypto ~15%
    AssetType.MEAL_VOUCHERS: {'mu': 0.0, 'sigma': 0.0},      # Titres resto = inflation
    AssetType.RETIREMENT: {'mu': 0.05, 'sigma': 0.08},       # PER ~5%
    AssetType.OTHER: {'mu': 0.03, 'sigma': 0.05},            # Autres ~3%
}


@dataclass
class AssetProjection:
    """
    Projection d'une classe d'actif spécifique.
    
    Attributes:
        asset_type: Type d'actif
        current_value: Valeur actuelle
        projected_values: Trajectoires projetées (n_simulations, n_months)
        time_points: Points temporels
        statistics: Statistiques (median, percentiles)
    """
    asset_type: AssetType
    current_value: float
    projected_values: np.ndarray
    time_points: np.ndarray
    statistics: Dict[str, np.ndarray]


@dataclass
class WealthProjectionResult:
    """
    Résultat complet de la projection patrimoniale.
    
    Attributes:
        total_net_worth_paths: Trajectoires du patrimoine net total
        asset_projections: Projections par classe d'actif
        debt_paths: Évolution de la dette
        time_points: Points temporels (en années)
        statistics: Statistiques globales
        initial_net_worth: Patrimoine net initial
        monthly_contribution: Versement mensuel
    """
    total_net_worth_paths: np.ndarray
    asset_projections: Dict[AssetType, AssetProjection]
    debt_paths: np.ndarray
    time_points: np.ndarray
    statistics: Dict[str, Any]
    initial_net_worth: float
    monthly_contribution: float
    years: int
    
    def get_net_worth_at_year(self, year: int, percentile: float = 50) -> float:
        """
        Retourne le patrimoine net à une année donnée.
        
        Args:
            year: Année (0 = aujourd'hui)
            percentile: Percentile souhaité (50 = médiane)
            
        Returns:
            Valeur du patrimoine net
        """
        month_idx = year * 12
        if month_idx >= len(self.time_points):
            month_idx = len(self.time_points) - 1
        
        return float(np.percentile(self.total_net_worth_paths[:, month_idx], percentile))
    
    def get_probability_of_target(self, target_amount: float, by_year: int) -> float:
        """
        Calcule la probabilité d'atteindre un objectif.
        
        Args:
            target_amount: Montant cible
            by_year: Année cible
            
        Returns:
            Probabilité entre 0 et 1
        """
        month_idx = by_year * 12
        if month_idx >= len(self.time_points):
            month_idx = len(self.time_points) - 1
        
        values_at_year = self.total_net_worth_paths[:, month_idx]
        successes = np.sum(values_at_year >= target_amount)
        return successes / len(values_at_year)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le résultat en dictionnaire."""
        return {
            'initial_net_worth': self.initial_net_worth,
            'final_median': float(np.median(self.total_net_worth_paths[:, -1])),
            'final_percentile_5': float(np.percentile(self.total_net_worth_paths[:, -1], 5)),
            'final_percentile_95': float(np.percentile(self.total_net_worth_paths[:, -1], 95)),
            'years': self.years,
            'monthly_contribution': self.monthly_contribution,
        }


def project_asset_class(
    current_value: float,
    asset_type: AssetType,
    years: int,
    monthly_contribution: float = 0.0,
    n_simulations: int = 1000,
    custom_returns: Optional[Dict] = None,
) -> AssetProjection:
    """
    Projette l'évolution d'une classe d'actif.
    
    Args:
        current_value: Valeur actuelle
        asset_type: Type d'actif
        years: Horizon de projection
        monthly_contribution: Versement mensuel
        n_simulations: Nombre de simulations
        custom_returns: Paramètres de rendement personnalisés
        
    Returns:
        Projection de l'actif
    """
    # Récupérer les paramètres de rendement
    if custom_returns and asset_type in custom_returns:
        params = custom_returns[asset_type]
    else:
        params = DEFAULT_ASSET_RETURNS.get(asset_type, {'mu': 0.03, 'sigma': 0.05})
    
    # Créer le simulateur
    simulator = MonteCarloSimulator(
        initial_capital=current_value,
        monthly_contribution=monthly_contribution,
        annual_return=params['mu'],
        volatility=params['sigma'],
        years=years,
    )
    
    # Lancer la simulation
    result = simulator.run_simulation(n_simulations=n_simulations)
    
    # Calculer les statistiques
    statistics = {
        'median': np.median(result.simulations, axis=0),
        'percentile_5': np.percentile(result.simulations, 5, axis=0),
        'percentile_25': np.percentile(result.simulations, 25, axis=0),
        'percentile_75': np.percentile(result.simulations, 75, axis=0),
        'percentile_95': np.percentile(result.simulations, 95, axis=0),
    }
    
    return AssetProjection(
        asset_type=asset_type,
        current_value=current_value,
        projected_values=result.simulations,
        time_points=result.time_points,
        statistics=statistics,
    )


def project_debt_evolution(
    wealth_manager: WealthManager,
    years: int,
) -> np.ndarray:
    """
    Projette l'évolution de la dette totale.
    
    Args:
        wealth_manager: Gestionnaire de patrimoine
        years: Horizon de projection
        
    Returns:
        Tableau des dettes restantes par mois
    """
    n_months = years * 12
    debt_evolution = np.zeros(n_months + 1)
    
    # Date de départ
    start_date = date.today()
    
    for month in range(n_months + 1):
        current_date = start_date + timedelta(days=30 * month)
        total_debt = 0.0
        
        # Dettes non immobilières
        for liability in wealth_manager.liabilities:
            if liability.maturity_date and current_date > liability.maturity_date:
                continue  # Dette remboursée
            total_debt += liability.remaining_amount
        
        # Crédits immobiliers
        for asset in wealth_manager.real_estate:
            if asset.mortgage:
                remaining = asset.mortgage.get_remaining_balance(current_date)
                total_debt += remaining
        
        debt_evolution[month] = total_debt
    
    return debt_evolution


def project_wealth_evolution(
    wealth_manager: WealthManager,
    years: int = 10,
    monthly_contribution: float = 500.0,
    contribution_allocation: Optional[Dict[AssetType, float]] = None,
    n_simulations: int = 1000,
    custom_returns: Optional[Dict[AssetType, Dict]] = None,
) -> WealthProjectionResult:
    """
    Projette l'évolution complète du patrimoine net.
    
    Cette fonction agrège toutes les classes d'actifs et projette
    leur évolution avec des rendements différenciés.
    
    Args:
        wealth_manager: Gestionnaire de patrimoine
        years: Horizon de projection
        monthly_monthly_contribution: Versement mensuel total
        contribution_allocation: Répartition des versements par classe
                                 (défaut: proportionnel à l'existant)
        n_simulations: Nombre de simulations Monte Carlo
        custom_returns: Paramètres de rendement personnalisés
        
    Returns:
        Résultat complet de la projection
        
    Example:
        >>> manager = WealthManager()
        >>> manager.set_cash_balance(20000)
        >>> # ... ajouter d'autres actifs ...
        >>> 
        >>> projection = project_wealth_evolution(
        ...     wealth_manager=manager,
        ...     years=20,
        ...     monthly_contribution=1000,
        ... )
        >>> 
        >>> print(f"Médiane dans 20 ans: €{projection.get_net_worth_at_year(20):,.2f}")
        >>> print(f"Proba > 500k€: {projection.get_probability_of_target(500000, 20):.1%}")
    """
    # Patrimoine net initial
    initial_net_worth = wealth_manager.get_total_net_worth()
    
    # 1. Projeter chaque classe d'actif
    asset_projections: Dict[AssetType, AssetProjection] = {}
    
    # Cash
    if wealth_manager.cash_balance > 0:
        cash_projection = project_asset_class(
            current_value=wealth_manager.cash_balance,
            asset_type=AssetType.CASH,
            years=years,
            monthly_contribution=0.0,  # Le cash est alimenté par les versements directs
            n_simulations=n_simulations,
            custom_returns=custom_returns,
        )
        asset_projections[AssetType.CASH] = cash_projection
    
    # Immobilier (valeur du bien, pas l'équité)
    real_estate_value = sum(a.current_value for a in wealth_manager.real_estate)
    if real_estate_value > 0:
        # Répartir le versement immobilier (si achat futur)
        real_estate_contribution = monthly_contribution * 0.1  # 10% pour l'immo
        
        real_estate_projection = project_asset_class(
            current_value=real_estate_value,
            asset_type=AssetType.REAL_ESTATE,
            years=years,
            monthly_contribution=real_estate_contribution,
            n_simulations=n_simulations,
            custom_returns=custom_returns,
        )
        asset_projections[AssetType.REAL_ESTATE] = real_estate_projection
    
    # Actifs financiers
    financial_value = sum(a.current_value for a in wealth_manager.financial_assets)
    if financial_value > 0:
        # Répartir les versements
        if contribution_allocation:
            financial_contribution = monthly_contribution * contribution_allocation.get(
                AssetType.SECURITIES, 0.4
            )
        else:
            financial_contribution = monthly_contribution * 0.4
        
        financial_projection = project_asset_class(
            current_value=financial_value,
            asset_type=AssetType.SECURITIES,
            years=years,
            monthly_contribution=financial_contribution,
            n_simulations=n_simulations,
            custom_returns=custom_returns,
        )
        asset_projections[AssetType.SECURITIES] = financial_projection
    
    # Crypto
    crypto_value = sum(c.current_value for c in wealth_manager.crypto_assets)
    if crypto_value > 0:
        if contribution_allocation:
            crypto_contribution = monthly_contribution * contribution_allocation.get(
                AssetType.CRYPTO, 0.1
            )
        else:
            crypto_contribution = monthly_contribution * 0.1
        
        crypto_projection = project_asset_class(
            current_value=crypto_value,
            asset_type=AssetType.CRYPTO,
            years=years,
            monthly_contribution=crypto_contribution,
            n_simulations=n_simulations,
            custom_returns=custom_returns,
        )
        asset_projections[AssetType.CRYPTO] = crypto_projection
    
    # 2. Projeter l'évolution de la dette
    debt_evolution = project_debt_evolution(wealth_manager, years)
    
    # 3. Calculer le patrimoine net total pour chaque simulation
    n_months = years * 12
    total_net_worth_paths = np.zeros((n_simulations, n_months + 1))
    
    for i, asset_proj in asset_projections.items():
        # Agréger toutes les classes d'actifs
        total_net_worth_paths += asset_proj.projected_values
    
    # Soustraire la dette
    for month in range(n_months + 1):
        total_net_worth_paths[:, month] -= debt_evolution[month]
    
    # 4. Calculer les statistiques globales
    time_points = np.arange(n_months + 1) / 12  # En années
    
    statistics = {
        'median': np.median(total_net_worth_paths, axis=0),
        'mean': np.mean(total_net_worth_paths, axis=0),
        'std': np.std(total_net_worth_paths, axis=0),
        'percentile_5': np.percentile(total_net_worth_paths, 5, axis=0),
        'percentile_25': np.percentile(total_net_worth_paths, 25, axis=0),
        'percentile_75': np.percentile(total_net_worth_paths, 75, axis=0),
        'percentile_95': np.percentile(total_net_worth_paths, 95, axis=0),
    }
    
    return WealthProjectionResult(
        total_net_worth_paths=total_net_worth_paths,
        asset_projections=asset_projections,
        debt_paths=debt_evolution,
        time_points=time_points,
        statistics=statistics,
        initial_net_worth=initial_net_worth,
        monthly_contribution=monthly_contribution,
        years=years,
    )


def compare_allocation_strategies(
    wealth_manager: WealthManager,
    years: int = 10,
    monthly_contribution: float = 500.0,
    strategies: Optional[List[Dict[str, Any]]] = None,
    n_simulations: int = 500,
) -> Dict[str, WealthProjectionResult]:
    """
    Compare différentes stratégies d'allocation.
    
    Args:
        wealth_manager: Gestionnaire de patrimoine
        years: Horizon de projection
        monthly_contribution: Versement mensuel
        strategies: Liste des stratégies à comparer
        n_simulations: Nombre de simulations
        
    Returns:
        Dict des résultats par stratégie
        
    Example:
        >>> strategies = [
        ...     {
        ...         'name': 'Conservateur',
        ...         'allocation': {AssetType.CASH: 0.3, AssetType.SECURITIES: 0.7},
        ...     },
        ...     {
        ...         'name': 'Agressif',
        ...         'allocation': {AssetType.SECURITIES: 0.6, AssetType.CRYPTO: 0.4},
        ...     },
        ... ]
        >>> results = compare_allocation_strategies(manager, strategies=strategies)
    """
    if strategies is None:
        # Stratégies par défaut
        strategies = [
            {
                'name': 'Conservateur',
                'allocation': {
                    AssetType.CASH: 0.3,
                    AssetType.SECURITIES: 0.5,
                    AssetType.CRYPTO: 0.0,
                    AssetType.REAL_ESTATE: 0.2,
                },
            },
            {
                'name': 'Équilibré',
                'allocation': {
                    AssetType.CASH: 0.1,
                    AssetType.SECURITIES: 0.6,
                    AssetType.CRYPTO: 0.1,
                    AssetType.REAL_ESTATE: 0.2,
                },
            },
            {
                'name': 'Agressif',
                'allocation': {
                    AssetType.CASH: 0.05,
                    AssetType.SECURITIES: 0.55,
                    AssetType.CRYPTO: 0.2,
                    AssetType.REAL_ESTATE: 0.2,
                },
            },
        ]
    
    results = {}
    
    for strategy in strategies:
        name = strategy['name']
        allocation = strategy['allocation']
        
        projection = project_wealth_evolution(
            wealth_manager=wealth_manager,
            years=years,
            monthly_contribution=monthly_contribution,
            contribution_allocation=allocation,
            n_simulations=n_simulations,
        )
        
        results[name] = projection
    
    return results


def generate_projection_summary(
    projection: WealthProjectionResult,
    life_goals: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """
    Génère un résumé lisible de la projection.
    
    Args:
        projection: Résultat de la projection
        life_goals: Objectifs de vie avec montant et année
        
    Returns:
        Résumé structuré
    """
    summary = {
        'initial_net_worth': projection.initial_net_worth,
        'projections_by_year': {},
        'life_goals_probability': {},
    }
    
    # Projections clés
    key_years = [5, 10, 15, 20, projection.years]
    for year in key_years:
        if year <= projection.years:
            summary['projections_by_year'][year] = {
                'median': projection.get_net_worth_at_year(year, 50),
                'pessimistic': projection.get_net_worth_at_year(year, 5),
                'optimistic': projection.get_net_worth_at_year(year, 95),
            }
    
    # Probabilités d'atteinte des objectifs
    if life_goals:
        for goal in life_goals:
            name = goal['name']
            amount = goal['amount']
            by_year = goal['year']
            
            prob = projection.get_probability_of_target(amount, by_year)
            summary['life_goals_probability'][name] = {
                'target_amount': amount,
                'by_year': by_year,
                'probability': prob,
                'is_likely': prob >= 0.7,
            }
    
    return summary


# ==================== Fonctions utilitaires ====================

def calculate_required_contribution(
    target_amount: float,
    target_year: int,
    wealth_manager: WealthManager,
    confidence_level: float = 0.5,
    n_simulations: int = 500,
) -> float:
    """
    Calcule le versement mensuel nécessaire pour atteindre un objectif.
    
    Args:
        target_amount: Montant cible
        target_year: Année cible
        wealth_manager: Gestionnaire de patrimoine
        confidence_level: Niveau de confiance (0.5 = médiane)
        n_simulations: Nombre de simulations
        
    Returns:
        Versement mensuel estimé
    """
    # Binary search pour trouver le versement optimal
    low, high = 0, 10000
    best_contribution = high
    
    for _ in range(10):  # 10 itérations suffisent
        mid = (low + high) / 2
        
        projection = project_wealth_evolution(
            wealth_manager=wealth_manager,
            years=target_year,
            monthly_contribution=mid,
            n_simulations=n_simulations,
        )
        
        prob = projection.get_probability_of_target(target_amount, target_year)
        
        if prob >= confidence_level:
            best_contribution = mid
            high = mid
        else:
            low = mid
    
    return round(best_contribution, 2)
