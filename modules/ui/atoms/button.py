"""Atom Button - Boutons standardisés.

Usage:
    from modules.ui.atoms import Button

    Button.primary("Sauvegarder", on_click=save_handler)
    Button.secondary("Annuler")
    Button.danger("Supprimer", confirm=True)
"""

from collections.abc import Callable
from enum import Enum

import streamlit as st

from modules.ui.tokens import Colors


class ButtonVariant(str, Enum):
    """Variantes de boutons."""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    DANGER = "danger"
    GHOST = "ghost"


class Button:
    """Boutons standardisés selon le Design System.

    Tous les boutons de l'application doivent utiliser cette classe.
    """

    @staticmethod
    def _render(
        label: str,
        variant: ButtonVariant = ButtonVariant.PRIMARY,
        key: str | None = None,
        on_click: Callable | None = None,
        disabled: bool = False,
        use_container_width: bool = True,
        icon: str | None = None,
    ) -> bool:
        """Rendu interne du bouton.

        Args:
            label: Texte du bouton
            variant: Style du bouton
            key: Clé unique Streamlit
            on_click: Callback au clic
            disabled: État désactivé
            use_container_width: Prendre toute la largeur
            icon: Emoji/icône optionnelle

        Returns:
            True si cliqué
        """
        label_text = f"{icon} {label}" if icon else label

        # Mapping vers les types Streamlit natifs
        type_mapping = {
            ButtonVariant.PRIMARY: "primary",
            ButtonVariant.SECONDARY: "secondary",
            ButtonVariant.TERTIARY: "secondary",
            ButtonVariant.DANGER: "primary",  # Streamlit n'a pas de type danger
            ButtonVariant.GHOST: "secondary",
        }

        # Pour les boutons danger, on ajoute une classe CSS
        if variant == ButtonVariant.DANGER:
            st.markdown(
                f"""
                <style>
                div[data-testid="stButton"] > button[key="{key}"] {{
                    background-color: {Colors.DANGER};
                    border-color: {Colors.DANGER};
                }}
                div[data-testid="stButton"] > button[key="{key}"]:hover {{
                    background-color: {Colors.DANGER_DARK};
                    border-color: {Colors.DANGER_DARK};
                }}
                </style>
                """,
                unsafe_allow_html=True,
            )

        clicked = st.button(
            label=label_text,
            key=key,
            on_click=on_click,
            disabled=disabled,
            use_container_width=use_container_width,
            type=type_mapping[variant],
        )

        return clicked

    @classmethod
    def primary(
        cls,
        label: str,
        key: str | None = None,
        on_click: Callable | None = None,
        disabled: bool = False,
        use_container_width: bool = True,
        icon: str | None = None,
    ) -> bool:
        """Bouton primaire (action principale).

        Usage:
            if Button.primary("Sauvegarder", key="save"):
                save_data()
        """
        return cls._render(
            label=label,
            variant=ButtonVariant.PRIMARY,
            key=key,
            on_click=on_click,
            disabled=disabled,
            use_container_width=use_container_width,
            icon=icon,
        )

    @classmethod
    def secondary(
        cls,
        label: str,
        key: str | None = None,
        on_click: Callable | None = None,
        disabled: bool = False,
        use_container_width: bool = True,
        icon: str | None = None,
    ) -> bool:
        """Bouton secondaire (action alternative).

        Usage:
            if Button.secondary("Annuler", key="cancel"):
                go_back()
        """
        return cls._render(
            label=label,
            variant=ButtonVariant.SECONDARY,
            key=key,
            on_click=on_click,
            disabled=disabled,
            use_container_width=use_container_width,
            icon=icon,
        )

    @classmethod
    def danger(
        cls,
        label: str,
        key: str | None = None,
        on_click: Callable | None = None,
        disabled: bool = False,
        use_container_width: bool = True,
        icon: str | None = None,
        confirm: bool = False,
        confirm_message: str = "Êtes-vous sûr ? Cette action est irréversible.",
    ) -> bool:
        """Bouton danger (action destructive).

        Args:
            confirm: Si True, affiche une confirmation avant l'action
            confirm_message: Message de confirmation

        Usage:
            if Button.danger("Supprimer", key="delete", confirm=True):
                delete_item()
        """
        if confirm and key:
            # Vérifier si on doit afficher la confirmation
            confirm_key = f"{key}_confirm_open"

            if not st.session_state.get(confirm_key, False):
                if cls._render(
                    label=label,
                    variant=ButtonVariant.DANGER,
                    key=key,
                    disabled=disabled,
                    use_container_width=use_container_width,
                    icon=icon or "🗑️",
                ):
                    st.session_state[confirm_key] = True
                    st.rerun()
                return False
            else:
                # Afficher la confirmation
                st.warning(confirm_message)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Confirmer", key=f"{key}_confirm_yes"):
                        st.session_state[confirm_key] = False
                        if on_click:
                            on_click()
                        return True
                with col2:
                    if st.button("❌ Annuler", key=f"{key}_confirm_no"):
                        st.session_state[confirm_key] = False
                        st.rerun()
                return False

        return cls._render(
            label=label,
            variant=ButtonVariant.DANGER,
            key=key,
            on_click=on_click,
            disabled=disabled,
            use_container_width=use_container_width,
            icon=icon,
        )

    @classmethod
    def ghost(
        cls,
        label: str,
        key: str | None = None,
        on_click: Callable | None = None,
        disabled: bool = False,
        use_container_width: bool = False,
        icon: str | None = None,
    ) -> bool:
        """Bouton ghost (action légère/subtile).

        Usage:
            if Button.ghost("Voir plus", key="see_more"):
                expand()
        """
        return cls._render(
            label=label,
            variant=ButtonVariant.GHOST,
            key=key,
            on_click=on_click,
            disabled=disabled,
            use_container_width=use_container_width,
            icon=icon,
        )

    @classmethod
    def icon_button(
        cls,
        icon: str,
        key: str | None = None,
        on_click: Callable | None = None,
        disabled: bool = False,
        help: str | None = None,
    ) -> bool:
        """Bouton icône seul (sans texte).

        Usage:
            if Button.icon_button("✏️", key="edit"):
                edit_item()
        """
        return st.button(
            icon,
            key=key,
            on_click=on_click,
            disabled=disabled,
            help=help,
        )
