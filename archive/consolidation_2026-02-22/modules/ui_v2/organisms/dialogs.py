"""Confirmation dialogs - Dialogs de confirmation utilisateur.

Fournit des dialogs standardisés pour les actions critiques
qui nécessitent une confirmation.
"""

from typing import Callable, Optional

import streamlit as st

from modules.ui_v2.atoms.icons import IconSet


def confirm_dialog(
    title: str = "Confirmer l'action",
    message: str = "Êtes-vous sûr ?",
    confirm_label: str = "Confirmer",
    cancel_label: str = "Annuler",
    danger: bool = False,
) -> bool:
    """Affiche un dialog de confirmation générique.

    Args:
        title: Titre du dialog
        message: Message explicatif
        confirm_label: Label du bouton de confirmation
        cancel_label: Label du bouton d'annulation
        danger: Si True, le bouton de confirmation est en rouge

    Returns:
        True si confirmé, False sinon
    """
    with st.container():
        st.markdown(f"### {title}")
        st.markdown(message)

        col1, col2 = st.columns(2)

        with col1:
            cancelled = st.button(cancel_label, key=f"cancel_{hash(title)}", use_container_width=True)

        with col2:
            confirmed = st.button(
                confirm_label,
                key=f"confirm_{hash(title)}",
                type="primary" if not danger else "secondary",
                use_container_width=True,
            )

            if danger:
                # Ajouter un style danger au bouton (via markdown hack)
                st.markdown(
                    """
                    <style>
                    div[data-testid="stButton"] > button[kind="secondary"] {
                        background-color: #dc3545;
                        color: white;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )

        if cancelled:
            return False
        if confirmed:
            return True

        return False


def confirm_delete(
    entity_name: str,
    entity_description: str = "",
    on_confirm: Optional[Callable] = None,
) -> bool:
    """Dialog de confirmation pour une suppression.

    Args:
        entity_name: Nom de l'entité à supprimer
        entity_description: Description supplémentaire
        on_confirm: Callback appelé si confirmé

    Returns:
        True si confirmé, False sinon
    """
    message = f"Vous êtes sur le point de supprimer **{entity_name}**."
    if entity_description:
        message += f"\n\n{entity_description}"
    message += "\n\nCette action est irréversible."

    confirmed = confirm_dialog(
        title=f"{IconSet.DELETE.value} Confirmer la suppression",
        message=message,
        confirm_label="Supprimer",
        cancel_label="Annuler",
        danger=True,
    )

    if confirmed and on_confirm:
        on_confirm()

    return confirmed


def confirm_action(
    action: str,
    target: str,
    consequences: str = "",
    on_confirm: Optional[Callable] = None,
) -> bool:
    """Dialog de confirmation pour une action critique.

    Args:
        action: Nom de l'action (ex: "fusionner", "archiver")
        target: Cible de l'action
        consequences: Description des conséquences
        on_confirm: Callback appelé si confirmé

    Returns:
        True si confirmé, False sinon
    """
    message = f"Vous êtes sur le point de **{action}** : **{target}**."
    if consequences:
        message += f"\n\n{consequences}"

    confirmed = confirm_dialog(
        title=f"{IconSet.WARNING.value} Confirmer l'action",
        message=message,
        confirm_label="Confirmer",
        cancel_label="Annuler",
        danger=False,
    )

    if confirmed and on_confirm:
        on_confirm()

    return confirmed


def info_dialog(title: str, message: str, button_label: str = "OK") -> bool:
    """Dialog informatif simple.

    Args:
        title: Titre du dialog
        message: Message à afficher
        button_label: Label du bouton

    Returns:
        True quand fermé
    """
    with st.container():
        st.markdown(f"### {IconSet.INFO.value} {title}")
        st.markdown(message)

        if st.button(button_label, key=f"info_{hash(title + message)}", use_container_width=True):
            return True

    return False
