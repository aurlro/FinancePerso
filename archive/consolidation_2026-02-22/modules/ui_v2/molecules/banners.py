"""Banner messages - Messages persistants dans la page.

Les banners sont des messages qui restent visibles jusqu'à ce que
l'utilisateur les ferme ou quitte la page.
"""

import streamlit as st

from modules.ui_v2.atoms.icons import IconSet


def show_success(message: str, icon: str = None):
    """Affiche un message de succès persistant.

    Args:
        message: Message à afficher
        icon: Icône à afficher avant le message
    """
    icon = icon or IconSet.SUCCESS.value
    st.success(f"{icon} {message}")


def show_error(message: str, icon: str = None):
    """Affiche un message d'erreur persistant.

    Args:
        message: Message à afficher
        icon: Icône à afficher avant le message
    """
    icon = icon or IconSet.ERROR.value
    st.error(f"{icon} {message}")


def show_warning(message: str, icon: str = None):
    """Affiche un message d'avertissement persistant.

    Args:
        message: Message à afficher
        icon: Icône à afficher avant le message
    """
    icon = icon or IconSet.WARNING.value
    st.warning(f"{icon} {message}")


def show_info(message: str, icon: str = None):
    """Affiche un message d'information persistant.

    Args:
        message: Message à afficher
        icon: Icône à afficher avant le message
    """
    icon = icon or IconSet.INFO.value
    st.info(f"{icon} {message}")


# Version enrichie avec plus de contexte
def show_rich_feedback(
    title: str,
    message: str,
    feedback_type: str = "info",
    icon: str = None,
    action_label: str = None,
    action_callback=None,
):
    """Affiche un message de feedback enrichi avec titre et action optionnelle.

    Args:
        title: Titre du message
        message: Contenu détaillé
        feedback_type: Type de feedback ('success', 'error', 'warning', 'info')
        icon: Icône personnalisée
        action_label: Label pour le bouton d'action (optionnel)
        action_callback: Fonction à appeler sur clic (optionnel)
    """
    icons = {
        "success": IconSet.SUCCESS.value,
        "error": IconSet.ERROR.value,
        "warning": IconSet.WARNING.value,
        "info": IconSet.INFO.value,
    }

    icon = icon or icons.get(feedback_type, IconSet.INFO.value)

    with st.container():
        st.markdown(f"### {icon} {title}")
        st.markdown(message)

        if action_label and action_callback:
            if st.button(action_label, key=f"rich_feedback_{hash(title + message)}"):
                action_callback()

    # Ajouter une ligne de séparation
    st.divider()
