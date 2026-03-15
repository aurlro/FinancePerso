# -*- coding: utf-8 -*-
"""
Toast notification molecule for the Design System.

Usage:
    toast_success("Opération réussie!")
    toast_error("Une erreur s'est produite")
    toast_info("Nouvelle mise à jour disponible")
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

import streamlit as st

from modules.ui.tokens.colors import Colors
from modules.ui.tokens.radius import BorderRadius
from modules.ui.tokens.spacing import Spacing


class ToastType(Enum):
    """Types de toast notifications."""

    SUCCESS = "success"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"


@dataclass
class ToastProps:
    """Props for the Toast component."""

    message: str
    title: str | None = None
    type: ToastType = ToastType.INFO
    duration: int = 5000  # milliseconds
    position: str = "top-right"


class Toast:
    """Toast notification component."""

    COLORS = {
        ToastType.SUCCESS: {
            "bg": Colors.SUCCESS_BG,
            "border": Colors.SUCCESS,
            "icon": "✓",
            "text": Colors.SUCCESS_DARK,
        },
        ToastType.ERROR: {
            "bg": Colors.DANGER_BG,
            "border": Colors.DANGER,
            "icon": "✕",
            "text": Colors.DANGER_DARK,
        },
        ToastType.INFO: {
            "bg": Colors.INFO_BG,
            "border": Colors.INFO,
            "icon": "ℹ",
            "text": Colors.INFO_DARK,
        },
        ToastType.WARNING: {
            "bg": Colors.WARNING_BG,
            "border": Colors.WARNING,
            "icon": "⚠",
            "text": Colors.WARNING_DARK,
        },
    }

    def __init__(
        self,
        message: str,
        title: str | None = None,
        type: ToastType = ToastType.INFO,
        duration: int = 5000,
    ):
        self.props = ToastProps(
            message=message,
            title=title,
            type=type,
            duration=duration,
        )

    def show(self) -> None:
        """Display the toast notification."""
        colors = self.COLORS.get(self.props.type, self.COLORS[ToastType.INFO])
        
        # Generate unique key based on timestamp
        unique_key = f"toast_{int(time.time() * 1000)}"
        
        toast_html = f"""
        <div id="{unique_key}" style="
            position: fixed;
            top: 20px;
            right: 20px;
            background: {colors['bg']};
            border-left: 4px solid {colors['border']};
            border-radius: {BorderRadius.MD}px;
            padding: {Spacing.MEDIUM}px {Spacing.LARGE}px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            z-index: 999999;
            max-width: 400px;
            animation: slideIn 0.3s ease-out;
        ">
            <div style="display: flex; align-items: center; gap: {Spacing.SMALL}px;">
                <span style="font-size: 1.2rem; color: {colors['border']};">
                    {colors['icon']}
                </span>
                <div>
                    {f'<div style="font-weight: 600; color: {colors["text"]}; margin-bottom: 2px;">{self.props.title}</div>' if self.props.title else ''}
                    <div style="color: {colors['text']}; font-size: 0.9rem;">
                        {self.props.message}
                    </div>
                </div>
            </div>
        </div>
        <style>
            @keyframes slideIn {{
                from {{ transform: translateX(100%); opacity: 0; }}
                to {{ transform: translateX(0); opacity: 1; }}
            }}
            @keyframes slideOut {{
                from {{ transform: translateX(0); opacity: 1; }}
                to {{ transform: translateX(100%); opacity: 0; }}
            }}
        </style>
        <script>
            setTimeout(function() {{
                var toast = document.getElementById('{unique_key}');
                if (toast) {{
                    toast.style.animation = 'slideOut 0.3s ease-in forwards';
                    setTimeout(function() {{
                        toast.remove();
                    }}, 300);
                }}
            }}, {self.props.duration});
        </script>
        """
        
        st.markdown(toast_html, unsafe_allow_html=True)


# Convenience functions

def toast_success(message: str, title: str | None = None, duration: int = 5000) -> None:
    """Show a success toast."""
    Toast(message, title, ToastType.SUCCESS, duration).show()


def toast_error(message: str, title: str | None = None, duration: int = 5000) -> None:
    """Show an error toast."""
    Toast(message, title, ToastType.ERROR, duration).show()


def toast_info(message: str, title: str | None = None, duration: int = 5000) -> None:
    """Show an info toast."""
    Toast(message, title, ToastType.INFO, duration).show()


def toast_warning(message: str, title: str | None = None, duration: int = 5000) -> None:
    """Show a warning toast."""
    Toast(message, title, ToastType.WARNING, duration).show()


def show_toast(
    message: str,
    type: str = "info",
    title: str | None = None,
    duration: int = 5000,
) -> None:
    """
    Generic toast function.
    
    Args:
        message: Message à afficher
        type: Type de toast (success, error, info, warning)
        title: Titre optionnel
        duration: Durée en millisecondes
    """
    type_mapping = {
        "success": ToastType.SUCCESS,
        "error": ToastType.ERROR,
        "info": ToastType.INFO,
        "warning": ToastType.WARNING,
    }
    
    toast_type = type_mapping.get(type, ToastType.INFO)
    Toast(message, title, toast_type, duration).show()
