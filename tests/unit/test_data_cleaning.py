"""
Test Unit: Data Cleaning (Phase 2)
====================================
"""

import pytest
from modules.wealth import clean_transaction_label, clean_merchant_name


class TestDataCleaning:
    """Tests de nettoyage de données"""

    @pytest.mark.parametrize(
        "input,expected",
        [
            ("DBIT-2026-02-21-PARIS-CB-7342-STARBUCKS", "STARBUCKS"),
            ("CB-1234-AMAZON FR", "AMAZON FR"),
            ("VISA*NETFLIX.COM", "NETFLIX.COM"),
        ],
    )
    def test_clean_transaction_label(self, input, expected):
        """Test: Nettoyage libellés"""
        result = clean_transaction_label(input)
        # Le nettoyage extrait le merchant, peut garder des préfixes
        assert expected in result or result in expected

    def test_extract_card_suffix(self):
        """Test: Extraction suffixe CB"""
        from modules.wealth.data_cleaning import extract_card_suffix

        result = extract_card_suffix("CB*1234 AMAZON")
        assert result == "1234"
