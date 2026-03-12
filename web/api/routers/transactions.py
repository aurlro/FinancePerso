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
    delete_transaction,
)
from modules.logger import logger

from models.schemas import (
    TransactionFilters,
    TransactionResponse,
    TransactionsListResponse,
    ErrorResponse,
)

from routers.auth import get_current_user, UserResponse

# Pydantic models for request/response
from pydantic import BaseModel, Field
from typing import Literal

class TransactionUpdateRequest(BaseModel):
    """Request model for updating a transaction."""
    label: str | None = None
    amount: float | None = None
    date: str | None = None
    category_validated: str | None = None
    status: Literal["pending", "validated"] | None = None
    member: str | None = None
    notes: str | None = None
    beneficiary: str | None = None
    tags: str | None = None

class BulkUpdateRequest(BaseModel):
    """Request model for bulk status update."""
    ids: list[int] = Field(..., description="List of transaction IDs to update")
    status: str = Field(..., description="New status value")

class BulkUpdateResponse(BaseModel):
    """Response model for bulk update."""
    updated: int
    ids: list[int]

class CategorizeRequest(BaseModel):
    """Request model for AI categorization."""
    transaction_ids: list[int] = Field(..., description="List of transaction IDs to categorize")

class CategorizeResult(BaseModel):
    """Result of AI categorization for one transaction."""
    id: int
    category: str
    confidence: float
    source: str = "ai"  # "ai", "rule", "manual"

class CategorizeResponse(BaseModel):
    """Response model for categorization."""
    categorized: list[CategorizeResult]

class DeleteResponse(BaseModel):
    """Response model for delete operation."""
    deleted: bool
    id: int

router = APIRouter(tags=["Transactions"])  # Prefix géré dans main.py


def _row_to_dict(row: tuple, columns: list[str]) -> dict:
    """Convert a database row to a dictionary, handling NaN values."""
    result = dict(zip(columns, row))
    # Handle NaN values
    for key, value in result.items():
        if pd.isna(value):
            result[key] = None
    return result


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
        Query(description="Filter by month (YYYY-MM)"),
    ] = None,
    status: Annotated[
        str | None,
        Query(description="Filter by status (pending, validated)"),
    ] = None,
    member: Annotated[
        str | None,
        Query(description="Filter by household member"),
    ] = None,
    search: Annotated[
        str | None,
        Query(description="Search in label and notes"),
    ] = None,
    current_user: UserResponse = Depends(get_current_user),
) -> TransactionsListResponse:
    """
    Get a paginated list of transactions with optional filtering.

    Args:
        limit: Number of items per page (1-1000, default 50)
        offset: Offset for pagination (default 0)
        category: Filter by category name
        month: Filter by month in YYYY-MM format
        status: Filter by status (pending, validated)
        member: Filter by household member name
        search: Search in label and notes
        current_user: The authenticated user

    Returns:
        TransactionsListResponse with paginated results

    Raises:
        HTTPException: 400 for invalid parameters, 500 for server errors
    """
    try:
        # Build filters
        filters = TransactionFilters(
            category=category,
            month=month,
            status=status,
            member=member,
            search=search,
        )

        # Get transactions using the database module
        df = get_all_transactions()

        # Apply filters
        if filters.category:
            df = df[df["category_validated"] == filters.category]
        if filters.status:
            df = df[df["status"] == filters.status]
        if filters.member:
            df = df[df["member"] == filters.member]
        if filters.month:
            df = df[df["date"].str.startswith(filters.month)]
        if filters.search:
            search_lower = filters.search.lower()
            label_match = df["label"].str.lower().str.contains(search_lower, na=False)
            notes_match = df["notes"].str.lower().str.contains(search_lower, na=False)
            df = df[label_match | notes_match]

        # Get total count before pagination
        total = len(df)

        # Apply pagination
        df = df.iloc[offset : offset + limit]

        # Convert to list of dicts, handling NaN values
        items = []
        for _, row in df.iterrows():
            item = row.to_dict()
            # Replace NaN with None for JSON serialization
            for key, value in item.items():
                if pd.isna(value):
                    item[key] = None
            items.append(item)

        logger.info(
            f"Listed transactions: offset={offset}, limit={limit}, "
            f"total={total}, returned={len(items)}"
        )

        return TransactionsListResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )

    except ValueError as e:
        logger.warning(f"Invalid filter parameters: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid filter parameters: {str(e)}",
        )
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
async def get_transaction(
    transaction_id: int,
    current_user: UserResponse = Depends(get_current_user),
) -> TransactionResponse:
    """
    Get a single transaction by its ID.

    Args:
        transaction_id: The unique identifier of the transaction
        current_user: The authenticated user

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


@router.put(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Update transaction",
    description="Update a transaction's fields.",
    responses={
        404: {"description": "Transaction not found"},
        500: {"description": "Internal server error"},
    },
)
async def update_transaction_endpoint(
    transaction_id: int,
    update_data: TransactionUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
) -> TransactionResponse:
    """
    Update a transaction by its ID.

    Args:
        transaction_id: The transaction ID to update
        update_data: Fields to update
        current_user: The authenticated user

    Returns:
        Updated transaction

    Raises:
        HTTPException: 404 if transaction not found
    """
    try:
        # Check if transaction exists
        existing = get_transaction_by_id(transaction_id)
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction with ID {transaction_id} not found",
            )

        # Build update fields dynamically
        update_fields = []
        params = []
        
        if update_data.label is not None:
            update_fields.append("label = ?")
            params.append(update_data.label)
        if update_data.amount is not None:
            update_fields.append("amount = ?")
            params.append(update_data.amount)
        if update_data.date is not None:
            update_fields.append("date = ?")
            params.append(update_data.date)
        if update_data.category_validated is not None:
            update_fields.append("category_validated = ?")
            params.append(update_data.category_validated)
        if update_data.status is not None:
            update_fields.append("status = ?")
            params.append(update_data.status)
        if update_data.member is not None:
            update_fields.append("member = ?")
            params.append(update_data.member)
        if update_data.notes is not None:
            update_fields.append("notes = ?")
            params.append(update_data.notes)
        if update_data.beneficiary is not None:
            update_fields.append("beneficiary = ?")
            params.append(update_data.beneficiary)
        if update_data.tags is not None:
            update_fields.append("tags = ?")
            params.append(update_data.tags)

        if not update_fields:
            # No fields to update, return existing
            for key, value in existing.items():
                if pd.isna(value):
                    existing[key] = None
            return TransactionResponse(**existing)

        # Add updated_at timestamp
        from datetime import datetime
        update_fields.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        
        # Add transaction_id to params
        params.append(transaction_id)

        # Execute update
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = f"UPDATE transactions SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()

        logger.info(f"Updated transaction {transaction_id}")
        
        # Clear cache
        get_all_transactions.clear()

        # Return updated transaction
        updated = get_transaction_by_id(transaction_id)
        for key, value in updated.items():
            if pd.isna(value):
                updated[key] = None
        return TransactionResponse(**updated)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating transaction {transaction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update transaction: {str(e)}",
        )


@router.delete(
    "/{transaction_id}",
    response_model=DeleteResponse,
    summary="Delete transaction",
    description="Delete a transaction permanently.",
    responses={
        404: {"description": "Transaction not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_transaction_endpoint(
    transaction_id: int,
    current_user: UserResponse = Depends(get_current_user),
) -> DeleteResponse:
    """
    Delete a transaction permanently.

    Args:
        transaction_id: The transaction ID to delete
        current_user: The authenticated user

    Returns:
        DeleteResponse with deletion status

    Raises:
        HTTPException: 404 if transaction not found
    """
    try:
        # Check if transaction exists
        existing = get_transaction_by_id(transaction_id)
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction with ID {transaction_id} not found",
            )

        # Delete permanently
        deleted_count = delete_transaction(transaction_id, permanent=True)
        
        if deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete transaction",
            )

        logger.info(f"Deleted transaction {transaction_id}")

        return DeleteResponse(deleted=True, id=transaction_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting transaction {transaction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete transaction: {str(e)}",
        )


@router.post(
    "/bulk-update",
    response_model=BulkUpdateResponse,
    summary="Bulk update transactions",
    description="Update status for multiple transactions at once.",
    responses={
        500: {"description": "Internal server error"},
    },
)
async def bulk_update_transactions(
    request: BulkUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
) -> BulkUpdateResponse:
    """
    Update status for multiple transactions.

    Args:
        request: Bulk update request with IDs and new status
        current_user: The authenticated user

    Returns:
        BulkUpdateResponse with count of updated transactions
    """
    try:
        if not request.ids:
            return BulkUpdateResponse(updated=0, ids=[])

        with get_db_connection() as conn:
            cursor = conn.cursor()
            placeholders = ",".join(["?"] * len(request.ids))
            query = f"""
                UPDATE transactions 
                SET status = ?, updated_at = datetime('now')
                WHERE id IN ({placeholders})
            """
            params = [request.status] + request.ids
            cursor.execute(query, params)
            conn.commit()
            updated_count = cursor.rowcount

        # Clear cache
        get_all_transactions.clear()

        logger.info(f"Bulk updated {updated_count} transactions to status '{request.status}'")

        return BulkUpdateResponse(updated=updated_count, ids=request.ids)

    except Exception as e:
        logger.error(f"Error bulk updating transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk update transactions: {str(e)}",
        )


@router.post(
    "/categorize",
    response_model=CategorizeResponse,
    summary="Auto-categorize transactions",
    description="Run AI categorization on pending transactions.",
    responses={
        500: {"description": "Internal server error"},
    },
)
async def categorize_transactions(
    request: CategorizeRequest,
    current_user: UserResponse = Depends(get_current_user),
) -> CategorizeResponse:
    """
    Run AI categorization on specified transactions.

    Args:
        request: Categorize request with transaction IDs
        current_user: The authenticated user

    Returns:
        CategorizeResponse with categorization results
    """
    try:
        if not request.transaction_ids:
            return CategorizeResponse(categorized=[])

        results = []
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            for tx_id in request.transaction_ids:
                # Get transaction details
                cursor.execute(
                    "SELECT label, original_category FROM transactions WHERE id = ?",
                    (tx_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    continue
                
                label, original_category = row
                
                # Simple rule-based categorization (placeholder for AI)
                # TODO: Integrate with actual AI categorization from modules.categorization
                category = original_category or "Inconnu"
                confidence = 0.5
                source = "rule"
                
                # Update transaction
                cursor.execute(
                    """
                    UPDATE transactions 
                    SET category_validated = ?, ai_confidence = ?, updated_at = datetime('now')
                    WHERE id = ?
                    """,
                    (category, confidence, tx_id)
                )
                
                results.append(CategorizeResult(
                    id=tx_id,
                    category=category,
                    confidence=confidence,
                    source=source
                ))
            
            conn.commit()

        # Clear cache
        get_all_transactions.clear()

        logger.info(f"Categorized {len(results)} transactions")

        return CategorizeResponse(categorized=results)

    except Exception as e:
        logger.error(f"Error categorizing transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to categorize transactions: {str(e)}",
        )
