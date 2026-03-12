"""
Budgets API Router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Budget, Category, Transaction
from ..schemas import (
    Budget as BudgetSchema,
    BudgetCreate,
    BudgetResponse,
    BudgetUpdate,
    BudgetWithSpending,
    SuccessResponse,
)

router = APIRouter()


@router.get("", response_model=list[BudgetWithSpending])
async def list_budgets(
    year: int = None,
    month: int = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List all budgets with spending data.
    """
    from datetime import datetime

    now = datetime.now()
    year = year or now.year
    month = month or now.month

    result = await db.execute(
        select(Budget)
        .where(
            and_(
                Budget.year == year,
                Budget.month == month,
            )
        )
        .order_by(Budget.amount.desc())
    )
    budgets = result.scalars().all()

    # Calculate spending for each budget
    budgets_with_spending = []
    for budget in budgets:
        # Get total spent in this category for the period
        spent_result = await db.execute(
            select(func.sum(Transaction.amount))
            .where(
                and_(
                    Transaction.category_id == budget.category_id,
                    extract("year", Transaction.date) == year,
                    extract("month", Transaction.date) == month,
                    Transaction.type == "expense",
                    Transaction.is_deleted == False,
                )
            )
        )
        spent = spent_result.scalar() or 0

        budget_data = BudgetWithSpending(
            **budget.__dict__,
            spent=float(spent),
            category_name=budget.category.name if budget.category else "",
            category_emoji=budget.category.emoji if budget.category else "",
            category_color=budget.category.color if budget.category else "",
        )
        budgets_with_spending.append(budget_data)

    return budgets_with_spending


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    data: BudgetCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new budget.
    """
    # Verify category exists
    category_result = await db.execute(
        select(Category).where(Category.id == data.category_id)
    )
    if not category_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    budget = Budget(**data.model_dump())
    db.add(budget)
    await db.commit()
    await db.refresh(budget)

    return BudgetResponse(data=budget)


@router.patch("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: str,
    data: BudgetUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a budget.
    """
    result = await db.execute(
        select(Budget).where(Budget.id == budget_id)
    )
    budget = result.scalar_one_or_none()

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(budget, field, value)

    await db.commit()
    await db.refresh(budget)

    return BudgetResponse(data=budget)


@router.delete("/{budget_id}", response_model=SuccessResponse)
async def delete_budget(
    budget_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a budget.
    """
    result = await db.execute(
        select(Budget).where(Budget.id == budget_id)
    )
    budget = result.scalar_one_or_none()

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found",
        )

    await db.delete(budget)
    await db.commit()

    return SuccessResponse(message="Budget deleted successfully")
