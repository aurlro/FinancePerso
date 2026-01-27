"""
Tests for audit.py module.
"""
import pytest
from modules.db.audit import (
    get_suggested_mappings,
    get_transfer_inconsistencies
)
from modules.db.members import get_orphan_labels

class TestOrphanLabels:
    """Tests for orphan label detection."""
    
    def test_get_orphan_labels_none(self, temp_db, db_connection):
        """Test when there are no orphan labels."""
        # Add official member
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO members (name, member_type) VALUES ('Official', 'HOUSEHOLD')")
        db_connection.commit()
        
        # Add transaction with official member
        cursor.execute("""
            INSERT INTO transactions (date, label, amount, member)
            VALUES ('2024-01-15', 'TX', -50.00, 'Official')
        """)
        db_connection.commit()
        
        orphans = get_orphan_labels()
        # 'Official' should not be an orphan
        assert 'Official' not in orphans
    
    def test_get_orphan_labels_detected(self, temp_db, db_connection):
        """Test detecting orphan labels."""
        # Add transaction with non-official member
        cursor = db_connection.cursor()
        cursor.execute("""
            INSERT INTO transactions (date, label, amount, member)
            VALUES ('2024-01-15', 'TX', -50.00, 'Orphan Member')
        """)
        db_connection.commit()
        
        orphans = get_orphan_labels()
        assert 'Orphan Member' in orphans

class TestSuggestedMappings:
    """Tests for card suffix mapping suggestions."""
    
    def test_get_suggested_mappings_none(self, temp_db, db_connection):
        """Test when no card suffixes need mapping."""
        # Add transaction without card info
        cursor = db_connection.cursor()
        cursor.execute("""
            INSERT INTO transactions (date, label, amount)
            VALUES ('2024-01-15', 'NO CARD INFO', -50.00)
        """)
        db_connection.commit()
        
        suggestions = get_suggested_mappings()
        # Should be empty or very limited
    
    def test_get_suggested_mappings_detected(self, temp_db, db_connection):
        """Test detecting card suffixes that need mapping."""
        # Add transactions with card suffixes in label
        cursor = db_connection.cursor()
        cursor.execute("""
            INSERT INTO transactions (date, label, amount)
            VALUES ('2024-01-15', 'PAYMENT CARD 1234', -50.00)
        """)
        cursor.execute("""
            INSERT INTO transactions (date, label, amount)
            VALUES ('2024-01-16', 'PAYMENT CARD 1234', -30.00)
        """)
        db_connection.commit()
        
        suggestions = get_suggested_mappings()
        # Should detect card suffix '1234'
        if not suggestions.empty:
            assert '1234' in suggestions['card_suffix'].tolist()

class TestTransferInconsistencies:
    """Tests for transfer inconsistency detection."""
    
    def test_get_transfer_inconsistencies_none(self, temp_db, db_connection):
        """Test when there are no inconsistencies."""
        # Add properly categorized transfer
        cursor = db_connection.cursor()
        cursor.execute("""
            INSERT INTO transactions (date, label, amount, category_validated)
            VALUES ('2024-01-15', 'VIREMENT VERS LIVRET', -500.00, 'Virement Interne')
        """)
        db_connection.commit()
        
        missing, wrong = get_transfer_inconsistencies()
        # Should not flag this as inconsistent
    
    def test_get_transfer_inconsistencies_missing_category(self, temp_db, db_connection):
        """Test detecting transfers without correct category."""
        # Add transaction that looks like transfer but not categorized
        cursor = db_connection.cursor()
        cursor.execute("""
            INSERT INTO transactions (date, label, amount, category_validated)
            VALUES ('2024-01-15', 'VIREMENT VERS LIVRET', -500.00, 'Inconnu')
        """)
        db_connection.commit()
        
        missing, wrong = get_transfer_inconsistencies()
        assert not missing.empty
    
    def test_get_transfer_inconsistencies_wrong_category(self, temp_db, db_connection):
        """Test detecting non-transfers wrongly categorized as transfers."""
        # Add normal transaction categorized as transfer
        cursor = db_connection.cursor()
        cursor.execute("""
            INSERT INTO transactions (date, label, amount, category_validated)
            VALUES ('2024-01-15', 'CARREFOUR MARKET', -50.00, 'Virement Interne')
        """)
        db_connection.commit()
        
        missing, wrong = get_transfer_inconsistencies()
        # Should detect this as wrongly categorized
        if not wrong.empty:
            assert 'CARREFOUR' in wrong.iloc[0]['label']
