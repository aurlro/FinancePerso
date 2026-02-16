"""
Import Analyzer - Analyse temps réel lors de l'import de transactions
"""

from datetime import datetime

import pandas as pd
import streamlit as st

from modules.notifications_realtime import RealTimeAlert, get_notification_manager
from modules.transaction_types import filter_expense_transactions, filter_income_transactions


def analyze_imported_transactions(df_new: pd.DataFrame, df_history: pd.DataFrame) -> list[dict]:
    """
    Analyse un batch de transactions nouvellement importées.
    Génère des alertes temps réel si nécessaire.

    Args:
        df_new: Nouvelles transactions importées
        df_history: Historique existant

    Returns:
        Liste des alertes générées
    """
    if df_new.empty:
        return []

    manager = get_notification_manager()
    alerts = []

    # Vérifier chaque nouvelle transaction
    for _, tx in df_new.iterrows():
        tx_dict = tx.to_dict()
        new_alerts = manager.check_new_transaction(tx_dict, df_history)
        alerts.extend(new_alerts)

    # Vérifier les budgets dépassés après l'import
    from modules.db.budgets import get_budgets

    budgets = get_budgets()

    if not budgets.empty and not df_new.empty:
        # Regrouper les nouvelles dépenses par catégorie
        current_month = datetime.now().strftime("%Y-%m")

        # Combiner historique + nouvelles pour ce mois
        df_combined = pd.concat([df_history, df_new], ignore_index=True)
        df_month = df_combined[df_combined["date_dt"].dt.strftime("%Y-%m") == current_month]

        for _, budget in budgets.iterrows():
            category = budget["category"]
            budget_amount = budget["amount"]

            # Calculer les dépenses actuelles
            spent = filter_expense_transactions(df_month)
            spent = spent[spent["category_validated"] == category]["amount"].abs().sum()

            # Vérifier si on vient de dépasser
            old_spent = filter_expense_transactions(df_history)
            old_spent = (
                old_spent[
                    (old_spent["category_validated"] == category)
                    & (old_spent["date_dt"].dt.strftime("%Y-%m") == current_month)
                ]["amount"]
                .abs()
                .sum()
            )

            # Si on dépasse maintenant mais pas avant
            if spent > budget_amount and old_spent <= budget_amount:
                alert = manager.check_budget_overrun(category, spent, budget_amount)
                if alert:
                    alerts.append(alert)

    return alerts


def render_import_summary(df_imported: pd.DataFrame, alerts: list[RealTimeAlert]):
    """
    Affiche un résumé de l'import avec les alertes détectées.

    Args:
        df_imported: DataFrame des transactions importées
        alerts: Liste des alertes générées
    """
    st.success(f"✅ **{len(df_imported)} transactions importées avec succès !**")

    if alerts:
        st.markdown("---")
        st.subheader("🚨 Alertes détectées")
        st.caption("Ces événements ont été détectés lors de l'import :")

        # Grouper par sévérité
        critical = [a for a in alerts if a.severity == "critical"]
        warnings = [a for a in alerts if a.severity == "warning"]
        info = [a for a in alerts if a.severity == "info"]

        if critical:
            with st.container(border=True):
                st.error(f"🔴 **{len(critical)} problème(s) critique(s)**")
                for alert in critical[:3]:
                    st.write(f"• {alert.title}: {alert.message}")

        if warnings:
            with st.container(border=True):
                st.warning(f"🟠 **{len(warnings)} avertissement(s)**")
                for alert in warnings[:3]:
                    st.write(f"• {alert.title}")

        if info:
            with st.expander(f"ℹ️ {len(info)} information(s)"):
                for alert in info[:5]:
                    st.write(f"• {alert.title}")

        st.info(
            "💡 Consultez le centre de notifications pour plus de détails et les actions recommandées."
        )
    else:
        st.balloons()
        st.success("🎉 Aucune anomalie détectée ! Tout semble normal.")


def get_import_insights(df_imported: pd.DataFrame) -> dict:
    """
    Génère des insights sur l'import effectué.

    Args:
        df_imported: Transactions importées

    Returns:
        Dict avec les insights
    """
    if df_imported.empty:
        return {}

    insights = {
        "total_imported": len(df_imported),
        "total_amount": df_imported["amount"].sum(),
        "income_count": len(filter_income_transactions(df_imported)),
        "expense_count": len(filter_expense_transactions(df_imported)),
        "categories": df_imported["category_validated"].nunique(),
        "date_range": {"min": df_imported["date"].min(), "max": df_imported["date"].max()},
    }

    # Top catégories
    expenses = filter_expense_transactions(df_imported)
    if not expenses.empty:
        insights["top_category"] = (
            expenses.groupby("category_validated")["amount"].sum().abs().idxmax()
        )
        insights["largest_expense"] = expenses["amount"].abs().max()

    return insights


__all__ = ["analyze_imported_transactions", "render_import_summary", "get_import_insights"]
