"""
Dashboard and analytics schemas
"""

from datetime import date
from typing import Optional

from pydantic import Field

from .base import BaseSchema


class DashboardStats(BaseSchema):
    """Main dashboard statistics."""

    total_balance: float = 0.0
    monthly_income: float = 0.0
    monthly_expenses: float = 0.0
    monthly_savings: float = 0.0
    savings_rate: float = Field(default=0.0, ge=0, le=100)
    pending_transactions: int = 0
    total_accounts: int = 0
    active_budgets: int = 0


class SpendingByCategory(BaseSchema):
    """Spending grouped by category."""

    category_id: str
    category_name: str
    category_emoji: str
    category_color: str
    amount: float
    percentage: float
    transaction_count: int
    budget_limit: Optional[float] = None
    budget_remaining: Optional[float] = None


class MonthlyTrend(BaseSchema):
    """Monthly financial trend."""

    month: str  # YYYY-MM format
    income: float
    expenses: float
    savings: float
    savings_rate: float


class CashflowForecast(BaseSchema):
    """Cashflow prediction."""

    date: date
    predicted_balance: float
    confidence_lower: float
    confidence_upper: float


class AccountBalanceHistory(BaseSchema):
    """Account balance over time."""

    account_id: str
    account_name: str
    balances: list[dict]  # [{"date": "2024-01", "balance": 1000.0}]


class TopTransaction(BaseSchema):
    """Top transaction by amount."""

    id: str
    date: date
    description: str
    amount: float
    type: str
    category_name: str
    category_emoji: str


class DashboardData(BaseSchema):
    """Complete dashboard data."""

    stats: DashboardStats
    spending_by_category: list[SpendingByCategory]
    monthly_trend: list[MonthlyTrend]
    recent_transactions: list[dict]  # Simplified transaction
    top_expenses: list[TopTransaction]
    alerts: list[str]
