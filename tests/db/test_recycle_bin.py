"""
Tests for recycle_bin.py module.
"""

import json
from datetime import datetime, timedelta

import pandas as pd
import pytest

from modules.db.recycle_bin import (
    init_recycle_bin,
    soft_delete_transaction,
    restore_transaction,
    get_recycle_bin_contents,
    purge_expired_items,
    get_recycle_bin_count,
    hard_delete_transaction,
)
from modules.db.transactions import save_transactions, get_all_transactions


class TestInitRecycleBin:
    """Tests for recycle bin initialization."""

    def test_init_recycle_bin_creates_table(self, temp_db, db_connection):
        """Test that init_recycle_bin creates the recycle_bin table."""
        init_recycle_bin()
        
        cursor = db_connection.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='recycle_bin'"
        )
        result = cursor.fetchone()
        assert result is not None
        assert result["name"] == "recycle_bin"

    def test_init_recycle_bin_idempotent(self, temp_db):
        """Test that init_recycle_bin can be called multiple times without error."""
        init_recycle_bin()
        init_recycle_bin()  # Should not raise
        init_recycle_bin()  # Should not raise


class TestSoftDeleteTransaction:
    """Tests for soft deleting transactions."""

    def test_soft_delete_existing_transaction(self, temp_db, sample_transactions, db_connection):
        """Test soft deleting an existing transaction."""
        init_recycle_bin()
        
        # First save a transaction
        df_sample = pd.DataFrame([sample_transactions[0]])
        save_transactions(df_sample)
        
        # Get the transaction ID
        cursor = db_connection.cursor()
        cursor.execute("SELECT id FROM transactions LIMIT 1")
        tx_id = cursor.fetchone()["id"]
        
        # Soft delete it
        result = soft_delete_transaction(tx_id, deleted_by="test_user")
        assert result is True  # soft_delete_transaction returns bool
        
        # Verify it's in recycle_bin
        cursor.execute("SELECT * FROM recycle_bin WHERE original_id = ?", (tx_id,))
        recycled = cursor.fetchone()
        assert recycled is not None
        assert recycled["deleted_by"] == "test_user"
        
        # Verify it's marked as deleted in transactions (soft delete)
        cursor.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,))
        tx = cursor.fetchone()
        assert tx is not None
        assert tx["status"] == "deleted"

    def test_soft_delete_nonexistent_transaction(self, temp_db):
        """Test soft deleting a transaction that doesn't exist."""
        init_recycle_bin()
        
        result = soft_delete_transaction(99999, deleted_by="test_user")
        assert result is False  # Returns bool for nonexistent

    def test_soft_delete_data_json_format(self, temp_db, sample_transactions, db_connection):
        """Test that soft deleted data is stored as valid JSON."""
        init_recycle_bin()
        
        # Save and delete a transaction
        df_sample = pd.DataFrame([sample_transactions[0]])
        save_transactions(df_sample)
        
        cursor = db_connection.cursor()
        cursor.execute("SELECT id FROM transactions LIMIT 1")
        tx_id = cursor.fetchone()["id"]
        
        soft_delete_transaction(tx_id)
        
        # Verify JSON data
        cursor.execute("SELECT data FROM recycle_bin WHERE original_id = ?", (tx_id,))
        data_json = cursor.fetchone()["data"]
        data = json.loads(data_json)
        
        assert "label" in data
        assert "amount" in data
        assert "date" in data
        assert data["label"] == sample_transactions[0]["label"]

    def test_soft_delete_sets_expires_at(self, temp_db, sample_transactions, db_connection):
        """Test that soft delete sets expiration date to 30 days later."""
        init_recycle_bin()
        
        df_sample = pd.DataFrame([sample_transactions[0]])
        save_transactions(df_sample)
        
        cursor = db_connection.cursor()
        cursor.execute("SELECT id FROM transactions LIMIT 1")
        tx_id = cursor.fetchone()["id"]
        
        soft_delete_transaction(tx_id)
        
        cursor.execute("SELECT expires_at FROM recycle_bin WHERE original_id = ?", (tx_id,))
        expires_at = cursor.fetchone()["expires_at"]
        
        # Parse the expires_at date
        expires_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00').replace('+00:00', ''))
        expected_date = datetime.now() + timedelta(days=30)
        
        # Should be approximately 30 days from now (within same day)
        assert (expires_date - expected_date).days < 2


class TestRestoreTransaction:
    """Tests for restoring transactions from recycle bin."""

    def test_restore_transaction_success(self, temp_db, sample_transactions, db_connection):
        """Test successfully restoring a transaction."""
        init_recycle_bin()
        
        # Save and soft delete
        df_sample = pd.DataFrame([sample_transactions[0]])
        save_transactions(df_sample)
        
        cursor = db_connection.cursor()
        cursor.execute("SELECT id FROM transactions LIMIT 1")
        tx_id = cursor.fetchone()["id"]
        
        soft_delete_transaction(tx_id)
        
        # Restore it
        success, message = restore_transaction(tx_id)
        assert success is True
        
        # Verify it's back in transactions
        cursor.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,))
        restored = cursor.fetchone()
        assert restored is not None
        assert restored["label"] == sample_transactions[0]["label"]
        
        # Verify it's marked as restored in recycle_bin
        cursor.execute("SELECT * FROM recycle_bin WHERE original_id = ?", (tx_id,))
        rb_entry = cursor.fetchone()
        assert rb_entry is not None
        assert rb_entry["restored"] == 1

    def test_restore_nonexistent_transaction(self, temp_db):
        """Test restoring a transaction not in recycle bin."""
        init_recycle_bin()
        
        success, message = restore_transaction(99999)
        assert success is False

    def test_restore_preserves_all_fields(self, temp_db, sample_transactions, db_connection):
        """Test that restore preserves all transaction fields."""
        init_recycle_bin()
        
        # Save a complete transaction
        df_sample = pd.DataFrame([sample_transactions[0]])
        save_transactions(df_sample)
        
        cursor = db_connection.cursor()
        cursor.execute("SELECT id FROM transactions LIMIT 1")
        tx_id = cursor.fetchone()["id"]
        
        soft_delete_transaction(tx_id)
        restore_transaction(tx_id)
        
        # Verify all fields are preserved
        cursor.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,))
        restored = cursor.fetchone()
        
        original = sample_transactions[0]
        assert restored["label"] == original["label"]
        assert restored["amount"] == original["amount"]
        assert restored["category_validated"] == original["category_validated"]
        assert restored["member"] == original["member"]
        assert restored["beneficiary"] == original["beneficiary"]


class TestGetRecycleBinContents:
    """Tests for getting recycle bin contents."""

    def test_get_empty_recycle_bin(self, temp_db):
        """Test getting contents of empty recycle bin."""
        init_recycle_bin()
        
        contents = get_recycle_bin_contents()
        assert contents.empty

    def test_get_recycle_bin_contents(self, temp_db, sample_transactions, db_connection):
        """Test getting contents with deleted transactions."""
        init_recycle_bin()
        
        # Save and delete multiple transactions
        df_sample = pd.DataFrame(sample_transactions[:2])
        save_transactions(df_sample)
        
        cursor = db_connection.cursor()
        cursor.execute("SELECT id FROM transactions")
        tx_ids = [row["id"] for row in cursor.fetchall()]
        
        for tx_id in tx_ids:
            soft_delete_transaction(tx_id)
        
        contents = get_recycle_bin_contents()
        assert len(contents) == 2
        assert "label" in contents.columns
        assert "amount" in contents.columns
        assert "deleted_at" in contents.columns

    def test_get_recycle_bin_with_limit(self, temp_db, sample_transactions, db_connection):
        """Test getting contents with limit."""
        init_recycle_bin()
        
        # Save and delete multiple transactions
        df_sample = pd.DataFrame(sample_transactions)
        save_transactions(df_sample)
        
        cursor = db_connection.cursor()
        cursor.execute("SELECT id FROM transactions")
        tx_ids = [row["id"] for row in cursor.fetchall()]
        
        for tx_id in tx_ids:
            soft_delete_transaction(tx_id)
        
        contents = get_recycle_bin_contents(limit=2)
        assert len(contents) == 2


class TestPurgeExpiredItems:
    """Tests for purging expired items."""

    def test_purge_no_expired_items(self, temp_db):
        """Test purging when no items are expired."""
        init_recycle_bin()
        
        count = purge_expired_items()
        assert count == 0

    def test_purge_expired_items(self, temp_db, sample_transactions, db_connection):
        """Test purging expired items."""
        init_recycle_bin()
        
        # Save and delete a transaction
        df_sample = pd.DataFrame([sample_transactions[0]])
        save_transactions(df_sample)
        
        cursor = db_connection.cursor()
        cursor.execute("SELECT id FROM transactions LIMIT 1")
        tx_id = cursor.fetchone()["id"]
        
        soft_delete_transaction(tx_id)
        
        # Manually set expiration to past
        cursor.execute(
            "UPDATE recycle_bin SET expires_at = ? WHERE original_id = ?",
            ((datetime.now() - timedelta(days=1)).isoformat(), tx_id)
        )
        db_connection.commit()
        
        # Purge should remove it
        count = purge_expired_items()
        assert count == 1
        
        # Verify it's gone
        cursor.execute("SELECT * FROM recycle_bin WHERE original_id = ?", (tx_id,))
        assert cursor.fetchone() is None


class TestGetRecycleBinCount:
    """Tests for getting recycle bin count."""

    def test_count_empty_recycle_bin(self, temp_db):
        """Test count of empty recycle bin."""
        init_recycle_bin()
        
        count = get_recycle_bin_count()
        assert count == 0

    def test_count_with_items(self, temp_db, sample_transactions, db_connection):
        """Test count with items in recycle bin."""
        init_recycle_bin()
        
        df_sample = pd.DataFrame(sample_transactions[:2])
        save_transactions(df_sample)
        
        cursor = db_connection.cursor()
        cursor.execute("SELECT id FROM transactions")
        tx_ids = [row["id"] for row in cursor.fetchall()]
        
        for tx_id in tx_ids:
            soft_delete_transaction(tx_id)
        
        count = get_recycle_bin_count()
        assert count == 2


class TestHardDeleteTransaction:
    """Tests for hard deleting transactions."""

    def test_hard_delete_from_recycle_bin(self, temp_db, sample_transactions, db_connection):
        """Test hard deleting a transaction from recycle bin."""
        init_recycle_bin()
        
        # Save, soft delete, then hard delete
        df_sample = pd.DataFrame([sample_transactions[0]])
        save_transactions(df_sample)
        
        cursor = db_connection.cursor()
        cursor.execute("SELECT id FROM transactions LIMIT 1")
        tx_id = cursor.fetchone()["id"]
        
        soft_delete_transaction(tx_id)
        
        success, message = hard_delete_transaction(tx_id)
        assert success is True
        
        # Verify completely gone
        cursor.execute("SELECT * FROM recycle_bin WHERE original_id = ?", (tx_id,))
        assert cursor.fetchone() is None
        
        cursor.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,))
        assert cursor.fetchone() is None

    def test_hard_delete_nonexistent(self, temp_db):
        """Test hard deleting a non-existent transaction."""
        init_recycle_bin()
        
        success, message = hard_delete_transaction(99999)
        assert success is False
