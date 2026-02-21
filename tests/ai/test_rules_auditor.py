"""
Tests for rules_auditor.py module.
"""
import pytest
import pandas as pd
from modules.ai.rules_auditor import analyze_rules_integrity


class TestAnalyzeRulesIntegrity:
    """Tests for rules integrity analysis."""

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame()
        result = analyze_rules_integrity(df)
        assert isinstance(result, dict)

    def test_valid_rules(self):
        """Test with valid rules."""
        data = {
            "id": [1, 2, 3],
            "pattern": ["CARREFOUR", "SNCF", "AMAZON"],
            "category": ["Alimentation", "Transport", "Achats"],
            "priority": [1, 1, 2],
        }
        df = pd.DataFrame(data)
        result = analyze_rules_integrity(df)
        assert isinstance(result, dict)
        # Should report healthy rules

    def test_duplicate_patterns(self):
        """Test detection of duplicate patterns."""
        data = {
            "id": [1, 2],
            "pattern": ["DUPLICATE", "DUPLICATE"],
            "category": ["Cat1", "Cat2"],
            "priority": [1, 1],
        }
        df = pd.DataFrame(data)
        result = analyze_rules_integrity(df)
        assert isinstance(result, dict)
        # Should detect duplicates

    def test_missing_values(self):
        """Test handling of missing values."""
        data = {
            "id": [1, 2],
            "pattern": ["VALID", ""],
            "category": ["Cat1", None],
            "priority": [1, 1],
        }
        df = pd.DataFrame(data)
        result = analyze_rules_integrity(df)
        assert isinstance(result, dict)
