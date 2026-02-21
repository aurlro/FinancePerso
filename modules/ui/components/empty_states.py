"""
Empty States Component (Legacy wrapper).
This module is deprecated. Use modules.ui_v2.molecules.empty_states instead.
"""

import streamlit as st
import warnings

def _warn_deprecation():
    st.warning("⚠️ L'utilisation de `modules.ui.components.empty_states` est dépréciée. Veuillez utiliser `modules.ui_v2.molecules.empty_states`.", icon="🔄")
    warnings.warn("modules.ui.components.empty_states is deprecated. Use modules.ui_v2.molecules.empty_states instead.", DeprecationWarning, stacklevel=3)

def render_empty_state(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.molecules.empty_states import render_empty_state as new_render
    return new_render(*args, **kwargs)

def render_no_transactions_state(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.molecules.empty_states import render_no_transactions_state as new_render
    return new_render(*args, **kwargs)

def render_no_budgets_state(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.molecules.empty_states import render_no_budgets_state as new_render
    return new_render(*args, **kwargs)

def render_no_rules_state(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.molecules.empty_states import render_no_rules_state as new_render
    return new_render(*args, **kwargs)

def render_no_categories_state(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.molecules.empty_states import render_no_categories_state as new_render
    return new_render(*args, **kwargs)

def render_no_search_results(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.molecules.empty_states import render_no_search_results as new_render
    return new_render(*args, **kwargs)

def render_no_data_state(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.molecules.empty_states import render_no_data_state as new_render
    return new_render(*args, **kwargs)

def render_error_state(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.molecules.empty_states import render_error_state as new_render
    return new_render(*args, **kwargs)

def render_loading_state(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.molecules.empty_states import render_loading_state as new_render
    return new_render(*args, **kwargs)

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
