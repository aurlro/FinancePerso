"""
Forms Components - Form-related UI molecules.

Migrated from:
- modules/ui/components/profile_form.py
- modules/ui/components/avatar_selector.py

Classification: Molecules (form input composites)
"""

from modules.ui_v2.molecules.components.forms.profile_form import render_profile_setup_form
from modules.ui_v2.molecules.components.forms.avatar_selector import render_avatar_selector

__all__ = [
    "render_profile_setup_form",
    "render_avatar_selector",
]
