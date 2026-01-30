"""
Tests for rules.py module.
"""
import pytest
from modules.db.rules import (
    get_learning_rules,
    add_learning_rule,
    delete_learning_rule
)
from modules.db.transactions import (
    get_pending_transactions, 
    update_transaction_category,
    save_transactions
)
from modules.categorization import categorize_transaction
import pandas as pd

# Helper function to simulate apply_rules_to_pending
def apply_rules_to_pending():
    """Apply rules to all pending transactions (Simulation for tests)."""
    df_pending = get_pending_transactions()
    count = 0
    for _, row in df_pending.iterrows():
        cat, source, conf = categorize_transaction(row['label'], row['amount'], row['date'])
        if source == 'rule' or source == 'rule_constraint':
            # Only apply if rule matched (or constraint)
            # In real app, we might apply AI too, but here we test rules
            if cat != 'Inconnu':
                update_transaction_category(row['id'], cat)
                count += 1
    return count

class TestGetRules:
    """Tests for fetching learning rules."""
    
    def test_get_learning_rules_empty(self, temp_db):
        """Test getting rules when none exist."""
        df = get_learning_rules()
        assert df.empty
    
    def test_get_learning_rules_with_data(self, temp_db, db_connection):
        """Test getting rules."""
        # Use add_learning_rule instead of direct insert to be safe
        add_learning_rule('CARREFOUR', 'Alimentation')
        add_learning_rule('TOTAL', 'Transport')
        
        df = get_learning_rules()
        assert len(df) == 2
        assert 'pattern' in df.columns
        assert 'category' in df.columns

class TestAddRule:
    """Tests for adding learning rules."""
    
    def test_add_learning_rule(self, temp_db):
        """Test adding a learning rule."""
        rule_id = add_learning_rule('AMAZON', 'Shopping')
        assert rule_id is True
        
        df = get_learning_rules()
        assert len(df) == 1
        assert df.iloc[0]['pattern'] == 'AMAZON'
        assert df.iloc[0]['category'] == 'Shopping'
    
    def test_add_rule_with_special_characters(self, temp_db):
        """Test adding rule with special characters in pattern."""
        rule_id = add_learning_rule('CAFÉ-RESTO', 'Alimentation')
        assert rule_id is True
        
        df = get_learning_rules()
        assert df.iloc[0]['pattern'] == 'CAFÉ-RESTO'

class TestDeleteRule:
    """Tests for deleting learning rules."""
    
    def test_delete_learning_rule(self, temp_db):
        """Test deleting a rule."""
        add_learning_rule('DELETE_ME', 'Test')
        df = get_learning_rules()
        rule_id = int(df[df['pattern'] == 'DELETE_ME'].iloc[0]['id'])
        
        deleted = delete_learning_rule(rule_id)
        assert deleted is True
        
        df = get_learning_rules()
        assert df.empty
    
    def test_delete_nonexistent_rule(self, temp_db):
        """Test deleting non-existent rule."""
        deleted = delete_learning_rule(99999)
        assert deleted is False

class TestApplyRules:
    """Tests for applying rules to transactions."""
    
    def _add_tx(self, date, label, amount):
        # Helper to add transaction via save_transactions
        df = pd.DataFrame([{
            'date': date, 'label': label, 'amount': amount, 'status': 'pending',
            'category_validated': 'Inconnu'
        }])
        save_transactions(df)
        # Get ID
        pending = get_pending_transactions()
        return pending[pending['label'] == label].iloc[0]['id']

    def test_apply_rules_to_pending_simple_match(self, temp_db, db_connection):
        """Test applying rules with simple pattern match."""
        # Add rule
        add_learning_rule('CARREFOUR', 'Alimentation')
        
        # Add pending transaction
        tx_id = self._add_tx('2024-01-15', 'CARREFOUR MARKET', -50.00)
        
        # Apply rules
        count = apply_rules_to_pending()
        assert count >= 1
        
        # Verify categorization
        cursor = db_connection.cursor()
        cursor.execute("SELECT category_validated FROM transactions WHERE id = ?", (int(tx_id),))
        category = cursor.fetchone()[0]
        assert category == 'Alimentation'
    
    def test_apply_rules_multiple_transactions(self, temp_db, db_connection):
        """Test applying rules to multiple transactions."""
        # Add rules
        add_learning_rule('CARREFOUR', 'Alimentation')
        add_learning_rule('TOTAL', 'Transport')
        
        # Add pending transactions
        self._add_tx('2024-01-15', 'CARREFOUR MARKET', -50.00)
        self._add_tx('2024-01-16', 'TOTAL STATION', -60.00)
        self._add_tx('2024-01-17', 'RANDOM SHOP', -30.00)
        
        # Apply rules
        count = apply_rules_to_pending()
        assert count >= 2  # Two should match
        
        # Verify
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM transactions 
            WHERE category_validated IN ('Alimentation', 'Transport')
        """)
        categorized = cursor.fetchone()[0]
        assert categorized == 2
    
    def test_apply_rules_no_match(self, temp_db, db_connection):
        """Test that transactions without matches remain unchanged."""
        add_learning_rule('SPECIFIC_PATTERN', 'Test')
        
        self._add_tx('2024-01-15', 'NO MATCH HERE', -50.00)
        
        apply_rules_to_pending()
        
        cursor = db_connection.cursor()
        cursor.execute("SELECT category_validated FROM transactions WHERE label='NO MATCH HERE'")
        category = cursor.fetchone()[0]
        assert category == 'Inconnu'
    
    def test_apply_rules_case_insensitive(self, temp_db, db_connection):
        """Test that rule matching is case insensitive."""
        add_learning_rule('amazon', 'Shopping')
        
        tx_id = self._add_tx('2024-01-15', 'AMAZON.FR PURCHASE', -50.00)
        
        apply_rules_to_pending()
        
        cursor = db_connection.cursor()
        cursor.execute("SELECT category_validated FROM transactions WHERE id = ?", (int(tx_id),))
        category = cursor.fetchone()[0]
        assert category == 'Shopping'
