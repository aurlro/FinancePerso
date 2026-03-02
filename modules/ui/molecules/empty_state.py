"""Molecule EmptyState - État vide standardisé.

Remplace toutes les variantes d'états vides dispersées dans l'application.

Usage:
    from modules.ui.molecules import EmptyState

    EmptyState.render(
        title="Aucune transaction",
        message="Commencez par importer vos données",
        icon="📄",
        action_text="Importer",
        on_action=import_handler
    )
"""

from collections.abc import Callable

import streamlit as st

from modules.ui.atoms import Button, Icon
from modules.ui.tokens import BorderRadius, Colors, Spacing, Typography


class EmptyState:
    """État vide unifié pour toute l'application.

    Remplace:
    - render_empty_state() de components/empty_states.py
    - render_no_transactions_state() de components/empty_states.py
    - render_no_budgets_state() de components/empty_states.py
    - render_empty_state() de assistant/components.py
    - etc.
    """

    @staticmethod
    def render(
        title: str,
        message: str,
        icon: str = "📭",
        action_text: str | None = None,
        on_action: Callable | None = None,
        secondary_action_text: str | None = None,
        on_secondary_action: Callable | None = None,
        key: str | None = None,
    ) -> None:
        """Rend un état vide standardisé.

        Args:
            title: Titre principal
            message: Description détaillée
            icon: Emoji/icône
            action_text: Texte bouton principal
            on_action: Callback bouton principal
            secondary_action_text: Texte bouton secondaire
            on_secondary_action: Callback bouton secondaire
            key: Clé unique Streamlit
        """
        container_style = f"""
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: {Spacing.XL_2};
            background: linear-gradient(135deg, {Colors.SLATE_50} 0%, {Colors.WHITE} 100%);
            border: 2px dashed {Colors.SLATE_300};
            border-radius: {BorderRadius.LG};
            text-align: center;
        """

        st.markdown(f'<div style="{container_style}">', unsafe_allow_html=True)

        # Icône
        st.markdown(
            f'<div style="font-size: 3rem; margin-bottom: {Spacing.MD};">{icon}</div>',
            unsafe_allow_html=True,
        )

        # Titre
        title_style = f"""
            font-size: {Typography.SIZE_XL};
            font-weight: {Typography.WEIGHT_SEMIBOLD};
            color: {Colors.SLATE_800};
            margin-bottom: {Spacing.XS};
        """
        st.markdown(f'<div style="{title_style}">{title}</div>', unsafe_allow_html=True)

        # Message
        message_style = f"""
            font-size: {Typography.SIZE_BASE};
            color: {Colors.SLATE_500};
            margin-bottom: {Spacing.LG};
            max-width: 400px;
        """
        st.markdown(f'<div style="{message_style}">{message}</div>', unsafe_allow_html=True)

        # Boutons
        if action_text and on_action and key:
            col1, col2 = st.columns([1, 1])
            with col1:
                Button.primary(
                    action_text, key=f"{key}_primary", on_click=on_action, use_container_width=True
                )

            if secondary_action_text and on_secondary_action:
                with col2:
                    Button.secondary(
                        secondary_action_text,
                        key=f"{key}_secondary",
                        on_click=on_secondary_action,
                        use_container_width=True,
                    )

        st.markdown("</div>", unsafe_allow_html=True)

    @classmethod
    def no_transactions(
        cls,
        on_import: Callable | None = None,
        key: str | None = None,
    ) -> None:
        """État vide spécifique: aucune transaction.

        Usage:
            EmptyState.no_transactions(on_import=import_handler)
        """
        cls.render(
            title="Aucune transaction",
            message="Vous n'avez pas encore importé de transactions. Commencez par importer votre relevé bancaire.",
            icon=Icon.FILE,
            action_text="📥 Importer des transactions",
            on_action=on_import,
            key=key or "no_transactions",
        )

    @classmethod
    def no_budgets(
        cls,
        on_create: Callable | None = None,
        key: str | None = None,
    ) -> None:
        """État vide spécifique: aucun budget.

        Usage:
            EmptyState.no_budgets(on_create=create_handler)
        """
        cls.render(
            title="Aucun budget défini",
            message="Définissez des budgets par catégorie pour suivre vos dépenses et recevoir des alertes.",
            icon=Icon.TARGET,
            action_text="🎯 Créer un budget",
            on_action=on_create,
            key=key or "no_budgets",
        )

    @classmethod
    def no_search_results(
        cls,
        search_term: str = "",
        on_clear: Callable | None = None,
        key: str | None = None,
    ) -> None:
        """État vide spécifique: recherche sans résultat.

        Usage:
            EmptyState.no_search_results(search_term="restaurant")
        """
        message = (
            f'Aucun résultat trouvé pour "{search_term}".'
            if search_term
            else "Aucun résultat trouvé."
        )
        cls.render(
            title="Pas de résultats",
            message=message,
            icon=Icon.SEARCH,
            action_text="🔄 Effacer la recherche",
            on_action=on_clear,
            key=key or "no_search_results",
        )

    @classmethod
    def no_data(
        cls,
        data_type: str = "données",
        on_action: Callable | None = None,
        key: str | None = None,
    ) -> None:
        """État vide générique.

        Usage:
            EmptyState.no_data(data_type="catégories")
        """
        cls.render(
            title=f"Aucune {data_type}",
            message=f"Il n'y a pas encore de {data_type} à afficher.",
            icon=Icon.INFO,
            action_text="🔄 Actualiser",
            on_action=on_action,
            key=key or f"no_{data_type}",
        )
