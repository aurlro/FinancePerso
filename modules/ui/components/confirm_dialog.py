"""
Confirmation dialogs (Legacy wrapper).
This module provides fallback implementations using native Streamlit components.
"""

import warnings
from collections.abc import Callable

import streamlit as st


def _warn_deprecation():
    """Affiche un avertissement de déprécation."""
    warnings.warn(
        "modules.ui.components.confirm_dialog is deprecated. "
        "Use native Streamlit components or st.dialog() instead.",
        DeprecationWarning,
        stacklevel=3,
    )


def confirm_dialog(
    title: str = "Confirmer l'action",
    message: str = "Êtes-vous sûr ?",
    confirm_label: str = "Confirmer",
    cancel_label: str = "Annuler",
    confirm_type: str = "primary",
    danger: bool = False,
) -> bool | None:
    """
    Affiche une boîte de dialogue de confirmation.
    
    Args:
        title: Titre du dialog
        message: Message explicatif
        confirm_label: Label du bouton de confirmation
        cancel_label: Label du bouton d'annulation
        confirm_type: Type du bouton confirm (primary/secondary)
        danger: Si True, affiche comme une action dangereuse
        
    Returns:
        True si confirmé, False si annulé, None si pas encore de réponse
    """
    _warn_deprecation()
    
    # Utiliser un container avec bordure pour simuler un dialog
    with st.container(border=True):
        if danger:
            st.error(f"⚠️ {title}")
        else:
            st.warning(f"⚠️ {title}")
        st.markdown(message)
        
        st.markdown("---")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            cancelled = st.button(
                cancel_label,
                key=f"cancel_dialog_{hash(title + message)}",
                use_container_width=True,
                type="secondary",
            )
        
        with col2:
            confirmed = st.button(
                confirm_label,
                key=f"confirm_dialog_{hash(title + message)}",
                use_container_width=True,
                type="primary" if not danger else "secondary",
            )
            
            if danger:
                # Style pour le bouton danger
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
        
        return None


def confirm_delete(
    entity_name: str,
    entity_description: str = "",
    on_confirm: Callable | None = None,
) -> bool | None:
    """
    Dialog de confirmation pour une suppression.
    
    Args:
        entity_name: Nom de l'entité à supprimer
        entity_description: Description supplémentaire
        on_confirm: Callback appelé si confirmé
        
    Returns:
        True si confirmé, False si annulé, None si pas encore de réponse
    """
    _warn_deprecation()
    
    message = f"Vous êtes sur le point de supprimer **{entity_name}**."
    if entity_description:
        message += f"\n\n{entity_description}"
    message += "\n\n🗑️ Cette action est irréversible."
    
    result = confirm_dialog(
        title="Confirmer la suppression",
        message=message,
        confirm_label="Supprimer",
        cancel_label="Annuler",
        danger=True,
    )
    
    if result is True and on_confirm:
        on_confirm()
    
    return result


def confirm_action(
    action: str,
    target: str,
    consequences: str = "",
    on_confirm: Callable | None = None,
) -> bool | None:
    """
    Dialog de confirmation pour une action critique.
    
    Args:
        action: Nom de l'action (ex: "fusionner", "archiver")
        target: Cible de l'action
        consequences: Description des conséquences
        on_confirm: Callback appelé si confirmé
        
    Returns:
        True si confirmé, False si annulé, None si pas encore de réponse
    """
    _warn_deprecation()
    
    message = f"Vous êtes sur le point de **{action}** : **{target}**."
    if consequences:
        message += f"\n\n{consequences}"
    
    result = confirm_dialog(
        title="Confirmer l'action",
        message=message,
        confirm_label="Confirmer",
        cancel_label="Annuler",
        danger=False,
    )
    
    if result is True and on_confirm:
        on_confirm()
    
    return result


def info_dialog(
    title: str,
    message: str,
    button_label: str = "OK",
) -> bool:
    """
    Dialog informatif simple.
    
    Args:
        title: Titre du dialog
        message: Message à afficher
        button_label: Label du bouton
        
    Returns:
        True quand fermé (bouton OK cliqué)
    """
    _warn_deprecation()
    
    with st.container(border=True):
        st.info(f"ℹ️ {title}")
        st.markdown(message)
        
        st.markdown("---")
        
        if st.button(
            button_label,
            key=f"info_dialog_{hash(title + message)}",
            use_container_width=True,
            type="primary",
        ):
            return True
    
    return False


__all__ = [
    "confirm_dialog",
    "confirm_delete",
    "confirm_action",
    "info_dialog",
]
