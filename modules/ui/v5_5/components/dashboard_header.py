"""Dashboard Header - Header personnalisé V5.5.

Affiche le header "Bonjour, [Nom] 👋" avec sélecteur de mois,
comme dans les maquettes FinCouple.

Usage:
    from modules.ui.v5_5.components import DashboardHeader

    selected_month = DashboardHeader.render(
        user_name="Alex",
        current_month="Février 2026",
        available_months=["Janvier 2026", "Février 2026", "Mars 2026"]
    )
"""

from datetime import datetime

import streamlit as st

from modules.ui.v5_5.theme import LightColors


class DashboardHeader:
    """Header du dashboard style maquette V5.5.

    Affiche:
    - Titre "Bonjour, [Nom] 👋"
    - Sous-titre avec le mois en cours
    - Sélecteur de mois aligné à droite

    Usage:
        selected = DashboardHeader.render(
            user_name="Alex",
            current_month="Février 2026"
        )
    """

    @staticmethod
    def render(
        user_name: str | None = None,
        current_month: str | None = None,
        available_months: list[str] | None = None,
        key: str = "dashboard_header",
    ) -> str | None:
        """Rend le header du dashboard.

        Args:
            user_name: Nom de l'utilisateur (affiché dans "Bonjour, [Nom]")
            current_month: Mois actuel (ex: "Février 2026")
            available_months: Liste des mois disponibles pour le sélecteur
            key: Clé unique pour le sélecteur Streamlit

        Returns:
            Le mois sélectionné si available_months fourni, sinon None
        """
        # Valeurs par défaut
        if current_month is None:
            current_month = get_current_month_name()

        if available_months is None:
            available_months = get_last_12_months()

        # Layout: titre à gauche, sélecteur à droite
        col_title, col_spacer, col_selector = st.columns([2, 1, 1])

        with col_title:
            # Titre principal
            name_part = f", {user_name}" if user_name else ""
            st.markdown(
                f"""
            <h1 style="
                font-size: 2rem;
                font-weight: 700;
                color: {LightColors.TEXT_PRIMARY};
                margin-bottom: 0.5rem;
                letter-spacing: -0.025em;
            ">
                Bonjour{name_part} 👋
            </h1>
            <p style="
                color: {LightColors.TEXT_SECONDARY};
                font-size: 1rem;
                margin-top: 0;
                margin-bottom: 1.5rem;
            ">
                Voici le résumé de vos finances pour {current_month}
            </p>
            """,
                unsafe_allow_html=True,
            )

        selected = None

        with col_selector:
            # Sélecteur de mois
            st.markdown("<br>", unsafe_allow_html=True)  # Espacement

            # Utiliser un container avec bordure pour le sélecteur
            with st.container():
                selected = st.selectbox(
                    "Mois",
                    options=available_months,
                    index=(
                        available_months.index(current_month)
                        if current_month in available_months
                        else 0
                    ),
                    label_visibility="collapsed",
                    key=f"{key}_month_selector",
                )

        return selected

    @staticmethod
    def render_simple(
        user_name: str | None = None,
        subtitle: str | None = None,
    ) -> None:
        """Version simplifiée sans sélecteur.

        Args:
            user_name: Nom de l'utilisateur
            subtitle: Sous-titre personnalisé
        """
        if subtitle is None:
            subtitle = f"Voici le résumé de vos finances pour {get_current_month_name()}"

        name_part = f", {user_name}" if user_name else ""

        st.markdown(
            f"""
        <h1 style="
            font-size: 2rem;
            font-weight: 700;
            color: {LightColors.TEXT_PRIMARY};
            margin-bottom: 0.5rem;
            letter-spacing: -0.025em;
        ">
            Bonjour{name_part} 👋
        </h1>
        <p style="
            color: {LightColors.TEXT_SECONDARY};
            font-size: 1rem;
            margin-top: 0;
            margin-bottom: 1.5rem;
        ">
            {subtitle}
        </p>
        """,
            unsafe_allow_html=True,
        )


def get_current_month_name() -> str:
    """Retourne le nom du mois courant formaté.

    Returns:
        Nom du mois (ex: "Février 2026")
    """
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

    now = datetime.now()
    return f"{months_fr[now.month - 1]} {now.year}"


def get_last_12_months() -> list[str]:
    """Retourne les 12 derniers mois.

    Returns:
        Liste des mois (ex: ["Mars 2025", ..., "Février 2026"])
    """
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

    result = []
    now = datetime.now()

    for i in range(11, -1, -1):
        # Calculer le mois (attention aux années qui décrémentent)
        month_idx = (now.month - 1 - i) % 12
        year = now.year + (now.month - 1 - i) // 12

        # Ajuster si on est passé en négatif
        if now.month - 1 - i < 0:
            year = now.year - 1
            month_idx = 12 + (now.month - 1 - i)

        result.append(f"{months_fr[month_idx]} {year}")

    return result


def format_month(year: int, month: int) -> str:
    """Formate un mois et une année.

    Args:
        year: Année (ex: 2026)
        month: Mois (1-12)

    Returns:
        Chaîne formatée (ex: "Février 2026")
    """
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

    return f"{months_fr[month - 1]} {year}"


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
