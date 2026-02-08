# modules/ui/components/avatar_selector.py

import streamlit as st
from typing import List, Optional, Callable


def render_avatar_selector(
    label: str,
    options: List[str],
    current_value: str,
    key: str,
    on_change: Optional[Callable] = None,
    color_map: Optional[dict] = None,
) -> str:
    """
    Render a horizontal avatar selector.

    Args:
        label: Label displayed above/aside
        options: List of names/identifiers
        current_value: Currently selected value
        key: Unique key for state
        on_change: Callback when selection changes
        color_map: Optional dict mapping names to colors

    Returns:
        The selected value
    """

    is_expanded_key = f"{key}_expanded"

    # CSS injection for clicking (Streamlit buttons don't support custom HTML seamlessly inside them,
    # so we use st.button with custom styling for the "Avatars")

    # We will use columns to render top 3-4 avatars
    # If more options exist, we show a "+" or dropdown

    st.caption(label)

    # Prepare top options (most frequent + current if set)
    # Ideally should be passed sorted by frequency

    top_n = 4
    visible_options = options[:top_n]

    # Ensure current value is visible if valid and not "custom"
    if current_value and current_value in options and current_value not in visible_options:
        visible_options[-1] = current_value  # Replace last one or expand logic?
        # Better: Just show it.
        if current_value not in visible_options:
            visible_options.append(current_value)

    cols = st.columns(len(visible_options) + 1)

    selected_val = current_value

    for i, opt in enumerate(visible_options):
        initials = opt[:2].upper() if len(opt) > 0 else "??"

        # Determine styling based on selection
        is_selected = opt == current_value
        type_str = "primary" if is_selected else "secondary"

        # Hack: Use button as avatar
        # Streamlit buttons expand to width, so we need to constrain them or use columns
        with cols[i]:
            if st.button(
                initials, key=f"{key}_av_{i}", help=opt, type=type_str, use_container_width=True
            ):
                selected_val = opt
                # Directly update state if possible?
                # or just return. Returning is safer for standard component usage.
                if on_change:
                    on_change(opt)
                st.rerun()

    # Dropdown for "More"
    with cols[-1]:
        if len(options) > len(visible_options):
            remaining = [o for o in options if o not in visible_options]
            more_sel = st.selectbox(
                "More", ["..."] + remaining, key=f"{key}_more", label_visibility="collapsed"
            )
            if more_sel != "...":
                selected_val = more_sel
                if on_change:
                    on_change(more_sel)
                st.rerun()

    return selected_val
