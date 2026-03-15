# -*- coding: utf-8 -*-
"""
Tests for the Toast molecule component.
"""

import pytest

from modules.ui.molecules.toast import (
    Toast,
    ToastType,
    show_toast,
    toast_error,
    toast_info,
    toast_success,
    toast_warning,
)


class TestToast:
    """Tests du composant Toast."""

    def test_toast_initialization(self):
        """Le toast s'initialise correctement."""
        toast = Toast("Test message")
        
        assert toast.props.message == "Test message"
        assert toast.props.type == ToastType.INFO
        assert toast.props.duration == 5000

    def test_toast_with_title(self):
        """Le toast peut avoir un titre."""
        toast = Toast("Message", title="Titre")
        
        assert toast.props.title == "Titre"

    def test_toast_types(self):
        """Les différents types de toast."""
        success = Toast("Success", type=ToastType.SUCCESS)
        error = Toast("Error", type=ToastType.ERROR)
        warning = Toast("Warning", type=ToastType.WARNING)
        info = Toast("Info", type=ToastType.INFO)
        
        assert success.props.type == ToastType.SUCCESS
        assert error.props.type == ToastType.ERROR
        assert warning.props.type == ToastType.WARNING
        assert info.props.type == ToastType.INFO

    def test_toast_colors(self):
        """Chaque type a ses couleurs."""
        assert Toast.COLORS[ToastType.SUCCESS]["icon"] == "✓"
        assert Toast.COLORS[ToastType.ERROR]["icon"] == "✕"
        assert Toast.COLORS[ToastType.INFO]["icon"] == "ℹ"
        assert Toast.COLORS[ToastType.WARNING]["icon"] == "⚠"

    def test_toast_duration(self):
        """La durée est configurable."""
        toast = Toast("Message", duration=10000)
        assert toast.props.duration == 10000


class TestToastHelpers:
    """Tests des fonctions utilitaires."""

    def test_toast_success_exists(self):
        """La fonction toast_success existe."""
        assert callable(toast_success)

    def test_toast_error_exists(self):
        """La fonction toast_error existe."""
        assert callable(toast_error)

    def test_toast_info_exists(self):
        """La fonction toast_info existe."""
        assert callable(toast_info)

    def test_toast_warning_exists(self):
        """La fonction toast_warning existe."""
        assert callable(toast_warning)

    def test_show_toast_exists(self):
        """La fonction show_toast existe."""
        assert callable(show_toast)
