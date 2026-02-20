"""Flash Messages System - Messages persistants entre pages.

Système de messages flash qui persistent dans le session_state
et s'affichent sur la page suivante.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

import streamlit as st

from modules.ui_v2.atoms.icons import IconSet
from modules.ui_v2.molecules.toasts import toast_error, toast_info, toast_success, toast_warning


class FlashType(Enum):
    """Types de messages flash."""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class FlashMessage:
    """Message flash avec métadonnées."""

    message: str
    msg_type: FlashType
    icon: Optional[str] = None
    timestamp: Optional[float] = None

    def __post_init__(self):
        if self.timestamp is None:
            import time

            self.timestamp = time.time()


# ============================================================================
# API PUBLIQUE
# ============================================================================


def set_flash_message(
    message: str,
    msg_type: FlashType = FlashType.SUCCESS,
    icon: Optional[str] = None,
):
    """Définit un message flash pour la page suivante.

    Args:
        message: Contenu du message
        msg_type: Type de message (success, error, warning, info)
        icon: Icône personnalisée (optionnel)
    """
    if "flash_messages" not in st.session_state:
        st.session_state.flash_messages = []

    flash = FlashMessage(
        message=message,
        msg_type=msg_type,
        icon=icon,
    )

    st.session_state.flash_messages.append(flash)


def display_flash_messages():
    """Affiche et vide tous les messages flash en attente."""
    if "flash_messages" not in st.session_state:
        return

    messages = st.session_state.flash_messages
    if not messages:
        return

    # Afficher chaque message
    for flash in messages:
        _display_flash(flash)

    # Vider la file
    st.session_state.flash_messages = []


def display_flash_toasts():
    """Affiche les messages flash comme des toasts (plus discrets)."""
    if "flash_messages" not in st.session_state:
        return

    messages = st.session_state.flash_messages
    if not messages:
        return

    # Afficher comme toasts
    for flash in messages:
        _display_flash_as_toast(flash)

    # Vider la file
    st.session_state.flash_messages = []


def clear_flash_messages():
    """Vide tous les messages flash sans les afficher."""
    if "flash_messages" in st.session_state:
        st.session_state.flash_messages = []


def has_flash_messages() -> bool:
    """Vérifie s'il y a des messages flash en attente.

    Returns:
        True s'il y a des messages en attente
    """
    if "flash_messages" not in st.session_state:
        return False
    return len(st.session_state.flash_messages) > 0


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================


def flash_success(message: str, icon: Optional[str] = None):
    """Message flash de succès (shortcut)."""
    set_flash_message(message, FlashType.SUCCESS, icon or IconSet.SUCCESS.value)


def flash_error(message: str, icon: Optional[str] = None):
    """Message flash d'erreur (shortcut)."""
    set_flash_message(message, FlashType.ERROR, icon or IconSet.ERROR.value)


def flash_warning(message: str, icon: Optional[str] = None):
    """Message flash d'avertissement (shortcut)."""
    set_flash_message(message, FlashType.WARNING, icon or IconSet.WARNING.value)


def flash_info(message: str, icon: Optional[str] = None):
    """Message flash d'information (shortcut)."""
    set_flash_message(message, FlashType.INFO, icon or IconSet.INFO.value)


# ============================================================================
# FONCTIONS INTERNES
# ============================================================================


def _display_flash(flash: FlashMessage):
    """Affiche un message flash dans un banner.

    Args:
        flash: Message flash à afficher
    """
    icons = {
        FlashType.SUCCESS: IconSet.SUCCESS.value,
        FlashType.ERROR: IconSet.ERROR.value,
        FlashType.WARNING: IconSet.WARNING.value,
        FlashType.INFO: IconSet.INFO.value,
    }

    icon = flash.icon or icons.get(flash.msg_type, IconSet.INFO.value)

    display_funcs = {
        FlashType.SUCCESS: st.success,
        FlashType.ERROR: st.error,
        FlashType.WARNING: st.warning,
        FlashType.INFO: st.info,
    }

    func = display_funcs.get(flash.msg_type, st.info)
    func(f"{icon} {flash.message}")


def _display_flash_as_toast(flash: FlashMessage):
    """Affiche un message flash comme un toast.

    Args:
        flash: Message flash à afficher
    """
    icons = {
        FlashType.SUCCESS: IconSet.SUCCESS.value,
        FlashType.ERROR: IconSet.ERROR.value,
        FlashType.WARNING: IconSet.WARNING.value,
        FlashType.INFO: IconSet.INFO.value,
    }

    icon = flash.icon or icons.get(flash.msg_type, IconSet.INFO.value)

    toast_funcs = {
        FlashType.SUCCESS: toast_success,
        FlashType.ERROR: toast_error,
        FlashType.WARNING: toast_warning,
        FlashType.INFO: toast_info,
    }

    func = toast_funcs.get(flash.msg_type, toast_info)
    func(flash.message, icon)
