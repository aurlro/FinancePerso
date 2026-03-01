"""
Moteur Mathématique - Simulations de Monte Carlo & GBM
======================================================

Ce module implémente la simulation de Monte Carlo basée sur le modèle
de Mouvement Brownien Géométrique (GBM) pour la projection patrimoniale.

Modèle Mathématique:
    dS_t = μ S_t dt + σ S_t dW_t
    
    Solution discrète:
    S_{t+1} = S_t * exp((μ - 0.5σ²)Δt + σ√Δt Z)
    où Z ~ N(0,1)

Usage:
    from modules.wealth.math_engine import MonteCarloSimulator
    
    simulator = MonteCarloSimulator(
        initial_capital=10000,
        monthly_contribution=500,
        annual_return=0.07,      # 7% rendement
        volatility=0.15,         # 15% volatilité
        years=10,
    )
    
    simulations = simulator.run_simulation(n_simulations=10000)
    stats = simulator.get_statistics(simulations)
    
    print(f"Capital médian projeté: {stats['median']:.2f}€")
    print(f"Intervalle confiance 90%: [{stats['percentile_5']:.2f}, {stats['percentile_95']:.2f}]€")
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Optional, Dict, Tuple, List
from enum import Enum

from modules.logger import logger


class ScenarioType(Enum):
    """Types de scénarios économiques prédéfinis."""
    CONSERVATEUR = "conservateur"      # μ=3%, σ=8%
    MODERE = "modere"                  # μ=7%, σ=15%
    AGRESSIF = "agressif"              # μ=10%, σ=25%
    CRYPTO = "crypto"                  # μ=20%, σ=80%
    DEFENSIF = "defensif"              # μ=2%, σ=5%



# Paramètres prédéfinis par scénario
SCENARIO_PARAMS = {
    ScenarioType.CONSERVATEUR: {"mu": 0.03, "sigma": 0.08},
    ScenarioType.MODERE: {"mu": 0.07, "sigma": 0.15},
    ScenarioType.AGRESSIF: {"mu": 0.10, "sigma": 0.25},
    ScenarioType.CRYPTO: {"mu": 0.20, "sigma": 0.80},
    ScenarioType.DEFENSIF: {"mu": 0.02, "sigma": 0.05},
}


@dataclass
class SimulationResult:
    """
    Résultat d'une simulation Monte Carlo.
    
    Attributes:
        simulations: Array (n_simulations, n_periods) des trajectoires
        time_points: Array des points temporels (en années)
        params: Paramètres utilisés pour la simulation
        statistics: Statistiques calculées (percentiles, etc.)
    """
    simulations: np.ndarray
    time_points: np.ndarray
    params: Dict
    statistics: Optional[Dict] = None
    
    def get_trajectory(self, index: int) -> np.ndarray:
        """Retourne une trajectoire spécifique."""
        return self.simulations[index]
    
    def get_percentile(self, percentile: float) -> np.ndarray:
        """Calcule un percentile sur toutes les trajectoires."""
        return np.percentile(self.simulations, percentile, axis=0)
    
    def get_final_values(self) -> np.ndarray:
        """Retourne les valeurs finales de toutes les simulations."""
        return self.simulations[:, -1]


class MonteCarloSimulator:
    """
    Simulateur Monte Carlo basé sur le modèle GBM.
    
    Implémente la solution discrète de l'équation différentielle stochastique
    du Mouvement Brownien Géométrique avec versements réguliers.
    
    Formule de mise à jour:
        S_{t+1} = S_t * exp((μ - 0.5σ²)Δt + σ√Δt Z) + C
        où:
        - μ: rendement annuel (drift)
        - σ: volatilité annuelle
        - Δt: pas de temps (1/12 pour mensuel)
        - Z: tirage aléatoire N(0,1)
        - C: contribution/versement mensuel
    
    Usage:
        simulator = MonteCarloSimulator(
            initial_capital=10000,
            monthly_contribution=500,
            annual_return=0.07,
            volatility=0.15,
            years=10,
        )
        
        # 10 000 simulations
        result = simulator.run_simulation(n_simulations=10000)
        
        # Statistiques
        stats = simulator.get_statistics(result)
    """
    
    def __init__(
        self,
        initial_capital: float,
        monthly_contribution: float,
        annual_return: float,
        volatility: float,
        years: int,
        months_offset: int = 0,
        annual_inflation: float = 0.0,
    ):
        """
        Initialise le simulateur.
        
        Args:
            initial_capital: Capital initial (€)
            monthly_contribution: Versement mensuel récurrent (€)
            annual_return: Rendement annuel attendu μ (ex: 0.07 pour 7%)
            volatility: Volatilité annuelle σ (ex: 0.15 pour 15%)
            years: Durée de projection (années)
            months_offset: Décalage en mois (pour démarrer plus tard)
            annual_inflation: Taux d'inflation annuel (ex: 0.02 pour 2%)
        """
        self.initial_capital = initial_capital
        self.monthly_contribution = monthly_contribution
        self.annual_return = annual_return
        self.volatility = volatility
        self.years = years
        self.months_offset = months_offset
        self.annual_inflation = annual_inflation
        
        # Calcul du drift ajusté pour la discrétisation
        # μ_disc = μ - 0.5σ² (correction de Itô)
        self.drift = annual_return - 0.5 * volatility ** 2
        
        # Pas de temps (mensuel)
        self.dt = 1 / 12
        
        # Nombre total de périodes
        self.n_periods = years * 12
        
        logger.info(
            f"MonteCarloSimulator initialisé: "
            f"S0={initial_capital}€, C={monthly_contribution}€/mois, "
            f"μ={annual_return:.1%}, σ={volatility:.1%}, "
            f"T={years}ans"
        )
    
    @classmethod
    def from_scenario(
        cls,
        scenario: ScenarioType,
        initial_capital: float,
        monthly_contribution: float,
        years: int,
    ) -> "MonteCarloSimulator":
        """
        Crée un simulateur à partir d'un scénario prédéfini.
        
        Args:
            scenario: Type de scénario (CONSERVATEUR, MODERE, AGRESSIF, etc.)
            initial_capital: Capital initial
            monthly_contribution: Versement mensuel
            years: Durée
            
        Returns:
            Instance de MonteCarloSimulator configurée
        """
        params = SCENARIO_PARAMS[scenario]
        return cls(
            initial_capital=initial_capital,
            monthly_contribution=monthly_contribution,
            annual_return=params["mu"],
            volatility=params["sigma"],
            years=years,
        )
    
    def run_simulation(
        self,
        n_simulations: int = 10000,
        seed: Optional[int] = None,
    ) -> SimulationResult:
        """
        Lance la simulation Monte Carlo.
        
        Args:
            n_simulations: Nombre de trajectoires à générer (défaut: 10000)
            seed: Graine aléatoire pour reproductibilité
            
        Returns:
            SimulationResult contenant toutes les trajectoires
            
        Performance:
            - Vectorisation numpy complète
            - ~100ms pour 10 000 simulations sur 10 ans (120 périodes)
        """
        if seed is not None:
            np.random.seed(seed)
        
        # Initialisation du tableau des simulations
        # Shape: (n_simulations, n_periods + 1)
        # +1 car on inclut le capital initial (période 0)
        simulations = np.zeros((n_simulations, self.n_periods + 1))
        simulations[:, 0] = self.initial_capital
        
        # Pré-calcul des constantes pour optimisation
        drift_term = self.drift * self.dt
        vol_term = self.volatility * np.sqrt(self.dt)
        
        # Génération des facteurs aléatoires (vectorisé)
        # Shape: (n_simulations, n_periods)
        random_shocks = np.random.standard_normal((n_simulations, self.n_periods))
        
        # Contribution mensuelle (peut être ajustée pour inflation)
        contribution = self.monthly_contribution
        
        # Simulation itérative sur les périodes
        for t in range(self.n_periods):
            # Récupérer les valeurs actuelles
            current_values = simulations[:, t]
            
            # Calcul du facteur de croissance GBM
            # exp((μ - 0.5σ²)Δt + σ√Δt Z)
            growth_factors = np.exp(
                drift_term + vol_term * random_shocks[:, t]
            )
 
            # Mise à jour avec versement mensuel
            # Nouvelle valeur = Ancienne * facteur + versement
            simulations[:, t + 1] = current_values * growth_factors + contribution
            
            # Optionnel: ajuster le versement pour inflation
            if self.annual_inflation > 0 and t > 0 and t % 12 == 0:
                contribution *= (1 + self.annual_inflation)
        
        # Points temporels (en années)
        time_points = np.linspace(0, self.years, self.n_periods + 1)
        
        result = SimulationResult(
            simulations=simulations,
            time_points=time_points,
            params={
                "initial_capital": self.initial_capital,
                "monthly_contribution": self.monthly_contribution,
                "annual_return": self.annual_return,
                "volatility": self.volatility,
                "years": self.years,
                "n_simulations": n_simulations,
            },
        )
        
        # Calcul des statistiques
        result.statistics = self.get_statistics(result)
        
        logger.info(
            f"Simulation terminée: {n_simulations} trajectoires, "
            f"Capital médian final: {result.statistics['median']:.2f}€"
        )
        
        return result
    
    def get_statistics(self, result: SimulationResult) -> Dict:
        """
        Calcule les statistiques descriptives des simulations.
        
        Args:
            result: Résultat de la simulation
            
        Returns:
            Dictionnaire avec médiane, percentiles, moyenne, etc.
        """
        final_values = result.get_final_values()
        
        stats = {
            # Valeurs finales
            "mean": float(np.mean(final_values)),
            "median": float(np.median(final_values)),
            "std": float(np.std(final_values)),
            "min": float(np.min(final_values)),
            "max": float(np.max(final_values)),
            
            # Percentiles clés
            "percentile_5": float(np.percentile(final_values, 5)),
            "percentile_10": float(np.percentile(final_values, 10)),
            "percentile_25": float(np.percentile(final_values, 25)),
            "percentile_75": float(np.percentile(final_values, 75)),
            "percentile_90": float(np.percentile(final_values, 90)),
            "percentile_95": float(np.percentile(final_values, 95)),
            
            # Trajectoire médiane (tout au long du temps)
            "median_trajectory": result.get_percentile(50),
            "percentile_5_trajectory": result.get_percentile(5),
            "percentile_95_trajectory": result.get_percentile(95),
        }
        
        return stats
    
    def get_probability_above_target(
        self,
        result: SimulationResult,
        target: float,
    ) -> float:
        """
        Calcule la probabilité d'atteindre un objectif.
        
        Args:
            result: Résultat de la simulation
            target: Objectif financier (€)
            
        Returns:
            Probabilité (0-1) d'atteindre ou dépasser l'objectif
        """
        final_values = result.get_final_values()
        prob = np.mean(final_values >= target)
        return float(prob)
    
    def get_time_to_target(
        self,
        result: SimulationResult,
        target: float,
        percentile: float = 50,
    ) -> Optional[int]:
        """
        Calcule le temps nécessaire pour atteindre un objectif.
        
        Args:
            result: Résultat de la simulation
            target: Objectif financier (€)
            percentile: Percentile de la trajectoire à considérer
            
        Returns:
            Nombre de mois pour atteindre l'objectif, ou None si jamais
        """
        trajectory = result.get_percentile(percentile)
        
        # Trouver le premier mois où on dépasse l'objectif
        months_above = np.where(trajectory >= target)[0]
        
        if len(months_above) > 0:
            return int(months_above[0])
        return None
    
    def run_what_if_scenarios(
        self,
        base_params: Dict,
        variations: List[Dict],
        n_simulations: int = 5000,
    ) -> List[SimulationResult]:
        """
        Lance plusieurs scénarios "What-If" pour comparaison.
        
        Args:
            base_params: Paramètres de base
            variations: Liste des variations à tester
            n_simulations: Nombre de simulations par scénario
            
        Returns:
            Liste des résultats pour chaque scénario
        """
        results = []
        
        for variation in variations:
            # Fusionner paramètres de base avec variation
            params = {**base_params, **variation}
            
            # Créer simulateur
            sim = MonteCarloSimulator(**params)
            result = sim.run_simulation(n_simulations=n_simulations)
            
            results.append(result)
        
        return results


def quick_simulation(
    initial_capital: float,
    monthly_contribution: float,
    years: int,
    scenario: ScenarioType = ScenarioType.MODERE,
    n_simulations: int = 10000,
) -> Dict:
    """
    Fonction utilitaire rapide pour lancer une simulation.
    
    Usage:
        result = quick_simulation(
            initial_capital=10000,
            monthly_contribution=500,
            years=10,
            scenario=ScenarioType.MODERE,
        )
        
        print(f"Capital projeté: {result['median']:.2f}€")
    """
    simulator = MonteCarloSimulator.from_scenario(
        scenario=scenario,
        initial_capital=initial_capital,
        monthly_contribution=monthly_contribution,
        years=years,
    )
    
    result = simulator.run_simulation(n_simulations=n_simulations)
    return result.statistics


# Paramètres par défaut selon le type d'actif
ASSET_PROFILES = {
    "livret_a": {"mu": 0.03, "sigma": 0.01, "label": "Livret A (sûr)"},
    "obligation": {"mu": 0.04, "sigma": 0.05, "label": "Obligations (stable)"},
    "action": {"mu": 0.08, "sigma": 0.18, "label": "Actions (moyen)"},
    "crypto": {"mu": 0.20, "sigma": 0.80, "label": "Crypto (risqué)"},
    "immobilier": {"mu": 0.05, "sigma": 0.10, "label": "Immobilier (stable)"},
}


def get_asset_profile(asset_type: str) -> Dict:
    """Retourne le profil de risque/rendement pour un type d'actif."""
    return ASSET_PROFILES.get(asset_type, ASSET_PROFILES["action"])
{
    "obligation": {"mu": 0.04, "sigma": 0.05, "label": "Obligations (stable)"},
    "action": {"mu": 0.08, "sigma": 0.18, "label": "Actions (moyen)"},
    "crypto": {"mu": 0.20, "sigma": 0.80, "label": "Crypto (risqué)"},
    "immobilier": {"mu": 0.05, "sigma": 0.10, "label": "Immobilier (stable)"},
}


def get_asset_profile(asset_type: str) -> Dict:
    """Retourne le profil de risque/rendement pour un type d'actif."""
    return ASSET_PROFILES.get(asset_type, ASSET_PROFILES["action"])


def get_default_monthly_contribution(
    current_balance: float = 1500.0,
    subscriptions: Optional[List] = None,
    saving_rate: float = 0.30,
    min_contribution: float = 50.0,
) -> float:
    """
    Calcule le versement mensuel par défaut basé sur le Reste à Vivre (Phase 3).
    
    Cette fonction intègre les données de Phase 3 (SubscriptionDetector) pour
    proposer un versement mensuel réaliste basé sur le budget disponible.
    
    Args:
        current_balance: Solde actuel du compte
        subscriptions: Liste des abonnements détectés (Phase 3)
        saving_rate: Taux d'épargne sur le reste à vivre (défaut: 30%)
        min_contribution: Versement minimum (défaut: 50€)
        
    Returns:
        Montant mensuel recommandé pour les simulations
        
    Example:
        >>> from src import get_default_monthly_contribution, SubscriptionDetector
        >>> detector = SubscriptionDetector()
        >>> subs = detector.detect_from_dataframe(df)
        >>> monthly = get_default_monthly_contribution(2000.0, subs)
        >>> print(f"Versement recommandé: €{monthly:.0f}/mois")
    """
    if subscriptions is None:
        subscriptions = []
    
    # Importer ici pour éviter les dépendances circulaires
    try:
        from modules.wealth.subscription_engine import calculate_remaining_budget
        
        # Calculer le Reste à Vivre sur 30 jours
        budget_result = calculate_remaining_budget(
            current_balance=current_balance,
            subscriptions=subscriptions,
            days_ahead=30
        )
        
        # Prendre 30% du reste à vivre comme base
        recommended = budget_result.remaining_budget * saving_rate
        
        # Arrondir à la dizaine la plus proche
        recommended = round(recommended / 10) * 10
        
        # Appliquer les bornes
        return max(min_contribution, recommended)
        
    except Exception:
        # Fallback si Phase 3 non disponible
        return max(min_contribution, round(current_balance * 0.10 / 10) * 10)
