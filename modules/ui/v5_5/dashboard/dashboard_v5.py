"""Dashboard V5.5 - Dashboard complet style maquette FinCouple.

Usage:
    from modules.ui.v5_5.dashboard import render_dashboard_v5

    render_dashboard_v5()
"""

from typing import TYPE_CHECKING

import pandas as pd
import streamlit as st

from modules.db.transactions import get_all_transactions

if TYPE_CHECKING:
    pass
from modules.ui.v5_5.components.charts import DonutChart
from modules.ui.v5_5.components.dashboard_header import (
    DashboardHeader,
    get_current_month_name,
    get_last_12_months,
)
from modules.ui.v5_5.components.savings_goals import SavingsGoalsWidget
from modules.ui.v5_5.components.transactions import TransactionList
from modules.ui.v5_5.dashboard.kpi_grid import calculate_kpis, render_kpi_grid
from modules.ui.v5_5.theme import apply_light_theme
from modules.ui.v5_5.welcome import has_transactions


def render_dashboard_v5(
    user_name: str | None = None,
    default_month: str | None = None,
) -> None:
    """Rend le dashboard complet V5.5.

    Affiche:
    - Header avec "Bonjour [Nom]" et sélecteur de mois
    - Grille de 4 KPIs (Reste à vivre, Dépenses, Revenus, Épargne)
    - Graphique de répartition des dépenses
    - Liste des transactions récentes
    - Objectifs d'épargne
    - Vue Couple (si configurée)

    Args:
        user_name: Nom de l'utilisateur
        default_month: Mois par défaut (sinon mois courant)
    """
    # Appliquer thème
    apply_light_theme()

    # Vérifier si données existent
    if not has_transactions():
        from modules.ui.v5_5.dashboard.empty_state import render_dashboard_empty

        render_dashboard_empty(user_name=user_name)
        return

    # Mois par défaut
    if default_month is None:
        default_month = get_current_month_name()

    available_months = get_last_12_months()

    # 1. Header
    selected_month = DashboardHeader.render(
        user_name=user_name,
        current_month=default_month,
        available_months=available_months,
        key="dashboard_v5",
    )

    # 2. Section Vue d'ensemble
    st.markdown(
        """
    <h2 style="
        font-size: 1.25rem;
        font-weight: 600;
        color: #1F2937;
        margin-top: 2rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    ">
        📊 Vue d'ensemble
    </h2>
    """,
        unsafe_allow_html=True,
    )

    # 3. KPIs
    kpis = calculate_kpis(selected_month or default_month)
    render_kpi_grid(kpis)

    # 4. Deux colonnes: Graphique + Transactions
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

    # Récupérer les données du mois sélectionné
    df_month = _get_month_data(selected_month or default_month)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        # Graphique donut avec le nouveau composant
        DonutChart.render_expenses(
            df=df_month,
            month_str=selected_month or default_month,
            top_n=5,
            height=350,
        )

    with col_right:
        # Liste transactions avec le nouveau composant
        st.markdown("#### 📝 Transactions récentes")
        TransactionList.render(
            df=df_month,
            limit=5,
            show_category=True,
            show_date=True,
            empty_message="Aucune transaction ce mois-ci",
        )

    # 5. Section Objectifs d'épargne
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    SavingsGoalsWidget.render(max_display=3)

    # 6. Vue Couple (si configurée)
    _render_couple_section_if_enabled()

    # Footer
    st.divider()
    st.caption("FinancePerso V5.5 - Dashboard")


def _get_month_data(month_str: str) -> "pd.DataFrame":
    """Récupère les données d'un mois spécifique.

    Args:
        month_str: Mois au format "Février 2026"

    Returns:
        DataFrame filtré pour ce mois
    """
    try:
        import pandas as pd

        from modules.ui.v5_5.dashboard.kpi_grid import parse_month

        year, month = parse_month(month_str)

        df = get_all_transactions()
        if df.empty:
            return pd.DataFrame()

        df["date"] = pd.to_datetime(df["date"])
        month_mask = (df["date"].dt.year == year) & (df["date"].dt.month == month)
        return df[month_mask]
    except Exception:
        import pandas as pd

        return pd.DataFrame()


def _render_couple_section_if_enabled() -> None:
    """Affiche la section couple si le mode couple est activé."""
    try:
        from modules.couple.couple_settings import is_couple_configured

        if not is_couple_configured():
            return

        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        st.markdown(
            """
        <h2 style="
            font-size: 1.25rem;
            font-weight: 600;
            color: #1F2937;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        ">
            💑 Vue Couple
        </h2>
        """,
            unsafe_allow_html=True,
        )

        # Résumé couple
        from modules.ui.v5_5.dashboard.couple_summary import render_couple_summary

        render_couple_summary()

    except ImportError:
        # Mode couple non disponible
        pass


def render_expenses_chart(month_str: str) -> None:
    """Affiche le graphique de répartition des dépenses (legacy).

    Args:
        month_str: Mois au format "Février 2026"
    """
    # Utilise maintenant DonutChart
    df_month = _get_month_data(month_str)
    DonutChart.render_expenses(df=df_month, month_str=month_str)


def render_recent_transactions(month_str: str, limit: int = 5) -> None:
    """Affiche les transactions récentes (legacy).

    Args:
        month_str: Mois au format "Février 2026"
        limit: Nombre de transactions à afficher
    """
    # Utilise maintenant TransactionList
    df_month = _get_month_data(month_str)
    st.markdown("#### 📝 Transactions récentes")
    TransactionList.render(
        df=df_month,
        limit=limit,
        empty_message="Aucune transaction ce mois-ci",
    )


def render_dashboard_simple() -> None:
    """Version simplifiée pour test rapide."""
    render_dashboard_v5(
        user_name="Alex",
        default_month=get_current_month_name(),
    )
