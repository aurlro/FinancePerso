"""Tests des calculs KPI.

Usage:
    pytest tests/v5_5/test_kpi_calculations.py -v
"""

import pytest

from modules.ui.v5_5.dashboard.kpi_grid import calculate_kpis, parse_month


class TestParseMonth:
    """Tests du parsing de mois."""

    def test_parse_january_2026(self):
        """Test parsing Janvier 2026."""
        year, month = parse_month("Janvier 2026")
        assert year == 2026
        assert month == 1

    def test_parse_february_2026(self):
        """Test parsing Février 2026."""
        year, month = parse_month("Février 2026")
        assert year == 2026
        assert month == 2

    def test_parse_december_2025(self):
        """Test parsing Décembre 2025."""
        year, month = parse_month("Décembre 2025")
        assert year == 2025
        assert month == 12

    def test_parse_lowercase(self):
        """Test parsing en minuscules."""
        year, month = parse_month("mars 2026")
        assert year == 2026
        assert month == 3

    def test_parse_with_accents(self):
        """Test parsing avec accents."""
        year, month = parse_month("février 2026")
        assert year == 2026
        assert month == 2


class TestCalculateKPIs:
    """Tests des calculs KPI."""

    def test_empty_dataframe(self):
        """Test avec un DataFrame vide."""
        kpis = calculate_kpis("Janvier 2026")

        # Devrait retourner 4 KPIs
        assert len(kpis) == 4
        # Les valeurs devraient être des chaînes formatées
        assert all(isinstance(kpi.value, str) for kpi in kpis)

    def test_kpi_structure(self):
        """Test la structure des KPIs retournés."""
        kpis = calculate_kpis("Janvier 2026")

        # Vérifier les labels
        labels = [kpi.label for kpi in kpis]
        assert "Reste à vivre" in labels
        assert "Dépenses" in labels
        assert "Revenus" in labels
        assert "Épargne" in labels

    def test_kpi_icons(self):
        """Test que les KPIs ont des icônes."""
        kpis = calculate_kpis("Janvier 2026")

        # Vérifier que tous les KPIs ont des icônes
        assert all(kpi.icon for kpi in kpis)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
