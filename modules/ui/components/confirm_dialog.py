"""
Confirmation dialogs (Legacy wrapper).
This module is deprecated. Use modules.ui_v2.organisms.dialogs instead.
"""

import streamlit as st
import warnings

def _warn_deprecation():
    st.warning("⚠️ L'utilisation de `modules.ui.components.confirm_dialog` est dépréciée. Veuillez utiliser `modules.ui_v2.organisms.dialogs`.", icon="🔄")
    warnings.warn("modules.ui.components.confirm_dialog is deprecated. Use modules.ui_v2.organisms.dialogs instead.", DeprecationWarning, stacklevel=3)

def confirm_dialog(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.organisms.dialogs import confirm_dialog as new_func
    return new_func(*args, **kwargs)

def confirm_delete(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.organisms.dialogs import confirm_delete as new_func
    return new_func(*args, **kwargs)

def confirm_action(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.organisms.dialogs import confirm_action as new_func
    return new_func(*args, **kwargs)

def info_dialog(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.organisms.dialogs import info_dialog as new_func
    return new_func(*args, **kwargs)

__all__ = [
    "confirm_dialog",
    "confirm_delete",
    "confirm_action",
    "info_dialog"
]
