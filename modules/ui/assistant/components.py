"""
Reusable UI components for Assistant page.
"""

from collections.abc import Callable
from typing import Any

import streamlit as st


def render_progress_card(title: str, current: int, total: int, status_text: str = ""):
    """Render a progress card for long-running operations."""
    progress = current / total if total > 0 else 0

    st.markdown(f"**{title}**")
    st.progress(progress, text=status_text)


def render_audit_summary_cards(stats: dict[str, int]):
    """Render summary cards for audit statistics."""
    cols = st.columns(4)

    with cols[0]:
        st.metric("Total", stats.get("total", 0))
    with cols[1]:
        st.metric("À corriger", stats.get("pending", 0), delta=None)
    with cols[2]:
        st.metric("Corrigés", stats.get("corrected", 0), delta=None)
    with cols[3]:
        st.metric("Ignorés", stats.get("hidden", 0), delta=None)


def render_anomaly_card(
    index: int,
    item: dict[str, Any],
    is_corrected: bool,
    is_hidden: bool,
    is_selected: bool,
    on_select: Callable[[int, bool], None],
    on_correct: Callable[[int], None],
    on_hide: Callable[[int], None],
    on_apply: Callable[[int], None] | None = None,
):
    """
    Render a single anomaly card with actions.

    Args:
        index: Anomaly index
        item: Anomaly data
        is_corrected: Whether anomaly is corrected
        is_hidden: Whether anomaly is hidden
        is_selected: Whether selected for bulk action
        on_select: Callback when selection changes
        on_correct: Callback when marked as corrected
        on_hide: Callback when hidden
        on_apply: Callback when applying suggestion
    """
    # Determine status icon
    if is_corrected:
        status_icon = "✅"
        border_color = "#22c55e"
    elif is_hidden:
        status_icon = "🗑️"
        border_color = "#6b7280"
    else:
        status_icon = "⚠️" if item.get("type") == "Incohérence" else "🤖"
        border_color = "#ef4444" if item.get("type") == "Incohérence" else "#f59e0b"

    # Card with custom border
    st.markdown(
        f"""
    <div style='
        border-left: 4px solid {border_color};
        padding: 1rem;
        margin: 0.5rem 0;
        background: {"#f0fdf4" if is_corrected else "#f9fafb" if is_hidden else "#fef2f2"};
        border-radius: 0 8px 8px 0;
    '>
        <h4 style='margin: 0;'>{status_icon} {item.get('type', 'Anomalie')} : {item.get('label', 'N/A')}</h4>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Selection checkbox
    col_check, col_info = st.columns([0.1, 0.9])
    with col_check:
        selected = st.checkbox(
            "", value=is_selected, key=f"anomaly_select_{index}", label_visibility="collapsed"
        )
        if selected != is_selected:
            on_select(index, selected)

    with col_info:
        st.write(f"**Détails :** {item.get('details', '')}")
        if is_corrected:
            st.success("✅ Cette anomalie a été corrigée.")

    # Action buttons
    cols = st.columns([1, 1, 1, 1])

    with cols[0]:
        if is_corrected:
            if st.button("↩️ Rouvrir", key=f"reopen_{index}", use_container_width=True):
                on_correct(index)  # Toggle off
        else:
            if st.button("✅ Corrigé", key=f"mark_fixed_{index}", use_container_width=True):
                on_correct(index)

    with cols[1]:
        if is_hidden:
            if st.button("🔄 Restaurer", key=f"restore_{index}", use_container_width=True):
                on_hide(index)  # Toggle off
        else:
            if st.button("🗑️ Ignorer", key=f"ignore_{index}", use_container_width=True):
                on_hide(index)

    with cols[2]:
        suggested = item.get("suggested_category")
        if suggested and not is_corrected and on_apply:
            if st.button(
                f"🧠 Appliquer '{suggested}'",
                key=f"apply_{index}",
                use_container_width=True,
                type="primary",
            ):
                on_apply(index)

    st.divider()


def render_insight_card(insight: dict[str, Any], index: int):
    """Render an insight card for trends/analytics."""
    title = insight.get("title", "Insight")
    description = insight.get("description", "")
    severity = insight.get("severity", "info")

    # Color based on severity
    colors = {
        "high": ("#ef4444", "🔴"),
        "medium": ("#f59e0b", "🟠"),
        "low": ("#3b82f6", "🔵"),
        "info": ("#6b7280", "💡"),
    }
    color, icon = colors.get(severity, colors["info"])

    with st.expander(f"{icon} {title}"):
        st.markdown(description)

        # Action buttons if available
        if "action" in insight:
            if st.button(insight["action"], key=f"insight_action_{index}"):
                # Handle action
                pass


def render_chat_interface(
    history: list[dict[str, str]],
    on_send: Callable[[str], None],
    suggestions: list[str] | None = None,
):
    """
    Render chat interface with history and input.

    Args:
        history: List of {'role': 'user'|'assistant', 'content': str}
        on_send: Callback when user sends message
        suggestions: Optional quick suggestion buttons
    """
    # Empty state with suggestions
    if not history and suggestions:
        st.markdown(
            """
        <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); 
                    border-radius: 12px; border: 1px dashed #94a3b8; margin: 1rem 0;'>
            <div style='font-size: 3rem; margin-bottom: 0.5rem;'>💡</div>
            <p style='color: #475569; margin-bottom: 1rem;'>Commencez par une question suggérée :</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Suggestion chips
        cols = st.columns(min(len(suggestions), 2))
        for i, suggestion in enumerate(suggestions[:4]):
            with cols[i % 2]:
                if st.button(f"💬 {suggestion}", key=f"chat_sugg_{i}", use_container_width=True):
                    on_send(suggestion)

    # Chat history
    for msg in history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    if prompt := st.chat_input("Posez votre question..."):
        on_send(prompt)


def render_empty_state(
    icon: str, title: str, description: str, actions: list[tuple] | None = None
):
    """
    Render an engaging empty state.

    Args:
        icon: Emoji icon
        title: Main title
        description: Description text
        actions: List of (label, callback) tuples
    """
    st.markdown(
        f"""
    <div style='
        text-align: center; 
        padding: 3rem; 
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); 
        border-radius: 15px; 
        border: 2px solid #86efac; 
        margin: 2rem 0;
    '>
        <h1 style='font-size: 3rem; margin-bottom: 1rem;'>{icon}</h1>
        <h2 style='color: #166534; margin-bottom: 1rem;'>{title}</h2>
        <p style='color: #166534; font-size: 1.1rem;'>{description}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if actions:
        st.markdown("### Que faire ensuite ?")
        cols = st.columns(len(actions))
        for i, (label, callback) in enumerate(actions):
            with cols[i]:
                if st.button(label, key=f"empty_action_{i}", use_container_width=True):
                    callback()


def render_quick_action_card(icon: str, label: str, description: str, on_click: Callable):
    """Render a clickable quick action card."""
    with st.container():
        st.markdown(
            f"""
        <div style='
            padding: 1.5rem;
            background: #f8fafc;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            text-align: center;
            cursor: pointer;
        '>
            <div style='font-size: 2rem; margin-bottom: 0.5rem;'>{icon}</div>
            <h4 style='margin: 0;'>{label}</h4>
            <p style='color: #64748b; font-size: 0.9rem;'>{description}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        if st.button(f"{label} →", key=f"quick_action_{label}", use_container_width=True):
            on_click()


def render_metric_row(metrics: list[dict[str, Any]]):
    """Render a row of metric cards."""
    cols = st.columns(len(metrics))
    for i, metric in enumerate(metrics):
        with cols[i]:
            st.metric(
                label=metric.get("label", ""),
                value=metric.get("value", ""),
                delta=metric.get("delta"),
                delta_color=metric.get("delta_color", "normal"),
            )
