"""Liste de transactions - Affichage amélioré avec icônes.

Usage:
    from modules.ui.v5_5.components.transactions import TransactionList

    TransactionList.render(df, limit=10)
"""

from datetime import datetime

import pandas as pd
import streamlit as st

# Mapping catégories → icônes
CATEGORY_ICONS = {
    "Alimentation": "🍽️",
    "Courses": "🛒",
    "Transport": "🚗",
    "Logement": "🏠",
    "Santé": "⚕️",
    "Loisirs": "🎮",
    "Shopping": "🛍️",
    "Vêtements": "👕",
    "Restaurants": "🍔",
    "Salaire": "💰",
    "Revenus": "💵",
    "Investissements": "📈",
    "Épargne": "🎯",
    "Factures": "📄",
    "Abonnements": "📺",
    "Voyage": "✈️",
    "Éducation": "📚",
    "Cadeaux": "🎁",
    "Virement Interne": "🔄",
    "Hors Budget": "⚡",
    "Inconnu": "❓",
    "Autre": "📌",
}


def get_category_icon(category: str | None) -> str:
    """Retourne l'icône pour une catégorie.

    Args:
        category: Nom de la catégorie

    Returns:
        Emoji icône
    """
    if not category:
        return "📌"
    return CATEGORY_ICONS.get(category, "📌")


class TransactionList:
    """Composant liste de transactions."""

    @staticmethod
    def render(
        df: pd.DataFrame,
        limit: int = 5,
        show_category: bool = True,
        show_date: bool = True,
        empty_message: str = "Aucune transaction",
    ) -> None:
        """Affiche une liste de transactions.

        Args:
            df: DataFrame avec colonnes [date, label, amount, category_validated]
            limit: Nombre maximum de transactions à afficher
            show_category: Afficher la catégorie
            show_date: Afficher la date
            empty_message: Message si vide
        """
        if df.empty:
            st.info(empty_message)
            return

        # Trier par date décroissante et limiter
        df = df.sort_values("date", ascending=False).head(limit)

        # Afficher chaque transaction
        for _, tx in df.iterrows():
            TransactionList._render_transaction_row(tx, show_category, show_date)

        # Lien vers toutes les transactions
        if len(df) == limit:
            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            if st.button("Voir toutes les transactions →", key=f"see_all_tx_{limit}"):
                st.switch_page("pages/01_Import.py")

    @staticmethod
    def _render_transaction_row(
        tx: pd.Series,
        show_category: bool,
        show_date: bool,
    ) -> None:
        """Affiche une ligne de transaction."""
        amount = tx["amount"]
        is_expense = amount < 0

        # Formater le montant
        amount_str = f"{amount:,.2f} €".replace(",", " ").replace(".", ",")
        amount_color = "#EF4444" if is_expense else "#10B981"

        # Icône de catégorie
        category = tx.get("category_validated", "Autre")
        icon = get_category_icon(category)

        # Date relative
        date_str = ""
        if show_date:
            tx_date = pd.to_datetime(tx["date"])
            today = datetime.now()
            delta = (today - tx_date).days

            if delta == 0:
                date_str = "Aujourd'hui"
            elif delta == 1:
                date_str = "Hier"
            else:
                date_str = tx_date.strftime("%d/%m")

        # Info catégorie
        category_info = f"{category} • " if show_category and category else ""

        # HTML pour la transaction
        st.markdown(
            f"""
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 0;
            border-bottom: 1px solid #E5E7EB;
            transition: background-color 0.2s;
        " onmouseover="this.style.backgroundColor='#F9FAFB'""
        "" onmouseout="this.style.backgroundColor='transparent'">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span style="
                    font-size: 1.25rem;
                    width: 1.5rem;
                    text-align: center;
                ">{icon}</span>
                <div>
                    <div style="font-weight: 500; color: #1F2937; font-size: 0.9375rem;">
                        {tx['label'][:35]}{'...' if len(tx['label']) > 35 else ''}
                    </div>
                    <div style="font-size: 0.8125rem; color: #6B7280; margin-top: 0.125rem;">
                        {category_info}{date_str}
                    </div>
                </div>
            </div>
            <div style="font-weight: 600; color: {amount_color}; font-size: 0.9375rem;">
                {amount_str}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )


class TransactionCard:
    """Carte de transaction individuelle."""

    @staticmethod
    def render(
        label: str,
        amount: float,
        category: str | None = None,
        date: datetime | None = None,
    ) -> None:
        """Affiche une carte de transaction.

        Args:
            label: Libellé de la transaction
            amount: Montant (négatif pour dépense)
            category: Catégorie (optionnel)
            date: Date (optionnel)
        """
        is_expense = amount < 0
        amount_str = f"{amount:,.2f} €".replace(",", " ").replace(".", ",")
        amount_color = "#EF4444" if is_expense else "#10B981"
        icon = get_category_icon(category)

        date_str = ""
        if date:
            date_str = date.strftime("%d/%m/%Y")

        with st.container(border=True):
            cols = st.columns([1, 3, 2])
            with cols[0]:
                st.markdown(
                    f"<span style='font-size: 1.5rem;'>{icon}</span>", unsafe_allow_html=True
                )
            with cols[1]:
                st.write(f"**{label}**")
                if category:
                    st.caption(category)
                if date_str:
                    st.caption(date_str)
            with cols[2]:
                st.markdown(
                    f"<p style='color: {amount_color}; font-weight: 600; "
                    f"text-align: right;'>{amount_str}</p>",
                    unsafe_allow_html=True,
                )
