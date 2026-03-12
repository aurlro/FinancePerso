"""
Dashboard API Router
Analytics and statistics endpoints
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Account, Category, Transaction, TransactionType
from ..schemas import (
    CashflowForecast,
    DashboardData,
    DashboardStats,
    MonthlyTrend,
    SpendingByCategory,
)

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
):
    """
    Get main dashboard statistics.
    """
    now = datetime.now()
    current_year = now.year
    current_month = now.month

    # Total balance across all accounts
    balance_result = await db.execute(
        select(func.sum(Account.balance)).where(Account.is_active == True)
    )
    total_balance = balance_result.scalar() or 0

    # Monthly income
    income_result = await db.execute(
        select(func.sum(Transaction.amount))
        .where(
            and_(
                Transaction.type == TransactionType.INCOME,
                extract("year", Transaction.date) == current_year,
                extract("month", Transaction.date) == current_month,
                Transaction.is_deleted == False,
            )
        )
    )
    monthly_income = income_result.scalar() or 0

    # Monthly expenses
    expenses_result = await db.execute(
        select(func.sum(Transaction.amount))
        .where(
            and_(
                Transaction.type == TransactionType.EXPENSE,
                extract("year", Transaction.date) == current_year,
                extract("month", Transaction.date) == current_month,
                Transaction.is_deleted == False,
            )
        )
    )
    monthly_expenses = expenses_result.scalar() or 0

    # Pending transactions count
    pending_result = await db.execute(
        select(func.count())
        .where(
            and_(
                Transaction.is_validated == False,
                Transaction.is_deleted == False,
            )
        )
    )
    pending_count = pending_result.scalar() or 0

    # Total accounts
    accounts_result = await db.execute(
        select(func.count()).where(Account.is_active == True)
    )
    total_accounts = accounts_result.scalar() or 0

    # Calculate savings and rate
    monthly_savings = monthly_income - monthly_expenses
    savings_rate = (monthly_savings / monthly_income * 100) if monthly_income > 0 else 0

    return DashboardStats(
        total_balance=float(total_balance),
        monthly_income=float(monthly_income),
        monthly_expenses=float(monthly_expenses),
        monthly_savings=float(monthly_savings),
        savings_rate=savings_rate,
        pending_transactions=pending_count,
        total_accounts=total_accounts,
        active_budgets=0,  # TODO: implement budget counting
    )


@router.get("/spending", response_model=list[SpendingByCategory])
async def get_spending_by_category(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get spending grouped by category.
    """
    now = datetime.now()
    
    # Default to current month if no dates provided
    if not start_date:
        start_date = f"{now.year}-{now.month:02d}-01"
    if not end_date:
        # Last day of current month
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1)
        else:
            next_month = now.replace(month=now.month + 1, day=1)
        end_date = (next_month - timedelta(days=1)).strftime("%Y-%m-%d")

    result = await db.execute(
        select(
            Category.id,
            Category.name,
            Category.emoji,
            Category.color,
            func.sum(Transaction.amount).label("total"),
            func.count().label("count"),
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .where(
            and_(
                Transaction.type == TransactionType.EXPENSE,
                Transaction.date >= start_date,
                Transaction.date <= end_date,
                Transaction.is_deleted == False,
            )
        )
        .group_by(Category.id, Category.name, Category.emoji, Category.color)
        .order_by(func.sum(Transaction.amount).desc())
    )

    rows = result.all()
    total_spent = sum(row.total for row in rows) or 1  # Avoid division by zero

    spending = [
        SpendingByCategory(
            category_id=str(row.id),
            category_name=row.name,
            category_emoji=row.emoji,
            category_color=row.color,
            amount=float(row.total),
            percentage=(row.total / total_spent) * 100,
            transaction_count=row.count,
        )
        for row in rows
    ]

    return spending


@router.get("/trend", response_model=list[MonthlyTrend])
async def get_monthly_trend(
    months: int = Query(default=12, ge=1, le=60),
    db: AsyncSession = Depends(get_db),
):
    """
    Get monthly financial trend for the last N months.
    """
    from dateutil.relativedelta import relativedelta

    now = datetime.now()
    trends = []

    for i in range(months - 1, -1, -1):
        month_date = now - relativedelta(months=i)
        year = month_date.year
        month = month_date.month

        # Income for this month
        income_result = await db.execute(
            select(func.sum(Transaction.amount))
            .where(
                and_(
                    Transaction.type == TransactionType.INCOME,
                    extract("year", Transaction.date) == year,
                    extract("month", Transaction.date) == month,
                    Transaction.is_deleted == False,
                )
            )
        )
        income = income_result.scalar() or 0

        # Expenses for this month
        expenses_result = await db.execute(
            select(func.sum(Transaction.amount))
            .where(
                and_(
                    Transaction.type == TransactionType.EXPENSE,
                    extract("year", Transaction.date) == year,
                    extract("month", Transaction.date) == month,
                    Transaction.is_deleted == False,
                )
            )
        )
        expenses = expenses_result.scalar() or 0

        savings = income - expenses
        savings_rate = (savings / income * 100) if income > 0 else 0

        trends.append(
            MonthlyTrend(
                month=f"{year}-{month:02d}",
                income=float(income),
                expenses=float(expenses),
                savings=float(savings),
                savings_rate=savings_rate,
            )
        )

    return trends


@router.get("/forecast", response_model=list[CashflowForecast])
async def get_cashflow_forecast(
    months: int = Query(default=6, ge=1, le=24),
    db: AsyncSession = Depends(get_db),
):
    """
    Get cashflow forecast for the next N months.
    Simple linear projection based on last 3 months average.
    """
    from dateutil.relativedelta import relativedelta

    now = datetime.now()
    
    # Calculate average monthly savings from last 3 months
    total_savings = 0
    for i in range(3):
        month_date = now - relativedelta(months=i)
        year = month_date.year
        month = month_date.month

        income_result = await db.execute(
            select(func.sum(Transaction.amount))
            .where(
                and_(
                    Transaction.type == TransactionType.INCOME,
                    extract("year", Transaction.date) == year,
                    extract("month", Transaction.date) == month,
                    Transaction.is_deleted == False,
                )
            )
        )
        income = income_result.scalar() or 0

        expenses_result = await db.execute(
            select(func.sum(Transaction.amount))
            .where(
                and_(
                    Transaction.type == TransactionType.EXPENSE,
                    extract("year", Transaction.date) == year,
                    extract("month", Transaction.date) == month,
                    Transaction.is_deleted == False,
                )
            )
        )
        expenses = expenses_result.scalar() or 0

        total_savings += income - expenses

    avg_monthly_savings = total_savings / 3

    # Get current total balance
    balance_result = await db.execute(
        select(func.sum(Account.balance)).where(Account.is_active == True)
    )
    current_balance = balance_result.scalar() or 0

    # Generate forecast
    forecasts = []
    for i in range(1, months + 1):
        forecast_date = now + relativedelta(months=i)
        predicted_balance = current_balance + (avg_monthly_savings * i)
        
        # Simple confidence interval (±20%)
        confidence_interval = abs(avg_monthly_savings * i * 0.2)

        forecasts.append(
            CashflowForecast(
                date=forecast_date.date(),
                predicted_balance=predicted_balance,
                confidence_lower=predicted_balance - confidence_interval,
                confidence_upper=predicted_balance + confidence_interval,
            )
        )

    return forecasts


@router.get("", response_model=DashboardData)
async def get_full_dashboard(
    db: AsyncSession = Depends(get_db),
):
    """
    Get complete dashboard data in a single request.
    """
    stats = await get_dashboard_stats(db)
    spending = await get_spending_by_category(db=db)
    trend = await get_monthly_trend(months=12, db=db)

    # Get recent transactions
    result = await db.execute(
        select(Transaction)
        .where(Transaction.is_deleted == False)
        .order_by(Transaction.date.desc())
        .limit(10)
    )
    recent_transactions = result.scalars().all()

    return DashboardData(
        stats=stats,
        spending_by_category=spending,
        monthly_trend=trend,
        recent_transactions=[t.to_dict() for t in recent_transactions],
        top_expenses=[],
        alerts=[],
    )
