"""
Recurring transaction detection and management.
Identifies regular income and expenses for forecasting.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

import numpy as np
import pandas as pd

from modules.db.transactions import get_all_transactions
from modules.logger import logger


class RecurringType(Enum):
    INCOME = "income"
    EXPENSE = "expense"


class RecurringFrequency(Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    BIMONTHLY = "bimonthly"  # Every 2 months
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    UNKNOWN = "unknown"


@dataclass
class RecurringTransaction:
    """A detected recurring transaction pattern."""

    label_pattern: str  # Regex pattern or substring to match
    amount: float
    type: RecurringType
    frequency: RecurringFrequency
    day_of_month: int | None  # Day when it usually occurs
    confidence: float  # 0-1, how sure we are
    last_occurrence: datetime
    next_expected: datetime
    category: str | None


def detect_recurring_transactions(
    min_occurrences: int = 3, min_confidence: float = 0.7
) -> list[RecurringTransaction]:
    """
    Detect recurring transactions from historical data.

    Algorithm:
    1. Group transactions by similar labels
    2. Analyze date patterns for each group
    3. Identify regular intervals (monthly, weekly, etc.)
    4. Return high-confidence patterns

    Args:
        min_occurrences: Minimum number of times seen to consider
        min_confidence: Minimum confidence score (0-1)

    Returns:
        List of detected recurring transactions
    """
    try:
        df = get_all_transactions()
        if df.empty or len(df) < 10:
            return []

        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.month
        df["day"] = df["date"].dt.day
        df["year"] = df["date"].dt.year

        recurring = []

        # Group by normalized label (first word + amount)
        df["label_key"] = (
            df["label"].str.extract(r"(\w+)") + "_" + df["amount"].abs().round(2).astype(str)
        )

        for label_key, group in df.groupby("label_key"):
            if len(group) < min_occurrences:
                continue

            # Analyze date patterns
            dates = sorted(group["date"].tolist())
            intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]

            if not intervals:
                continue

            # Detect frequency
            avg_interval = np.mean(intervals)
            interval_std = np.std(intervals)

            # Determine frequency
            if 6 <= avg_interval <= 8:
                freq = RecurringFrequency.WEEKLY
            elif 28 <= avg_interval <= 32:
                freq = RecurringFrequency.MONTHLY
            elif 58 <= avg_interval <= 65:
                freq = RecurringFrequency.BIMONTHLY
            elif 85 <= avg_interval <= 95:
                freq = RecurringFrequency.QUARTERLY
            elif 360 <= avg_interval <= 380:
                freq = RecurringFrequency.YEARLY
            else:
                freq = RecurringFrequency.UNKNOWN

            # Calculate confidence based on regularity
            if avg_interval > 0:
                regularity = 1 - min(interval_std / avg_interval, 1)
                confidence = regularity * min(
                    len(group) / 6, 1
                )  # More occurrences = higher confidence
            else:
                confidence = 0

            if confidence < min_confidence:
                continue

            # Get most common day of month for monthly patterns
            day_of_month = None
            if freq == RecurringFrequency.MONTHLY:
                day_of_month = (
                    int(group["day"].mode().iloc[0]) if len(group["day"].mode()) > 0 else None
                )

            # Calculate next expected date
            last_date = dates[-1]
            if freq == RecurringFrequency.MONTHLY:
                next_date = last_date + timedelta(days=30)
            elif freq == RecurringFrequency.WEEKLY:
                next_date = last_date + timedelta(days=7)
            elif freq == RecurringFrequency.BIMONTHLY:
                next_date = last_date + timedelta(days=60)
            elif freq == RecurringFrequency.QUARTERLY:
                next_date = last_date + timedelta(days=90)
            elif freq == RecurringFrequency.YEARLY:
                next_date = last_date + timedelta(days=365)
            else:
                next_date = last_date + timedelta(days=int(avg_interval))

            amount = group["amount"].iloc[0]

            recurring.append(
                RecurringTransaction(
                    label_pattern=group["label"].iloc[0][:20],  # First 20 chars as pattern
                    amount=amount,
                    type=RecurringType.INCOME if amount > 0 else RecurringType.EXPENSE,
                    frequency=freq,
                    day_of_month=day_of_month,
                    confidence=confidence,
                    last_occurrence=last_date,
                    next_expected=next_date,
                    category=(
                        group["category_validated"].mode().iloc[0]
                        if len(group["category_validated"].mode()) > 0
                        else None
                    ),
                )
            )

        # Sort by confidence
        recurring.sort(key=lambda x: x.confidence, reverse=True)
        return recurring

    except Exception as e:
        logger.error(f"Error detecting recurring transactions: {e}")
        return []


def get_upcoming_recurring(days_ahead: int = 30) -> list[RecurringTransaction]:
    """
    Get recurring transactions expected in the next N days.

    Args:
        days_ahead: Number of days to look ahead

    Returns:
        List of upcoming recurring transactions
    """
    recurring = detect_recurring_transactions()
    today = datetime.now()
    cutoff = today + timedelta(days=days_ahead)

    upcoming = []
    for rec in recurring:
        if today <= rec.next_expected <= cutoff:
            upcoming.append(rec)

    return upcoming


def render_upcoming_recurring():
    """Render upcoming recurring transactions in Streamlit."""
    import streamlit as st

    upcoming = get_upcoming_recurring(days_ahead=30)

    if not upcoming:
        st.info("Aucune transaction récurrente détectée dans les 30 prochains jours")
        return

    st.subheader("📅 Transactions récurrentes à venir")

    total_income = sum(r.amount for r in upcoming if r.type == RecurringType.INCOME)
    total_expense = sum(r.amount for r in upcoming if r.type == RecurringType.EXPENSE)

    cols = st.columns(2)
    with cols[0]:
        st.metric("💰 Revenus attendus", f"{total_income:,.2f}€")
    with cols[1]:
        st.metric("💸 Dépenses prévues", f"{abs(total_expense):,.2f}€")

    for rec in upcoming[:5]:  # Show top 5
        icon = "💰" if rec.type == RecurringType.INCOME else "💸"
        with st.container():
            cols = st.columns([0.1, 0.5, 0.2, 0.2])
            cols[0].write(icon)
            cols[1].write(f"{rec.label_pattern}")
            cols[2].write(f"{rec.amount:,.2f}€")
            cols[3].write(f"{rec.next_expected.strftime('%d/%m')}")
