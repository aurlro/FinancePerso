"""
Package src - Data Engineering, Analytics & Wealth Management pour FinancePerso.
===============================================================================

Ce package contient les modules de traitement des données :
- data_cleaning: Nettoyage et normalisation des libellés (Phase 2)
- subscription_engine: Détection des abonnements (Phase 3)
- math_engine: Simulations Monte Carlo (Phase 4)
- visualizations: Graphiques interactifs (Phase 4)
- wealth_manager: Gestion patrimoniale holistique (Phase 5)
- agent_core: Orchestrateur d'IA agentique (Phase 5)

Usage:
    from src import clean_transaction_label  # Phase 2
    from src import SubscriptionDetector      # Phase 3
    from src import MonteCarloSimulator      # Phase 4
    from src import WealthManager            # Phase 5
    from src import AgentOrchestrator        # Phase 5
"""

# Phase 2: Data Engineering
# Phase 5: Agentic AI
from modules.wealth.agent_core import (
    Action,
    ActionType,
    # Classes principales
    AgentOrchestrator,
    DocumentGenerator,
    Mission,
    MissionPriority,
    MissionStatus,
    TriggerDetector,
    # Enums
    TriggerType,
    # Fonctions utilitaires
    quick_analyze,
)
from modules.wealth.data_cleaning import (
    batch_clean_labels,
    clean_merchant_name,
    clean_transaction_label,
    extract_card_suffix,
    extract_location,
    extract_transaction_metadata,
    normalize_merchant_name,
)

# Phase 4: Monte Carlo Engine
from modules.wealth.math_engine import (
    MonteCarloSimulator,
    ScenarioType,
    SimulationResult,
    get_default_monthly_contribution,
    quick_simulation,
)

# Phase 3: Subscription Engine
from modules.wealth.subscription_engine import (
    FrequencyType,
    RemainingBudgetResult,
    Subscription,
    SubscriptionDetector,
    SubscriptionStatus,
    calculate_remaining_budget,
)

# Phase 4: Visualizations
from modules.wealth.visualizations import (
    plot_probability_distribution,
    plot_scenario_comparison,
    plot_wealth_projection,
)

# Phase 5: Wealth Management
from modules.wealth.wealth_manager import (
    AssetLiquidity,
    # Enums
    AssetType,
    CryptoAsset,
    FinancialAsset,
    Liability,
    LiabilityType,
    MortgageSchedule,
    RealEstateAsset,
    # Classes principales
    WealthManager,
    calculate_debt_to_income_ratio,
    # Fonctions utilitaires
    calculate_monthly_debt_service,
    calculate_savings_rate,
)

# Phase 5: Wealth Projections (Integration Phase 4 × Phase 5)
from modules.wealth.wealth_projection import (
    DEFAULT_ASSET_RETURNS,
    AssetProjection,
    WealthProjectionResult,
    calculate_required_contribution,
    compare_allocation_strategies,
    generate_projection_summary,
    project_asset_class,
    project_wealth_evolution,
)

__all__ = [
    # Phase 2
    "clean_merchant_name",
    "clean_transaction_label",
    "extract_card_suffix",
    "extract_location",
    "extract_transaction_metadata",
    "normalize_merchant_name",
    "batch_clean_labels",
    # Phase 3
    "Subscription",
    "SubscriptionStatus",
    "FrequencyType",
    "SubscriptionDetector",
    "RemainingBudgetResult",
    "calculate_remaining_budget",
    # Phase 4
    "ScenarioType",
    "SimulationResult",
    "MonteCarloSimulator",
    "quick_simulation",
    "get_default_monthly_contribution",
    "plot_wealth_projection",
    "plot_scenario_comparison",
    "plot_probability_distribution",
    # Phase 5: Wealth
    "WealthManager",
    "RealEstateAsset",
    "FinancialAsset",
    "CryptoAsset",
    "Liability",
    "MortgageSchedule",
    "AssetType",
    "LiabilityType",
    "AssetLiquidity",
    "calculate_monthly_debt_service",
    "calculate_debt_to_income_ratio",
    "calculate_savings_rate",
    # Phase 5: Wealth Projections
    "project_wealth_evolution",
    "compare_allocation_strategies",
    "project_asset_class",
    "generate_projection_summary",
    "calculate_required_contribution",
    "WealthProjectionResult",
    "AssetProjection",
    "DEFAULT_ASSET_RETURNS",
    # Phase 5: Agent
    "AgentOrchestrator",
    "Mission",
    "Action",
    "TriggerDetector",
    "DocumentGenerator",
    "TriggerType",
    "MissionPriority",
    "MissionStatus",
    "ActionType",
    "quick_analyze",
]
