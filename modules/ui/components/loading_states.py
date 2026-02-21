"""
Loading States Component (Legacy wrapper).
This module is deprecated. Use modules.ui_v2.molecules.loading_states instead.
"""

import streamlit as st
import warnings
from contextlib import contextmanager

def _warn_deprecation():
    st.warning("⚠️ L'utilisation de `modules.ui.components.loading_states` est dépréciée. Veuillez utiliser `modules.ui_v2.molecules.loading_states`.", icon="🔄")
    warnings.warn("modules.ui.components.loading_states is deprecated. Use modules.ui_v2.molecules.loading_states instead.", DeprecationWarning, stacklevel=3)

def render_skeleton_card(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.molecules.loading_states import render_skeleton_card as new_render
    return new_render(*args, **kwargs)

def render_skeleton_text(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.molecules.loading_states import render_skeleton_text as new_render
    return new_render(*args, **kwargs)

def render_skeleton_kpi_cards(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.molecules.loading_states import render_skeleton_kpi_cards as new_render
    return new_render(*args, **kwargs)

def render_skeleton_table(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.molecules.loading_states import render_skeleton_table as new_render
    return new_render(*args, **kwargs)

@contextmanager
def loading_spinner(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.molecules.loading_states import loading_spinner as new_render
    with new_render(*args, **kwargs) as update_msg:
        yield update_msg

def render_progress_steps(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.molecules.loading_states import render_progress_steps as new_render
    return new_render(*args, **kwargs)

def render_operation_progress(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.molecules.loading_states import render_operation_progress as new_render
    return new_render(*args, **kwargs)

def clear_operation_progress(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.molecules.loading_states import clear_operation_progress as new_clear
    return new_clear(*args, **kwargs)

__all__ = [
    "render_skeleton_card",
    "render_skeleton_text",
    "render_skeleton_kpi_cards",
    "render_skeleton_table",
    "loading_spinner",
    "render_progress_steps",
    "render_operation_progress",
    "clear_operation_progress",
]
