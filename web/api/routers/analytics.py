"""
Advanced Analytics API Router (PR #9)
Handles predictions, trends, anomaly detection, and insights.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query

from modules.ai.anomaly_detector import detect_amount_anomalies
from modules.cashflow.predictor import predict_monthly_cashflow
from modules.cashflow.recurring import detect_recurring_transactions
from modules.db.connection import get_db_connection
from modules.db.transactions import get_all_transactions
from modules.logger import logger

from models.schemas import UserResponse
from routers.auth import get_current_user

router = APIRouter(tags=["Analytics"])


# ============================================================================
# Anomaly Detection
# ============================================================================

@router.get("/anomalies")
async def get_anomalies(
    threshold: float = Query(2.0, ge=1.0, le=5.0, description="Standard deviations threshold"),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Detect anomalous transactions based on amount patterns.
    
    Returns transactions with unusual amounts compared to historical patterns
    for the same merchant/category.
    """
    try:
        df = get_all_transactions()
        if df.empty:
            return {"anomalies": [], "total_checked": 0}
        
        anomalies = detect_amount_anomalies(df, threshold_sigma=threshold)
        
        # Convert to serializable format
        result = []
        for anomaly in anomalies:
            rows = anomaly.get("rows", pd.DataFrame())
            transactions = []
            if not rows.empty:
                for _, row in rows.iterrows():
                    transactions.append({
                        "id": int(row.get("id", 0)),
                        "date": str(row.get("date", "")),
                        "label": str(row.get("label", "")),
                        "amount": float(row.get("amount", 0)),
                        "category": str(row.get("category_validated", "")),
                    })
            
            mean, std = anomaly.get("expected_range", (0, 0))
            result.append({
                "type": anomaly.get("type", "Anomalie"),
                "label": anomaly.get("label", ""),
                "details": anomaly.get("details", ""),
                "expected_mean": round(mean, 2),
                "expected_std": round(std, 2),
                "transactions": transactions,
                "transaction_count": len(transactions),
            })
        
        return {
            "anomalies": result,
            "total_checked": len(df),
            "threshold_sigma": threshold,
            "generated_at": datetime.now().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to detect anomalies: {str(e)}")


# ============================================================================
# Cashflow Predictions
# ============================================================================

@router.get("/predictions/cashflow")
async def get_cashflow_predictions(
    months_ahead: int = Query(3, ge=1, le=12, description="Number of months to predict"),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Predict future cashflow for upcoming months.
    
    Uses recurring transaction detection and historical patterns to project
    income, expenses, and balance.
    """
    try:
        predictions = predict_monthly_cashflow(months_ahead=months_ahead)
        
        result = []
        for pred in predictions:
            result.append({
                "start_date": pred.start_date.isoformat(),
                "end_date": pred.end_date.isoformat(),
                "starting_balance": round(pred.starting_balance, 2),
                "predicted_income": round(pred.predicted_income, 2),
                "predicted_expenses": round(pred.predicted_expenses, 2),
                "predicted_balance": round(pred.predicted_balance, 2),
                "confidence": round(pred.confidence, 2),
                "warnings": pred.warnings,
            })
        
        return {
            "predictions": result,
            "months_ahead": months_ahead,
            "generated_at": datetime.now().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Error predicting cashflow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to predict cashflow: {str(e)}")


# ============================================================================
# Recurring Transactions
# ============================================================================

@router.get("/recurring")
async def get_recurring_transactions(
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Detect and list recurring transactions.
    
    Identifies regular income and expense patterns (subscriptions, salary, etc.)
    """
    try:
        recurring = detect_recurring_transactions()
        
        result = []
        for item in recurring:
            result.append({
                "label": item.get("label", ""),
                "category": item.get("category", ""),
                "amount": round(item.get("amount", 0), 2),
                "frequency": item.get("frequency", ""),
                "confidence": round(item.get("confidence", 0), 2),
                "occurrence_count": item.get("occurrence_count", 0),
                "first_seen": item.get("first_seen", ""),
                "last_seen": item.get("last_seen", ""),
            })
        
        return {
            "recurring": result,
            "total_count": len(result),
            "generated_at": datetime.now().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Error detecting recurring: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to detect recurring: {str(e)}")


# ============================================================================
# Category Trends
# ============================================================================

@router.get("/trends/categories")
async def get_category_trends(
    months: int = Query(6, ge=3, le=24, description="Number of months to analyze"),
    category: Optional[str] = Query(None, description="Specific category (optional)"),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Analyze spending trends by category over time.
    
    Returns trend direction (increasing/decreasing/stable) and statistics
    for each category or a specific category.
    """
    try:
        df = get_all_transactions()
        if df.empty:
            return {"trends": [], "months_analyzed": months}
        
        # Filter by date range
        start_date = (datetime.now() - timedelta(days=30 * months)).strftime("%Y-%m-%d")
        df = df[df["date"] >= start_date]
        
        if category:
            df = df[df["category_validated"] == category]
        
        # Simple trend analysis by comparing recent vs older months
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M")
        
        # Group by category and month
        expenses = df[df["amount"] < 0].copy()
        expenses["abs_amount"] = expenses["amount"].abs()
        
        # Calculate monthly averages by category
        category_monthly = expenses.groupby(["category_validated", "month"])["abs_amount"].sum().reset_index()
        
        result = []
        for cat in category_monthly["category_validated"].unique():
            cat_data = category_monthly[category_monthly["category_validated"] == cat]
            if len(cat_data) >= 2:
                recent = cat_data.tail(2)["abs_amount"].mean()
                older = cat_data.head(len(cat_data) - 2)["abs_amount"].mean() if len(cat_data) > 2 else recent
                
                if older > 0:
                    change_pct = ((recent - older) / older) * 100
                else:
                    change_pct = 0
                
                # Determine trend
                if change_pct > 10:
                    trend = "increasing"
                elif change_pct < -10:
                    trend = "decreasing"
                else:
                    trend = "stable"
                
                result.append({
                    "category": cat,
                    "trend": trend,
                    "avg_monthly": round(cat_data["abs_amount"].mean(), 2),
                    "current_month": round(cat_data.tail(1)["abs_amount"].values[0], 2),
                    "change_percent": round(change_pct, 2),
                })
        
        # Sort by absolute change
        result.sort(key=lambda x: abs(x["change_percent"]), reverse=True)
        
        return {
            "trends": result,
            "months_analyzed": months,
            "categories_count": len(result),
            "generated_at": datetime.now().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Error analyzing trends: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze trends: {str(e)}")


# ============================================================================
# Seasonality Analysis
# ============================================================================

@router.get("/seasonality")
async def get_seasonality(
    category: Optional[str] = Query(None, description="Filter by category"),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Detect seasonal patterns in spending.
    
    Identifies which months have higher/lower spending and recurring annual patterns.
    """
    try:
        df = get_all_transactions()
        if df.empty:
            return {"seasonality": {}, "has_pattern": False}
        
        if category:
            df = df[df["category_validated"] == category]
        
        # Simple seasonality analysis by month
        df["month"] = pd.to_datetime(df["date"]).dt.month
        monthly = df.groupby("month")["amount"].apply(lambda x: abs(x[x < 0]).sum()).to_dict()
        
        # Find peak and low months
        if monthly:
            max_month = max(monthly, key=monthly.get)
            min_month = min(monthly, key=monthly.get)
            peak_months = [max_month] if max_month else []
            low_months = [min_month] if min_month else []
        else:
            peak_months = []
            low_months = []
        
        return {
            "seasonality": {str(k): round(v, 2) for k, v in monthly.items()},
            "peak_months": peak_months,
            "low_months": low_months,
            "has_pattern": len(monthly) > 3,
            "category": category,
            "generated_at": datetime.now().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Error analyzing seasonality: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze seasonality: {str(e)}")


# ============================================================================
# Spending Insights
# ============================================================================

@router.get("/insights")
async def get_spending_insights(
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Get AI-powered spending insights and recommendations.
    
    Returns actionable insights about spending patterns and suggestions
    for optimization.
    """
    try:
        df = get_all_transactions()
        if df.empty:
            return {"insights": [], "score": 0}
        
        # Calculate various metrics
        total_income = df[df["amount"] > 0]["amount"].sum()
        total_expenses = abs(df[df["amount"] < 0]["amount"].sum())
        savings_rate = (total_income - total_expenses) / total_income if total_income > 0 else 0
        
        # Category breakdown
        expenses_by_category = df[df["amount"] < 0].groupby("category_validated")["amount"].sum().abs().sort_values(ascending=False)
        top_categories = expenses_by_category.head(5).to_dict()
        
        # Generate insights
        insights = []
        
        # Savings rate insight
        if savings_rate < 0:
            insights.append({
                "type": "warning",
                "title": "Dépenses supérieures aux revenus",
                "message": f"Vous dépensez {abs(savings_rate)*100:.1f}% de plus que vos revenus. Envisagez de réduire vos dépenses.",
                "priority": "high",
            })
        elif savings_rate < 0.1:
            insights.append({
                "type": "info",
                "title": "Taux d'épargne faible",
                "message": f"Votre taux d'épargne est de {savings_rate*100:.1f}%. Essayez d'atteindre au moins 20%.",
                "priority": "medium",
            })
        else:
            insights.append({
                "type": "success",
                "title": "Bon taux d'épargne",
                "message": f"Excellent ! Vous épargnez {savings_rate*100:.1f}% de vos revenus.",
                "priority": "low",
            })
        
        # Top spending category
        if top_categories:
            top_cat = list(top_categories.keys())[0]
            top_amount = list(top_categories.values())[0]
            top_percent = (top_amount / total_expenses) * 100 if total_expenses > 0 else 0
            
            if top_percent > 40:
                insights.append({
                    "type": "warning",
                    "title": f"Dépenses concentrées en '{top_cat}'",
                    "message": f"{top_percent:.1f}% de vos dépenses vont dans cette catégorie. Diversifiez ou réduisez.",
                    "priority": "medium",
                })
        
        # Transaction count trend
        df["month"] = pd.to_datetime(df["date"]).dt.to_period("M")
        monthly_counts = df.groupby("month").size()
        if len(monthly_counts) >= 2:
            recent_avg = monthly_counts.tail(3).mean()
            older_avg = monthly_counts.head(len(monthly_counts)-3).mean() if len(monthly_counts) > 3 else monthly_counts.iloc[0]
            
            if recent_avg > older_avg * 1.2:
                insights.append({
                    "type": "info",
                    "title": "Augmentation du nombre de transactions",
                    "message": "Vous faites plus de transactions qu'auparavant. Cela peut indiquer une fragmentation des dépenses.",
                    "priority": "low",
                })
        
        # Financial health score (0-100)
        score = min(100, max(0, int(savings_rate * 200) + 50))
        if savings_rate < 0:
            score = max(0, int(50 + savings_rate * 100))
        
        return {
            "insights": insights,
            "score": score,
            "metrics": {
                "total_income": round(total_income, 2),
                "total_expenses": round(total_expenses, 2),
                "savings_rate": round(savings_rate * 100, 2),
                "transaction_count": len(df),
            },
            "top_expense_categories": {k: round(v, 2) for k, v in top_categories.items()},
            "generated_at": datetime.now().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")


# ============================================================================
# Comparison with Previous Periods
# ============================================================================

@router.get("/comparison")
async def get_period_comparison(
    period: str = Query("month", regex="^(month|quarter|year)$"),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Compare current period with previous period.
    
    Returns side-by-side comparison of income, expenses, and categories.
    """
    try:
        df = get_all_transactions()
        if df.empty:
            return {"comparison": {}, "has_data": False}
        
        df["date"] = pd.to_datetime(df["date"])
        now = datetime.now()
        
        # Define periods
        if period == "month":
            current_start = now.replace(day=1)
            previous_start = (current_start - timedelta(days=1)).replace(day=1)
            previous_end = current_start - timedelta(days=1)
        elif period == "quarter":
            quarter = (now.month - 1) // 3
            current_start = now.replace(month=quarter*3+1, day=1)
            previous_start = (current_start - timedelta(days=1)).replace(day=1)
            previous_start = previous_start.replace(month=((quarter-1)%4)*3+1)
            previous_end = current_start - timedelta(days=1)
        else:  # year
            current_start = now.replace(month=1, day=1)
            previous_start = current_start.replace(year=current_start.year-1)
            previous_end = current_start - timedelta(days=1)
        
        # Filter data
        current_df = df[df["date"] >= current_start]
        previous_df = df[(df["date"] >= previous_start) & (df["date"] <= previous_end)]
        
        # Calculate metrics
        def calc_metrics(subdf):
            income = subdf[subdf["amount"] > 0]["amount"].sum()
            expenses = abs(subdf[subdf["amount"] < 0]["amount"].sum())
            return {
                "income": round(income, 2),
                "expenses": round(expenses, 2),
                "balance": round(income - expenses, 2),
                "transaction_count": len(subdf),
            }
        
        current_metrics = calc_metrics(current_df)
        previous_metrics = calc_metrics(previous_df)
        
        # Calculate changes
        changes = {}
        for key in ["income", "expenses", "balance"]:
            if previous_metrics[key] != 0:
                changes[key] = round(((current_metrics[key] - previous_metrics[key]) / abs(previous_metrics[key])) * 100, 2)
            else:
                changes[key] = 100 if current_metrics[key] > 0 else 0
        
        return {
            "period": period,
            "current": {
                "start_date": current_start.isoformat(),
                **current_metrics,
            },
            "previous": {
                "start_date": previous_start.isoformat(),
                "end_date": previous_end.isoformat(),
                **previous_metrics,
            },
            "changes_percent": changes,
            "generated_at": datetime.now().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Error comparing periods: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to compare periods: {str(e)}")
