"""
Tests for budgets.py module.
"""
import pytest
from modules.db.budgets import (
    get_budgets,
    set_budget,
    delete_budget
)

class TestGetBudgets:
    """Tests for fetching budgets."""
    
    def test_get_budgets_empty(self, temp_db):
        """Test getting budgets when none exist."""
        df = get_budgets()
        assert df.empty
    
    def test_get_budgets_with_data(self, temp_db, db_connection):
        """Test getting budgets."""
        # Use set_budget to populate
        set_budget('Alimentation', 500.00)
        set_budget('Transport', 200.00)
        
        df = get_budgets()
        assert len(df) == 2
        assert 'category' in df.columns
        assert 'amount' in df.columns
        assert 'Alimentation' in df['category'].values
        assert 'Transport' in df['category'].values

class TestSetBudget:
    """Tests for setting/adding budgets."""
    
    def test_add_new_budget(self, temp_db):
        """Test adding a new budget."""
        set_budget('Loisirs', 300.00)
        
        df = get_budgets()
        assert len(df) == 1
        row = df[df['category'] == 'Loisirs'].iloc[0]
        assert row['amount'] == 300.00
    
    def test_update_existing_budget(self, temp_db):
        """Test updating an existing budget."""
        set_budget('Loisirs', 300.00)
        # Update
        set_budget('Loisirs', 400.00)
        
        df = get_budgets()
        assert len(df) == 1
        row = df[df['category'] == 'Loisirs'].iloc[0]
        assert row['amount'] == 400.00
    
    def test_set_budget_zero_amount(self, temp_db):
        """Test setting budget to zero."""
        set_budget('Test', 0.00)
        
        df = get_budgets()
        row = df[df['category'] == 'Test'].iloc[0]
        assert row['amount'] == 0.00

class TestDeleteBudget:
    """Tests for deleting budgets."""
    
    def test_delete_budget(self, temp_db):
        """Test deleting a budget."""
        set_budget('ToDelete', 100.00)
        deleted = delete_budget('ToDelete')
        assert deleted is True
        
        df = get_budgets()
        assert df.empty
    
    def test_delete_nonexistent_budget(self, temp_db):
        """Test deleting non-existent budget."""
        deleted = delete_budget('NonExistent')
        assert deleted is False
