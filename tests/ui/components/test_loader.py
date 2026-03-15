# -*- coding: utf-8 -*-
"""
Tests for the Loader molecule component.
"""

import pytest

from modules.ui.molecules.loader import (
    Loader,
    hide_loader,
    inline_spinner,
    loader,
    show_loader,
    skeleton_loader,
    update_loader_progress,
)


class TestLoader:
    """Tests du composant Loader."""

    def test_loader_initialization(self):
        """Le loader s'initialise correctement."""
        loader_comp = Loader("Chargement...")
        
        assert loader_comp.props.message == "Chargement..."
        assert loader_comp.props.size == "medium"
        assert loader_comp.props.fullscreen is False

    def test_loader_sizes(self):
        """Les différentes tailles sont disponibles."""
        small = Loader("Small", size="small")
        medium = Loader("Medium", size="medium")
        large = Loader("Large", size="large")
        
        assert small.props.size == "small"
        assert medium.props.size == "medium"
        assert large.props.size == "large"

    def test_loader_fullscreen(self):
        """Le mode fullscreen est configurable."""
        loader_full = Loader("Fullscreen", fullscreen=True)
        assert loader_full.props.fullscreen is True

    def test_loader_sizes_dict(self):
        """Les tailles ont des dimensions définies."""
        assert "spinner" in Loader.SIZES["small"]
        assert "font" in Loader.SIZES["small"]
        assert Loader.SIZES["small"]["spinner"] == 24
        assert Loader.SIZES["medium"]["spinner"] == 40
        assert Loader.SIZES["large"]["spinner"] == 64

    def test_loader_progress(self):
        """Le loader peut afficher une progression."""
        loader_prog = Loader("Progress", show_progress=True)
        assert loader_prog.props.show_progress is True


class TestLoaderHelpers:
    """Tests des fonctions utilitaires."""

    def test_loader_context_manager_exists(self):
        """Le context manager loader existe."""
        assert callable(loader)

    def test_show_loader_exists(self):
        """La fonction show_loader existe."""
        assert callable(show_loader)

    def test_hide_loader_exists(self):
        """La fonction hide_loader existe."""
        assert callable(hide_loader)

    def test_update_loader_progress_exists(self):
        """La fonction update_loader_progress existe."""
        assert callable(update_loader_progress)

    def test_skeleton_loader_exists(self):
        """La fonction skeleton_loader existe."""
        assert callable(skeleton_loader)

    def test_inline_spinner_exists(self):
        """La fonction inline_spinner existe."""
        assert callable(inline_spinner)
