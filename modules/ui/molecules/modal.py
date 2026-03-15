# -*- coding: utf-8 -*-
"""
Modal molecule for the Design System.

Usage:
    with modal("Titre", key="my_modal"):
        st.write("Contenu du modal")
        if st.button("Valider"):
            modal.close()
"""

from dataclasses import dataclass
from typing import Callable, Generator

import streamlit as st

from modules.ui.tokens.colors import Colors
from modules.ui.tokens.spacing import Spacing


@dataclass
class ModalProps:
    """Props for the Modal component."""

    title: str
    key: str
    width: str = "large"  # small, medium, large, full
    show_close_button: bool = True
    on_close: Callable | None = None


class Modal:
    """Modal component with Emerald Design System styling."""

    WIDTHS = {
        "small": 400,
        "medium": 600,
        "large": 800,
        "full": "95%",
    }

    def __init__(
        self,
        title: str,
        key: str,
        width: str = "large",
        show_close_button: bool = True,
        on_close: Callable | None = None,
    ):
        self.props = ModalProps(
            title=title,
            key=key,
            width=width,
            show_close_button=show_close_button,
            on_close=on_close,
        )
        self._state_key = f"modal_open_{key}"

    def open(self) -> None:
        """Open the modal."""
        st.session_state[self._state_key] = True

    def close(self) -> None:
        """Close the modal."""
        st.session_state[self._state_key] = False
        if self.props.on_close:
            self.props.on_close()

    def is_open(self) -> bool:
        """Check if modal is open."""
        return st.session_state.get(self._state_key, False)

    def __enter__(self) -> "Modal":
        """Context manager entry."""
        # Initialize state
        if self._state_key not in st.session_state:
            st.session_state[self._state_key] = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        pass

    def render_content(self) -> None:
        """Override this or use context manager."""
        pass


def modal(
    title: str,
    key: str,
    width: str = "large",
    show_close_button: bool = True,
    on_close: Callable | None = None,
) -> Generator[Modal, None, None]:
    """
    Context manager for modal.
    
    Usage:
        with modal("Confirmation", key="confirm") as m:
            st.write("Êtes-vous sûr ?")
            if st.button("Oui"):
                do_something()
                m.close()
    """
    modal_instance = Modal(title, key, width, show_close_button, on_close)
    
    with modal_instance:
        if modal_instance.is_open():
            # CSS for modal overlay
            modal_css = f"""
            <style>
            .modal-overlay {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                z-index: 999999;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .modal-content {{
                background: white;
                border-radius: {Spacing.RADIUS_LARGE}px;
                padding: {Spacing.LARGE}px;
                width: {Modal.WIDTHS.get(width, 800)}px;
                max-width: 95%;
                max-height: 90vh;
                overflow-y: auto;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            }}
            .modal-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: {Spacing.MEDIUM}px;
                border-bottom: 1px solid #e5e7eb;
                padding-bottom: {Spacing.MEDIUM}px;
            }}
            .modal-title {{
                font-size: 1.25rem;
                font-weight: 600;
                color: {Colors.GRAY_900};
                margin: 0;
            }}
            .modal-close {{
                background: none;
                border: none;
                font-size: 1.5rem;
                cursor: pointer;
                color: {Colors.GRAY_500};
            }}
            .modal-close:hover {{
                color: {Colors.GRAY_700};
            }}
            </style>
            """
            st.markdown(modal_css, unsafe_allow_html=True)
            
            # Modal container
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 1])
                with col2:
                    # Header
                    header_cols = st.columns([5, 1])
                    with header_cols[0]:
                        st.markdown(f"<h3 class='modal-title'>{title}</h3>", unsafe_allow_html=True)
                    with header_cols[1]:
                        if show_close_button and st.button("✕", key=f"{key}_close"):
                            modal_instance.close()
                            st.rerun()
                    
                    st.markdown("---")
                    
                    # Content
                    yield modal_instance


def confirm_modal(
    title: str = "Confirmation",
    message: str = "Êtes-vous sûr ?",
    confirm_text: str = "Confirmer",
    cancel_text: str = "Annuler",
    danger: bool = False,
    key: str = "confirm",
) -> bool:
    """
    Simple confirmation modal.
    
    Returns:
        True if confirmed, False otherwise
    """
    confirmed = False
    
    with modal(title, key=key) as m:
        st.write(message)
        
        cols = st.columns([1, 1, 2])
        with cols[0]:
            if st.button(cancel_text, key=f"{key}_cancel"):
                m.close()
                st.rerun()
        with cols[1]:
            btn_type = "primary" if danger else "secondary"
            if st.button(confirm_text, key=f"{key}_confirm", type=btn_type):
                confirmed = True
                m.close()
                st.rerun()
    
    return confirmed
