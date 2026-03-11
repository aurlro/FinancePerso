"""
CSV Import Router - Import bank statements from CSV files.

Handles:
- CSV parsing with various formats
- Column mapping (date, label, amount)
- Duplicate detection via transaction hash
- Internal transfer detection
- Auto-categorization via rules
- Auto-attribution to household members
"""

import csv
import hashlib
import io
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status

# Add FinancePerso root to path for importing modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from modules.db.connection import get_db_connection
from modules.logger import logger

from models.schemas import (
    ImportRequest,
    ImportResponse,
    ImportResultItem,
    CsvMapping,
    ErrorResponse,
)

from routers.auth import get_current_user, UserResponse

router = APIRouter(tags=["Import"])


def parse_csv_content(content: str) -> tuple[list[str], list[dict]]:
    """
    Parse CSV content and return headers and rows.
    
    Auto-detects separator (; , or tab) and handles quoted values.
    """
    # Detect separator from first line
    first_line = content.split("\n")[0] if content else ""
    if ";" in first_line:
        delimiter = ";"
    elif "\t" in first_line:
        delimiter = "\t"
    else:
        delimiter = ","
    
    # Parse CSV
    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
    headers = reader.fieldnames or []
    rows = list(reader)
    
    return headers, rows


def parse_date(value: str) -> Optional[str]:
    """
    Parse a date string in common French bank formats.
    Returns ISO format (YYYY-MM-DD) or None if invalid.
    """
    value = value.strip()
    if not value:
        return None
    
    # DD/MM/YYYY or DD-MM-YYYY
    dmy = re.match(r"^(\d{2})[/\-.](\d{2})[/\-.](\d{4})$", value)
    if dmy:
        return f"{dmy.group(3)}-{dmy.group(2)}-{dmy.group(1)}"
    
    # YYYY-MM-DD (ISO)
    iso = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", value)
    if iso:
        return value
    
    return None


def parse_amount(value: str) -> Optional[float]:
    """
    Parse amount: handles French format (1 234,56) and standard (1234.56).
    Returns float or None if invalid.
    """
    if not value or not value.strip():
        return None
    
    cleaned = value.replace(" ", "").replace("€", "").strip()
    
    # French decimal comma (e.g., "1.234,56" or "1234,56")
    if "," in cleaned:
        if "." in cleaned and cleaned.find(",") > cleaned.find("."):
            # Format: 1.234,56 → remove dots, replace comma
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            # Format: 1234,56 → just replace comma
            cleaned = cleaned.replace(",", ".")
    
    try:
        return float(cleaned)
    except ValueError:
        return None


def compute_tx_hash(date: str, label: str, amount: float) -> str:
    """
    Compute a unique hash for a transaction to detect duplicates.
    """
    data = f"{date}|{label.strip().lower()}|{amount:.2f}"
    return hashlib.md5(data.encode()).hexdigest()


def get_existing_hashes(conn, hashes: list[str]) -> set[str]:
    """
    Get set of existing transaction hashes from database.
    """
    if not hashes:
        return set()
    
    cursor = conn.cursor()
    # SQLite doesn't support IN with many parameters well, so chunk it
    existing = set()
    chunk_size = 900  # SQLite max parameters is 999
    
    for i in range(0, len(hashes), chunk_size):
        chunk = hashes[i:i + chunk_size]
        placeholders = ",".join(["?"] * len(chunk))
        cursor.execute(
            f"SELECT tx_hash FROM transactions WHERE tx_hash IN ({placeholders})",
            chunk
        )
        existing.update(row[0] for row in cursor.fetchall())
    
    return existing


def init_rules_tables(conn):
    """Initialize rules tables if they don't exist."""
    cursor = conn.cursor()
    
    # Categorization rules table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorization_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            pattern TEXT NOT NULL,
            pattern_type TEXT DEFAULT 'contains',
            category_id INTEGER,
            priority INTEGER DEFAULT 10,
            is_active INTEGER DEFAULT 1,
            match_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Attribution rules table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attribution_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            pattern TEXT NOT NULL,
            pattern_type TEXT DEFAULT 'contains',
            member_id INTEGER,
            household_id INTEGER,
            priority INTEGER DEFAULT 10,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()


def get_category_for_label(conn, label: str) -> Optional[tuple[int, str]]:
    """
    Find matching category for a label using categorization rules.
    Returns (category_id, category_name) or None.
    """
    cursor = conn.cursor()
    
    # Initialize tables
    init_rules_tables(conn)
    
    # Get all active rules ordered by priority
    cursor.execute("""
        SELECT id, pattern, pattern_type, category_id, priority
        FROM categorization_rules
        WHERE is_active = 1
        ORDER BY priority DESC, id ASC
    """)
    rules = cursor.fetchall()
    
    label_lower = label.lower()
    
    for rule in rules:
        _, pattern, pattern_type, category_id, _ = rule
        pattern_lower = pattern.lower()
        
        matched = False
        if pattern_type == "contains":
            matched = pattern_lower in label_lower
        elif pattern_type == "exact":
            matched = pattern_lower == label_lower
        elif pattern_type == "starts_with":
            matched = label_lower.startswith(pattern_lower)
        elif pattern_type == "ends_with":
            matched = label_lower.endswith(pattern_lower)
        elif pattern_type == "regex":
            try:
                matched = bool(re.search(pattern, label, re.IGNORECASE))
            except re.error:
                continue
        
        if matched:
            # Get category name
            cursor.execute("SELECT name FROM categories WHERE id = ?", (category_id,))
            cat_row = cursor.fetchone()
            if cat_row:
                return (category_id, cat_row[0])
    
    return None


def detect_transfers(new_transactions: list[dict]) -> set[int]:
    """
    Detect internal transfers within a batch of new transactions.
    Returns set of indices that are transfers.
    """
    transfer_indices = set()
    
    # Look for pairs with opposite amounts on same date
    for i, tx1 in enumerate(new_transactions):
        if i in transfer_indices:
            continue
        for j, tx2 in enumerate(new_transactions[i+1:], i+1):
            if j in transfer_indices:
                continue
            if (tx1.get("date") == tx2.get("date") and
                tx1.get("amount") == -tx2.get("amount") and
                tx1.get("amount", 0) != 0):
                transfer_indices.add(i)
                transfer_indices.add(j)
                break
    
    return transfer_indices


@router.post(
    "/import",
    response_model=ImportResponse,
    summary="Import CSV transactions",
    description="Import transactions from a CSV file.",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        400: {"model": ErrorResponse, "description": "Invalid data"},
        404: {"model": ErrorResponse, "description": "Account not found"},
        500: {"description": "Internal server error"},
    }
)
async def import_csv(
    request: ImportRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> ImportResponse:
    """
    Import transactions from CSV content.
    
    Args:
        request: Import configuration including CSV content and column mapping
    
    Returns:
        Import results with counts and per-row status
    """
    logger.info(f"Starting CSV import for user {current_user.id}, account {request.account_id}")
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verify account exists and belongs to user's household
            cursor.execute(
                "SELECT id, account_type FROM bank_accounts WHERE id = ?",
                (request.account_id,)
            )
            account_row = cursor.fetchone()
            if not account_row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Account not found"
                )
            
            account_type = account_row[1]
            
            # Parse CSV
            try:
                headers, rows = parse_csv_content(request.csv_content)
            except Exception as e:
                logger.error(f"CSV parsing error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to parse CSV: {str(e)}"
                )
            
            if not rows:
                return ImportResponse(
                    total_rows=0,
                    imported=0,
                    duplicates=0,
                    errors=0,
                    transactions=[],
                )
            
            # Validate mapping columns exist
            mapping = request.mapping
            required_cols = [mapping.date_column, mapping.label_column]
            if mapping.use_debit_credit:
                required_cols.extend([mapping.debit_column, mapping.credit_column])
            else:
                required_cols.append(mapping.amount_column)
            
            missing_cols = [col for col in required_cols if col and col not in headers]
            if missing_cols:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing columns in CSV: {', '.join(missing_cols)}"
                )
            
            # Process rows
            transactions = []
            hashes = []
            
            for idx, row in enumerate(rows):
                # Extract values
                date_str = row.get(mapping.date_column, "").strip()
                label = row.get(mapping.label_column, "").strip()
                
                if mapping.use_debit_credit:
                    debit_str = row.get(mapping.debit_column or "", "").strip()
                    credit_str = row.get(mapping.credit_column or "", "").strip()
                    
                    debit = parse_amount(debit_str) if debit_str else None
                    credit = parse_amount(credit_str) if credit_str else None
                    
                    if debit and debit != 0:
                        amount = -abs(debit)  # Expense (negative)
                    elif credit and credit != 0:
                        amount = abs(credit)  # Income (positive)
                    else:
                        amount = 0
                else:
                    amount_str = row.get(mapping.amount_column or "", "").strip()
                    amount = parse_amount(amount_str) or 0
                
                # Parse date
                date = parse_date(date_str)
                
                # Skip empty rows
                if not label or not date or amount == 0:
                    continue
                
                # Compute hash for duplicate detection
                tx_hash = compute_tx_hash(date, label, amount)
                
                transactions.append({
                    "row_index": idx,
                    "date": date,
                    "label": label,
                    "amount": amount,
                    "hash": tx_hash,
                    "raw_data": row,
                })
                hashes.append(tx_hash)
            
            # Check for existing duplicates
            existing_hashes = get_existing_hashes(conn, hashes) if request.skip_duplicates else set()
            
            # Get auto-categorization for each transaction
            for tx in transactions:
                category = get_category_for_label(conn, tx["label"])
                tx["category"] = category
            
            # Detect internal transfers within the batch
            transfer_indices = detect_transfers(transactions)
            
            # Insert transactions
            results = []
            imported_count = 0
            duplicate_count = 0
            error_count = 0
            inserted_ids = []
            
            now = datetime.utcnow().isoformat()
            
            for idx, tx in enumerate(transactions):
                row_idx = tx["row_index"]
                
                # Check for duplicate
                if tx["hash"] in existing_hashes:
                    results.append(ImportResultItem(
                        row_index=row_idx,
                        status="duplicate",
                        label=tx["label"],
                        amount=tx["amount"],
                    ))
                    duplicate_count += 1
                    continue
                
                try:
                    # Determine if this is a transfer
                    is_transfer = idx in transfer_indices
                    
                    # Insert transaction
                    category_id = tx["category"][0] if tx["category"] else None
                    
                    cursor.execute("""
                        INSERT INTO transactions 
                        (date, label, amount, account_id, category_validated, 
                         tx_hash, is_internal_transfer, status, import_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        tx["date"],
                        tx["label"],
                        tx["amount"],
                        str(request.account_id),  # account_id is TEXT in DB
                        category_id,
                        tx["hash"],
                        is_transfer,
                        "pending",  # Will be validated later
                        now,
                    ))
                    
                    tx_id = cursor.lastrowid
                    inserted_ids.append(tx_id)
                    
                    results.append(ImportResultItem(
                        row_index=row_idx,
                        status="imported",
                        transaction_id=tx_id,
                        label=tx["label"],
                        amount=tx["amount"],
                    ))
                    imported_count += 1
                    
                except Exception as e:
                    logger.error(f"Error inserting transaction: {e}")
                    results.append(ImportResultItem(
                        row_index=row_idx,
                        status="error",
                        error_message=str(e),
                        label=tx["label"],
                        amount=tx["amount"],
                    ))
                    error_count += 1
            
            # Get household members for attribution
            cursor.execute(
                "SELECT household_id FROM api_users WHERE id = ?",
                (current_user.id,)
            )
            household_row = cursor.fetchone()
            household_id = household_row[0] if household_row else None
            
            # Create household_members table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS household_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT,
                    user_id INTEGER,
                    household_id INTEGER,
                    card_identifier TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            
            attributed_count = 0
            if household_id and inserted_ids:
                # Get members with card identifiers
                cursor.execute("""
                    SELECT id, name, card_identifier
                    FROM household_members
                    WHERE household_id = ? AND card_identifier IS NOT NULL
                """, (household_id,))
                members = cursor.fetchall()
                
                # Get attribution rules
                cursor.execute("""
                    SELECT pattern, member_id
                    FROM attribution_rules
                    WHERE household_id = ? AND is_active = 1
                    ORDER BY priority DESC
                """, (household_id,))
                attr_rules = cursor.fetchall()
                
                # Get inserted transactions for attribution
                cursor.execute("""
                    SELECT id, label
                    FROM transactions
                    WHERE id IN ({})
                """.format(",".join(["?"] * len(inserted_ids))),
                inserted_ids)
                
                new_txs = cursor.fetchall()
                
                # Attribution logic
                to_attribute = {}  # tx_id -> member_id
                
                for tx_id, label in new_txs:
                    label_lower = label.lower()
                    
                    # 1. Try card identifier matching
                    for member_id, member_name, card_id in members:
                        if card_id and card_id.lower() in label_lower:
                            to_attribute[tx_id] = member_id
                            break
                    
                    # 2. Try attribution rules
                    if tx_id not in to_attribute:
                        for pattern, member_id in attr_rules:
                            if pattern.lower() in label_lower:
                                to_attribute[tx_id] = member_id
                                break
                
                # Apply attributions
                if to_attribute:
                    for tx_id, member_id in to_attribute.items():
                        cursor.execute("""
                            UPDATE transactions
                            SET member = (SELECT name FROM household_members WHERE id = ?)
                            WHERE id = ?
                        """, (member_id, tx_id))
                    
                    attributed_count = len(to_attribute)
                    logger.info(f"Auto-attributed {attributed_count} transactions")
            
            conn.commit()
            
            logger.info(
                f"Import completed: {imported_count} imported, "
                f"{duplicate_count} duplicates, {error_count} errors, "
                f"{len(transfer_indices)} transfers detected"
            )
            
            return ImportResponse(
                total_rows=len(rows),
                imported=imported_count,
                duplicates=duplicate_count,
                errors=error_count,
                transactions=results,
                transfer_detected_count=len(transfer_indices),
                attributed_count=attributed_count,
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Import error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )
