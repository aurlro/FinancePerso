"""
Budget Tracker Widget

Suivi des budgets avec barres de progression et tendances.
"""

import pandas as pd
import streamlit as st

from modules.db.budgets import get_budgets
from modules.ui_v2.molecules.toasts import toast_success


def render_budget_tracker(df_exp: pd.DataFrame, cat_emoji_map: dict, df_full: pd.DataFrame = None):
    """
    Render budget tracking section with progress bars and trends.

    Args:
        df_exp: Expense dataframe with 'Catégorie' column
        cat_emoji_map: Category to emoji mapping
        df_full: Full dataset for historical comparison (optional)
    """
    st.header("🎯 Suivi des Budgets")

    budgets = get_budgets()

    if budgets.empty:
        st.info("📝 **Aucun budget défini**")
        st.caption(
            "Configurez vos budgets pour suivre vos dépenses et recevoir des alertes intelligentes."
        )

        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("➕ Créer mon premier budget", type="primary", use_container_width=True):
                toast_success("Ouverture de la configuration des budgets...", icon="🎯")
                st.session_state["intel_active_tab"] = "🎯 Budgets"
                st.switch_page("pages/4_Intelligence.py")
        with col2:
            st.caption(
                "💡 Conseil: Commencez par les catégories où vous dépensez le plus (Courses, Transport, Loisirs)"
            )
        return

    # Calculate number of months in selection for proportional budget
    if "date_dt" in df_exp.columns:
        num_months = len(df_exp["date_dt"].dt.strftime("%Y-%m").unique())
        if num_months == 0:
            num_months = 1
    else:
        num_months = 1

    # Calculate spending by category (amounts are now net, usually negative for expenses)
    spending_map = df_exp.groupby("Catégorie")["amount"].sum().to_dict()

    # Calculate historical spending for trends if df_full provided
    historical_map = {}
    if (
        df_full is not None
        and "date_dt" in df_full.columns
        and "category_validated" in df_full.columns
    ):
        try:
            # Get previous period (same duration)
            current_start = df_exp["date_dt"].min()
            current_end = df_exp["date_dt"].max()
            period_duration = (current_end - current_start).days

            prev_start = current_start - pd.Timedelta(days=period_duration)
            prev_end = current_start - pd.Timedelta(days=1)

            df_prev = df_full[
                (df_full["date_dt"] >= prev_start) & (df_full["date_dt"] <= prev_end)
            ].copy()

            # Use same expense filtering as current
            from modules.transaction_types import filter_expense_transactions

            df_prev_exp = filter_expense_transactions(df_prev)

            if not df_prev_exp.empty:
                df_prev_exp["display_cat"] = df_prev_exp.apply(
                    lambda x: f"{cat_emoji_map.get(x['category_validated'], '🏷️')} {x['category_validated']}",
                    axis=1,
                )
                # Sum and take abs for comparison
                historical_map = df_prev_exp.groupby("display_cat")["amount"].sum().abs().to_dict()
        except Exception:
            pass

    # Summary metrics
    # spent is the absolute value of the sum of negative net amounts
    # (if total is positive, it means we earned more refunds than we spent, spent = 0)
    total_spent_raw = sum(spending_map.values())
    total_spent = abs(total_spent_raw) if total_spent_raw < 0 else 0
    total_limit = budgets["amount"].sum() * num_months

    col_summary1, col_summary2, col_summary3 = st.columns(3)
    with col_summary1:
        st.metric("Budgets actifs", len(budgets))
    with col_summary2:
        utilization = (total_spent / total_limit * 100) if total_limit > 0 else 0
        st.metric(
            "Utilisation globale",
            f"{utilization:.0f}%",
            delta=f"{total_spent:.0f}€ / {total_limit:.0f}€",
        )
    with col_summary3:
        remaining = total_limit - total_spent
        st.metric(
            "Reste à dépenser",
            f"{remaining:+.0f}€",
            delta="⚠️ Dépassement" if remaining < 0 else "✅ OK",
            delta_color="inverse" if remaining < 0 else "normal",
        )

    st.divider()

    # Display budget progress cards with trends
    st.caption(f"**Détail par catégorie** — Période: {num_months} mois")

    # Sort by severity (highest % first)
    budget_list = []
    for _, row in budgets.iterrows():
        cat_name = row["category"]
        display_cat = f"{cat_emoji_map.get(cat_name, '🏷️')} {cat_name}"
        limit = row["amount"] * num_months

        spent_raw = spending_map.get(display_cat, 0.0)
        spent = abs(spent_raw) if spent_raw < 0 else 0

        percent = (spent / limit * 100) if limit > 0 else 0
        budget_list.append(
            {
                "cat_name": cat_name,
                "display_cat": display_cat,
                "limit": limit,
                "spent": spent,
                "percent": percent,
                "delta": limit - spent,
            }
        )

    # Sort by percentage (highest first)
    budget_list.sort(key=lambda x: x["percent"], reverse=True)

    # Display in grid
    cols_b = st.columns(min(3, len(budget_list)))
    for index, budget in enumerate(budget_list):
        col_idx = index % 3

        with cols_b[col_idx]:
            with st.container(border=True):
                # Header with category name
                st.markdown(f"**{budget['display_cat']}**")

                # Trend vs historical
                if budget["display_cat"] in historical_map:
                    prev_spent = historical_map[budget["display_cat"]]
                    if prev_spent > 0:
                        change = ((budget["spent"] - prev_spent) / prev_spent) * 100
                        trend_emoji = "📈" if change > 5 else "📉" if change < -5 else "➡️"
                        st.caption(f"{trend_emoji} vs période précédente: {change:+.0f}%")

                # Progress bar with color coding
                percent_normalized = min(budget["percent"] / 100, 1.0)

                if budget["percent"] > 100:
                    st.progress(1.0, text=f"⚠️ {budget['percent']:.0f}% — DÉPASSEMENT")
                    overrun = budget["spent"] - budget["limit"]
                    st.error(
                        f"🔴 **+{overrun:.0f}€** dépassé ({budget['spent']:.0f}/{budget['limit']:.0f}€)"
                    )
                elif budget["percent"] > 85:
                    st.progress(percent_normalized, text=f"⚠️ {budget['percent']:.0f}%")
                    st.warning(f"🟠 **{budget['delta']:.0f}€** restant — Surveillez!")
                elif budget["percent"] > 60:
                    st.progress(percent_normalized, text=f"{budget['percent']:.0f}%")
                    st.info(
                        f"**{budget['delta']:.0f}€** restant ({budget['spent']:.0f}/{budget['limit']:.0f}€)"
                    )
                else:
                    st.progress(percent_normalized, text=f"{budget['percent']:.0f}%")
                    st.success(f"✅ **{budget['delta']:.0f}€** restant")

                # Actions for critical budgets
                if budget["percent"] > 90:
                    cols_action = st.columns(2)
                    with cols_action[0]:
                        if st.button(
                            "💡 Conseils", key=f"tip_{budget['cat_name']}", use_container_width=True
                        ):
                            st.toast(f"Analyse de {budget['cat_name']}...", icon="💡")
                    with cols_action[1]:
                        if st.button(
                            "⚙️ Ajuster",
                            key=f"adjust_{budget['cat_name']}",
                            use_container_width=True,
                        ):
                            st.session_state["intel_active_tab"] = "🎯 Budgets"
                            st.switch_page("pages/4_Intelligence.py")
