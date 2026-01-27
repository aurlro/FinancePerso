"""
Tag Manager Component
Handles tag selection, creation, and category association for transactions.

This component combines:
- Multiselect with smart suggestions based on category
- Tag creation popover with automatic category association
- Session-based temporary tags for immediate availability
"""
import streamlit as st
from modules.db.tags import get_all_tags
from modules.db.categories import get_categories_suggested_tags, add_tag_to_category


def render_tag_selector(
    transaction_id: int,
    current_tags: list[str],
    category: str,
    key_suffix: str = "",
    allow_create: bool = True,
    strict_mode: bool = True
) -> list[str]:
    """
    Render tag multiselect with smart suggestions and creation capability.
    
    Args:
        transaction_id: Transaction ID for unique keys
        current_tags: List of tags currently applied to transaction
        category: Current category name (for smart suggestions)
        key_suffix: Optional suffix for widget keys (for multiple instances)
        allow_create: Whether to show the "Add Tag" button
        strict_mode: If True, show only category-suggested tags + current tags
                     If False, show all existing tags
    
    Returns:
        List of selected tag names
        
    Example:
        >>> selected = render_tag_selector(
        ...     transaction_id=123,
        ...     current_tags=["Courses", "Bio"],
        ...     category="Alimentation"
        ... )
        >>> # User selects tags, creates new ones
        >>> print(selected)  # ["Courses", "Bio", "Supermarché"]
    """
    # Initialize session state for temporary custom tags
    if 'temp_custom_tags' not in st.session_state:
        st.session_state['temp_custom_tags'] = []
    
    if 'pending_tag_additions' not in st.session_state:
        st.session_state['pending_tag_additions'] = {}
    
    # Add pending tags for this transaction (auto-select after creation)
    if transaction_id in st.session_state.get('pending_tag_additions', {}):
        pending = st.session_state['pending_tag_additions'][transaction_id]
        current_tags = list(set(current_tags + pending))
        del st.session_state['pending_tag_additions'][transaction_id]
    
    # Build tag options
    existing_tags = get_all_tags()
    cat_suggested_tags = get_categories_suggested_tags()
    allowed_tags = cat_suggested_tags.get(category, [])
    
    if strict_mode and allowed_tags:
        # Strict: Only show category-specific tags + current tags + session temps
        display_tags = sorted(list(set(
            allowed_tags + 
            current_tags + 
            st.session_state['temp_custom_tags']
        )))
    else:
        # Permissive: Show all tags
        display_tags = sorted(list(set(
            existing_tags + 
            st.session_state['temp_custom_tags'] + 
            current_tags
        )))
    
    # Layout: Multiselect + Add Button
    if allow_create:
        t_col1, t_col2 = st.columns([0.85, 0.15], vertical_alignment="bottom")
    else:
        t_col1 = st.container()
        t_col2 = None
    
    # Multiselect
    tag_key = f"tag_sel_{transaction_id}{key_suffix}"
    with t_col1:
        selected_tags = st.multiselect(
            "🏷️ Tags", 
            display_tags, 
            default=current_tags, 
            key=tag_key
        )
    
    # Add Tag Button
    if allow_create and t_col2:
        with t_col2:
            with st.popover("➕", use_container_width=True):
                new_tag_input = st.text_input(
                    "Nouveau tag", 
                    key=f"new_tag_{transaction_id}{key_suffix}"
                )
                if st.button("Ajouter", key=f"add_tag_btn_{transaction_id}{key_suffix}"):
                    if new_tag_input:
                        # 1. Add to session for immediate availability
                        if new_tag_input not in st.session_state['temp_custom_tags']:
                            st.session_state['temp_custom_tags'].append(new_tag_input)
                        
                        # 2. Associate with category permanently
                        add_tag_to_category(category, new_tag_input)
                        
                        # 3. Auto-select for this transaction
                        if transaction_id not in st.session_state['pending_tag_additions']:
                            st.session_state['pending_tag_additions'][transaction_id] = []
                        st.session_state['pending_tag_additions'][transaction_id].append(new_tag_input)
                        
                        st.toast(f"Tag '{new_tag_input}' créé et associé à '{category}' !", icon="🔗")
                        st.rerun()
    
    # Show suggested tags as pills (if any remain unselected)
    suggestions = cat_suggested_tags.get(category, [])
    if suggestions:
        filtered_sugg = [s for s in suggestions if s not in selected_tags]
        if filtered_sugg:
            pill_key = f"pills_{transaction_id}{key_suffix}"
            selected_pill = st.pills(
                "Suggestions", 
                filtered_sugg, 
                selection_mode="single", 
                key=pill_key,
                label_visibility="collapsed"
            )
            
            if selected_pill:
                # Auto-add the selected pill
                if transaction_id not in st.session_state['pending_tag_additions']:
                    st.session_state['pending_tag_additions'][transaction_id] = []
                st.session_state['pending_tag_additions'][transaction_id].append(selected_pill)
                st.rerun()
    
    return selected_tags


def render_tag_selector_simple(
    current_tags: list[str],
    all_tags: list[str],
    key: str,
    label: str = "🏷️ Tags"
) -> list[str]:
    """
    Simple tag multiselect without creation capability.
    
    Useful for filtering or viewing tags in read-only contexts.
    
    Args:
        current_tags: Currently selected tags
        all_tags: All available tags to choose from
        key: Unique widget key
        label: Label for the multiselect
        
    Returns:
        List of selected tags
    """
    return st.multiselect(label, sorted(all_tags), default=current_tags, key=key)
