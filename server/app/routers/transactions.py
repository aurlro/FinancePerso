"""
Transactions API Router
"""

from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Category, Transaction, TransactionStatus, TransactionType
from ..schemas import (
    PaginatedResponse,
    SuccessResponse,
    Transaction,
    TransactionBulkUpdate,
    TransactionCreate,
    TransactionFilters,
    TransactionResponse,
    TransactionUpdate,
)

router = APIRouter()


def generate_transaction_hash(date, amount: float, description: str, account_id: str) -> str:
    """Generate unique hash for deduplication."""
    import hashlib

    content = f"{date}:{amount}:{description}:{account_id}"
    return hashlib.sha256(content.encode()).hexdigest()


@router.get("", response_model=PaginatedResponse[Transaction])
async def list_transactions(
    filters: TransactionFilters = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    List transactions with optional filtering.
    """
    query = select(Transaction).where(Transaction.is_deleted == False)

    # Apply filters
    if filters.start_date:
        query = query.where(Transaction.date >= filters.start_date)
    if filters.end_date:
        query = query.where(Transaction.date <= filters.end_date)
    if filters.category_id:
        query = query.where(Transaction.category_id == filters.category_id)
    if filters.account_id:
        query = query.where(Transaction.account_id == filters.account_id)
    if filters.type:
        query = query.where(Transaction.type == filters.type)
    if filters.status:
        query = query.where(Transaction.status == filters.status)
    if filters.min_amount:
        query = query.where(Transaction.amount >= filters.min_amount)
    if filters.max_amount:
        query = query.where(Transaction.amount <= filters.max_amount)
    if filters.search:
        search = f"%{filters.search}%"
        query = query.where(
            or_(
                Transaction.description.ilike(search),
                Transaction.beneficiary.ilike(search),
            )
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    # Apply pagination and ordering
    query = query.order_by(desc(Transaction.date))
    query = query.offset(filters.offset).limit(filters.limit)

    # Execute query with relationships
    result = await db.execute(query)
    transactions = result.scalars().all()

    # Load relationships
    for t in transactions:
        if t.category_id:
            await db.refresh(t, ["category"])
        await db.refresh(t, ["account"])

    pages = (total + filters.limit - 1) // filters.limit

    return PaginatedResponse(
        items=transactions,
        total=total,
        page=(filters.offset // filters.limit) + 1,
        page_size=filters.limit,
        pages=pages,
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single transaction by ID.
    """
    result = await db.execute(
        select(Transaction).where(
            and_(
                Transaction.id == transaction_id,
                Transaction.is_deleted == False,
            )
        )
    )
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    return TransactionResponse(data=transaction)


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    data: TransactionCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new transaction.
    """
    # Generate hash for deduplication
    hash_value = generate_transaction_hash(
        data.date,
        data.amount,
        data.description,
        data.account_id,
    )

    # Check for duplicates
    existing = await db.execute(
        select(Transaction).where(Transaction.hash == hash_value)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate transaction detected",
        )

    transaction = Transaction(
        date=data.date,
        amount=data.amount,
        description=data.description,
        type=data.type,
        category_id=data.category_id,
        account_id=data.account_id,
        beneficiary=data.beneficiary,
        notes=data.notes,
        tags=str(data.tags) if data.tags else None,
        is_recurring=data.is_recurring,
        hash=hash_value,
    )

    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)

    return TransactionResponse(data=transaction)


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    data: TransactionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a transaction.
    """
    result = await db.execute(
        select(Transaction).where(
            and_(
                Transaction.id == transaction_id,
                Transaction.is_deleted == False,
            )
        )
    )
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)

    await db.commit()
    await db.refresh(transaction)

    return TransactionResponse(data=transaction)


@router.delete("/{transaction_id}", response_model=SuccessResponse)
async def delete_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Soft delete a transaction.
    """
    result = await db.execute(
        select(Transaction).where(
            and_(
                Transaction.id == transaction_id,
                Transaction.is_deleted == False,
            )
        )
    )
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    transaction.is_deleted = True
    transaction.deleted_at = func.now()

    await db.commit()

    return SuccessResponse(message="Transaction deleted successfully")


@router.post("/{transaction_id}/validate", response_model=TransactionResponse)
async def validate_transaction(
    transaction_id: str,
    category_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Validate a transaction and assign a category.
    """
    result = await db.execute(
        select(Transaction).where(
            and_(
                Transaction.id == transaction_id,
                Transaction.is_deleted == False,
            )
        )
    )
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    # Verify category exists
    category_result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    if not category_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    transaction.category_id = category_id
    transaction.status = TransactionStatus.VALIDATED
    transaction.is_validated = True

    await db.commit()
    await db.refresh(transaction)

    return TransactionResponse(data=transaction)


@router.post("/bulk", response_model=list[Transaction])
async def bulk_update_transactions(
    data: TransactionBulkUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Bulk update multiple transactions.
    """
    result = await db.execute(
        select(Transaction).where(
            and_(
                Transaction.id.in_(data.ids),
                Transaction.is_deleted == False,
            )
        )
    )
    transactions = result.scalars().all()

    update_count = 0
    for transaction in transactions:
        if data.category_id:
            transaction.category_id = data.category_id
        if data.status:
            transaction.status = data.status
        if data.tags:
            transaction.set_tags(data.tags)
        update_count += 1

    await db.commit()

    return transactions
