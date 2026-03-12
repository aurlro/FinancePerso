"""
Accounts API Router - Bank account management.

Handles CRUD operations for bank accounts.
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

# Add FinancePerso root to path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from modules.db.connection import get_db_connection
from modules.logger import logger

from models.schemas import (
    AccountCreateRequest,
    AccountUpdateRequest,
    AccountResponse,
    AccountsListResponse,
    ErrorResponse,
)

# Import auth dependencies
from routers.auth import get_current_user, UserResponse

router = APIRouter(tags=["Accounts"])


def init_accounts_tables():
    """Initialize accounts tables if they don't exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Households table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS households (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Accounts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bank_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                bank_name TEXT,
                account_type TEXT NOT NULL,
                balance REAL DEFAULT 0.0,
                household_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (household_id) REFERENCES households(id)
            )
        """)
        
        conn.commit()
        logger.info("Accounts tables initialized")


@router.get(
    "",
    response_model=AccountsListResponse,
    summary="List accounts",
    description="Get all bank accounts for the current user.",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        500: {"description": "Internal server error"},
    }
)
async def list_accounts(
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> AccountsListResponse:
    """
    Get all bank accounts for the current user.
    
    Returns:
        List of bank accounts
    """
    init_accounts_tables()
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get user's household_id
            cursor.execute(
                "SELECT household_id FROM api_users WHERE id = ?",
                (current_user.id,)
            )
            result = cursor.fetchone()
            household_id = result[0] if result else None
            
            # Get accounts for the household or user
            if household_id:
                cursor.execute(
                    """
                    SELECT id, name, bank_name, account_type, balance, 
                           household_id, created_at, updated_at
                    FROM bank_accounts
                    WHERE household_id = ?
                    ORDER BY created_at DESC
                    """,
                    (household_id,)
                )
            else:
                # If no household, return empty list
                # In future, could support personal accounts without household
                cursor.execute(
                    """
                    SELECT id, name, bank_name, account_type, balance, 
                           household_id, created_at, updated_at
                    FROM bank_accounts
                    WHERE 1=0
                    """
                )
            
            rows = cursor.fetchall()
            
            accounts = []
            for row in rows:
                accounts.append(AccountResponse(
                    id=row[0],
                    name=row[1],
                    bank_name=row[2],
                    account_type=row[3],
                    balance=row[4] or 0.0,
                    household_id=row[5],
                    created_at=row[6],
                    updated_at=row[7],
                ))
            
            logger.info(f"Listed {len(accounts)} accounts for user {current_user.id}")
            
            return AccountsListResponse(
                items=accounts,
                total=len(accounts)
            )
            
    except Exception as e:
        logger.error(f"Error listing accounts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve accounts: {str(e)}"
        )


@router.post(
    "",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create account",
    description="Create a new bank account.",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        400: {"model": ErrorResponse, "description": "Invalid data"},
        500: {"description": "Internal server error"},
    }
)
async def create_account(
    request: AccountCreateRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> AccountResponse:
    """
    Create a new bank account.
    
    Args:
        request: Account creation data
    
    Returns:
        Created account information
    """
    init_accounts_tables()
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get user's household_id or create one
            cursor.execute(
                "SELECT household_id FROM api_users WHERE id = ?",
                (current_user.id,)
            )
            result = cursor.fetchone()
            household_id = result[0] if result and result[0] else None
            
            # If no household, create one
            if not household_id:
                cursor.execute(
                    "INSERT INTO households (name) VALUES (?)",
                    (f"Foyer de {current_user.name}",)
                )
                household_id = cursor.lastrowid
                
                # Update user with household
                cursor.execute(
                    "UPDATE api_users SET household_id = ? WHERE id = ?",
                    (household_id, current_user.id)
                )
            
            # Create account
            now = datetime.utcnow().isoformat()
            cursor.execute(
                """
                INSERT INTO bank_accounts (name, bank_name, account_type, balance, household_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request.name,
                    request.bank_name,
                    request.account_type.value,
                    request.balance,
                    household_id,
                    now,
                    now,
                )
            )
            conn.commit()
            
            account_id = cursor.lastrowid
            
            logger.info(f"Created account {account_id} for user {current_user.id}")
            
            return AccountResponse(
                id=account_id,
                name=request.name,
                bank_name=request.bank_name,
                account_type=request.account_type.value,
                balance=request.balance,
                household_id=household_id,
                created_at=now,
                updated_at=now,
            )
            
    except sqlite3.IntegrityError as e:
        logger.error(f"Integrity error creating account: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account with this name already exists"
        )
    except Exception as e:
        logger.error(f"Error creating account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create account: {str(e)}"
        )


@router.get(
    "/{account_id}",
    response_model=AccountResponse,
    summary="Get account",
    description="Get a specific bank account by ID.",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Account not found"},
        500: {"description": "Internal server error"},
    }
)
async def get_account(
    account_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> AccountResponse:
    """
    Get a specific bank account by ID.
    
    Args:
        account_id: Account ID
    
    Returns:
        Account information
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get user's household_id
            cursor.execute(
                "SELECT household_id FROM api_users WHERE id = ?",
                (current_user.id,)
            )
            result = cursor.fetchone()
            household_id = result[0] if result else None
            
            # Get account
            cursor.execute(
                """
                SELECT id, name, bank_name, account_type, balance, 
                       household_id, created_at, updated_at
                FROM bank_accounts
                WHERE id = ? AND (household_id = ? OR household_id IS NULL)
                """,
                (account_id, household_id)
            )
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Account not found"
                )
            
            return AccountResponse(
                id=row[0],
                name=row[1],
                bank_name=row[2],
                account_type=row[3],
                balance=row[4] or 0.0,
                household_id=row[5],
                created_at=row[6],
                updated_at=row[7],
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting account {account_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve account: {str(e)}"
        )


@router.put(
    "/{account_id}",
    response_model=AccountResponse,
    summary="Update account",
    description="Update a bank account.",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Account not found"},
        400: {"model": ErrorResponse, "description": "Invalid data"},
        500: {"description": "Internal server error"},
    }
)
async def update_account(
    account_id: int,
    request: AccountUpdateRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> AccountResponse:
    """
    Update a bank account.
    
    Args:
        account_id: Account ID
        request: Account update data
    
    Returns:
        Updated account information
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get user's household_id
            cursor.execute(
                "SELECT household_id FROM api_users WHERE id = ?",
                (current_user.id,)
            )
            result = cursor.fetchone()
            household_id = result[0] if result else None
            
            # Check account exists and belongs to user's household
            cursor.execute(
                "SELECT id FROM bank_accounts WHERE id = ? AND household_id = ?",
                (account_id, household_id)
            )
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Account not found"
                )
            
            # Build update query dynamically
            updates = []
            params = []
            
            if request.name is not None:
                updates.append("name = ?")
                params.append(request.name)
            if request.bank_name is not None:
                updates.append("bank_name = ?")
                params.append(request.bank_name)
            if request.account_type is not None:
                updates.append("account_type = ?")
                params.append(request.account_type.value)
            if request.balance is not None:
                updates.append("balance = ?")
                params.append(request.balance)
            
            if not updates:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields to update"
                )
            
            updates.append("updated_at = ?")
            params.append(datetime.utcnow().isoformat())
            params.append(account_id)
            
            cursor.execute(
                f"UPDATE bank_accounts SET {', '.join(updates)} WHERE id = ?",
                params
            )
            conn.commit()
            
            logger.info(f"Updated account {account_id}")
            
            # Return updated account
            cursor.execute(
                """
                SELECT id, name, bank_name, account_type, balance, 
                       household_id, created_at, updated_at
                FROM bank_accounts
                WHERE id = ?
                """,
                (account_id,)
            )
            row = cursor.fetchone()
            
            return AccountResponse(
                id=row[0],
                name=row[1],
                bank_name=row[2],
                account_type=row[3],
                balance=row[4] or 0.0,
                household_id=row[5],
                created_at=row[6],
                updated_at=row[7],
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating account {account_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update account: {str(e)}"
        )


@router.delete(
    "/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete account",
    description="Delete a bank account.",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Account not found"},
        500: {"description": "Internal server error"},
    }
)
async def delete_account(
    account_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> None:
    """
    Delete a bank account.
    
    Args:
        account_id: Account ID to delete
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get user's household_id
            cursor.execute(
                "SELECT household_id FROM api_users WHERE id = ?",
                (current_user.id,)
            )
            result = cursor.fetchone()
            household_id = result[0] if result else None
            
            # Check account exists and belongs to user's household
            cursor.execute(
                "SELECT id FROM bank_accounts WHERE id = ? AND household_id = ?",
                (account_id, household_id)
            )
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Account not found"
                )
            
            # Delete account
            cursor.execute(
                "DELETE FROM bank_accounts WHERE id = ?",
                (account_id,)
            )
            conn.commit()
            
            logger.info(f"Deleted account {account_id}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting account {account_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete account: {str(e)}"
        )
