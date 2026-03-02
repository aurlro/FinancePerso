"""
Cashflow forecasting module for FinancePerso.
Predicts future financial state based on historical data and recurring patterns.
"""

from modules.cashflow.predictor import (
    get_cashflow_insights,
    predict_account_balance,
    predict_monthly_cashflow,
)
from modules.cashflow.recurring import (
    detect_recurring_transactions,
    get_upcoming_recurring,
)
from modules.cashflow.scenarios import (
    ScenarioType,
    simulate_scenario,
)

__all__ = [
    "predict_monthly_cashflow",
    "predict_account_balance",
    "get_cashflow_insights",
    "detect_recurring_transactions",
    "get_upcoming_recurring",
    "simulate_scenario",
    "ScenarioType",
]
