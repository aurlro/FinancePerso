"""
Unit tests for MyFinance Companion.
Run with: pytest tests/ -v
"""
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.utils import clean_label, extract_card_member, validate_csv_file

class TestCleanLabel:
    """Tests for the clean_label utility function."""
    
    def test_removes_card_info(self):
        result = clean_label("Carte 30/12/25 Restaurant PAPY CB*6759")
        assert "CB*6759" not in result
        assert "Carte" not in result
        
    def test_removes_dates(self):
        result = clean_label("30/12/25 AMAZON PRIME")
        assert "30/12" not in result
        assert "AMAZON" in result
        
    def test_removes_bank_prefixes(self):
        result = clean_label("PRLV SEPA EDF COMMERCE")
        assert "PRLV" not in result
        assert "SEPA" not in result
        assert "EDF" in result
        
    def test_trims_whitespace(self):
        result = clean_label("   CARREFOUR   ")
        assert result == "CARREFOUR"
        
    def test_handles_empty_string(self):
        result = clean_label("")
        assert result == ""

class TestExtractCardMember:
    """Tests for card member extraction."""
    
    def test_extracts_known_card(self):
        card_map = {'6759': 'Aurélien', '7238': 'Élise'}
        result = extract_card_member("Restaurant CB*6759", card_map)
        assert result == "Aurélien"
        
    def test_extracts_unknown_card(self):
        card_map = {'6759': 'Aurélien'}
        result = extract_card_member("Restaurant CB*9999", card_map)
        assert result == "Carte 9999"
        
    def test_no_card_returns_empty(self):
        card_map = {'6759': 'Aurélien'}
        result = extract_card_member("VIREMENT SALAIRE", card_map)
        assert result == ""

class TestValidateCsvFile:
    """Tests for CSV file validation."""
    
    def test_rejects_none(self):
        is_valid, msg = validate_csv_file(None)
        assert not is_valid
        assert "Aucun fichier" in msg
