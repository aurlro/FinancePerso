# -*- coding: utf-8 -*-
"""
Loader/Loading states molecule for the Design System.

Usage:
    with loader("Chargement des données..."):
        long_running_operation()
    
    # Ou
    show_loader("Chargement...")
    do_work()
    hide_loader()
"""

from dataclasses import dataclass
from typing import Generator

import streamlit as st

from modules.ui.tokens.colors import Colors
from modules.ui.tokens.radius import BorderRadius
from modules.ui.tokens.spacing import Spacing


@dataclass
class LoaderProps:
    """Props for the Loader component."""

    message: str = "Chargement..."
    size: str = "medium"  # small, medium, large
    fullscreen: bool = False
    show_progress: bool = False
    progress: float = 0.0  # 0.0 to 1.0


class Loader:
    """Loader component with Emerald Design System styling."""

    SIZES = {
        "small": {"spinner": 24, "font": "0.875rem"},
        "medium": {"spinner": 40, "font": "1rem"},
        "large": {"spinner": 64, "font": "1.25rem"},
    }

    def __init__(
        self,
        message: str = "Chargement...",
        size: str = "medium",
        fullscreen: bool = False,
        show_progress: bool = False,
    ):
        self.props = LoaderProps(
            message=message,
            size=size,
            fullscreen=fullscreen,
            show_progress=show_progress,
        )
        self._state_key = f"loader_active_{id(self)}"

    def _get_spinner_css(self) -> str:
        """Generate spinner CSS."""
        size = self.SIZES.get(self.props.size, self.SIZES["medium"])
        
        return f"""
        <style>
        .loader-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: {Spacing.XLARGE}px;
            {'' if not self.props.fullscreen else 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(255, 255, 255, 0.9); z-index: 999999;'}
        }}
        
        .loader-spinner {{
            width: {size['spinner']}px;
            height: {size['spinner']}px;
            border: 3px solid {Colors.GRAY_200};
            border-top: 3px solid {Colors.EMERALD_600};
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}
        
        .loader-message {{
            margin-top: {Spacing.MEDIUM}px;
            color: {Colors.GRAY_600};
            font-size: {size['font']};
            font-weight: 500;
        }}
        
        .loader-progress {{
            width: 200px;
            height: 4px;
            background: {Colors.GRAY_200};
            border-radius: {BorderRadius.SM}px;
            margin-top: {Spacing.SMALL}px;
            overflow: hidden;
        }}
        
        .loader-progress-bar {{
            height: 100%;
            background: {Colors.EMERALD_500};
            border-radius: {BorderRadius.SM}px;
            transition: width 0.3s ease;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        </style>
        """

    def render(self, progress: float | None = None) -> None:
        """Render the loader."""
        progress = progress if progress is not None else self.props.progress
        
        css = self._get_spinner_css()
        
        progress_html = ""
        if self.props.show_progress:
            progress_pct = int(progress * 100)
            progress_html = f"""
            <div class="loader-progress">
                <div class="loader-progress-bar" style="width: {progress_pct}%;"></div>
            </div>
            <div style="text-align: center; color: {Colors.GRAY_500}; font-size: 0.875rem; margin-top: 4px;">
                {progress_pct}%
            </div>
            """
        
        html = f"""
        {css}
        <div class="loader-container">
            <div class="loader-spinner"></div>
            <div class="loader-message">{self.props.message}</div>
            {progress_html}
        </div>
        """
        
        st.markdown(html, unsafe_allow_html=True)

    def __enter__(self) -> "Loader":
        """Context manager entry."""
        self.render()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - clear the loader."""
        # In Streamlit, we can't really clear output easily
        # The loader will disappear on next rerun
        pass


def loader(
    message: str = "Chargement...",
    size: str = "medium",
    fullscreen: bool = False,
    show_progress: bool = False,
) -> Generator[Loader, None, None]:
    """
    Context manager for showing a loader.
    
    Usage:
        with loader("Traitement en cours..."):
            result = long_operation()
    """
    loader_instance = Loader(message, size, fullscreen, show_progress)
    with loader_instance:
        yield loader_instance


def show_loader(
    message: str = "Chargement...",
    key: str = "loader",
) -> None:
    """
    Show a persistent loader.
    
    Usage:
        show_loader("Chargement...")
        do_work()
        hide_loader()
    """
    st.session_state[f"{key}_active"] = True
    st.session_state[f"{key}_message"] = message
    
    loader_instance = Loader(message)
    loader_instance.render()


def hide_loader(key: str = "loader") -> None:
    """Hide the persistent loader."""
    st.session_state[f"{key}_active"] = False
    st.rerun()


def update_loader_progress(
    progress: float,
    message: str | None = None,
    key: str = "loader",
) -> None:
    """
    Update loader progress.
    
    Args:
        progress: Progress between 0.0 and 1.0
        message: Optional new message
        key: Loader key
    """
    st.session_state[f"{key}_progress"] = progress
    if message:
        st.session_state[f"{key}_message"] = message


def skeleton_loader(
    height: int = 100,
    count: int = 1,
) -> None:
    """
    Show skeleton loading placeholders.
    
    Usage:
        skeleton_loader(height=50, count=3)  # 3 skeleton lines
    """
    css = f"""
    <style>
    .skeleton {{
        background: linear-gradient(90deg, {Colors.GRAY_200} 25%, {Colors.GRAY_100} 50%, {Colors.GRAY_200} 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: {BorderRadius.SM}px;
        height: {height}px;
        margin-bottom: {Spacing.SMALL}px;
    }}
    
    @keyframes shimmer {{
        0% {{ background-position: 200% 0; }}
        100% {{ background-position: -200% 0; }}
    }}
    </style>
    """
    
    html = css
    for _ in range(count):
        html += '<div class="skeleton"></div>'
    
    st.markdown(html, unsafe_allow_html=True)


def inline_spinner(
    message: str = "",
    size: str = "small",
) -> None:
    """
    Show an inline spinner (for use inside other components).
    
    Usage:
        inline_spinner("Sauvegarde...")
    """
    size_px = {"small": 16, "medium": 24, "large": 32}.get(size, 16)
    
    html = f"""
    <span style="display: inline-flex; align-items: center; gap: 8px;">
        <span style="
            display: inline-block;
            width: {size_px}px;
            height: {size_px}px;
            border: 2px solid {Colors.GRAY_200};
            border-top: 2px solid {Colors.EMERALD_600};
            border-radius: 50%;
            animation: spin 1s linear infinite;
        "></span>
        {message}
    </span>
    <style>
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
    """
    
    st.markdown(html, unsafe_allow_html=True)
