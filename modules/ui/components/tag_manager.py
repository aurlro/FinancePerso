"""
Tag Manager Component (Legacy wrapper).
This module is deprecated. Use modules.ui_v2.molecules.tag_manager instead.
"""

import streamlit as st
import warnings

def _warn_deprecation():
    st.warning("⚠️ L'utilisation de `modules.ui.components.tag_manager` est dépréciée. Veuillez utiliser `modules.ui_v2.molecules.tag_manager`.", icon="🔄")
    warnings.warn("modules.ui.components.tag_manager is deprecated. Use modules.ui_v2.molecules.tag_manager instead.", DeprecationWarning, stacklevel=3)

def get_tag_color(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.molecules.tag_manager import get_tag_color as new_func
    return new_func(*args, **kwargs)

def render_pill_tags(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.molecules.tag_manager import render_pill_tags as new_func
    return new_func(*args, **kwargs)

def find_similar_transactions(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.molecules.tag_manager import find_similar_transactions as new_func
    return new_func(*args, **kwargs)

def render_smart_tag_selector(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.molecules.tag_manager import render_smart_tag_selector as new_func
    return new_func(*args, **kwargs)

def batch_apply_tags_to_similar(*args, **kwargs):
    _warn_deprecation()
    from modules.ui_v2.molecules.tag_manager import batch_apply_tags_to_similar as new_func
    return new_func(*args, **kwargs)

__all__ = [
    "get_tag_color",
    "render_pill_tags",
    "find_similar_transactions",
    "render_smart_tag_selector",
    "batch_apply_tags_to_similar",
]
