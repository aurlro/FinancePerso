"""
Accounts API Router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Account
from ..schemas import (
    Account as AccountSchema,
    AccountCreate,
    AccountResponse,
    AccountUpdate,
    SuccessResponse,
)

router = APIRouter()


@router.get("", response_model=list[AccountSchema])
async def list_accounts(
    db: AsyncSession = Depends(get_db),
):
    """
    List all accounts.
    """
    result = await db.execute(
        select(Account).order_by(Account.name)
    )
    accounts = result.scalars().all()
    return accounts


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    data: AccountCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new account.
    """
    account = Account(**data.model_dump())
    db.add(account)
    await db.commit()
    await db.refresh(account)

    return AccountResponse(data=account)


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single account by ID.
    """
    result = await db.execute(
        select(Account).where(Account.id == account_id)
    )
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    return AccountResponse(data=account)


@router.patch("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: str,
    data: AccountUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an account.
    """
    result = await db.execute(
        select(Account).where(Account.id == account_id)
    )
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)

    await db.commit()
    await db.refresh(account)

    return AccountResponse(data=account)


@router.delete("/{account_id}", response_model=SuccessResponse)
async def delete_account(
    account_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an account.
    """
    result = await db.execute(
        select(Account).where(Account.id == account_id)
    )
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    await db.delete(account)
    await db.commit()

    return SuccessResponse(message="Account deleted successfully")
