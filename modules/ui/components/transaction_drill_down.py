"""
Transaction Drill-Down Component (Legacy wrapper).
This module is deprecated. Use modules.ui_v2.organisms.transaction_drill_down instead.
"""

import streamlit as st
import warnings

def _warn_deprecation():
    st.warning("⚠️ L'utilisation de `modules.ui.components.transaction_drill_down` est dépréciée. Veuillez utiliser `modules.ui_v2.organisms.transaction_drill_down`.", icon="🔄")
    warnings.warn("modules.ui.components.transaction_drill_down is deprecated. Use modules.ui_v2.organisms.transaction_drill_down instead.", DeprecationWarning, stacklevel=3)

def render_transaction_drill_down(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.organisms.transaction_drill_down import render_transaction_drill_down as new_func
    return new_func(*args, **kwargs)

def render_category_drill_down_expander(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.organisms.transaction_drill_down import render_category_drill_down_expander as new_func
    return new_func(*args, **kwargs)

__all__ = [
    "render_transaction_drill_down",
    "render_category_drill_down_expander",
]
