"""
Explorer Launcher - Boutons et utilitaires pour lancer l'explorateur.
"""


import streamlit as st


def launch_explorer(explorer_type: str, value: str, from_page: str = "3_Synthèse") -> None:
    """
    Launch explorer with given parameters.

    Args:
        explorer_type: 'category' or 'tag'
        value: Category or tag value to explore
        from_page: Page to return to (for back button)
    """
    # Store params in session state (older Streamlit workaround)
    st.session_state["_explorer_type"] = explorer_type
    st.session_state["_explorer_value"] = value
    st.session_state["_explorer_from"] = from_page

    # Navigate
    st.switch_page("pages/8_Recherche.py")


def render_explore_button(
    explorer_type: str,
    value: str,
    from_page: str = "3_Synthèse",
    label: str | None = None,
    use_container_width: bool = False,
    button_type: str = "secondary",
    key_suffix: str | None = None,
    **button_kwargs,
) -> None:
    """
    Render a button that launches the explorer.

    Args:
        explorer_type: 'category' or 'tag'
        value: Value to explore
        from_page: Origin page
        label: Button label (auto-generated if None)
        use_container_width: Whether to use full width
        button_type: 'primary' or 'secondary'
        key_suffix: Additional suffix for unique key
        **button_kwargs: Additional Streamlit button arguments
    """
    # Generate label if not provided
    if label is None:
        icon = "📂" if explorer_type == "category" else "🏷️"
        label = f"{icon} Explorer"

    # Generate unique key
    key = f"explore_{explorer_type}_{value[:20]}"
    if key_suffix:
        key += f"_{key_suffix}"

    # Render button
    if st.button(
        label, key=key, type=button_type, use_container_width=use_container_width, **button_kwargs
    ):
        launch_explorer(explorer_type, value, from_page)


def render_explore_link(
    explorer_type: str, value: str, from_page: str = "3_Synthèse", label: str | None = None
) -> None:
    """
    Render a link that launches the explorer.

    Args:
        explorer_type: 'category' or 'tag'
        value: Value to explore
        from_page: Origin page
        label: Link label (auto-generated if None)
    """
    if label is None:
        icon = "📂" if explorer_type == "category" else "🏷️"
        label = f"{icon} Explorer {value}"

    # Use query params to pass data
    params = f"type={explorer_type}&value={value}&from={from_page}"

    st.markdown(f"[➡️ {label}](/Recherche?{params})")


def render_category_pill(
    category: str, amount: float, count: int, emoji: str = "📂", from_page: str = "3_Synthèse"
) -> None:
    """
    Render a clickable category pill/card with explore button.

    Args:
        category: Category name
        amount: Total amount
        count: Transaction count
        emoji: Category emoji
        from_page: Origin page
    """
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([2, 1, 1, 0.8])

        with col1:
            st.markdown(f"**{emoji} {category}**")
            st.caption(f"{count} transaction(s)")

        with col2:
            st.markdown(f"**{amount:,.2f} €**")

        with col3:
            avg = amount / count if count > 0 else 0
            st.markdown(f"{avg:,.2f} €")
            st.caption("moyenne")

        with col4:
            render_explore_button(
                "category",
                category,
                from_page,
                label="🔍",
                button_type="secondary",
                use_container_width=True,
            )


def render_tag_pill(tag: str, amount: float, count: int, from_page: str = "3_Synthèse") -> None:
    """
    Render a clickable tag pill/card with explore button.

    Args:
        tag: Tag name
        amount: Total amount
        count: Transaction count
        from_page: Origin page
    """
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([2, 1, 1, 0.8])

        with col1:
            st.markdown(f"**🏷️ {tag}**")
            st.caption(f"{count} transaction(s)")

        with col2:
            st.markdown(f"**{amount:,.2f} €**")

        with col3:
            avg = amount / count if count > 0 else 0
            st.markdown(f"{avg:,.2f} €")
            st.caption("moyenne")

        with col4:
            render_explore_button(
                "tag", tag, from_page, label="🔍", button_type="secondary", use_container_width=True
            )


def get_explorer_url(explorer_type: str, value: str, from_page: str = "3_Synthèse") -> str:
    """
    Get the URL for the explorer with given parameters.

    Args:
        explorer_type: 'category' or 'tag'
        value: Value to explore
        from_page: Origin page

    Returns:
        URL string
    """
    return f"/Recherche?type={explorer_type}&value={value}&from={from_page}"


def render_back_button(from_page: str = "3_Synthèse") -> None:
    """
    Render a back button that returns to the origin page.

    Args:
        from_page: Page to return to
    """
    page_names = {
        "1_Opérations": "Opérations",
        "3_Synthèse": "Synthèse",
        "4_Intelligence": "Intelligence",
        "7_Assistant": "Assistant",
        "8_Recherche": "Recherche",
        "app": "Accueil",
    }

    page_label = page_names.get(from_page, "Retour")

    if st.button(f"⬅️ {page_label}", type="secondary"):
        if from_page == "app":
            st.switch_page("app.py")
        else:
            st.switch_page(f"pages/{from_page}.py")
