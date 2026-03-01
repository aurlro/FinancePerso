"""
Daily Widget - Creates a daily engagement hook.
Displays personalized insights to encourage daily app usage.
"""

from datetime import date, datetime
from dataclasses import dataclass
from typing import Any, Callable

import pandas as pd
import streamlit as st

from modules.db.budgets import get_budgets
from modules.db.stats import get_global_stats
from modules.db.transactions import get_all_transactions, get_pending_transactions
from modules.logger import logger


@dataclass
class DailyInsight:
    """A daily insight to display to the user."""

    title: str
    message: str
    icon: str
    priority: int  # 1 = highest, 10 = lowest
    action_label: str | None = None
    action: Callable | None = None
    color: str = "blue"  # blue, green, yellow, red, orange, gray
    metric: str | None = None
    metric_label: str | None = None
    progress: float | None = None


def get_pending_validations_count() -> int:
    """Get number of pending transactions to validate."""
    try:
        df = get_pending_transactions()
        return len(df)
    except Exception:
        return 0


def get_budget_alerts(threshold: float = 0.8) -> list[dict]:
    """Get budgets that are over threshold (default 80%) used."""
    try:
        today = datetime.now()
        budgets_df = get_budgets()

        if budgets_df.empty:
            return []

        # Get monthly spending by category
        all_tx = get_all_transactions()
        first_day = today.replace(day=1)
        spending_by_category = {}

        if not all_tx.empty and "date" in all_tx.columns and "amount" in all_tx.columns:
            all_tx["date"] = pd.to_datetime(all_tx["date"])
            month_tx = all_tx[all_tx["date"] >= first_day]
            if not month_tx.empty and "category" in month_tx.columns:
                spending_by_category = month_tx.groupby("category")["amount"].sum().to_dict()

        alerts = []
        for _, budget in budgets_df.iterrows():
            category = budget["category"]
            limit = budget["amount"]
            spent = spending_by_category.get(category, 0)
            percentage = (spent / limit) if limit > 0 else 0

            if percentage >= threshold:
                alerts.append(
                    {
                        "category": category,
                        "spent": spent,
                        "limit": limit,
                        "percentage": percentage * 100,
                        "critical": percentage >= 0.9,
                    }
                )

        # Sort by percentage descending
        alerts.sort(key=lambda x: x["percentage"], reverse=True)
        return alerts

    except Exception as e:
        logger.warning(f"Could not get budget alerts: {e}")
        return []


def get_current_streak() -> int:
    """Get current daily login streak."""
    return st.session_state.get("login_streak", 0)


def track_daily_login():
    """Track daily login for streak calculation. Should be called once per session."""
    today = date.today()
    last_login = st.session_state.get("last_login_date")

    if last_login == today.isoformat():
        return  # Already logged today

    streak = st.session_state.get("login_streak", 0)

    if last_login:
        try:
            last_date = date.fromisoformat(last_login)
            days_diff = (today - last_date).days

            if days_diff == 1:
                streak += 1  # Consecutive day
            elif days_diff > 1:
                streak = 1  # Reset streak
        except (ValueError, TypeError):
            streak = 1  # Reset on error
    else:
        streak = 1  # First login

    st.session_state["login_streak"] = streak
    st.session_state["last_login_date"] = today.isoformat()
    logger.info(f"Daily login tracked - streak: {streak}")


def _get_savings_goal_insight() -> DailyInsight | None:
    """Try to get insight from savings goals module."""
    try:
        from modules.savings_goals import get_closest_savings_goal

        closest = get_closest_savings_goal()
        if closest and not closest.is_achieved():
            progress = closest.progress_pct

            if progress >= 90:
                message = f"🎉 Presque là ! Plus que {closest.remaining_amount:.0f}€ pour atteindre votre objectif"
            elif progress >= 50:
                message = "💪 Plus de la moitié atteinte ! Continuez comme ça"
            else:
                message = f"🌱 Objectif: {closest.target_amount:.0f}€ | Actuel: {closest.current_amount:.0f}€"

            return DailyInsight(
                title=f"{closest.emoji} {closest.name}",
                message=message,
                icon="🎯",
                priority=2,
                action_label="Contribuer",
                action=lambda: st.switch_page("pages/02_Dashboard.py"),
                color="green",
                metric=f"{progress:.0f}%",
                metric_label="atteint",
                progress=progress / 100,
            )
    except Exception:
        pass  # Module not available
    return None


def _get_budget_alert_insight(budget_alerts: list[dict]) -> DailyInsight | None:
    """Generate insight from budget alerts."""
    if not budget_alerts:
        return None

    alert = budget_alerts[0]
    is_critical = alert.get("critical", False)

    return DailyInsight(
        title=f"🚨 Budget {alert['category']}" if is_critical else f"⚠️ Budget {alert['category']}",
        message=f"{alert['percentage']:.0f}% utilisé ({alert['spent']:.2f}€ / {alert['limit']:.2f}€)",
        icon="🚨" if is_critical else "⚠️",
        priority=1 if is_critical else 2,
        action_label="Ajuster le budget",
        action=lambda: st.switch_page("pages/04_Budgets.py"),
        color="red" if is_critical else "orange",
        metric=f"{alert['percentage']:.0f}%",
        metric_label="utilisé",
        progress=min(alert["percentage"] / 100, 1.0),
    )


def _get_pending_validation_insight(pending: int) -> DailyInsight | None:
    """Generate insight from pending validations."""
    if pending <= 5:
        return None

    return DailyInsight(
        title=f"⏳ {pending} transactions en attente",
        message="Validez vos transactions pour des insights précis",
        icon="⏳",
        priority=3,
        action_label="Valider",
        action=lambda: st.switch_page("pages/01_Import.py"),
        color="yellow",
    )


def _get_streak_insight(streak: int) -> DailyInsight | None:
    """Generate streak milestone insight."""
    if streak <= 0:
        return None

    # Show streak on weekly milestones or day 1
    if streak == 1:
        return DailyInsight(
            title="🌟 Bienvenue !",
            message="Commencez votre streak quotidien aujourd'hui",
            icon="🌟",
            priority=5,
            color="blue",
        )

    if streak % 7 == 0:  # Weekly milestone
        return DailyInsight(
            title=f"🔥 Streak de {streak} jours !",
            message="Vous utilisez régulièrement l'app, bravo !",
            icon="🔥",
            priority=4,
            color="green",
            metric=f"{streak}j",
            metric_label="streak",
        )

    return None


def _get_spending_insight() -> DailyInsight | None:
    """Generate insight based on today's spending."""
    try:
        today = datetime.now()
        today_str = today.strftime("%Y-%m-%d")

        all_tx = get_all_transactions()
        if all_tx.empty or "date" not in all_tx.columns or "amount" not in all_tx.columns:
            return None

        all_tx["date"] = pd.to_datetime(all_tx["date"])
        today_tx = all_tx[all_tx["date"].dt.strftime("%Y-%m-%d") == today_str]

        if today_tx.empty:
            return None

        today_spending = today_tx["amount"].sum()

        if today_spending > 100:
            return DailyInsight(
                title="💸 Journée chargée",
                message=f"Vous avez dépensé {today_spending:.2f}€ aujourd'hui",
                icon="💸",
                priority=6,
                action_label="Voir les détails",
                action=lambda: st.switch_page("pages/01_Import.py"),
                color="orange",
                metric=f"{today_spending:.2f}€",
                metric_label="aujourd'hui",
            )

        if today_spending > 0:
            return DailyInsight(
                title="💰 Dépenses du jour",
                message=f"{today_spending:.2f}€ dépensés aujourd'hui",
                icon="💰",
                priority=7,
                color="blue",
                metric=f"{today_spending:.2f}€",
                metric_label="aujourd'hui",
            )

    except Exception:
        pass

    return None


def _get_top_category_insight() -> DailyInsight | None:
    """Generate insight about top spending category this month."""
    try:
        today = datetime.now()
        all_tx = get_all_transactions()

        if all_tx.empty or "date" not in all_tx.columns or "category" not in all_tx.columns:
            return None

        all_tx["date"] = pd.to_datetime(all_tx["date"])
        first_day = today.replace(day=1)
        month_tx = all_tx[all_tx["date"] >= first_day]

        if month_tx.empty:
            return None

        top_category = (
            month_tx.groupby("category")["amount"].sum().sort_values(ascending=False).head(1)
        )

        if top_category.empty:
            return None

        cat_name = top_category.index[0]
        cat_amount = top_category.values[0]

        return DailyInsight(
            title=f"📊 Top dépense: {cat_name}",
            message=f"{cat_amount:.2f}€ ce mois",
            icon="📊",
            priority=8,
            action_label="Explorer",
            action=lambda: st.switch_page("pages/07_Recherche.py"),
            color="blue",
            metric=f"{cat_amount:.2f}€",
            metric_label=cat_name,
        )

    except Exception:
        pass

    return None


def _get_daily_tip() -> DailyInsight:
    """Get a random daily tip."""
    import random

    tips = [
        ("💡 Astuce", "Utilisez les tags pour retrouver facilement vos transactions"),
        ("💡 Astuce", "Vérifiez vos budgets avant de faire des achats importants"),
        ("💡 Astuce", "Importez vos relevés régulièrement pour un suivi précis"),
        ("💡 Astuce", "Les règles d'apprentissage accélèrent la catégorisation"),
        ("💡 Astuce", "Consultez la synthèse mensuelle pour suivre vos progrès"),
        ("💡 Astuce", "Activez les notifications pour ne rien manquer"),
    ]

    title, message = random.choice(tips)

    return DailyInsight(
        title=title,
        message=message,
        icon="💡",
        priority=10,
        color="blue",
    )


def generate_daily_insight() -> DailyInsight | None:
    """
    Generate the most relevant daily insight based on user's data.

    Priority order:
    1. Budget alerts (> 90% = critical, > 80% = warning)
    2. Savings goal progress (if available)
    3. Pending validations (> 10 transactions)
    4. Streak notification (weekly milestones)
    5. Today's spending (if significant)
    6. Top category of the month
    7. Daily tip (lowest priority)
    """
    # Get base data
    budget_alerts = get_budget_alerts(threshold=0.8)
    pending = get_pending_validations_count()
    streak = get_current_streak()

    # Priority 1: Budget alerts (critical > 90%)
    critical_alerts = [a for a in budget_alerts if a.get("critical", False)]
    if critical_alerts:
        return _get_budget_alert_insight(critical_alerts)

    # Priority 2: Savings goal
    savings_insight = _get_savings_goal_insight()
    if savings_insight:
        return savings_insight

    # Priority 3: Budget warnings (> 80%)
    if budget_alerts:
        return _get_budget_alert_insight(budget_alerts)

    # Priority 4: Pending validations
    pending_insight = _get_pending_validation_insight(pending)
    if pending_insight:
        return pending_insight

    # Priority 5: Streak milestone
    streak_insight = _get_streak_insight(streak)
    if streak_insight:
        return streak_insight

    # Priority 6: Today's spending
    spending_insight = _get_spending_insight()
    if spending_insight:
        return spending_insight

    # Priority 7: Top category
    top_cat_insight = _get_top_category_insight()
    if top_cat_insight:
        return top_cat_insight

    # Default: Daily tip
    return _get_daily_tip()


def render_daily_widget(force_show: bool = False):
    """
    Render the daily widget if not already shown today.

    Args:
        force_show: If True, show even if already shown today

    Should be called at the top of the main page.
    """
    today = date.today()

    # Track login for streak
    track_daily_login()

    # Check if already shown today (unless forced)
    if not force_show:
        last_shown = st.session_state.get("daily_widget_date")
        if last_shown == today.isoformat():
            return

    # Generate insight
    insight = generate_daily_insight()
    if not insight:
        return

    # Don't show low priority insights (> 5) unless forced
    if insight.priority > 5 and not force_show:
        st.session_state["daily_widget_date"] = today.isoformat()
        return

    # Couleurs selon le type
    colors = {
        "blue": ("blue", "🔵"),
        "green": ("green", "🟢"),
        "yellow": ("yellow", "🟡"),
        "orange": ("orange", "🟠"),
        "red": ("red", "🔴"),
        "gray": ("gray", "⚪"),
    }

    color, _ = colors.get(insight.color, ("gray", "ℹ️"))

    # Style CSS pour le widget
    st.markdown(
        f"""
    <style>
    .daily-widget {{
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 4px solid var(--{color}-500);
        background: linear-gradient(135deg, var(--{color}-50) 0%, rgba(255,255,255,0) 100%);
        margin: 1rem 0;
    }}
    .daily-widget h3 {{
        margin: 0 0 0.5rem 0;
        color: var(--{color}-700);
    }}
    .daily-widget .metric {{
        font-size: 2rem;
        font-weight: bold;
        color: var(--{color}-600);
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Render widget
    with st.container():
        col1, col2 = st.columns([0.7, 0.3])

        with col1:
            st.subheader(f"{insight.icon} {insight.title}")
            st.write(insight.message)

            if insight.action and insight.action_label:
                if st.button(
                    insight.action_label,
                    key=f"daily_action_{today}",
                    type="primary",
                    use_container_width=True,
                ):
                    insight.action()
            elif insight.action_label:
                # Use page_link if action is a string path
                if isinstance(insight.action, str):
                    st.page_link(insight.action, label=f"→ {insight.action_label}")

        with col2:
            if insight.metric:
                st.metric(label=insight.metric_label or "", value=insight.metric)

            if insight.progress is not None:
                st.progress(
                    value=min(insight.progress, 1.0),
                    text=f"{insight.progress:.0%}",
                )

    st.divider()

    # Mark as shown
    st.session_state["daily_widget_date"] = today.isoformat()


def render_quick_stats_row():
    """Render a row of quick stats below the daily widget."""
    today = datetime.now()
    stats = get_global_stats()

    if not stats:
        return

    cols = st.columns(4)

    with cols[0]:
        pending = get_pending_validations_count()
        st.metric(
            label="⏳ En attente",
            value=pending,
            delta="à valider" if pending > 0 else None,
        )

    with cols[1]:
        budget_alerts_count = len(get_budget_alerts(threshold=0.8))
        st.metric(
            label="🚨 Alertes budget",
            value=budget_alerts_count,
            delta="critique" if budget_alerts_count > 0 else None,
            delta_color="inverse" if budget_alerts_count > 0 else "normal",
        )

    with cols[2]:
        total_tx = stats.get("total_transactions", 0)
        st.metric(label="📊 Transactions", value=f"{total_tx:,}")

    with cols[3]:
        savings = stats.get("current_month_savings", 0)
        rate = stats.get("current_month_rate", 0)
        st.metric(
            label="💰 Épargne du mois",
            value=f"{savings:+.0f}€",
            delta=f"{rate:.1f}%",
        )


__all__ = [
    "DailyInsight",
    "generate_daily_insight",
    "render_daily_widget",
    "render_quick_stats_row",
    "track_daily_login",
    "get_pending_validations_count",
    "get_budget_alerts",
    "get_current_streak",
]
