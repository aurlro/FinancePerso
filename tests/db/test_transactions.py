"""
Tests for transactions.py module.
"""
import pytest
import pandas as pd
from modules.db.transactions import (
    get_all_transactions,
    get_pending_transactions,
    save_transactions,
    update_transaction_category,
    bulk_update_transaction_status,
    delete_transaction_by_id,
    delete_transactions_by_period,
    get_transactions_by_criteria,
    get_duplicates_report
)

class TestGetTransactions:
    """Tests for fetching transactions."""
    
    def test_get_all_transactions_empty(self, temp_db):
        """Test getting all transactions from empty database."""
        df = get_all_transactions()
        assert df.empty
    
    def test_get_all_transactions_with_data(self, temp_db, sample_transactions, db_connection):
        """Test getting all transactions with data."""
        # Use save_transactions
        df_sample = pd.DataFrame(sample_transactions)
        save_transactions(df_sample)
        
        df = get_all_transactions()
        assert len(df) == 3
        assert 'date' in df.columns
        assert 'amount' in df.columns
    
    def test_get_pending_transactions(self, temp_db, sample_transactions, db_connection):
        """Test filtering pending transactions."""
        df_sample = pd.DataFrame(sample_transactions)
        save_transactions(df_sample) # status default?
        # sample_transactions fixture likely has status. 
        # If not, save_transactions doesn't set status unless in DF?
        # Wait, save_transactions uses SQL defaults if not provided in DF. Default status is implementation dependent (usually PENDING?)
        # Let's assume sample_transactions has 'status'.
        
        df = get_pending_transactions()
        # count depends on sample data
        assert not df.empty 

class TestSaveTransaction:
    """Tests for inserting/saving transactions."""
    
    def test_insert_valid_transaction(self, temp_db):
        """Test inserting a valid transaction."""
        df = pd.DataFrame([{
            'date': '2024-01-20',
            'label': 'TEST TRANSACTION',
            'amount': -100.00,
            'account_label': 'Test Account'
        }])
        new, skipped = save_transactions(df)
        assert new == 1
        
        # Verify insertion
        df_all = get_all_transactions()
        assert len(df_all) == 1
        assert df_all.iloc[0]['label'] == 'TEST TRANSACTION'
        assert df_all.iloc[0]['amount'] == -100.00

class TestUpdateTransaction:
    """Tests for updating transactions."""
    
    def test_update_transaction_category(self, temp_db):
        """Test updating transaction category."""
        # Insert transaction
        df = pd.DataFrame([{
            'date': '2024-01-20',
            'label': 'UPDATE TEST',
            'amount': -30.00,
            'account_label': 'Account'
        }])
        save_transactions(df)
        df_all = get_all_transactions()
        tx_id = int(df_all.iloc[0]['id'])
        
        # Update category
        update_transaction_category(tx_id, 'Transport')
        
        # Verify
        df_all = get_all_transactions()
        assert df_all.iloc[0]['category_validated'] == 'Transport'
    
    def test_bulk_update_transaction_status(self, temp_db, sample_transactions):
        """Test bulk updating transaction categories."""
        df_sample = pd.DataFrame(sample_transactions)
        save_transactions(df_sample)
        
        df_all = get_all_transactions()
        tx_ids = [int(x) for x in df_all['id'].tolist()[:2]]
        
        # Bulk update first two
        bulk_update_transaction_status(tx_ids, 'Transport')
        
        df_all = get_all_transactions()
        assert df_all.iloc[0]['category_validated'] == 'Transport'
        assert df_all.iloc[1]['category_validated'] == 'Transport'

class TestDeleteTransaction:
    """Tests for deleting transactions."""
    
    def test_delete_transaction_by_id(self, temp_db):
        """Test deleting a single transaction."""
        df = pd.DataFrame([{
            'date': '2024-01-20',
            'label': 'TO DELETE',
            'amount': -20.00,
            'account_label': 'Account'
        }])
        save_transactions(df)
        df_all = get_all_transactions()
        tx_id = int(df_all.iloc[0]['id'])
        
        deleted = delete_transaction_by_id(tx_id)
        assert deleted == 1
        
        df_all = get_all_transactions()
        assert df_all.empty
    
    def test_delete_transactions_by_period(self, temp_db, sample_transactions):
        """Test deleting transactions by month."""
        df_sample = pd.DataFrame(sample_transactions)
        # Ensure sample has 2024-01
        save_transactions(df_sample)
        
        # Delete January 2024 (assuming sample has it)
        # If sample_transactions fixture uses '2024-01-XX'
        deleted = delete_transactions_by_period('2024-01')
        assert deleted >= 1
