"""
Export API Router (PR #8)
Handles CSV and PDF exports of transactions and reports.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import csv
import io
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse

from modules.db.connection import get_db_connection
from modules.db.transactions import get_all_transactions
from modules.logger import logger

from models.schemas import UserResponse
from routers.auth import get_current_user

router = APIRouter(tags=["Export"])


@router.get(
    "/transactions/csv",
    summary="Export transactions CSV",
    description="Export transactions to CSV format.",
    response_class=StreamingResponse,
)
async def export_transactions_csv(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Export transactions to CSV.
    
    Returns a CSV file with all transaction data.
    """
    try:
        # Get transactions
        df = get_all_transactions()
        
        # Apply filters
        if start_date:
            df = df[df["date"] >= start_date]
        if end_date:
            df = df[df["date"] <= end_date]
        if category:
            df = df[df["category_validated"] == category]
        if status:
            df = df[df["status"] == status]
        
        if df.empty:
            raise HTTPException(
                status_code=404,
                detail="No transactions found for the given filters"
            )
        
        # Select and rename columns for export
        columns_to_export = {
            "date": "Date",
            "label": "Libellé",
            "amount": "Montant",
            "category_validated": "Catégorie",
            "status": "Statut",
            "member": "Membre",
            "account_label": "Compte",
            "beneficiary": "Bénéficiaire",
            "notes": "Notes",
            "tags": "Tags",
        }
        
        export_df = df[list(columns_to_export.keys())].copy()
        export_df.columns = list(columns_to_export.values())
        
        # Generate CSV
        output = io.StringIO()
        export_df.to_csv(output, index=False, encoding='utf-8', sep=';')
        output.seek(0)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transactions_{timestamp}.csv"
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export CSV: {str(e)}"
        )


@router.get(
    "/transactions/json",
    summary="Export transactions JSON",
    description="Export transactions to JSON format.",
)
async def export_transactions_json(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: UserResponse = Depends(get_current_user),
):
    """Export transactions to JSON."""
    try:
        df = get_all_transactions()
        
        # Apply filters
        if start_date:
            df = df[df["date"] >= start_date]
        if end_date:
            df = df[df["date"] <= end_date]
        if category:
            df = df[df["category_validated"] == category]
        if status:
            df = df[df["status"] == status]
        
        if df.empty:
            raise HTTPException(
                status_code=404,
                detail="No transactions found for the given filters"
            )
        
        # Convert to records
        records = df.to_dict(orient='records')
        
        return {
            "exported_at": datetime.now().isoformat(),
            "count": len(records),
            "filters": {
                "start_date": start_date,
                "end_date": end_date,
                "category": category,
                "status": status,
            },
            "transactions": records,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting JSON: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export JSON: {str(e)}"
        )


@router.get(
    "/report/monthly",
    summary="Monthly report",
    description="Generate a monthly financial report.",
)
async def monthly_report(
    month: str = Query(..., regex=r"^\d{4}-\d{2}$", description="Month (YYYY-MM)"),
    current_user: UserResponse = Depends(get_current_user),
):
    """Generate monthly report."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get all transactions for the month
            cursor.execute(
                """
                SELECT * FROM transactions 
                WHERE strftime('%Y-%m', date) = ?
                ORDER BY date
                """,
                (month,)
            )
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            if not rows:
                raise HTTPException(
                    status_code=404,
                    detail=f"No transactions found for {month}"
                )
            
            transactions = [dict(zip(columns, row)) for row in rows]
            
            # Calculate totals
            total_income = sum(t["amount"] for t in transactions if t["amount"] > 0)
            total_expenses = sum(abs(t["amount"]) for t in transactions if t["amount"] < 0)
            balance = total_income - total_expenses
            
            # Group by category
            categories = {}
            for t in transactions:
                cat = t.get("category_validated") or "Non catégorisé"
                if cat not in categories:
                    categories[cat] = {"income": 0, "expenses": 0, "count": 0}
                
                if t["amount"] > 0:
                    categories[cat]["income"] += t["amount"]
                else:
                    categories[cat]["expenses"] += abs(t["amount"])
                categories[cat]["count"] += 1
            
            # Sort by expenses (descending)
            sorted_categories = dict(sorted(
                categories.items(), 
                key=lambda x: x[1]["expenses"], 
                reverse=True
            ))
            
            return {
                "month": month,
                "generated_at": datetime.now().isoformat(),
                "summary": {
                    "total_income": round(total_income, 2),
                    "total_expenses": round(total_expenses, 2),
                    "balance": round(balance, 2),
                    "transaction_count": len(transactions),
                },
                "by_category": sorted_categories,
                "transactions": transactions[:100],  # Limit to first 100
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.get(
    "/report/annual",
    summary="Annual report",
    description="Generate an annual financial report.",
)
async def annual_report(
    year: int = Query(..., ge=2020, le=2030, description="Year (YYYY)"),
    current_user: UserResponse = Depends(get_current_user),
):
    """Generate annual report."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get all transactions for the year
            cursor.execute(
                """
                SELECT * FROM transactions 
                WHERE strftime('%Y', date) = ?
                ORDER BY date
                """,
                (str(year),)
            )
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            if not rows:
                raise HTTPException(
                    status_code=404,
                    detail=f"No transactions found for {year}"
                )
            
            transactions = [dict(zip(columns, row)) for row in rows]
            
            # Calculate yearly totals
            total_income = sum(t["amount"] for t in transactions if t["amount"] > 0)
            total_expenses = sum(abs(t["amount"]) for t in transactions if t["amount"] < 0)
            
            # Monthly breakdown
            months = {}
            for t in transactions:
                month = t["date"][:7]  # YYYY-MM
                if month not in months:
                    months[month] = {"income": 0, "expenses": 0, "count": 0}
                
                if t["amount"] > 0:
                    months[month]["income"] += t["amount"]
                else:
                    months[month]["expenses"] += abs(t["amount"])
                months[month]["count"] += 1
            
            # Sort by month
            sorted_months = dict(sorted(months.items()))
            
            # Category breakdown
            categories = {}
            for t in transactions:
                cat = t.get("category_validated") or "Non catégorisé"
                if cat not in categories:
                    categories[cat] = {"income": 0, "expenses": 0, "count": 0}
                
                if t["amount"] > 0:
                    categories[cat]["income"] += t["amount"]
                else:
                    categories[cat]["expenses"] += abs(t["amount"])
                categories[cat]["count"] += 1
            
            # Top categories by expenses
            top_categories = dict(sorted(
                categories.items(),
                key=lambda x: x[1]["expenses"],
                reverse=True
            )[:10])  # Top 10
            
            return {
                "year": year,
                "generated_at": datetime.now().isoformat(),
                "summary": {
                    "total_income": round(total_income, 2),
                    "total_expenses": round(total_expenses, 2),
                    "balance": round(total_income - total_expenses, 2),
                    "transaction_count": len(transactions),
                    "average_monthly_income": round(total_income / 12, 2),
                    "average_monthly_expenses": round(total_expenses / 12, 2),
                },
                "monthly_breakdown": sorted_months,
                "top_categories": top_categories,
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating annual report: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate annual report: {str(e)}"
        )


@router.get(
    "/backup/full",
    summary="Full backup",
    description="Export all user data as a JSON backup.",
)
async def full_backup(
    current_user: UserResponse = Depends(get_current_user),
):
    """Create full data backup."""
    try:
        backup = {
            "exported_at": datetime.now().isoformat(),
            "version": "1.0",
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "name": current_user.name,
            },
        }
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get accounts
            cursor.execute(
                "SELECT * FROM bank_accounts WHERE household_id = ?",
                (current_user.household_id,)
            )
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            backup["accounts"] = [dict(zip(columns, row)) for row in rows]
            
            # Get transactions
            df = get_all_transactions()
            backup["transactions"] = df.to_dict(orient='records')
            
            # Get categories
            cursor.execute("SELECT * FROM categories")
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            backup["categories"] = [dict(zip(columns, row)) for row in rows]
            
            # Get budgets
            cursor.execute("SELECT * FROM budgets")
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            backup["budgets"] = [dict(zip(columns, row)) for row in rows]
            
            # Get rules
            cursor.execute("SELECT * FROM learning_rules")
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            backup["rules"] = [dict(zip(columns, row)) for row in rows]
        
        return backup
        
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create backup: {str(e)}"
        )
