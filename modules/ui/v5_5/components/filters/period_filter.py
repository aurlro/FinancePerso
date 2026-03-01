"""Filtre de période - Sélecteur de date range.

Usage:
    from modules.ui.v5_5.components.filters import render_period_filter

    start_date, end_date = render_period_filter()
"""

from datetime import datetime, timedelta

import streamlit as st


def render_period_filter() -> tuple[datetime | None, datetime | None]:
    """Affiche les filtres de période.

    Returns:
        Tuple (start_date, end_date) ou (None, None) si pas de filtre
    """
    st.markdown("### 📅 Période")

    # Préréglages rapides
    presets = {
        "Ce mois": (datetime.now().replace(day=1), datetime.now()),
        "Mois dernier": _get_last_month(),
        "Cette année": (datetime.now().replace(month=1, day=1), datetime.now()),
        "Année dernière": _get_last_year(),
        "Tout": (None, None),
    }

    col1, col2 = st.columns([1, 1])

    with col1:
        preset = st.selectbox(
            "Préréglage",
            options=list(presets.keys()),
            index=0,
            key="period_preset",
        )

    start_date, end_date = presets[preset]

    # Filtres personnalisés si "Tout" sélectionné
    if preset == "Tout":
        with col2:
            use_custom = st.checkbox("Personnaliser", key="use_custom_date")

        if use_custom:
            col3, col4 = st.columns(2)
            with col3:
                start_date = st.date_input(
                    "Du", value=datetime.now() - timedelta(days=30), key="custom_start_date"
                )
            with col4:
                end_date = st.date_input("Au", value=datetime.now(), key="custom_end_date")

    return start_date, end_date


def get_date_range(months: int = 12) -> tuple[datetime, datetime]:
    """Retourne une plage de dates par défaut.

    Args:
        months: Nombre de mois en arrière

    Returns:
        Tuple (start_date, end_date)
    """
    end = datetime.now()
    start = end - timedelta(days=30 * months)
    return start, end


def _get_last_month() -> tuple[datetime, datetime]:
    """Retourne le mois dernier."""
    today = datetime.now()
    first_day = today.replace(day=1)
    last_month_end = first_day - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    return last_month_start, last_month_end


def _get_last_year() -> tuple[datetime, datetime]:
    """Retourne l'année dernière."""
    today = datetime.now()
    last_year = today.year - 1
    start = datetime(last_year, 1, 1)
    end = datetime(last_year, 12, 31)
    return start, end
