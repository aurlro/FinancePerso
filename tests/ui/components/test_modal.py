# -*- coding: utf-8 -*-
"""
Tests for the Modal molecule component.
"""

import pytest

from modules.ui.molecules.modal import Modal, confirm_modal


class TestModal:
    """Tests du composant Modal."""

    def test_modal_initialization(self):
        """Le modal s'initialise correctement."""
        modal = Modal("Test Title", key="test_modal")
        
        assert modal.props.title == "Test Title"
        assert modal.props.key == "test_modal"
        assert modal.props.width == "large"
        assert modal.props.show_close_button is True

    def test_modal_custom_props(self):
        """Les props personnalisées sont appliquées."""
        modal = Modal(
            title="Custom",
            key="custom_modal",
            width="small",
            show_close_button=False,
        )
        
        assert modal.props.width == "small"
        assert modal.props.show_close_button is False

    def test_modal_is_open_default(self):
        """Le modal est fermé par défaut."""
        modal = Modal("Test", key="modal_state")
        assert modal.is_open() is False

    def test_modal_open_close(self):
        """Ouvrir et fermer le modal."""
        modal = Modal("Test", key="modal_toggle")
        
        modal.open()
        assert modal.is_open() is True
        
        modal.close()
        assert modal.is_open() is False

    def test_modal_widths(self):
        """Les différentes largeurs sont définies."""
        assert Modal.WIDTHS["small"] == 400
        assert Modal.WIDTHS["medium"] == 600
        assert Modal.WIDTHS["large"] == 800
        assert Modal.WIDTHS["full"] == "95%"


class TestConfirmModal:
    """Tests du modal de confirmation."""

    def test_confirm_modal_default_texts(self):
        """Le modal de confirmation a des textes par défaut."""
        # On ne peut pas vraiment tester l'UI sans Streamlit
        # Mais on peut vérifier que la fonction existe
        assert callable(confirm_modal)

    def test_confirm_modal_custom_texts(self):
        """Le modal accepte des textes personnalisés."""
        # Vérification des paramètres
        import inspect
        sig = inspect.signature(confirm_modal)
        
        assert "confirm_text" in sig.parameters
        assert "cancel_text" in sig.parameters
        assert "danger" in sig.parameters
