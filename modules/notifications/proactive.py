"""
Proactive notifications for FinancePerso.
Detects patterns and alerts users before problems occur.
"""

from datetime import date, datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from typing import Callable

import pandas as pd
import streamlit as st

from modules.logger import logger


class AlertPriority(Enum):
    """Priority levels for proactive alerts."""

    CRITICAL = "critical"  # Action required immediately
    WARNING = "warning"  # Attention needed soon
    INFO = "info"  # FYI, good to know


@dataclass
class ProactiveAlert:
    """A proactive alert with actionable information."""

    id: str
    title: str
    message: str
    priority: AlertPriority
    icon: str
    action_label: str | None = None
    action: Callable | None = None
    dismissible: bool = True
    auto_dismiss_after: int | None = None  # Days


def detect_overspending_pattern() -> ProactiveAlert | None:
    """
    Detect if user is overspending compared to previous months.
    Alert if current month spending is 20%+ higher than average.
    """
    try:
        from modules.db.transactions import get_all_transactions

        df = get_all_transactions()
        if df.empty or len(df) < 30:
            return None

        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M")
        df["amount_abs"] = df["amount"].abs()

        # Get spending by month (only expenses)
        monthly = df[df["amount"] < 0].groupby("month")["amount_abs"].sum()

        if len(monthly) < 2:
            return None

        current_month = monthly.index[-1]
        current_spend = monthly.iloc[-1]
        avg_spend = monthly.iloc[:-1].mean()

        if current_spend > avg_spend * 1.2:  # 20% increase
            increase_pct = ((current_spend - avg_spend) / avg_spend) * 100
            return ProactiveAlert(
                id=f"overspend_{current_month}",
                title="📈 Dépenses en hausse",
                message=f"Vos dépenses ce mois sont {increase_pct:.0f}% plus élevées que la moyenne ({current_spend:.0f}€ vs {avg_spend:.0f}€)",
                priority=AlertPriority.WARNING,
                icon="📈",
                action_label="Voir les détails",
                action=lambda: st.switch_page("pages/02_Dashboard.py"),
            )
    except Exception as e:
        logger.warning(f"Error detecting overspending: {e}")
    return None


def detect_duplicate_transactions() -> ProactiveAlert | None:
    """Detect potential duplicate transactions in last 7 days."""
    try:
        from modules.db.transactions import get_all_transactions

        df = get_all_transactions()
        if df.empty or len(df) < 5:
            return None

        df["date"] = pd.to_datetime(df["date"])
        last_week = datetime.now() - timedelta(days=7)
        recent = df[df["date"] >= last_week]

        if len(recent) < 2:
            return None

        # Find duplicates by label + amount on same day
        # Normalize date to remove time component
        recent["date_only"] = recent["date"].dt.date
        duplicates = recent.groupby(["date_only", "label", "amount"]).size()
        duplicates = duplicates[duplicates > 1]

        if len(duplicates) > 0:
            count = len(duplicates)
            return ProactiveAlert(
                id=f"duplicates_{date.today()}",
                title=f"⚠️ {count} transaction(s) en double détectée(s)",
                message="Des transactions similaires ont été importées plusieurs fois dans les 7 derniers jours",
                priority=AlertPriority.WARNING,
                icon="⚠️",
                action_label="Vérifier",
                action=lambda: st.switch_page("pages/01_Import.py"),
            )
    except Exception as e:
        logger.warning(f"Error detecting duplicates: {e}")
    return None


def detect_unusual_merchant() -> ProactiveAlert | None:
    """Detect spending at unusual/new merchants."""
    try:
        from modules.db.transactions import get_all_transactions

        df = get_all_transactions()
        if df.empty or len(df) < 20:
            return None

        df["date"] = pd.to_datetime(df["date"])

        # Get merchants from labels (simplified - extract first word)
        df["merchant"] = df["label"].str.extract(r"^(\S+)")
        df = df.dropna(subset=["merchant"])

        # Find first-time merchants in last 30 days
        last_month = datetime.now() - timedelta(days=30)
        recent_df = df[df["date"] >= last_month]
        old_df = df[df["date"] < last_month]

        if len(recent_df) == 0 or len(old_df) == 0:
            return None

        recent_merchants = set(recent_df["merchant"].dropna().str.upper())
        old_merchants = set(old_df["merchant"].dropna().str.upper())

        new_merchants = recent_merchants - old_merchants

        # Filter out common/generic terms
        generic_terms = {"VIREMENT", "PRELEVEMENT", "FRAIS", "RETRAIT", "CARTE"}
        new_merchants = new_merchants - generic_terms

        if len(new_merchants) > 0:
            merchant_list = ", ".join(sorted(new_merchants)[:3])
            if len(new_merchants) > 3:
                merchant_list += f" et {len(new_merchants) - 3} autres"
            return ProactiveAlert(
                id=f"new_merchants_{date.today()}",
                title=f"🆕 {len(new_merchants)} nouveau(x) commerçant(s)",
                message=f"Commerçants détectés ce mois: {merchant_list}",
                priority=AlertPriority.INFO,
                icon="🆕",
            )
    except Exception as e:
        logger.warning(f"Error detecting unusual merchants: {e}")
    return None


def detect_missing_salary() -> ProactiveAlert | None:
    """Alert if salary not received by expected date."""
    try:
        from modules.db.transactions import get_all_transactions

        df = get_all_transactions()
        if df.empty or len(df) < 10:
            return None

        # Look for salary pattern (positive amount + "SALAIRE" in label)
        salary_patterns = df[
            (df["amount"] > 1000)
            & (
                df["label"].str.contains(
                    "SALAIRE|PAIE|VIREMENT.*EMPLOI", case=False, na=False, regex=True
                )
            )
        ]

        if salary_patterns.empty:
            return None

        salary_patterns = salary_patterns.copy()
        salary_patterns["date"] = pd.to_datetime(salary_patterns["date"])
        last_salary = salary_patterns["date"].max()

        # Expected around same day each month
        today = datetime.now()
        days_since_salary = (today - last_salary).days

        if days_since_salary > 35:  # More than 35 days
            return ProactiveAlert(
                id=f"missing_salary_{today.month}",
                title="💰 Salaire non détecté",
                message=f"Votre dernier salaire date du {last_salary.strftime('%d/%m/%Y')} ({days_since_salary} jours)",
                priority=AlertPriority.INFO,
                icon="💰",
            )
    except Exception as e:
        logger.warning(f"Error detecting salary: {e}")
    return None


def detect_high_variance_category() -> ProactiveAlert | None:
    """Detect categories with unusually high variance."""
    try:
        from modules.db.transactions import get_all_transactions

        df = get_all_transactions()
        if df.empty or len(df) < 50:
            return None

        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M")

        # Get spending by category and month
        expenses = df[df["amount"] < 0].copy()
        if len(expenses) < 30:
            return None

        expenses["amount_abs"] = expenses["amount"].abs()

        category_variance = {}
        for category in expenses["category_validated"].dropna().unique():
            cat_data = expenses[expenses["category_validated"] == category]
            monthly = cat_data.groupby("month")["amount_abs"].sum()

            if len(monthly) >= 3 and monthly.mean() > 0:
                # Coefficient of variation (std/mean)
                cv = monthly.std() / monthly.mean()
                if cv > 0.5:  # High variance (>50% of mean)
                    category_variance[category] = cv

        if category_variance:
            highest = max(category_variance, key=category_variance.get)
            cv_value = category_variance[highest]
            return ProactiveAlert(
                id=f"variance_{highest}_{date.today().month}",
                title=f"📊 Dépenses irrégulières: {highest}",
                message=f"Vos dépenses '{highest}' varient beaucoup d'un mois à l'autre ({cv_value:.0%} de variation)",
                priority=AlertPriority.INFO,
                icon="📊",
                action_label="Voir l'historique",
                action=lambda: st.switch_page("pages/04_Budgets.py"),
            )
    except Exception as e:
        logger.warning(f"Error detecting variance: {e}")
    return None


def detect_weekend_spending_spike() -> ProactiveAlert | None:
    """Detect if weekend spending is significantly higher than usual."""
    try:
        from modules.db.transactions import get_all_transactions

        df = get_all_transactions()
        if df.empty or len(df) < 60:
            return None

        df["date"] = pd.to_datetime(df["date"])
        df["dayofweek"] = df["date"].dt.dayofweek  # 5=Saturday, 6=Sunday
        df["amount_abs"] = df["amount"].abs()

        # Weekend = Saturday (5) or Sunday (6)
        expenses = df[df["amount"] < 0].copy()
        weekend_expenses = expenses[expenses["dayofweek"].isin([5, 6])]
        weekday_expenses = expenses[~expenses["dayofweek"].isin([5, 6])]

        if len(weekend_expenses) < 10 or len(weekday_expenses) < 20:
            return None

        avg_weekend = weekend_expenses["amount_abs"].mean()
        avg_weekday = weekday_expenses["amount_abs"].mean()

        # Alert if weekend spending is 50% higher per transaction
        if avg_weekend > avg_weekday * 1.5:
            return ProactiveAlert(
                id=f"weekend_spike_{date.today().month}",
                title="🎉 Dépenses de week-end élevées",
                message=f"Vos dépenses le week-end sont {avg_weekend:.0f}€ en moyenne vs {avg_weekday:.0f}€ en semaine",
                priority=AlertPriority.INFO,
                icon="🎉",
            )
    except Exception as e:
        logger.warning(f"Error detecting weekend spending: {e}")
    return None


def detect_recurring_payment_missing() -> ProactiveAlert | None:
    """Detect if a recurring monthly payment hasn't occurred."""
    try:
        from modules.db.transactions import get_all_transactions

        df = get_all_transactions()
        if df.empty or len(df) < 50:
            return None

        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M")

        # Find transactions that appear almost every month
        current_month = pd.Period.now("M")
        last_3_months = current_month - 3

        recent_df = df[df["month"] >= last_3_months]

        # Group by label pattern (simplified)
        recurring_candidates = recent_df[
            recent_df["label"].str.contains(
                "EDF|ORANGE|SFR|FREE|SPOTIFY|NETFLIX|ASSURANCE|LOYER", case=False, na=False
            )
        ]

        if len(recurring_candidates) < 3:
            return None

        # Check which ones are missing this month
        current_month_transactions = set(
            recurring_candidates[recurring_candidates["month"] == current_month][
                "label"
            ].str.upper()
        )

        # Check previous month to see what should have occurred
        prev_month = current_month - 1
        prev_transactions = recurring_candidates[recurring_candidates["month"] == prev_month]

        missing = []
        for label in prev_transactions["label"].unique():
            # Check if similar transaction exists this month
            if not any(label.upper() in curr for curr in current_month_transactions):
                # Check if it was present 2 months ago too (confirming it's recurring)
                two_months_ago = current_month - 2
                two_month_data = recurring_candidates[
                    recurring_candidates["month"] == two_months_ago
                ]
                if label in two_month_data["label"].values:
                    missing.append(label[:30])  # Truncate for display

        if missing:
            return ProactiveAlert(
                id=f"missing_recurring_{current_month}",
                title="📅 Paiement récurrent manquant",
                message=f"Paiement habituel non détecté: {missing[0]}{'...' if len(missing) > 1 else ''}",
                priority=AlertPriority.WARNING,
                icon="📅",
            )
    except Exception as e:
        logger.warning(f"Error detecting recurring payment: {e}")
    return None


def detect_large_expense_anomaly() -> ProactiveAlert | None:
    """Detect unusually large expenses compared to user's history."""
    try:
        from modules.db.transactions import get_all_transactions

        df = get_all_transactions()
        if df.empty or len(df) < 20:
            return None

        df["date"] = pd.to_datetime(df["date"])
        df["amount_abs"] = df["amount"].abs()

        # Look at expenses only
        expenses = df[df["amount"] < 0].copy()

        # Get recent large expenses (last 14 days)
        two_weeks_ago = datetime.now() - timedelta(days=14)
        recent = expenses[expenses["date"] >= two_weeks_ago]
        older = expenses[expenses["date"] < two_weeks_ago]

        if len(recent) < 1 or len(older) < 10:
            return None

        # Calculate user's usual expense range (95th percentile)
        usual_max = older["amount_abs"].quantile(0.95)

        # Find recent expenses that exceed this significantly (2x the usual max)
        large_recent = recent[recent["amount_abs"] > usual_max * 2]

        if len(large_recent) > 0:
            largest = large_recent.loc[large_recent["amount_abs"].idxmax()]
            return ProactiveAlert(
                id=f"large_expense_{largest.name}_{date.today()}",
                title="💸 Dépense inhabituelle",
                message=f"Dépense de {largest['amount_abs']:.0f}€ ({largest['label'][:30]}) détectée - supérieure à votre moyenne",
                priority=AlertPriority.WARNING,
                icon="💸",
            )
    except Exception as e:
        logger.warning(f"Error detecting large expense: {e}")
    return None


def check_all_proactive_alerts() -> list[ProactiveAlert]:
    """
    Run all alert detectors and return actionable alerts.

    Returns:
        List of alerts sorted by priority
    """
    detectors = [
        detect_overspending_pattern,
        detect_duplicate_transactions,
        detect_unusual_merchant,
        detect_missing_salary,
        detect_high_variance_category,
        detect_weekend_spending_spike,
        detect_recurring_payment_missing,
        detect_large_expense_anomaly,
    ]

    alerts = []
    for detector in detectors:
        try:
            alert = detector()
            if alert:
                alerts.append(alert)
        except Exception as e:
            logger.warning(f"Alert detector {detector.__name__} failed: {e}")

    # Sort by priority
    priority_order = {AlertPriority.CRITICAL: 0, AlertPriority.WARNING: 1, AlertPriority.INFO: 2}
    alerts.sort(key=lambda x: priority_order[x.priority])

    return alerts


def render_proactive_alerts(max_alerts: int = 3):
    """
    Render proactive alerts in the UI.
    Call this on dashboard or home page.
    """
    alerts = check_all_proactive_alerts()

    if not alerts:
        return

    # Show only top N alerts
    for alert in alerts[:max_alerts]:
        with st.container():
            cols = st.columns([0.1, 0.9])

            with cols[0]:
                st.markdown(f"<h2 style='margin: 0;'>{alert.icon}</h2>", unsafe_allow_html=True)

            with cols[1]:
                # Color based on priority
                border_color = {
                    AlertPriority.CRITICAL: "#ff4b4b",
                    AlertPriority.WARNING: "#ffa421",
                    AlertPriority.INFO: "#0068c9",
                }[alert.priority]

                with st.container():
                    st.markdown(
                        f"""
                        <div style='
                            border-left: 4px solid {border_color};
                            padding-left: 12px;
                            margin-bottom: 8px;
                        '>
                            <strong>{alert.title}</strong><br>
                            <span style='color: #666; font-size: 0.9em;'>{alert.message}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    if alert.action and alert.action_label:
                        if st.button(alert.action_label, key=f"alert_{alert.id}", type="primary"):
                            alert.action()

            st.divider()


def get_alert_summary() -> dict:
    """
    Get a summary of current alerts without rendering.
    Useful for badges or notification counts.
    """
    alerts = check_all_proactive_alerts()

    return {
        "total": len(alerts),
        "critical": len([a for a in alerts if a.priority == AlertPriority.CRITICAL]),
        "warning": len([a for a in alerts if a.priority == AlertPriority.WARNING]),
        "info": len([a for a in alerts if a.priority == AlertPriority.INFO]),
        "alerts": alerts,
    }


__all__ = [
    "AlertPriority",
    "ProactiveAlert",
    "detect_overspending_pattern",
    "detect_duplicate_transactions",
    "detect_unusual_merchant",
    "detect_missing_salary",
    "detect_high_variance_category",
    "detect_weekend_spending_spike",
    "detect_recurring_payment_missing",
    "detect_large_expense_anomaly",
    "check_all_proactive_alerts",
    "render_proactive_alerts",
    "get_alert_summary",
]
