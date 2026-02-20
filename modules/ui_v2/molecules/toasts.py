"""Toast notifications - Messages brefs en haut à droite.

Les toasts sont des notifications temporaires qui apparaissent
en haut à droite de l'écran et disparaissent automatiquement.
"""

import streamlit as st

from modules.ui_v2.atoms.icons import IconSet


def toast_success(message: str, icon: str = None):
    """Affiche un toast de succès.

    Args:
        message: Message à afficher
        icon: Icône personnalisée (défaut: ✅)
    """
    icon = icon or IconSet.SUCCESS.value
    st.toast(message, icon=icon)


def toast_error(message: str, icon: str = None):
    """Affiche un toast d'erreur.

    Args:
        message: Message à afficher
        icon: Icône personnalisée (défaut: ❌)
    """
    icon = icon or IconSet.ERROR.value
    st.toast(message, icon=icon)


def toast_warning(message: str, icon: str = None):
    """Affiche un toast d'avertissement.

    Args:
        message: Message à afficher
        icon: Icône personnalisée (défaut: ⚠️)
    """
    icon = icon or IconSet.WARNING.value
    st.toast(message, icon=icon)


def toast_info(message: str, icon: str = None):
    """Affiche un toast d'information.

    Args:
        message: Message à afficher
        icon: Icône personnalisée (défaut: ℹ️)
    """
    icon = icon or IconSet.INFO.value
    st.toast(message, icon=icon)


# Alias pour compatibilité
toast = toast_info
