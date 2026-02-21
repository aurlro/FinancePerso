
"""
UI Module - Design System et composants
========================================

Ce module contient le design system et les composants UI réutilisables.

Usage:
    from modules.ui import DesignSystem, apply_vibe_theme
    apply_vibe_theme()
"""

from modules.ui.design_system import (
    DesignSystem,
    ColorScheme,
    Typography,
    Spacing,
    Animation,
    apply_vibe_theme,
    vibe_container,
    vibe_metric,
    vibe_badge,
)

__all__ = [
    'DesignSystem',
    'ColorScheme',
    'Typography',
    'Spacing',
    'Animation',
    'apply_vibe_theme',
    'vibe_container',
    'vibe_metric',
    'vibe_badge',
]
