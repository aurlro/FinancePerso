"""Widgets réutilisables pour le dashboard couple."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.ui.design_system import Colors
from modules.utils import format_currency


def render_personal_card(
    title: str,
    metrics: dict,
    show_details: bool = True,
    categories_df: pd.DataFrame = None,
    emoji: str = "👤",
):
    """Rend une carte personnelle avec métriques.

    Args:
        title: Titre de la carte (ex: "Mes dépenses")
        metrics: Dict avec transaction_count, total_income, total_expenses, net
        show_details: Si True, affiche les détails (catégories, etc.)
        categories_df: DataFrame avec les catégories (pour les détails)
        emoji: Emoji à afficher
    """
    with st.container(border=True):
        # Header
        st.markdown(f"**{emoji} {title}**")

        # Métriques principales
        cols = st.columns(3)

        with cols[0]:
            income = metrics.get("total_income", 0)
            st.metric("Revenus", format_currency(income))

        with cols[1]:
            expenses = metrics.get("total_expenses", 0)
            st.metric("Dépenses", format_currency(expenses))

        with cols[2]:
            net = metrics.get("net", 0)
            delta_color = "normal" if net >= 0 else "inverse"
            st.metric("Net", format_currency(net), delta_color=delta_color)

        # Détails si autorisé
        if show_details and categories_df is not None and not categories_df.empty:
            st.divider()
            st.caption("**Répartition par catégorie:**")

            # Afficher top 5 catégories
            display_df = categories_df.head(5).copy()

            for _, row in display_df.iterrows():
                cat_cols = st.columns([3, 2, 1])

                with cat_cols[0]:
                    category = row.get("category", "Autre")
                    st.text(f"{category}")

                with cat_cols[1]:
                    amount = row.get("total_amount", 0)
                    st.text(format_currency(amount))

                with cat_cols[2]:
                    count = row.get("transaction_count", 0)
                    st.caption(f"({count})")

            if len(categories_df) > 5:
                st.caption(f"... et {len(categories_df) - 5} autres catégories")

        elif not show_details:
            # Mode confidentiel
            st.divider()
            render_confidentiality_badge()

            if categories_df is not None and not categories_df.empty:
                st.caption("**Répartition (agrégée):**")

                for _, row in categories_df.head(5).iterrows():
                    cat_cols = st.columns([3, 2])

                    with cat_cols[0]:
                        st.text(f"{row.get('category', 'Autre')}")

                    with cat_cols[1]:
                        st.text(format_currency(row.get("total_amount", 0)))


def render_transfer_section(transfers_data: dict):
    """Rend la section des virements internes.

    Args:
        transfers_data: Dict avec pending_count, validated_transfers, etc.
    """
    with st.container(border=True):
        st.markdown("**🔄 Virements internes**")
        st.caption("Transferts entre vos comptes (exclus des statistiques)")

        pending = transfers_data.get("pending_count", 0)
        validated_amount = transfers_data.get("total_validated_amount", 0)

        cols = st.columns([2, 2, 1])

        with cols[0]:
            if pending > 0:
                st.warning(f"⏳ {pending} virement(s) en attente de validation")
            else:
                st.success("✅ Tous les virements sont validés")

        with cols[1]:
            st.metric("Total masqué", format_currency(validated_amount))

        with cols[2]:
            if st.button("🔍 Voir", key="view_transfers"):
                st.session_state["show_transfer_details"] = True


def render_confidentiality_badge():
    """Affiche un badge de confidentialité."""
    st.markdown(
        f"""
        <div style="
            background-color: {Colors.BACKGROUND_ELEVATED};
            border: 1px solid {Colors.ACCENT_WARNING};
            border-radius: 4px;
            padding: 8px 12px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 0.85em;
            color: {Colors.TEXT_SECONDARY};
        ">
            <span>🔒</span>
            <span>Données agrégées uniquement - Confidentialité respectée</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_partner_anonymous_card(title: str, metrics: dict):
    """Rend une carte pour le partenaire (sans détails).

    Args:
        title: Titre de la carte
        metrics: Dict avec les métriques agrégées
    """
    with st.container(border=True):
        st.markdown(f"**👤 {title}** 🔒")

        cols = st.columns(3)

        with cols[0]:
            st.metric("Revenus", format_currency(metrics.get("total_income", 0)))

        with cols[1]:
            st.metric("Dépenses", format_currency(metrics.get("total_expenses", 0)))

        with cols[2]:
            net = metrics.get("net", 0)
            st.metric("Net", format_currency(net))

        st.divider()
        st.caption("🔒 Données confidentielles - Vue agrégée uniquement")


def render_comparison_bar(me_value: float, partner_value: float, label: str):
    """Rend une barre de comparaison entre deux valeurs.

    Args:
        me_value: Valeur pour l'utilisateur
        partner_value: Valeur pour le partenaire
        label: Label de la métrique
    """
    total = me_value + partner_value
    if total == 0:
        me_pct = 50
        partner_pct = 50
    else:
        me_pct = (me_value / total) * 100
        partner_pct = (partner_value / total) * 100

    st.markdown(f"**{label}**")

    # Barre visuelle
    st.markdown(
        f"""
        <div style="
            display: flex;
            height: 24px;
            border-radius: 4px;
            overflow: hidden;
            margin: 8px 0;
        ">
            <div style="
                width: {me_pct}%;
                background-color: {Colors.ACCENT_SECONDARY};
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 0.8em;
            ">{format_currency(me_value)}</div>
            <div style="
                width: {partner_pct}%;
                background-color: {Colors.ACCENT_TERTIARY};
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 0.8em;
            ">{format_currency(partner_value)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_joint_transactions_section(transactions_df: pd.DataFrame):
    """Rend la section des transactions communes.

    Args:
        transactions_df: DataFrame des transactions communes
    """
    with st.container(border=True):
        st.markdown("**👥 Dépenses communes**")

        if transactions_df.empty:
            st.info("Aucune transaction commune pour cette période")
            return

        # Métriques
        total = transactions_df["amount"].sum()
        count = len(transactions_df)
        expenses = transactions_df[transactions_df["amount"] < 0]["amount"].sum()

        cols = st.columns(3)
        with cols[0]:
            st.metric("Total", format_currency(total))
        with cols[1]:
            st.metric("Dépenses", format_currency(expenses))
        with cols[2]:
            st.metric("Transactions", count)

        # Top catégories
        if not transactions_df.empty:
            st.divider()
            st.caption("**Top catégories:**")

            by_cat = transactions_df.groupby("category")["amount"].sum().reset_index()
            by_cat = by_cat.sort_values("amount").head(5)

            for _, row in by_cat.iterrows():
                st.text(f"{row['category']}: {format_currency(row['amount'])}")
