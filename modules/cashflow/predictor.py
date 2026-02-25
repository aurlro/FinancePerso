"""
Cashflow prediction and forecasting.
Projects future account balance based on patterns.
"""

from datetime import datetime, timedelta
from dataclasses import dataclass

import pandas as pd
import numpy as np

from modules.db.transactions import get_all_transactions
from modules.cashflow.recurring import detect_recurring_transactions, RecurringType
from modules.logger import logger


@dataclass
class CashflowPrediction:
    """A cashflow prediction for a specific period."""
    start_date: datetime
    end_date: datetime
    starting_balance: float
    predicted_income: float
    predicted_expenses: float
    predicted_balance: float
    confidence: float
    warnings: list[str]


def predict_monthly_cashflow(months_ahead: int = 3) -> list[CashflowPrediction]:
    """
    Predict cashflow for upcoming months.
    
    Args:
        months_ahead: Number of months to predict
    
    Returns:
        List of monthly predictions
    """
    try:
        # Get historical data
        df = get_all_transactions()
        if df.empty:
            return []
        
        df['date'] = pd.to_datetime(df['date'])
        
        # Get recurring transactions
        recurring = detect_recurring_transactions()
        
        predictions = []
        today = datetime.now()
        
        # Calculate current balance
        current_balance = df['amount'].sum()
        
        for i in range(months_ahead):
            month_start = (today.replace(day=1) + timedelta(days=32*i)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            # Predict income from recurring
            predicted_income = sum(
                r.amount for r in recurring 
                if r.type == RecurringType.INCOME and r.frequency.value in ['monthly', 'bimonthly']
            )
            
            # Predict expenses from recurring
            predicted_expenses = sum(
                r.amount for r in recurring 
                if r.type == RecurringType.EXPENSE and r.frequency.value in ['monthly', 'bimonthly']
            )
            
            # Add historical average for non-recurring
            monthly_avg_income = df[df['amount'] > 0].groupby(df['date'].dt.month)['amount'].sum().mean()
            monthly_avg_expense = df[df['amount'] < 0].groupby(df['date'].dt.month)['amount'].sum().mean()
            
            # Adjust for already-accounted recurring
            recurring_income = sum(r.amount for r in recurring if r.type == RecurringType.INCOME)
            recurring_expense = sum(r.amount for r in recurring if r.type == RecurringType.EXPENSE)
            
            additional_income = max(0, monthly_avg_income - recurring_income)
            additional_expense = min(0, monthly_avg_expense - recurring_expense)
            
            total_income = predicted_income + additional_income
            total_expenses = predicted_expenses + additional_expense
            
            # Update running balance
            if i == 0:
                starting_balance = current_balance
            else:
                starting_balance = predictions[-1].predicted_balance
            
            predicted_balance = starting_balance + total_income + total_expenses
            
            # Generate warnings
            warnings = []
            if predicted_balance < 0:
                warnings.append("⚠️ Solde prévisionnel négatif!")
            elif predicted_balance < 500:
                warnings.append("⚠️ Solde faible (< 500€)")
            
            predictions.append(CashflowPrediction(
                start_date=month_start,
                end_date=month_end,
                starting_balance=starting_balance,
                predicted_income=total_income,
                predicted_expenses=total_expenses,
                predicted_balance=predicted_balance,
                confidence=0.7 if recurring else 0.5,
                warnings=warnings
            ))
        
        return predictions
        
    except Exception as e:
        logger.error(f"Error predicting cashflow: {e}")
        return []


def predict_account_balance(target_date: datetime) -> dict:
    """
    Predict account balance at a specific future date.
    
    Args:
        target_date: The date to predict balance for
        
    Returns:
        Dict with predicted balance and confidence
    """
    try:
        # Get all monthly predictions up to target date
        months_ahead = (target_date.year - datetime.now().year) * 12 + (target_date.month - datetime.now().month) + 1
        predictions = predict_monthly_cashflow(months_ahead=max(1, months_ahead))
        
        if not predictions:
            return {"predicted_balance": 0, "confidence": 0, "error": "Pas assez de données"}
        
        # Find the prediction for the target month
        for pred in predictions:
            if pred.start_date.month == target_date.month and pred.start_date.year == target_date.year:
                return {
                    "predicted_balance": pred.predicted_balance,
                    "confidence": pred.confidence,
                    "warnings": pred.warnings
                }
        
        # If no exact match, return the last prediction
        last_pred = predictions[-1]
        return {
            "predicted_balance": last_pred.predicted_balance,
            "confidence": last_pred.confidence,
            "warnings": last_pred.warnings
        }
        
    except Exception as e:
        logger.error(f"Error predicting account balance: {e}")
        return {"predicted_balance": 0, "confidence": 0, "error": str(e)}


def get_cashflow_insights() -> dict:
    """
    Get key insights about cashflow.
    
    Returns:
        Dict with insights
    """
    try:
        predictions = predict_monthly_cashflow(months_ahead=3)
        
        if not predictions:
            return {"error": "Pas assez de données pour les prévisions"}
        
        insights = {
            "current_balance": predictions[0].starting_balance,
            "predicted_3m_balance": predictions[-1].predicted_balance if len(predictions) >= 3 else None,
            "trend": "up" if predictions[-1].predicted_balance > predictions[0].starting_balance else "down",
            "warnings": [],
            "avg_monthly_income": sum(p.predicted_income for p in predictions) / len(predictions),
            "avg_monthly_expense": abs(sum(p.predicted_expenses for p in predictions) / len(predictions)),
        }
        
        # Collect all warnings
        for p in predictions:
            insights["warnings"].extend(p.warnings)
        
        insights["warnings"] = list(set(insights["warnings"]))  # Deduplicate
        
        return insights
        
    except Exception as e:
        logger.error(f"Error getting cashflow insights: {e}")
        return {"error": str(e)}
