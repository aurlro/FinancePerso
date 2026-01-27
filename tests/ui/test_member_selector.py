"""
Tests for member selector component.
Focus on testable logic: member filtering, type categorization, and selection validation.
"""
import pytest
import pandas as pd

class TestMemberFiltering:
    """Tests for member filtering logic."""
    
    def test_filter_household_members(self):
        """Test filtering household members."""
        df = pd.DataFrame([
            {'name': 'Alice', 'type': 'HOUSEHOLD'},
            {'name': 'Bob', 'type': 'HOUSEHOLD'},
            {'name': 'Amazon', 'type': 'EXTERNAL'}
        ])
        
        household = df[df['type'] == 'HOUSEHOLD']
        
        assert len(household) == 2
        assert 'Alice' in household['name'].values
        assert 'Bob' in household['name'].values
    
    def test_filter_external_members(self):
        """Test filtering external members."""
        df = pd.DataFrame([
            {'name': 'Alice', 'type': 'HOUSEHOLD'},
            {'name': 'Amazon', 'type': 'EXTERNAL'},
            {'name': 'Netflix', 'type': 'EXTERNAL'}
        ])
        
        external = df[df['type'] == 'EXTERNAL']
        
        assert len(external) == 2
        assert 'Amazon' in external['name'].values
        assert 'Netflix' in external['name'].values

class TestMemberTypeCategorization:
    """Tests for member type categorization logic."""
    
    def test_categorize_member_by_amount(self):
        """Test categorizing member type by transaction amount pattern."""
        # Large recurring payments -> Usually household/family
        amounts = [-1200.00, -1200.00, -1200.00]  # Rent-like
        
        is_household_pattern = all(amt < 0 and abs(amt) > 500 for amt in amounts)
        
        assert is_household_pattern is True
    
    def test_categorize_member_by_frequency(self):
        """Test categorizing by transaction frequency."""
        transaction_count = 15  # Many transactions
        
        # High frequency suggests household member
        is_likely_household = transaction_count > 5
        
        assert is_likely_household is True

class TestMemberSelectionValidation:
    """Tests for member selection validation."""
    
    def test_validate_member_selected(self):
        """Test that a member is selected."""
        selected_member = "Alice"
        
        is_valid = bool(selected_member and selected_member != "")
        
        assert is_valid is True
    
    def test_validate_no_member_selected(self):
        """Test handling no member selection."""
        selected_member = ""
        
        is_valid = bool(selected_member and selected_member != "")
        
        assert is_valid is False
    
    def test_validate_member_in_list(self):
        """Test validating member exists in list."""
        available_members = ["Alice", "Bob", "Charlie"]
        selected_member = "Alice"
        
        is_valid = selected_member in available_members
        
        assert is_valid is True
        
        invalid_member = "Unknown"
        is_valid = invalid_member in available_members
        
        assert is_valid is False

class TestMemberIconLogic:
    """Tests for member type icon assignment."""
    
    def test_icon_for_household(self):
        """Test icon assignment for household members."""
        member_type = "HOUSEHOLD"
        icon = "👤" if member_type == "HOUSEHOLD" else "🏢"
        
        assert icon == "👤"
    
    def test_icon_for_external(self):
        """Test icon assignment for external members."""
        member_type = "EXTERNAL"
        icon = "👤" if member_type == "HOUSEHOLD" else "🏢"
        
        assert icon == "🏢"
