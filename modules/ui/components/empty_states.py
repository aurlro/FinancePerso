"""
Empty States Component - Engaging empty states for better UX.
Prevents user abandonment by providing clear next steps.
"""

from collections.abc import Callable

import streamlit as st


def render_empty_state(
    icon: str = "📭",
    title: str = "Aucune donnée",
    message: str = "Commencez par ajouter des données.",
    action_label: str | None = None,
    action_icon: str = "➕",
    action_page: str | None = None,
    action_callback: Callable | None = None,
    help_text: str | None = None,
    illustration: str | None = None,
    key: str = "empty_state",
):
    """
    Render an engaging empty state with clear CTA.

    Args:
        icon: Emoji icon for the empty state
        title: Title text
        message: Description message
        action_label: Label for the action button (None = no button)
        action_icon: Icon for the action button
        action_page: Page to navigate to (e.g., "pages/1_Opérations.py")
        action_callback: Optional callback function instead of page navigation
        help_text: Additional help text below the button
        illustration: Optional SVG or HTML illustration
        key: Unique key for the component
    """
    # Container with styling
    with st.container(border=True):
        # Centered content
        col1, col2, col3 = st.columns([1, 3, 1])

        with col2:
            # Large icon
            st.markdown(
                f"<div style='text-align: center; font-size: 4rem; margin-bottom: 1rem;'>{icon}</div>",
                unsafe_allow_html=True,
            )

            # Title
            st.markdown(
                f"<h3 style='text-align: center; color: #475569; margin-bottom: 0.5rem;'>{title}</h3>",
                unsafe_allow_html=True,
            )

            # Message
            st.markdown(
                f"<p style='text-align: center; color: #64748b; margin-bottom: 1.5rem;'>{message}</p>",
                unsafe_allow_html=True,
            )

            # Action button
            if action_label:
                if action_callback:
                    if st.button(
                        f"{action_icon} {action_label}",
                        type="primary",
                        use_container_width=True,
                        key=f"{key}_action",
                    ):
                        action_callback()
                elif action_page:
                    if st.button(
                        f"{action_icon} {action_label}",
                        type="primary",
                        use_container_width=True,
                        key=f"{key}_action",
                    ):
                        st.switch_page(action_page)

            # Help text
            if help_text:
                st.markdown(
                    f"<p style='text-align: center; color: #94a3b8; font-size: 0.9rem; margin-top: 1rem;'>{help_text}</p>",
                    unsafe_allow_html=True,
                )


def render_no_transactions_state(key: str = "no_transactions"):
    """Empty state for when no transactions exist."""
    render_empty_state(
        icon="📊",
        title="Aucune transaction",
        message="Commencez par importer vos relevés bancaires pour visualiser vos finances.",
        action_label="Importer des transactions",
        action_icon="📥",
        action_page="pages/1_Opérations.py",
        help_text="💡 Vous pouvez importer des fichiers CSV de votre banque (BoursoBank, etc.)",
        key=key,
    )


def render_no_budgets_state(key: str = "no_budgets"):
    """Empty state for when no budgets are defined."""
    render_empty_state(
        icon="🎯",
        title="Aucun budget défini",
        message="Définissez des budgets par catégorie pour suivre vos dépenses et recevoir des alertes.",
        action_label="Créer un budget",
        action_icon="➕",
        action_page="pages/4_Intelligence.py",
        help_text="💡 Commencez par les catégories où vous dépensez le plus",
        key=key,
    )


def render_no_rules_state(key: str = "no_rules"):
    """Empty state for when no learning rules exist."""
    render_empty_state(
        icon="🧠",
        title="Aucune règle de catégorisation",
        message="Créez des règles pour automatiser la catégorisation de vos transactions.",
        action_label="Créer une règle",
        action_icon="⚡",
        action_page="pages/4_Intelligence.py",
        help_text="💡 Les règles apprennent de vos habitudes de validation",
        key=key,
    )


def render_no_categories_state(key: str = "no_categories"):
    """Empty state for when no custom categories exist."""
    render_empty_state(
        icon="🏷️",
        title="Aucune catégorie personnalisée",
        message="Créez des catégories pour organiser vos dépenses selon vos besoins.",
        action_label="Gérer les catégories",
        action_icon="⚙️",
        action_page="pages/9_Configuration.py",
        help_text="💡 Les catégories par défaut suffisent pour commencer",
        key=key,
    )


def render_no_search_results(query: str = "", key: str = "no_results"):
    """Empty state for when search returns no results."""
    render_empty_state(
        icon="🔍",
        title="Aucun résultat",
        message=(
            f"Aucune transaction ne correspond à '{query}'."
            if query
            else "Aucune transaction ne correspond à vos critères."
        ),
        action_label="Effacer les filtres",
        action_icon="🔄",
        help_text="💡 Essayez avec des termes plus généraux ou vérifiez l'orthographe",
        key=key,
    )


def render_no_data_state(
    title: str = "Aucune donnée",
    message: str = "Les données ne sont pas encore disponibles.",
    key: str = "no_data",
):
    """Generic empty state for missing data."""
    render_empty_state(icon="📭", title=title, message=message, key=key)


def render_error_state(
    error_message: str = "Une erreur s'est produite",
    retry_callback: Callable | None = None,
    key: str = "error_state",
):
    """Error state with retry option."""
    render_empty_state(
        icon="⚠️",
        title="Oups !",
        message=error_message,
        action_label="Réessayer" if retry_callback else None,
        action_icon="🔄",
        action_callback=retry_callback,
        help_text="💡 Si le problème persiste, contactez le support",
        key=key,
    )


def render_loading_state(message: str = "Chargement...", key: str = "loading"):
    """Loading state with spinner and message."""
    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<div style='text-align: center; padding: 2rem;'>", unsafe_allow_html=True)
            with st.spinner(message):
                st.empty()
            st.markdown("</div>", unsafe_allow_html=True)


# Export
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
