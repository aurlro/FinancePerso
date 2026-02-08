"""
Loading States Component - Skeletons and progress indicators.
Provides visual feedback during long operations.
"""
import streamlit as st
import time
from typing import Optional, Iterator
from contextlib import contextmanager


def render_skeleton_card(height: int = 100, key: str = "skeleton"):
    """Render a skeleton loading card."""
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        height: {height}px;
        border-radius: 8px;
        margin-bottom: 1rem;
    "></div>
    <style>
        @keyframes shimmer {{
            0% {{ background-position: 200% 0; }}
            100% {{ background-position: -200% 0; }}
        }}
    </style>
    """, unsafe_allow_html=True)


def render_skeleton_text(lines: int = 3, key: str = "skeleton_text"):
    """Render skeleton text lines."""
    for i in range(lines):
        width = 100 if i < lines - 1 else 60  # Last line shorter
        st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
            height: 16px;
            width: {width}%;
            border-radius: 4px;
            margin-bottom: 8px;
        "></div>
        <style>
            @keyframes shimmer {{
                0% {{ background-position: 200% 0; }}
                100% {{ background-position: -200% 0; }}
            }}
        </style>
        """, unsafe_allow_html=True)


def render_skeleton_kpi_cards(count: int = 4, key: str = "skeleton_kpis"):
    """Render skeleton KPI cards."""
    cols = st.columns(count)
    for i, col in enumerate(cols):
        with col:
            render_skeleton_card(height=80, key=f"{key}_card_{i}")


def render_skeleton_table(rows: int = 5, key: str = "skeleton_table"):
    """Render skeleton table."""
    # Header
    st.markdown("""
    <div style="
        background: #e2e8f0;
        height: 40px;
        border-radius: 4px 4px 0 0;
        margin-bottom: 2px;
    "></div>
    """, unsafe_allow_html=True)
    
    # Rows
    for i in range(rows):
        st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, #f1f5f9 25%, #e8ecf1 50%, #f1f5f9 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
            animation-delay: {i * 0.1}s;
            height: 48px;
            border-bottom: 1px solid #e2e8f0;
        "></div>
        <style>
            @keyframes shimmer {{
                0% {{ background-position: 200% 0; }}
                100% {{ background-position: -200% 0; }}
            }}
        </style>
        """, unsafe_allow_html=True)


@contextmanager
def loading_spinner(message: str = "Chargement...", show_time: bool = True):
    """
    Context manager for showing a spinner during operations.
    
    Args:
        message: Message to display
        show_time: Whether to show elapsed time
    """
    import time
    start_time = time.time()
    
    if show_time:
        placeholder = st.empty()
        
        def update_message():
            elapsed = time.time() - start_time
            if elapsed < 60:
                time_str = f"{elapsed:.1f}s"
            else:
                minutes = int(elapsed // 60)
                seconds = int(elapsed % 60)
                time_str = f"{minutes}m {seconds}s"
            placeholder.text(f"⏱️ {message} ({time_str})")
        
        try:
            with st.spinner(message):
                yield update_message
        finally:
            placeholder.empty()
    else:
        with st.spinner(message):
            yield lambda: None


def render_progress_steps(
    steps: list,
    current_step: int,
    key: str = "progress_steps"
):
    """
    Render a step-by-step progress indicator.
    
    Args:
        steps: List of step labels
        current_step: Current step index (0-based)
        key: Unique key
    """
    cols = st.columns(len(steps))
    
    for i, (col, step) in enumerate(zip(cols, steps)):
        with col:
            if i < current_step:
                # Completed step
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="
                        width: 32px;
                        height: 32px;
                        background: #10b981;
                        border-radius: 50%;
                        margin: 0 auto;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-weight: bold;
                    ">✓</div>
                    <div style="font-size: 0.8rem; color: #10b981; margin-top: 4px;">{step}</div>
                </div>
                """, unsafe_allow_html=True)
            elif i == current_step:
                # Current step
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="
                        width: 32px;
                        height: 32px;
                        background: #3b82f6;
                        border-radius: 50%;
                        margin: 0 auto;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-weight: bold;
                        border: 3px solid #93c5fd;
                    ">{i + 1}</div>
                    <div style="font-size: 0.8rem; color: #3b82f6; font-weight: bold; margin-top: 4px;">{step}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Future step
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="
                        width: 32px;
                        height: 32px;
                        background: #e2e8f0;
                        border-radius: 50%;
                        margin: 0 auto;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: #94a3b8;
                        font-weight: bold;
                    ">{i + 1}</div>
                    <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 4px;">{step}</div>
                </div>
                """, unsafe_allow_html=True)


def render_operation_progress(
    total: int,
    current: int,
    operation_name: str = "opération",
    key: str = "op_progress"
):
    """
    Render progress for batch operations.
    
    Args:
        total: Total number of items
        current: Current progress
        operation_name: Name of the operation
        key: Unique key
    """
    progress = current / total if total > 0 else 0
    
    st.progress(progress, text=f"{operation_name.capitalize()} : {current}/{total}")
    
    # ETA calculation
    if hasattr(st.session_state, '_op_start_time'):
        elapsed = time.time() - st.session_state._op_start_time
        if current > 0:
            rate = elapsed / current
            remaining = (total - current) * rate
            if remaining < 60:
                eta_text = f"~{int(remaining)}s restantes"
            else:
                eta_text = f"~{int(remaining/60)}min restantes"
            st.caption(f"⏱️ {eta_text}")
    else:
        st.session_state._op_start_time = time.time()


def clear_operation_progress(key: str = "op_progress"):
    """Clear operation progress tracking."""
    if hasattr(st.session_state, '_op_start_time'):
        del st.session_state._op_start_time


# Export
__all__ = [
    'render_skeleton_card',
    'render_skeleton_text',
    'render_skeleton_kpi_cards',
    'render_skeleton_table',
    'loading_spinner',
    'render_progress_steps',
    'render_operation_progress',
    'clear_operation_progress',
]
