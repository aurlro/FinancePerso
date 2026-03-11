"""
Budgets API Router
Handles CRUD operations for budgets.
"""

import sys
from pathlib import Path
# Add FinancePerso root to path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status

from modules.db.budgets import (
    delete_budget,
    get_budget_spending,
    get_budgets,
    set_budget,
)
from modules.logger import logger

from models.schemas import (
    BudgetCreateRequest,
    BudgetResponse,
    BudgetUpdateRequest,
    BudgetsListResponse,
)

from routers.auth import get_current_user, UserResponse

router = APIRouter(tags=["Budgets"])


def _calculate_spending(category: str, month: str | None = None) -> float:
    """Calculate spending for a category in a given month."""
    try:
        # Default to current month if not specified
        if month is None:
            month = datetime.now().strftime("%Y-%m")
        
        # Get spending from database
        return get_budget_spending(category) or 0.0
    except Exception:
        return 0.0


@router.get(
    "",
    response_model=BudgetsListResponse,
    summary="List budgets",
    description="Get all budgets with optional spending information.",
    responses={
        500: {"description": "Internal server error"},
    },
)
async def list_budgets(
    month: str | None = Query(None, pattern=r"^\d{4}-\d{2}$", description="Month in YYYY-MM format"),
    current_user: UserResponse = Depends(get_current_user),
) -> BudgetsListResponse:
    """
    Get all budgets.

    Args:
        month: Month to calculate spending for (defaults to current month)
        current_user: The authenticated user

    Returns:
        BudgetsListResponse with all budgets
    """
    try:
        df = get_budgets()
        
        items = []
        for _, row in df.iterrows():
            category = row["category"]
            amount = float(row["amount"])
            spent = _calculate_spending(category, month)
            
            items.append(BudgetResponse(
                category=category,
                amount=amount,
                updated_at=row.get("updated_at", ""),
                spent=round(spent, 2),
                remaining=round(amount - spent, 2),
            ))

        logger.info(f"Listed {len(items)} budgets")
        return BudgetsListResponse(items=items, total=len(items))

    except Exception as e:
        logger.error(f"Error listing budgets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve budgets: {str(e)}",
        )


@router.post(
    "",
    response_model=BudgetResponse,
    summary="Create or update budget",
    description="Set a budget for a category (creates if not exists, updates if exists).",
    responses={
        500: {"description": "Internal server error"},
    },
)
async def create_or_update_budget(
    request: BudgetCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
) -> BudgetResponse:
    """
    Create or update a budget.

    Args:
        request: Budget creation data
        current_user: The authenticated user

    Returns:
        Created/updated budget
    """
    try:
        set_budget(request.category, request.amount)

        logger.info(f"Set budget for {request.category}: {request.amount}")
        return BudgetResponse(
            category=request.category,
            amount=request.amount,
            updated_at=datetime.now().isoformat(),
            spent=0.0,
            remaining=request.amount,
        )

    except Exception as e:
        logger.error(f"Error setting budget: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set budget: {str(e)}",
        )


@router.put(
    "/{category}",
    response_model=BudgetResponse,
    summary="Update budget",
    description="Update budget amount for a category.",
    responses={
        404: {"description": "Budget not found"},
        500: {"description": "Internal server error"},
    },
)
async def update_budget(
    category: str,
    request: BudgetUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
) -> BudgetResponse:
    """
    Update a budget.

    Args:
        category: Category name
        request: Update data
        current_user: The authenticated user

    Returns:
        Updated budget
    """
    try:
        # Check if budget exists
        df = get_budgets()
        existing = df[df["category"] == category]
        
        if existing.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Budget for category '{category}' not found",
            )

        set_budget(category, request.amount)
        
        spent = _calculate_spending(category)

        logger.info(f"Updated budget for {category}: {request.amount}")
        return BudgetResponse(
            category=category,
            amount=request.amount,
            updated_at=datetime.now().isoformat(),
            spent=round(spent, 2),
            remaining=round(request.amount - spent, 2),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating budget for {category}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update budget: {str(e)}",
        )


@router.delete(
    "/{category}",
    response_model=dict,
    summary="Delete budget",
    description="Delete a budget for a category.",
    responses={
        404: {"description": "Budget not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_budget_endpoint(
    category: str,
    current_user: UserResponse = Depends(get_current_user),
) -> dict:
    """
    Delete a budget.

    Args:
        category: Category name
        current_user: The authenticated user

    Returns:
        Deletion confirmation
    """
    try:
        success = delete_budget(category)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Budget for category '{category}' not found",
            )

        logger.info(f"Deleted budget for: {category}")
        return {"deleted": True, "category": category}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting budget for {category}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete budget: {str(e)}",
        )
