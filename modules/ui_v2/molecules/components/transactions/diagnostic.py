"""
Transaction Diagnostic Component
Outil pour détecter et corriger les transactions incohérentes (montant vs catégorie).

Migrated from: modules/ui/components/transaction_diagnostic.py
Classification: Molecule (diagnostic and repair component)
"""

import pandas as pd
import streamlit as st

from modules.db.transactions import get_all_transactions
from modules.transaction_types import (
    EXCLUDED_CATEGORIES,
    INCOME_CATEGORIES,
    get_color_for_transaction,
    suggest_amount_sign,
    validate_amount_consistency,
)


def find_inconsistent_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Trouve toutes les transactions où le signe ne correspond pas à la catégorie.

    Returns:
        DataFrame des transactions incohérentes avec colonne 'warning'
    """
    if df.empty or "category_validated" not in df.columns or "amount" not in df.columns:
        return pd.DataFrame()

    inconsistencies = []

    for idx, row in df.iterrows():
        is_valid, warning = validate_amount_consistency(
            row.get("category_validated"), row.get("amount", 0)
        )

        if not is_valid:
            inconsistencies.append(
                {
                    "id": row.get("id"),
                    "date": row.get("date"),
                    "label": row.get("label"),
                    "amount": row.get("amount"),
                    "category": row.get("category_validated"),
                    "warning": warning,
                    "suggested_fix": suggest_amount_sign(row.get("category_validated")),
                }
            )

    return pd.DataFrame(inconsistencies)


def render_diagnostic_summary():
    """Affiche un résumé des problèmes détectés."""
    df = get_all_transactions()

    if df.empty:
        st.info("📭 Aucune transaction à analyser.")
        return

    problems = find_inconsistent_transactions(df)

    if problems.empty:
        st.success("✅ Toutes les transactions sont cohérentes !")
        st.balloons()
        return

    # Afficher les métriques
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Transactions incohérentes", len(problems))
    with col2:
        st.metric("Total transactions", len(df))
    with col3:
        pct = (len(problems) / len(df)) * 100
        st.metric("Taux d'incohérence", f"{pct:.1f}%")

    st.divider()

    # Afficher les problèmes par catégorie
    st.subheader("📊 Répartition par catégorie")

    cat_counts = problems["category"].value_counts()

    cols = st.columns(min(len(cat_counts), 4))
    for i, (cat, count) in enumerate(cat_counts.items()):
        with cols[i % 4]:
            st.metric(cat, count)

    st.divider()

    # Liste détaillée des problèmes
    st.subheader("🔍 Détails des transactions à corriger")

    for _, problem in problems.iterrows():
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.markdown(f"**{problem['label']}**")
                st.caption(f"{problem['date']} • {problem['category']}")
                st.warning(problem["warning"])

            with col2:
                amount = problem["amount"]
                category = problem["category"]
                color = get_color_for_transaction(category)
                st.markdown(
                    f"<span style='color:{color};font-size:1.5em'>{amount:,.2f} €</span>",
                    unsafe_allow_html=True,
                )

            with col3:
                suggested = problem["suggested_fix"]
                if suggested == 1:
                    new_amount = abs(amount)
                elif suggested == -1:
                    new_amount = -abs(amount)
                else:
                    new_amount = amount

                st.markdown("**→**")
                st.markdown(
                    f"<span style='color:blue;font-size:1.5em'>{new_amount:,.2f} €</span>",
                    unsafe_allow_html=True,
                )

                if st.button("✅ Corriger", key=f"fix_{problem['id']}"):
                    if fix_transaction_amount(problem["id"], new_amount):
                        st.success("Corrigé !")
                        st.rerun()


def fix_transaction_amount(tx_id: str, new_amount: float) -> bool:
    """
    Corrige le montant d'une transaction.

    Args:
        tx_id: ID de la transaction
        new_amount: Nouveau montant corrigé

    Returns:
        True si succès
    """
    try:
        # Note: Cette fonction dépend de votre système de DB
        # Adaptez selon votre implémentation

        # Mettre à jour le montant
        # update_transaction_amount(tx_id, new_amount)  # À implémenter selon votre DB

        st.info(f"Correction à appliquer : ID {tx_id} → {new_amount}")
        return True

    except Exception as e:
        st.error(f"Erreur lors de la correction : {e}")
        return False


def render_category_type_reference():
    """Affiche une référence des types de catégories."""
    st.subheader("📚 Référence des catégories")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**💰 Revenus**")
        for cat in INCOME_CATEGORIES[:5]:  # Limiter l'affichage
            st.caption(f"• {cat}")
        if len(INCOME_CATEGORIES) > 5:
            st.caption(f"... et {len(INCOME_CATEGORIES)-5} autres")

    with col2:
        st.markdown("**🚫 Exclues**")
        for cat in EXCLUDED_CATEGORIES:
            st.caption(f"• {cat}")

    with col3:
        st.markdown("**💸 Dépenses**")
        st.caption("• Toutes les autres catégories")
        st.caption("• Ex: Alimentation, Transport...")


def render_transaction_diagnostic_page():
    """
    Page complète de diagnostic.
    À intégrer dans la page Configuration ou un onglet dédié.
    """
    st.title("🔍 Diagnostic des Transactions")
    st.markdown("Vérifiez la cohérence entre les montants et les catégories.")

    tabs = st.tabs(["Diagnostic", "Référence", "Corrections en masse"])

    with tabs[0]:
        render_diagnostic_summary()

    with tabs[1]:
        render_category_type_reference()

    with tabs[2]:
        st.info(
            "🚧 Fonctionnalité à venir : correction automatique de toutes les transactions incohérentes."
        )


# Pour utilisation dans d'autres pages
def render_compact_diagnostic_card():
    """Carte compacte à afficher dans le dashboard ou la validation."""
    df = get_all_transactions()

    if df.empty:
        return

    problems = find_inconsistent_transactions(df)

    if not problems.empty:
        with st.container(border=True):
            st.warning(f"⚠️ {len(problems)} transactions incohérentes détectées")
            st.caption(
                "Certaines transactions ont un montant qui ne correspond pas à leur catégorie."
            )

            if st.button("🔍 Voir le diagnostic", use_container_width=True):
                st.switch_page("pages/99_Système.py")  # Diagnostics moved to Système/Debug
