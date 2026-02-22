"""
AI Insights Widget

Widgets pour les insights et analyses générées par IA.
"""

import calendar
import datetime

import pandas as pd
import streamlit as st

from modules.categorization import generate_financial_report
from modules.transaction_types import (
    calculate_true_expenses,
    calculate_true_income,
    filter_expense_transactions,
)
from modules.ui import card_kpi


def render_month_end_forecast(
    df: pd.DataFrame, selected_years: list, selected_months: list, fixed_categories: list
):
    """
    Render month-end forecasting with multiple scenarios.

    Args:
        df: Full transaction dataset
        selected_years: List of selected years
        selected_months: List of selected month numbers
        fixed_categories: List of fixed expense categories
    """
    st.header("🔮 Prévisions Fin de Mois")

    today = datetime.date.today()

    if today.year not in selected_years or today.month not in selected_months:
        st.caption(f"Prévisions disponibles pour le mois en cours ({today.strftime('%B %Y')}).")
        return

    days_in_month = calendar.monthrange(today.year, today.month)[1]
    days_passed = today.day
    days_remaining = days_in_month - days_passed

    # date_dt est déjà présent depuis la page principale (cache)
    df_month = df[
        (df["date_dt"].dt.year == today.year) & (df["date_dt"].dt.month == today.month)
    ].copy()

    if df_month.empty:
        st.info("Aucune donnée pour le mois en cours pour les prévisions.")
        return

    # Prepare expense data using categories (not amount sign!)
    df_m_exp = filter_expense_transactions(df_month).copy()
    df_m_exp["amount"] = df_m_exp["amount"].abs()  # Take absolute for display
    df_m_exp["raw_cat"] = df_m_exp.apply(
        lambda x: (
            x["category_validated"]
            if x["category_validated"] != "Inconnu"
            else (x["original_category"] or "Inconnu")
        ),
        axis=1,
    )
    df_m_exp["type"] = df_m_exp["raw_cat"].apply(
        lambda x: "Fixe" if x in fixed_categories else "Variable"
    )

    exp_fixed = df_m_exp[df_m_exp["type"] == "Fixe"]["amount"].sum()
    exp_var = df_m_exp[df_m_exp["type"] == "Variable"]["amount"].sum()

    # Income using categories (not amount sign!)
    income = calculate_true_income(df_month, include_refunds=False)

    if days_passed > 0:
        # Calcul intelligent: moyenne sur jours avec dépenses UNIQUEMENT
        days_with_expenses = len(
            df_m_exp[df_m_exp["type"] == "Variable"]["date_dt"].dt.date.unique()
        )
        if days_with_expenses > 0:
            avg_daily_var = exp_var / days_with_expenses
        else:
            avg_daily_var = exp_var / days_passed if days_passed > 0 else 0

        # Scénarios
        scenarios = {
            "pessimiste": {
                "multiplier": 1.3,  # +30% (dépenses augmentent)
                "label": "🔴 Si dépenses augmentent",
                "emoji": "🔴",
            },
            "realiste": {
                "multiplier": 1.0,  # Tendance actuelle
                "label": "🟡 Tendance actuelle",
                "emoji": "🟡",
            },
            "optimiste": {
                "multiplier": 0.75,  # -25% (réduction)
                "label": "🟢 Si réduit de 25%",
                "emoji": "🟢",
            },
        }

        # Affichage des scénarios
        st.caption("**Projection selon différents scénarios**")

        cols = st.columns(3)
        for i, (name, scenario) in enumerate(scenarios.items()):
            proj_var = avg_daily_var * days_remaining * scenario["multiplier"]
            proj_total = exp_fixed + exp_var + proj_var
            balance = income - proj_total

            with cols[i]:
                with st.container(border=True):
                    st.markdown(f"{scenario['label']}")

                    # Montant principal coloré selon le résultat
                    if balance >= 0:
                        st.markdown(
                            f"<h3 style='color: #22c55e; margin: 0;'>{balance:+.0f}€</h3>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f"<h3 style='color: #ef4444; margin: 0;'>{balance:+.0f}€</h3>",
                            unsafe_allow_html=True,
                        )

                    st.caption(f"Dépenses totales: {proj_total:.0f}€")

                    # Message contextuel
                    if name == "pessimiste" and balance < 0:
                        st.error(f"⚠️ Déficit de {abs(balance):.0f}€")
                    elif name == "realiste":
                        if balance >= 0:
                            st.success(f"✅ +{balance:.0f}€ d'épargne")
                        else:
                            st.warning(f"⚠️ -{abs(balance):.0f}€ de déficit")
                    elif name == "optimiste" and balance > 0:
                        st.success("🎯 Objectif atteint!")

        # KPIs actuels
        st.divider()
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            current_balance = income - (exp_fixed + exp_var)
            card_kpi(
                "Solde Actuel",
                f"{current_balance:+.0f} €",
                trend=f"Recettes: {income:.0f}€",
                trend_color="positive" if current_balance >= 0 else "negative",
            )
        with col_f2:
            card_kpi(
                "Dépenses à ce jour",
                f"{exp_fixed + exp_var:.0f} €",
                trend=f"{exp_fixed:.0f}€ fixes + {exp_var:.0f}€ var.",
                trend_color="negative",
            )
        with col_f3:
            days_left = days_in_month - days_passed
            card_kpi(
                "Jours restants",
                f"{days_left}",
                trend=f"Sur {days_in_month} jours",
                trend_color="neutral",
            )

        # Recommandation personnalisée
        st.divider()
        remaining_budget = income - exp_fixed - exp_var

        if days_remaining > 0:
            daily_budget = remaining_budget / days_remaining

            if daily_budget < 0:
                st.error(
                    "💡 **Alerte critique**: Vous avez déjà dépassé votre capacité. "
                    "Objectif: **0€/jour** jusqu'à la fin du mois pour limiter les dégâts."
                )
            elif daily_budget < 20:
                st.warning(
                    f"💡 **Attention serré**: Pour tenir, ne dépassez pas **{daily_budget:.0f}€/jour** "
                    f"en dépenses variables sur les {days_remaining} jours restants."
                )
            else:
                st.info(
                    f"💡 **Conseil**: Budget journalier recommandé: **{daily_budget:.0f}€/jour** "
                    "pour finir le mois à l'équilibre."
                )

        # Historique comparatif si données dispo
        try:
            prev_month = today.replace(day=1) - datetime.timedelta(days=1)
            df_prev = df[
                (df["date_dt"].dt.year == prev_month.year)
                & (df["date_dt"].dt.month == prev_month.month)
            ].copy()

            if not df_prev.empty:
                prev_exp = calculate_true_expenses(df_prev, include_refunds=True)
                prev_inc = calculate_true_income(df_prev, include_refunds=False)
                prev_bal = prev_inc - prev_exp

                evolution = (
                    ((current_balance - prev_bal) / abs(prev_bal) * 100) if prev_bal != 0 else 0
                )
                trend_emoji = "📈" if evolution > 0 else "📉" if evolution < 0 else "➡️"

                st.caption(
                    f"{trend_emoji} **vs mois dernier**: {prev_bal:+.0f}€ → {current_balance:+.0f}€ "
                    f"({evolution:+.0f}%)"
                )
        except Exception:
            pass
    else:
        st.write("📅 Début de mois — les prévisions seront disponibles dans quelques jours.")


def render_ai_financial_report(
    df_current: pd.DataFrame,
    df_prev: pd.DataFrame,
    df: pd.DataFrame,
    selected_years: list,
    selected_months: list,
):
    """
    Render AI-powered financial report and recommendations.

    Args:
        df_current: Current period transactions
        df_prev: Previous period transactions
        df: Full transaction dataset
        selected_years: List of selected years
        selected_months: List of selected month numbers
    """
    st.subheader("🔮 Analyse & Conseils IA")

    if df_current.empty:
        st.info("Sélectionnez une période avec des données pour générer un rapport.")
        return

    # 1. Current Period Stats (from df_current) - using categories not amount sign
    cur_inc = calculate_true_income(df_current, include_refunds=False)
    cur_exp_val = calculate_true_expenses(df_current, include_refunds=True)
    cur_top_cat = (
        filter_expense_transactions(df_current)
        .groupby("category_validated")["amount"]
        .sum()
        .abs()
        .nlargest(3)
        .to_dict()
    )

    # 2. Previous Period Stats (from df_prev)
    prev_exp_val = (
        calculate_true_expenses(df_prev, include_refunds=True) if not df_prev.empty else 0
    )

    # 3. YTD context (all data for the latest year in selection)
    latest_year = max(selected_years) if selected_years else datetime.date.today().year
    # date_dt est déjà présent depuis la page principale (cache)
    df_ytd = df[df["date_dt"].dt.year == latest_year]
    ytd_inc = calculate_true_income(df_ytd, include_refunds=False)
    ytd_exp = calculate_true_expenses(df_ytd, include_refunds=True)
    ytd_sav = ytd_inc - ytd_exp

    stats_payload = {
        "period_label": f"Sélection: {', '.join(map(str, selected_years))} ({len(selected_months)} mois)",
        "current_period": {
            "income": round(cur_inc, 2),
            "expenses": round(cur_exp_val, 2),
            "balance": round(cur_inc - cur_exp_val, 2),
            "top_categories": {k: round(v, 2) for k, v in cur_top_cat.items()},
        },
        "previous_period": {
            "expenses": round(prev_exp_val, 2),
            "evolution_percent": (
                round(((cur_exp_val - prev_exp_val) / prev_exp_val * 100), 1)
                if prev_exp_val > 0
                else 0
            ),
        },
        "ytd_context": {
            "year": latest_year,
            "total_income": round(ytd_inc, 2),
            "total_expenses": round(ytd_exp, 2),
            "total_savings": round(ytd_sav, 2),
            "savings_rate_percent": round((ytd_sav / ytd_inc * 100), 1) if ytd_inc > 0 else 0,
        },
    }

    if st.button("Générer le rapport & conseils 🪄", key="button_ai_report"):
        with st.spinner("L'IA analyse vos finances sur cette période..."):
            report = generate_financial_report(stats_payload)
            st.markdown(report)
            st.success("Rapport généré avec succès !")
