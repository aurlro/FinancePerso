"""KPI Grid - Grille de métriques pour le dashboard.

Affiche 4 KPIs dans une grille responsive.

Usage:
    from modules.ui.v5_5.dashboard import render_kpi_grid, calculate_kpis

    kpis = calculate_kpis("Février 2026")
    render_kpi_grid(kpis)
"""

from datetime import datetime

import pandas as pd
import streamlit as st

from modules.db.transactions import get_all_transactions
from modules.ui.v5_5.components.kpi_card import KPICard, KPIData, format_currency


def render_kpi_grid(kpis: list[KPIData]) -> None:
    """Affiche une grille de 4 KPIs.

    Args:
        kpis: Liste de 4 KPIData à afficher
    """
    if len(kpis) != 4:
        st.warning(f"⚠️ Attendu 4 KPIs, reçu {len(kpis)}")

    # Créer 4 colonnes égales
    cols = st.columns(4)

    # Afficher chaque KPI dans sa colonne
    for idx, kpi in enumerate(kpis[:4]):  # Max 4
        with cols[idx]:
            KPICard.render(kpi)


def calculate_kpis(month_str: str) -> list[KPIData]:
    """Calcule les 4 KPIs principaux pour un mois donné.

    Args:
        month_str: Mois au format "Février 2026"

    Returns:
        Liste des 4 KPIData
    """
    # Parser le mois
    year, month = parse_month(month_str)

    # Récupérer les transactions du mois
    try:
        df = get_all_transactions()
        if df.empty:
            return _get_empty_kpis()
    except Exception:
        return _get_empty_kpis()

    # Filtrer par mois
    df["date"] = pd.to_datetime(df["date"])
    month_mask = (df["date"].dt.year == year) & (df["date"].dt.month == month)
    df_month = df[month_mask]

    # Mois précédent pour les variations
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    prev_mask = (df["date"].dt.year == prev_year) & (df["date"].dt.month == prev_month)
    df_prev = df[prev_mask]

    # Calculs
    income = df_month[df_month["amount"] > 0]["amount"].sum()
    expenses = abs(df_month[df_month["amount"] < 0]["amount"].sum())

    # Épargne (catégorie épargne ou objectifs)
    savings_mask = df_month["category_validated"].str.contains(
        "épargne|objectif|savings|goal", case=False, na=False
    )
    savings = abs(df_month[savings_mask & (df_month["amount"] < 0)]["amount"].sum())

    # Reste à vivre
    remaining = income - expenses

    # Calculs mois précédent
    prev_income = df_prev[df_prev["amount"] > 0]["amount"].sum()
    prev_expenses = abs(df_prev[df_prev["amount"] < 0]["amount"].sum())
    prev_remaining = prev_income - prev_expenses

    # Variations
    def calc_var(current, previous):
        if previous == 0:
            return None
        return ((current - previous) / abs(previous)) * 100

    remaining_var = calc_var(remaining, prev_remaining)
    expenses_var = calc_var(expenses, prev_expenses)
    income_var = calc_var(income, prev_income)

    # Formater les variations
    def fmt_var(var):
        if var is None:
            return None
        return f"{var:+.1f}%"

    # Déterminer le mois précédent pour l'affichage
    months_fr = [
        "Janvier",
        "Février",
        "Mars",
        "Avril",
        "Mai",
        "Juin",
        "Juillet",
        "Août",
        "Septembre",
        "Octobre",
        "Novembre",
        "Décembre",
    ]
    prev_month_name = months_fr[prev_month - 1]

    return [
        KPIData(
            label="Reste à vivre",
            value=format_currency(remaining),
            value_color="positive" if remaining > 0 else "negative",
            icon="💚",
            icon_bg="#DCFCE7",
            variation=fmt_var(remaining_var),
            variation_label=f"vs {prev_month_name} {prev_year}",
        ),
        KPIData(
            label="Dépenses",
            value=f"-{format_currency(expenses)}",
            value_color="negative",
            icon="💳",
            icon_bg="#FEE2E2",
            variation=fmt_var(expenses_var),
            variation_label=f"vs {prev_month_name} {prev_year}",
        ),
        KPIData(
            label="Revenus",
            value=format_currency(income),
            value_color="positive" if income_var and income_var >= 0 else "neutral",
            icon="📈",
            icon_bg="#DBEAFE",
            variation=fmt_var(income_var),
            variation_label=f"vs {prev_month_name} {prev_year}",
        ),
        KPIData(
            label="Épargne",
            value=format_currency(savings),
            value_color="positive" if savings > 0 else "neutral",
            icon="🎯",
            icon_bg="#F3E8FF",
            variation=None,
            variation_label="🎉 Premier versement !" if savings > 0 else None,
        ),
    ]


def _get_empty_kpis() -> list[KPIData]:
    """Retourne des KPIs vides pour l'état initial."""
    return [
        KPIData(
            label="Reste à vivre",
            value="0,00 €",
            value_color="neutral",
            icon="💚",
            icon_bg="#DCFCE7",
        ),
        KPIData(
            label="Dépenses", value="0,00 €", value_color="neutral", icon="💳", icon_bg="#FEE2E2"
        ),
        KPIData(
            label="Revenus", value="0,00 €", value_color="neutral", icon="📈", icon_bg="#DBEAFE"
        ),
        KPIData(
            label="Épargne", value="0,00 €", value_color="neutral", icon="🎯", icon_bg="#F3E8FF"
        ),
    ]


def parse_month(month_str: str) -> tuple[int, int]:
    """Parse une chaîne de mois.

    Args:
        month_str: Chaîne (ex: "Février 2026")

    Returns:
        Tuple (year, month)
    """
    months_fr = {
        "janvier": 1,
        "février": 2,
        "mars": 3,
        "avril": 4,
        "mai": 5,
        "juin": 6,
        "juillet": 7,
        "août": 8,
        "septembre": 9,
        "octobre": 10,
        "novembre": 11,
        "décembre": 12,
    }

    parts = month_str.lower().split()
    month = months_fr.get(parts[0], 1)
    year = int(parts[1]) if len(parts) > 1 else datetime.now().year

    return year, month
