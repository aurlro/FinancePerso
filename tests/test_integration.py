"""
Integration Tests for FinancePerso
Tests complete workflows and interactions between modules.
"""
import pytest
import pandas as pd
from datetime import date, timedelta

# Import flow
from modules.db.transactions import (
    save_transactions,
    get_all_transactions,
    get_pending_transactions,
    update_transaction_category,
    bulk_update_transaction_status
)
from modules.db.categories import get_categories
from modules.db.members import add_member, get_members
from modules.db.rules import add_learning_rule, get_learning_rules
from modules.db.tags import get_all_tags, remove_tag_from_all_transactions
from modules.categorization import categorize_transaction

# Helper to simulate apply_rules_to_pending
def apply_rules_to_pending():
    """Apply rules to all pending transactions (Simulation for tests)."""
    df_pending = get_pending_transactions()
    count = 0
    if df_pending.empty:
        return 0
        
    for _, row in df_pending.iterrows():
        cat, source, conf = categorize_transaction(row['label'], row['amount'], row['date'])
        if source == 'rule' or source == 'rule_constraint':
            if cat != 'Inconnu':
                update_transaction_category(row['id'], cat)
                count += 1
    return count

class TestImportToCategorization:
    """Test import → auto-categorization workflow."""
    
    def test_import_and_auto_categorize(self, temp_db, db_connection):
        """Test that imported transactions are auto-categorized by rules."""
        # Step 1: Create a learning rule
        add_learning_rule('CARREFOUR', 'Alimentation')
        
        # Step 2: Import transactions (simulate CSV import)
        df = pd.DataFrame([
            {'date': '2024-01-15', 'label': 'CARREFOUR MARKET PARIS', 'amount': -85.50, 'status': 'pending', 'category_validated': 'Inconnu'},
            {'date': '2024-01-16', 'label': 'CARREFOUR EXPRESS', 'amount': -42.30, 'status': 'pending', 'category_validated': 'Inconnu'},
            {'date': '2024-01-17', 'label': 'TOTAL STATION', 'amount': -55.00, 'status': 'pending', 'category_validated': 'Inconnu'}
        ])
        save_transactions(df)
        
        # Step 3: Apply rules
        count = apply_rules_to_pending()
        assert count >= 2  # At least CARREFOUR ones
        
        # Step 4: Verify categorization
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT category_validated FROM transactions 
            WHERE label LIKE '%CARREFOUR%'
        """)
        categories = [row[0] for row in cursor.fetchall()]
        assert all(cat == 'Alimentation' for cat in categories)
    
    def test_import_with_member_attribution(self, temp_db, db_connection):
        """Test import with automatic member attribution."""
        # Step 1: Create member
        add_member('Alice', 'HOUSEHOLD')
        
        # Step 2: Import transactions with member info
        # Member attribution typically happens via card_suffix mapping or direct col in CSV
        # We test direct column here
        df = pd.DataFrame([
            {'date': '2024-01-15', 'label': 'COURSES', 'amount': -50.00, 'member': 'Alice'}
        ])
        save_transactions(df)
        
        # Step 3: Verify member attribution
        cursor = db_connection.cursor()
        cursor.execute("SELECT member FROM transactions WHERE label = 'COURSES'")
        member = cursor.fetchone()[0]
        assert member == 'Alice'


class TestValidationWorkflow:
    """Test validation → learning → re-categorization workflow."""
    
    def test_validate_creates_learning_rule(self, temp_db, db_connection):
        """Test that validation can create learning rules."""
        # Step 1: Import pending transaction
        df = pd.DataFrame([
            {'date': '2024-01-15', 'label': 'AMAZON.FR ACHAT', 'amount': -79.99, 'status': 'pending', 'category_validated': 'Inconnu'}
        ])
        save_transactions(df)
        df_all = get_all_transactions()
        tx_id = int(df_all.iloc[-1]['id'])
        
        # Step 2: User validates and categorizes
        # Logic: In UI, user sets category. Does it create rule auto? No, separate button usually.
        # But we can simulate "User creates rule" manually aka add_learning_rule
        update_transaction_category(tx_id, 'Shopping')
        
        # Step 3: Create learning rule from this validation
        add_learning_rule('AMAZON', 'Shopping')
        
        # Step 4: Import another similar transaction
        df2 = pd.DataFrame([
            {'date': '2024-01-20', 'label': 'AMAZON PRIME', 'amount': -5.99, 'status': 'pending', 'category_validated': 'Inconnu'}
        ])
        save_transactions(df2)
        
        # Step 5: Apply rules
        apply_rules_to_pending()
        
        # Step 6: Verify auto-categorization
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT category_validated FROM transactions 
            WHERE label = 'AMAZON PRIME'
        """)
        category = cursor.fetchone()[0]
        assert category == 'Shopping'
    
    def test_bulk_validation_with_tags(self, temp_db, db_connection):
        """Test bulk validation with tag assignment."""
        # Step 1: Import multiple similar transactions
        df = pd.DataFrame([
            {'date': '2024-01-15', 'label': 'REMBOURSEMENT SECU', 'amount': 45.00, 'status': 'pending'},
            {'date': '2024-01-16', 'label': 'REMBOURSEMENT SECU', 'amount': 45.00, 'status': 'pending'},
            {'date': '2024-01-17', 'label': 'REMBOURSEMENT SECU', 'amount': 45.00, 'status': 'pending'}
        ])
        save_transactions(df)
        
        # Get IDs
        df_all = get_all_transactions()
        tx_ids = [int(x) for x in df_all['id'].tolist()]
        
        # Step 2: Bulk validate and tag
        # Use bulk_update_transaction_status
        bulk_update_transaction_status(tx_ids, 'Santé', tags='Remboursement')
        
        # Step 3: Verify all are tagged
        tags = get_all_tags()
        assert 'remboursement' in [t.lower() for t in tags]


class TestBudgetTracking:
    """Test budget tracking workflow."""
    
    def test_budget_vs_actual_flow(self, temp_db, db_connection):
        """Test setting budget and comparing with actuals."""
        from modules.db.budgets import set_budget, get_budgets
        
        # Step 1: Set budget
        set_budget('Alimentation', 500.00)
        
        # Step 2: Add transactions
        df = pd.DataFrame([
            {'date': '2024-01-15', 'label': 'COURSES 1', 'amount': -150.00, 'category_validated': 'Alimentation', 'status': 'validated'},
            {'date': '2024-01-20', 'label': 'COURSES 2', 'amount': -200.00, 'category_validated': 'Alimentation', 'status': 'validated'}
        ])
        save_transactions(df)
        
        # Step 3: Calculate actual spending
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT SUM(ABS(amount)) FROM transactions
            WHERE category_validated = 'Alimentation'
            AND status = 'validated'
        """)
        actual = cursor.fetchone()[0]
        
        # Step 4: Compare with budget
        budgets = get_budgets()
        budget_amount = budgets[budgets['category'] == 'Alimentation'].iloc[0]['amount']
        
        assert actual == 350.00
        assert budget_amount == 500.00
        assert actual < budget_amount  # Under budget


class TestAuditWorkflows:
    """Test audit and data cleanup workflows."""
    
    def test_orphan_detection_and_cleanup(self, temp_db, db_connection):
        """Test detecting and fixing orphan members."""
        from modules.db.members import get_orphan_labels, add_member
        
        # Step 1: Add transactions with unknown member
        df = pd.DataFrame([
             {'date': '2024-01-15', 'label': 'TX 1', 'amount': -50.00, 'member': 'UnknownPerson'},
             {'date': '2024-01-16', 'label': 'TX 2', 'amount': -30.00, 'member': 'UnknownPerson'}
        ])
        save_transactions(df)
        
        # Step 2: Detect orphans
        orphans = get_orphan_labels()
        assert 'UnknownPerson' in orphans
        
        # Step 3: Add member officially
        add_member('UnknownPerson', 'HOUSEHOLD')
        
        # Step 4: Verify orphan is resolved
        orphans_after = get_orphan_labels()
        assert 'UnknownPerson' not in orphans_after
    
    def test_duplicate_detection_flow(self, temp_db, db_connection):
        """Test detecting duplicate transactions."""
        from modules.db.transactions import get_duplicates_report
        
        # Step 1: Add duplicate transactions
        # save_transactions automatically handles deduplication so we must bypass it 
        # OR force insertion via simple cursor if we want to test duplicate detection report
        cursor = db_connection.cursor()
        duplicates = [
            ('2024-01-15', 'SAME TRANSACTION', -50.00),
            ('2024-01-15', 'SAME TRANSACTION', -50.00),
            ('2024-01-15', 'SAME TRANSACTION', -50.00),
        ]
        cursor.executemany("""
            INSERT INTO transactions (date, label, amount)
            VALUES (?, ?, ?)
        """, duplicates)
        db_connection.commit()
        
        # Step 2: Detect duplicates
        duplicates_df = get_duplicates_report()
        
        # Should find the duplicate pair
        assert not duplicates_df.empty
