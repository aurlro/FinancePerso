"""
Dashboard API Router - Phase 1
Handles dashboard statistics, breakdowns, and evolution data.
"""

import datetime
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, status

# Import existing modules (adjust path for web/api/ location)
import sys
from pathlib import Path
# Add FinancePerso root to path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from modules.db.categories import get_categories_with_emojis
from modules.db.connection import get_db_connection
from modules.db.stats import get_available_months
from modules.db.transactions import get_all_transactions
from modules.logger import logger
from modules.transaction_types import (
    calculate_savings_rate,
    calculate_true_expenses,
    calculate_true_income,
)

from models.schemas import (
    DashboardBreakdownResponse,
    DashboardEvolutionResponse,
    DashboardStatsResponse,
    CategoryBreakdownItem,
)

router = APIRouter(tags=["Dashboard"])  # Prefix géré dans main.py


def get_current_month() -> str:
    """Get current month in YYYY-MM format."""
    return datetime.date.today().strftime("%Y-%m")


def parse_month(month_str: str | None) -> str:
    """Parse and validate month string."""
    if month_str is None:
        return get_current_month()

    try:
        datetime.datetime.strptime(month_str, "%Y-%m")
        return month_str
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid month format: '{month_str}'. Expected YYYY-MM",
        )


@router.get(
    "/stats",
    response_model=DashboardStatsResponse,
    summary="Get dashboard statistics",
    description="Returns key financial metrics for a given month: remaining budget, expenses, income, and savings.",
    responses={
        400: {"description": "Invalid month format"},
        500: {"description": "Internal server error"},
    },
)
async def get_dashboard_stats(
    month: Annotated[
        str | None,
        Query(pattern=r"^\d{4}-\d{2}$", description="Month in YYYY-MM format"),
    ] = None,
) -> DashboardStatsResponse:
    """
    Get dashboard statistics for a specific month.

    Args:
        month: Month in YYYY-MM format (defaults to current month)

    Returns:
        DashboardStatsResponse with financial metrics
    """
    period = parse_month(month)

    try:
        with get_db_connection() as conn:
            # Get all transactions for the month
            query = """
                SELECT amount, category_validated, status
                FROM transactions
                WHERE strftime('%Y-%m', date) = ?
            """
            df = pd.read_sql(query, conn, params=(period,))

            if df.empty:
                logger.info(f"No transactions found for period {period}")
                return DashboardStatsResponse(
                    reste_a_vivre=0.0,
                    total_expenses=0.0,
                    total_income=0.0,
                    epargne_nette=0.0,
                    period=period,
                )

            # Calculate metrics using existing business logic
            total_income = calculate_true_income(df, include_refunds=False)
            total_expenses = calculate_true_expenses(df, include_refunds=True)
            epargne_nette = total_income - total_expenses

            # "Reste à vivre" is the same as net savings in this context
            # Could be adjusted based on budget allocations in future versions
            reste_a_vivre = epargne_nette

            logger.info(
                f"Dashboard stats for {period}: income={total_income:.2f}, "
                f"expenses={total_expenses:.2f}, savings={epargne_nette:.2f}"
            )

            return DashboardStatsResponse(
                reste_a_vivre=round(reste_a_vivre, 2),
                total_expenses=round(total_expenses, 2),
                total_income=round(total_income, 2),
                epargne_nette=round(epargne_nette, 2),
                period=period,
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard statistics: {str(e)}",
        )


@router.get(
    "/breakdown",
    response_model=DashboardBreakdownResponse,
    summary="Get category breakdown",
    description="Returns expense breakdown by category for a given month with percentages.",
    responses={
        400: {"description": "Invalid month format"},
        500: {"description": "Internal server error"},
    },
)
async def get_category_breakdown(
    month: Annotated[
        str | None,
        Query(pattern=r"^\d{4}-\d{2}$", description="Month in YYYY-MM format"),
    ] = None,
) -> DashboardBreakdownResponse:
    """
    Get expense breakdown by category for a specific month.

    Args:
        month: Month in YYYY-MM format (defaults to current month)

    Returns:
        DashboardBreakdownResponse with category breakdown
    """
    period = parse_month(month)

    try:
        with get_db_connection() as conn:
            # Get expense transactions grouped by category
            # Filter out income and excluded categories
            query = """
                SELECT
                    category_validated as category,
                    SUM(
                        CASE
                            WHEN amount < 0 THEN ABS(amount)
                            ELSE amount
                        END
                    ) as total_amount,
                    COUNT(*) as transaction_count
                FROM transactions
                WHERE strftime('%Y-%m', date) = ?
                    AND category_validated NOT IN (
                        'Revenus', 'Salaire', 'Prime', 'Revenus secondaires',
                        'Investissements', 'Intérêts', 'Dividendes', 'Cadeaux reçus', 'Ventes',
                        'Virement Interne', 'Hors Budget', 'Transfert', 'Épargne',
                        'Contribution Partenaire', 'Apport Externe', 'Remboursement',
                        'Remboursement santé', 'Remboursement assurance'
                    )
                    AND category_validated IS NOT NULL
                    AND category_validated != 'Inconnu'
                GROUP BY category_validated
                ORDER BY total_amount DESC
            """
            df = pd.read_sql(query, conn, params=(period,))

            if df.empty:
                logger.info(f"No expense categories found for period {period}")
                return DashboardBreakdownResponse(categories=[], total=0.0)

            # Get category emojis
            category_emojis = get_categories_with_emojis()

            # Calculate total and percentages
            grand_total = df["total_amount"].sum()

            categories = []
            for _, row in df.iterrows():
                category_name = row["category"]
                amount = float(row["total_amount"])
                percentage = round((amount / grand_total * 100), 1) if grand_total > 0 else 0.0

                categories.append(
                    CategoryBreakdownItem(
                        name=category_name,
                        amount=round(amount, 2),
                        percentage=percentage,
                        emoji=category_emojis.get(category_name),
                    )
                )

            logger.info(
                f"Category breakdown for {period}: {len(categories)} categories, "
                f"total={grand_total:.2f}"
            )

            return DashboardBreakdownResponse(
                categories=categories,
                total=round(grand_total, 2),
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting category breakdown: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve category breakdown: {str(e)}",
        )


@router.get(
    "/evolution",
    response_model=DashboardEvolutionResponse,
    summary="Get 12-month evolution",
    description="Returns income, expenses, and savings evolution over the last 12 months.",
    responses={
        500: {"description": "Internal server error"},
    },
)
async def get_evolution(
    months: Annotated[
        int,
        Query(ge=3, le=24, description="Number of months to return (3-24)"),
    ] = 12,
) -> DashboardEvolutionResponse:
    """
    Get financial evolution over the last N months.

    Args:
        months: Number of months to include (default: 12, min: 3, max: 24)

    Returns:
        DashboardEvolutionResponse with monthly data
    """
    try:
        with get_db_connection() as conn:
            # Get available months from the database
            available_months = get_available_months()

            if not available_months:
                logger.info("No transaction data available for evolution")
                return DashboardEvolutionResponse(
                    months=[], expenses=[], income=[], savings=[]
                )

            # Take the last N months (already sorted descending)
            selected_months = available_months[:months]
            # Reverse to get chronological order
            selected_months = selected_months[::-1]

            result_months = []
            result_expenses = []
            result_income = []
            result_savings = []

            for period in selected_months:
                query = """
                    SELECT amount, category_validated
                    FROM transactions
                    WHERE strftime('%Y-%m', date) = ?
                """
                df = pd.read_sql(query, conn, params=(period,))

                if df.empty:
                    income = 0.0
                    expenses = 0.0
                    savings = 0.0
                else:
                    income = calculate_true_income(df, include_refunds=False)
                    expenses = calculate_true_expenses(df, include_refunds=True)
                    savings = income - expenses

                result_months.append(period)
                result_income.append(round(income, 2))
                result_expenses.append(round(expenses, 2))
                result_savings.append(round(savings, 2))

            logger.info(f"Evolution data calculated for {len(result_months)} months")

            return DashboardEvolutionResponse(
                months=result_months,
                expenses=result_expenses,
                income=result_income,
                savings=result_savings,
            )

    except Exception as e:
        logger.error(f"Error getting evolution data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve evolution data: {str(e)}",
        )
