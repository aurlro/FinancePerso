"""Tests des composants V5.5.

Usage:
    pytest tests/v5_5/test_components.py -v
"""

from datetime import datetime

import pandas as pd
import pytest

from modules.ui.v5_5.components.charts import DonutChart
from modules.ui.v5_5.components.savings_goals import SavingsGoal
from modules.ui.v5_5.components.transactions import TransactionList, get_category_icon


class TestCategoryIcons:
    """Tests des icônes de catégories."""

    def test_known_categories(self):
        """Test que les catégories connues ont des icônes."""
        assert get_category_icon("Alimentation") == "🍽️"
        assert get_category_icon("Transport") == "🚗"
        assert get_category_icon("Logement") == "🏠"
        assert get_category_icon("Salaire") == "💰"

    def test_unknown_category(self):
        """Test qu'une catégorie inconnue retourne une icône par défaut."""
        assert get_category_icon("Catégorie Inconnue") == "📌"

    def test_none_category(self):
        """Test que None retourne une icône par défaut."""
        assert get_category_icon(None) == "📌"

    def test_empty_category(self):
        """Test qu'une chaîne vide retourne une icône par défaut."""
        assert get_category_icon("") == "📌"


class TestSavingsGoal:
    """Tests des objectifs d'épargne."""

    def test_progress_calculation(self):
        """Test du calcul de progression."""
        goal = SavingsGoal("Test", 1000, 500, "🎯")
        assert goal.progress == 50.0

    def test_progress_capped_at_100(self):
        """Test que la progression est plafonnée à 100%."""
        goal = SavingsGoal("Test", 1000, 1500, "🎯")
        assert goal.progress == 100.0

    def test_progress_zero_target(self):
        """Test avec un target à 0."""
        goal = SavingsGoal("Test", 0, 500, "🎯")
        assert goal.progress == 0

    def test_remaining_calculation(self):
        """Test du calcul du montant restant."""
        goal = SavingsGoal("Test", 1000, 300, "🎯")
        assert goal.remaining == 700

    def test_remaining_zero(self):
        """Test quand l'objectif est atteint."""
        goal = SavingsGoal("Test", 1000, 1000, "🎯")
        assert goal.remaining == 0


class TestDonutChart:
    """Tests du graphique donut."""

    def test_category_colors_defined(self):
        """Test que les couleurs sont définies pour les catégories."""
        assert len(DonutChart.CATEGORY_COLORS) > 0
        assert "Alimentation" in DonutChart.CATEGORY_COLORS
        assert "Logement" in DonutChart.CATEGORY_COLORS

    def test_default_colors_defined(self):
        """Test que les couleurs par défaut sont définies."""
        assert len(DonutChart.DEFAULT_COLORS) >= 6


class TestTransactionList:
    """Tests de la liste de transactions."""

    def test_empty_dataframe(self):
        """Test avec un DataFrame vide."""
        df = pd.DataFrame()
        # Ne devrait pas lever d'exception
        TransactionList.render(df, limit=5)

    def test_dataframe_with_data(self):
        """Test avec un DataFrame contenant des données."""
        df = pd.DataFrame(
            {
                "date": [datetime.now()],
                "label": ["Test Transaction"],
                "amount": [-50.0],
                "category_validated": ["Alimentation"],
            }
        )
        # Ne devrait pas lever d'exception
        TransactionList.render(df, limit=5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
