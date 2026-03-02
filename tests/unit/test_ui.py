"""
Test Unit: Design System (Phase 6)
===================================
"""

import pytest
from modules.ui import DesignSystem, ColorScheme


class TestDesignSystem:
    """Tests du Design System"""

    def test_design_system_creation(self):
        """Test: Création du design system"""
        design = DesignSystem()

        assert design is not None
        assert design.colors.PRIMARY.value == "#6366F1"

    def test_css_generation(self):
        """Test: Génération CSS"""
        design = DesignSystem()
        css = design.get_css()

        assert len(css) > 1000
        assert "--fp-primary" in css

    def test_badge_creation(self):
        """Test: Création badge"""
        design = DesignSystem()
        badge = design.create_badge("Test", "primary")

        assert "Test" in badge
        assert "primary" in badge or "#6366F1" in badge
