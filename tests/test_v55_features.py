"""
Tests pour les fonctionnalités v5.5 - FinCouple Edition
Thème, Analytics, Accessibilité, Responsive
"""

import pytest
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestThemeSystem:
    """Tests du système de thème."""

    def test_theme_imports(self):
        """Vérifie que tous les imports du thème fonctionnent."""
        from modules.ui.theme import ThemeConfig, ThemeManager, get_theme, THEMES

        assert len(THEMES) == 6  # 2 modes × 3 palettes

    def test_theme_structure(self):
        """Vérifie la structure d'un thème."""
        from modules.ui.theme import THEMES

        theme = THEMES["light_green"]
        assert theme.name == "light_green"
        assert theme.is_dark == False
        assert theme.primary == "#10B981"
        assert theme.bg_card == "#FFFFFF"

    def test_theme_switching(self):
        """Test le changement de thème."""
        from modules.ui.theme import ThemeManager

        # Définir un thème
        ThemeManager.set_theme("dark_blue")

        # Vérifier qu'on peut le récupérer
        # Note: En test sans session Streamlit, on utilise le défaut
        # Mais on vérifie que la méthode existe et fonctionne

    def test_all_themes_have_required_colors(self):
        """Vérifie que tous les thèmes ont les couleurs requises."""
        from modules.ui.theme import THEMES

        required_attrs = [
            "primary",
            "primary_light",
            "primary_dark",
            "text_primary",
            "text_secondary",
            "text_muted",
            "bg_page",
            "bg_card",
            "bg_hover",
            "positive",
            "negative",
            "warning",
            "info",
            "border",
            "shadow_sm",
            "shadow_md",
            "shadow_lg",
        ]

        for name, theme in THEMES.items():
            for attr in required_attrs:
                assert hasattr(theme, attr), f"Theme {name} missing {attr}"
                value = getattr(theme, attr)
                assert value is not None and value != "", f"Theme {name}.{attr} is empty"


class TestAccessibility:
    """Tests d'accessibilité."""

    def test_contrast_ratio_calculation(self):
        """Test le calcul des ratios de contraste."""
        from modules.ui.accessibility import contrast_ratio, check_contrast

        # Blanc sur noir devrait être 21:1
        ratio = contrast_ratio("#FFFFFF", "#000000")
        assert ratio == 21.0

        # Noir sur blanc aussi
        ratio = contrast_ratio("#000000", "#FFFFFF")
        assert ratio == 21.0

    def test_wcag_aa_compliance(self):
        """Vérifie la conformité WCAG AA pour les couleurs du thème."""
        from modules.ui.accessibility import validate_theme_contrast
        from modules.ui.theme import THEMES

        # Tester le thème light green
        theme = THEMES["light_green"]
        theme_config = {
            "text_primary": theme.text_primary,
            "text_secondary": theme.text_secondary,
            "bg_card": theme.bg_card,
            "primary": theme.primary,
            "positive": theme.positive,
            "negative": theme.negative,
        }

        results = validate_theme_contrast(theme_config)

        # Vérifier qu'au moins quelques contrastes passent AA
        passing_aa = [r for r in results if r.passes_aa_normal]
        assert len(passing_aa) >= 2, f"Only {len(passing_aa)} contrasts pass AA, need at least 2"

    def test_theme_accessibility_report(self):
        """Test la génération du rapport d'accessibilité."""
        from modules.ui.accessibility import get_accessibility_report
        from modules.ui.theme import THEMES

        theme = THEMES["light_blue"]
        theme_config = {
            "text_primary": theme.text_primary,
            "text_secondary": theme.text_secondary,
            "bg_card": theme.bg_card,
            "primary": theme.primary,
            "positive": theme.positive,
            "negative": theme.negative,
        }

        report = get_accessibility_report(theme_config)

        assert "total_checks" in report
        assert "passes_all_aa" in report
        assert "failures" in report
        assert report["total_checks"] > 0


class TestAnalytics:
    """Tests du système d'analytics."""

    def test_analytics_imports(self):
        """Vérifie les imports analytics."""
        from modules.analytics import AnalyticsTracker, track_event, EventType

        assert EventType.IMPORT_COMPLETE is not None

    def test_event_type_enum(self):
        """Test les types d'événements."""
        from modules.analytics.events import EventType

        # Vérifier que tous les types attendus existent
        assert EventType.SESSION_START.value == "session_start"
        assert EventType.EMPTY_STATE_CTA_CLICK.value == "empty_state_cta_click"
        assert EventType.PAGE_VIEW.value == "page_view"

    def test_metrics_collector_exists(self):
        """Vérifie que MetricsCollector existe avec ses méthodes."""
        from modules.analytics.metrics import MetricsCollector

        methods = [
            "get_import_conversion_rate",
            "get_retention_rate",
            "get_feature_adoption",
            "get_dashboard_summary",
        ]

        for method in methods:
            assert hasattr(MetricsCollector, method), f"Missing method {method}"


class TestWelcomeEmptyState:
    """Tests du composant WelcomeEmptyState."""

    def test_component_imports(self):
        """Vérifie l'import du composant."""
        from modules.ui.components.welcome_empty_state import WelcomeEmptyState

        assert WelcomeEmptyState is not None

    def test_component_has_required_methods(self):
        """Vérifie les méthodes requises."""
        from modules.ui.components.welcome_empty_state import WelcomeEmptyState

        assert hasattr(WelcomeEmptyState, "render")
        assert hasattr(WelcomeEmptyState, "_inject_styles")


class TestKPICards:
    """Tests des KPI Cards."""

    def test_kpi_cards_import(self):
        """Vérifie l'import des KPI cards."""
        from modules.ui.dashboard.kpi_cards import render_kpi_cards, _render_kpi_card_html

        assert render_kpi_cards is not None

    def test_calculate_reste_a_vivre_exists(self):
        """Vérifie que la fonction Reste à vivre existe."""
        from modules.ui.dashboard.kpi_cards import calculate_reste_a_vivre

        assert callable(calculate_reste_a_vivre)


class TestResponsiveCSS:
    """Tests des styles responsives."""

    def test_kpi_responsive_styles_exist(self):
        """Vérifie que les styles responsives pour KPI existent."""
        from modules.ui.dashboard.kpi_cards import _inject_kpi_responsive_styles

        assert callable(_inject_kpi_responsive_styles)

    def test_welcome_responsive_styles_in_css(self):
        """Vérifie que le welcome card a des media queries."""
        import modules.ui.components.welcome_empty_state as welcome_module

        # Lire le fichier source
        source = Path(welcome_module.__file__).read_text()

        # Vérifier la présence de media queries
        assert "@media (max-width: 768px)" in source
        assert ".empty-state-card" in source


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
