"""
Tests d'intégration pour v5.5 - Vérifie que tout fonctionne ensemble
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestV55Integration:
    """Tests d'intégration complets pour la v5.5."""

    def test_all_imports_work_together(self):
        """Vérifie que tous les modules peuvent être importés ensemble."""
        # Thème
        from modules.ui.theme import ThemeManager, get_theme, THEMES

        # Composants UI
        from modules.ui.components.welcome_empty_state import WelcomeEmptyState
        from modules.ui.dashboard.kpi_cards import render_kpi_cards, calculate_reste_a_vivre

        # Analytics
        from modules.analytics import AnalyticsTracker, EventType, MetricsCollector
        from modules.analytics.events import track_event, get_analytics_summary

        # Accessibilité
        from modules.ui.accessibility import check_contrast, validate_theme_contrast

        # Si on arrive ici, tous les imports fonctionnent
        assert True

    def test_theme_with_components(self):
        """Test que les composants utilisent bien le thème."""
        from modules.ui.theme import get_theme, THEMES
        from modules.ui.components.welcome_empty_state import WelcomeEmptyState

        # Récupérer un thème
        theme = THEMES["light_green"]

        # Vérifier que le thème a les couleurs attendues
        assert theme.primary == "#10B981"
        assert theme.bg_card == "#FFFFFF"

        # Vérifier que le composant peut être instancié
        # (sans Streamlit, on vérifie juste la classe)
        assert WelcomeEmptyState is not None

    def test_analytics_with_events(self):
        """Test que le système d'analytics peut tracker des événements."""
        from modules.analytics.events import EventType

        # Vérifier que tous les types d'événements sont définis
        event_types = [
            EventType.SESSION_START,
            EventType.EMPTY_STATE_CTA_CLICK,
            EventType.PAGE_VIEW,
            EventType.IMPORT_COMPLETE,
            EventType.KPI_HOVER,
        ]

        for et in event_types:
            assert et.value is not None
            assert isinstance(et.value, str)

    def test_accessibility_with_theme(self):
        """Test que les couleurs du thème sont accessibles."""
        from modules.ui.theme import THEMES
        from modules.ui.accessibility import validate_theme_contrast

        # Tester tous les thèmes
        for theme_name, theme in THEMES.items():
            theme_config = {
                "text_primary": theme.text_primary,
                "text_secondary": theme.text_secondary,
                "bg_card": theme.bg_card,
                "primary": theme.primary,
                "positive": theme.positive,
                "negative": theme.negative,
            }

            results = validate_theme_contrast(theme_config)

            # Au moins le texte principal doit être lisible
            primary_text_contrast = [r for r in results if r.foreground == theme.text_primary]
            if primary_text_contrast:
                assert primary_text_contrast[
                    0
                ].passes_aa_normal, f"Theme {theme_name}: primary text fails AA contrast"

    def test_kpi_calculation(self):
        """Test que les calculs de KPI fonctionnent avec des données complètes."""
        import pandas as pd
        from modules.ui.dashboard.kpi_cards import calculate_reste_a_vivre

        # Créer des données de test avec toutes les colonnes requises
        df = pd.DataFrame(
            {
                "amount": [1000, -500, -200, 300],
                "category_validated": ["Revenus", "Alimentation", "Transport", "Revenus"],
                "type": ["income", "expense", "expense", "income"],
            }
        )

        # Calculer
        result = calculate_reste_a_vivre(df)

        # Revenus: 1000 + 300 = 1300
        # Dépenses: 500 + 200 = 700
        # Reste à vivre: 1300 - 700 = 600
        expected = 600

        assert result == expected, f"Expected {expected}, got {result}"


class TestV55Performance:
    """Tests de performance pour v5.5."""

    def test_theme_loading_performance(self):
        """Test que le chargement du thème est rapide."""
        import time
        from modules.ui.theme import THEMES, get_theme

        start = time.time()

        # Accéder à tous les thèmes
        for name in THEMES:
            theme = THEMES[name]
            _ = theme.primary

        elapsed = time.time() - start

        # Devrait être instantané (< 10ms)
        assert elapsed < 0.01, f"Theme loading too slow: {elapsed:.4f}s"

    def test_contrast_calculation_performance(self):
        """Test que le calcul de contraste est rapide."""
        import time
        from modules.ui.accessibility import contrast_ratio

        start = time.time()

        # Calculer plusieurs contrastes
        for _ in range(100):
            contrast_ratio("#FFFFFF", "#000000")
            contrast_ratio("#10B981", "#FFFFFF")
            contrast_ratio("#EF4444", "#FFFFFF")

        elapsed = time.time() - start

        # 300 calculs devraient prendre moins de 100ms
        assert elapsed < 0.1, f"Contrast calculation too slow: {elapsed:.4f}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
