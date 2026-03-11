"""
Transactions API Router
Handles CRUD operations for transactions.
"""

import sys
from pathlib import Path
# Add FinancePerso root to path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, status

from modules.db.connection import get_db_connection
from modules.db.transactions import (
    get_all_transactions,
    get_transactions_count,
    get_transaction_by_id,
)
from modules.logger import logger

from models.schemas import (
    TransactionFilters,
    TransactionResponse,
    TransactionsListResponse,
)

router = APIRouter(tags=["Transactions"])  # Prefix géré dans main.py


@router.get(
    "",
    response_model=TransactionsListResponse,
    summary="List transactions",
    description="Get paginated list of transactions with optional filtering.",
    responses={
        400: {"description": "Invalid filter parameters"},
        500: {"description": "Internal server error"},
    },
)
async def list_transactions(
    limit: Annotated[
        int,
        Query(ge=1, le=1000, description="Number of items per page"),
    ] = 50,
    offset: Annotated[
        int,
        Query(ge=0, description="Offset for pagination"),
    ] = 0,
    category: Annotated[
        str | None,
        Query(description="Filter by category"),
    ] = None,
    month: Annotated[
        str | None,
        Query(pattern=r"^\d{4}-\d{2}$", description="Filter by month (YYYY-MM)"),
    ] = None,
    status: Annotated[
        str | None,
        Query(description="Filter by status (pending/validated)"),
    ] = None,
    member: Annotated[
        str | None,
        Query(description="Filter by member"),
    ] = None,
    search: Annotated[
        str | None,
        Query(description="Search in label or beneficiary"),
    ] = None,
) -> TransactionsListResponse:
    """
    Get paginated list of transactions with optional filtering.

    Args:
        limit: Maximum number of transactions to return (1-1000)
        offset: Number of transactions to skip for pagination
        category: Filter by category name
        month: Filter by month in YYYY-MM format
        status: Filter by status (pending or validated)
        member: Filter by member name
        search: Search term for label or beneficiary (case-insensitive)

    Returns:
        TransactionsListResponse with paginated transactions and total count
    """
    try:
        # Build filters dictionary
        filters = {}

        if category:
            filters["category_validated"] = category

        if status:
            if status not in ["pending", "validated"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: '{status}'. Must be 'pending' or 'validated'",
                )
            filters["status"] = status

        if member:
            filters["member"] = member

        # Handle month filter (requires special SQL)
        if month:
            # Add date filter using tuple syntax for custom operator
            filters["date"] = ("LIKE", f"{month}%")

        # Get total count for pagination
        total = get_transactions_count(filters=filters if filters else None)

        # Get transactions with pagination
        df = get_all_transactions(
            limit=limit,
            offset=offset,
            filters=filters if filters else None,
            order_by="date DESC",
        )

        # Handle search filter (post-query filtering for label/beneficiary)
        if search and not df.empty:
            search_lower = search.lower()
            mask = (
                df["label"].str.lower().str.contains(search_lower, na=False)
            )
            if "beneficiary" in df.columns:
                mask = mask | df["beneficiary"].str.lower().str.contains(search_lower, na=False)
            df = df[mask]
            # Update total after filtering
            total = len(df)

        # Convert DataFrame to list of TransactionResponse
        transactions = []
        if not df.empty:
            for _, row in df.iterrows():
                tx_data = row.to_dict()
                # Handle NaN values
                for key, value in tx_data.items():
                    if pd.isna(value):
                        tx_data[key] = None

                transactions.append(TransactionResponse(**tx_data))

        logger.info(
            f"Listed transactions: {len(transactions)} items, "
            f"total={total}, offset={offset}, limit={limit}"
        )

        return TransactionsListResponse(
            items=transactions,
            total=total,
            limit=limit,
            offset=offset,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve transactions: {str(e)}",
        )


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Get transaction by ID",
    description="Retrieve a single transaction by its ID.",
    responses={
        404: {"description": "Transaction not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_transaction(transaction_id: int) -> TransactionResponse:
    """
    Get a single transaction by its ID.

    Args:
        transaction_id: The unique identifier of the transaction

    Returns:
        TransactionResponse with transaction details

    Raises:
        HTTPException: 404 if transaction not found
    """
    try:
        transaction = get_transaction_by_id(transaction_id)

        if transaction is None:
            logger.warning(f"Transaction {transaction_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction with ID {transaction_id} not found",
            )

        # Handle NaN values
        for key, value in transaction.items():
            if pd.isna(value):
                transaction[key] = None

        return TransactionResponse(**transaction)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transaction {transaction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve transaction: {str(e)}",
        )
