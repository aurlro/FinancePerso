"""
Empty States Component.
Implémentations fallback utilisant Streamlit natif.
"""

import streamlit as st


def render_empty_state(title, message, icon="📭"):
    """Affiche un état vide générique."""
    st.info(f"{icon} **{title}**: {message}")


def render_no_transactions_state(
    title="Aucune transaction",
    message="Aucune transaction à afficher pour cette période.",
    icon="📭",
    key=None,
):
    """Affiche un état vide pour les transactions."""
    st.info(f"{icon} **{title}**: {message}")


def render_no_budgets_state(
    title="Aucun budget", message="Aucun budget défini. Créez un budget pour commencer.", icon="💰"
):
    """Affiche un état vide pour les budgets."""
    st.info(f"{icon} **{title}**: {message}")


def render_no_rules_state(
    title="Aucune règle", message="Aucune règle de catégorisation définie.", icon="📋"
):
    """Affiche un état vide pour les règles."""
    st.info(f"{icon} **{title}**: {message}")


def render_no_categories_state(
    title="Aucune catégorie",
    message="Aucune catégorie définie. Créez des catégories pour organiser vos transactions.",
    icon="🏷️",
):
    """Affiche un état vide pour les catégories."""
    st.info(f"{icon} **{title}**: {message}")


def render_no_search_results(
    title="Aucun résultat", message="La recherche n'a retourné aucun résultat.", icon="🔍"
):
    """Affiche un état vide pour les résultats de recherche."""
    st.warning(f"{icon} **{title}**: {message}")


def render_no_data_state(title="Pas de données", message="Aucune donnée disponible.", icon="📊"):
    """Affiche un état vide générique pour l'absence de données."""
    st.info(f"{icon} **{title}**: {message}")


def render_error_state(title="Erreur", message="Une erreur s'est produite.", icon="⚠️"):
    """Affiche un état d'erreur."""
    st.error(f"{icon} **{title}**: {message}")


def render_loading_state(message="Chargement en cours...", icon="⏳"):
    """Affiche un état de chargement."""
    st.info(f"{icon} {message}")


__all__ = [
    "render_empty_state",
    "render_no_transactions_state",
    "render_no_budgets_state",
    "render_no_rules_state",
    "render_no_categories_state",
    "render_no_search_results",
    "render_no_data_state",
    "render_error_state",
    "render_loading_state",
]
