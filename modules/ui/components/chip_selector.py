from collections.abc import Callable

import streamlit as st


def render_chip_selector(
    label: str,
    options: list[str],
    current_value: str,  # or List[str] if multi
    key: str,
    on_change: Callable | None = None,
    multi: bool = False,
) -> str | list[str]:
    """
    Render a horizontal chip selector.
    """
    if "pills" in dir(st):
        # Use new Streamlit Pills if available (since 1.40+)
        selection = st.pills(
            label,
            options,
            selection_mode="multi" if multi else "single",
            default=current_value,
            key=key,
        )
        return selection

    # Fallback to buttons
    st.caption(label)
    cols = st.columns(min(len(options), 8))
    for i, opt in enumerate(options[:8]):
        with cols[i]:
            if st.button(
                opt,
                key=f"{key}_chip_{i}",
                type=(
                    "primary"
                    if (opt == current_value or (multi and opt in current_value))
                    else "secondary"
                ),
            ):
                if multi:
                    pass  # logic for multi
                else:
                    return opt
    return current_value
