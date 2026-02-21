"""
Tags Components - Tag-related UI molecules.

Migrated from:
- modules/ui/components/tag_manager.py
- modules/ui/components/tag_selector_compact.py
- modules/ui/components/tag_selector_smart.py

Classification: Molecules (composite tag management components)
"""

from modules.ui_v2.molecules.components.tags.tag_manager import (
    batch_apply_tags_to_similar,
    find_similar_transactions,
    get_tag_color,
    render_pill_tags,
    render_smart_tag_selector,
)
from modules.ui_v2.molecules.components.tags.tag_selector_compact import (
    render_cheque_nature_field,
    render_tag_selector_compact,
)
from modules.ui_v2.molecules.components.tags.tag_selector_smart import (
    apply_tag_to_similar,
    render_smart_tag_selector as render_smart_tag_selector_v2,
    render_tag_propagation_dialog,
)

__all__ = [
    # From tag_manager
    "get_tag_color",
    "render_pill_tags",
    "find_similar_transactions",
    "render_smart_tag_selector",
    "batch_apply_tags_to_similar",
    # From tag_selector_compact
    "render_tag_selector_compact",
    "render_cheque_nature_field",
    # From tag_selector_smart
    "render_tag_propagation_dialog",
    "apply_tag_to_similar",
    "render_smart_tag_selector_v2",
]
