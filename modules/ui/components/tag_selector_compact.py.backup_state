"""
Tag Selector Compact Component
A streamlined tag management interface optimized for space and usability.

Features:
- Quick-add chips for suggested tags
- Compact multiselect for all tags
- Visual hierarchy: current tags > quick adds > selector
"""
import streamlit as st
from typing import List
from modules.db.tags import get_all_tags
from modules.db.categories import get_categories_suggested_tags, add_tag_to_category


def render_tag_selector_compact(
    transaction_id: int,
    current_tags: List[str],
    category: str,
    key_suffix: str = "",
    max_quick_tags: int = 3
) -> List[str]:
    """
    Render a compact tag selector optimized for table/grid layouts.
    
    Layout (vertical, compact):
    [Multiselect with current tags]
    [Quick add buttons in a row below]
    
    Args:
        transaction_id: Transaction ID for unique keys
        current_tags: List of currently selected tags
        category: Category name for context-aware suggestions
        key_suffix: Optional suffix for multiple instances
        max_quick_tags: Number of quick-tag buttons to show
    
    Returns:
        List of selected tag names
    """
    # Initialize session state
    if 'temp_custom_tags' not in st.session_state:
        st.session_state['temp_custom_tags'] = []
    
    if 'pending_tag_additions' not in st.session_state:
        st.session_state['pending_tag_additions'] = {}
    
    # Apply pending additions
    if transaction_id in st.session_state.get('pending_tag_additions', {}):
        pending = st.session_state['pending_tag_additions'][transaction_id]
        current_tags = list(set(current_tags + pending))
        del st.session_state['pending_tag_additions'][transaction_id]
    
    # Get available tags
    existing_tags = get_all_tags()
    cat_suggested_tags = get_categories_suggested_tags()
    suggested = cat_suggested_tags.get(category, [])
    
    # Build options list (must include current tags to avoid errors)
    all_available = sorted(list(set(
        existing_tags + 
        suggested + 
        st.session_state['temp_custom_tags'] +
        current_tags  # Ensure current tags are always in options
    )))
    
    # Determine quick tags (suggestions not already selected)
    quick_tags = [t for t in suggested if t not in current_tags][:max_quick_tags]
    
    container = st.container()
    
    with container:
        # ROW 1: Main selector with add button inline
        selector_col, add_col = st.columns([0.88, 0.12])
        
        with selector_col:
            selected = st.multiselect(
                "Tags",
                options=all_available,
                default=current_tags,
                key=f"tag_select_{transaction_id}{key_suffix}",
                label_visibility="collapsed",
                placeholder="🏷️ Tags..."
            )
        
        with add_col:
            with st.popover("➕", use_container_width=True):
                st.markdown("**Nouveau tag**")
                new_tag = st.text_input(
                    "Nom",
                    key=f"new_tag_input_{transaction_id}{key_suffix}",
                    label_visibility="collapsed",
                    placeholder="ex: Urgent"
                )
                
                if st.button("Créer", type="primary", use_container_width=True,
                           key=f"create_tag_{transaction_id}{key_suffix}"):
                    if new_tag and new_tag.strip():
                        new_tag_clean = new_tag.strip()
                        if new_tag_clean not in st.session_state['temp_custom_tags']:
                            st.session_state['temp_custom_tags'].append(new_tag_clean)
                        add_tag_to_category(category, new_tag_clean)
                        if transaction_id not in st.session_state['pending_tag_additions']:
                            st.session_state['pending_tag_additions'][transaction_id] = []
                        st.session_state['pending_tag_additions'][transaction_id].append(new_tag_clean)
                        st.rerun()
        
        # ROW 2: Quick add buttons (only if suggestions exist)
        if quick_tags:
            # Use very compact buttons in a single row
            quick_cols = st.columns(min(len(quick_tags), 3))
            for i, tag in enumerate(quick_tags[:3]):
                with quick_cols[i]:
                    if st.button(
                        f"+{tag[:8]}",  # Truncate long names
                        key=f"quick_tag_{tag}_{transaction_id}{key_suffix}",
                        use_container_width=True,
                        type="secondary",
                        help=f"Ajouter '{tag}'"
                    ):
                        if transaction_id not in st.session_state['pending_tag_additions']:
                            st.session_state['pending_tag_additions'][transaction_id] = []
                        st.session_state['pending_tag_additions'][transaction_id].append(tag)
                        st.rerun()
    
    return selected


def render_cheque_nature_field(
    transaction_id: int,
    current_nature: str = "",
    key_suffix: str = ""
) -> str:
    """
    Render a dedicated field for cheque nature/description.
    Creates a specific tag for the cheque purpose.
    """
    # Subtle section with border
    st.markdown("""
        <style>
        .cheque-nature-box {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 12px;
            margin-top: 8px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.caption("📝 Nature du chèque")
        
        # Horizontal layout: text input + quick select
        nature_col, quick_col = st.columns([0.6, 0.4])
        
        with nature_col:
            nature = st.text_input(
                "Nature",
                value=current_nature,
                key=f"cheque_nature_{transaction_id}{key_suffix}",
                label_visibility="collapsed",
                placeholder="Usage du chèque..."
            )
        
        with quick_col:
            common_natures = ["Santé", "Voiture", "Maison", "Loisirs", "Cadeau", "Professionnel"]
            quick = st.selectbox(
                "Rapide",
                options=["-- Choisir --"] + common_natures,
                key=f"cheque_quick_{transaction_id}{key_suffix}",
                label_visibility="collapsed"
            )
            if quick != "-- Choisir --" and not nature:
                nature = quick
        
        # Preview tag
        if nature:
            tag_name = f"chèque-{nature.lower().replace(' ', '-')}"
            st.caption(f"🏷️ Sera créé : `#{tag_name}`")
    
    return nature
