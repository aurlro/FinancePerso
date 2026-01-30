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


class TestImportWorkflowComplete:
    """Test complete import workflow with all features."""

    def test_import_csv_with_duplicate_detection(self, temp_db, db_connection):
        """Test full CSV import workflow with duplicate detection."""
        # Step 1: First import batch
        df1 = pd.DataFrame([
            {'date': '2024-01-15', 'label': 'COURSES CARREFOUR', 'amount': -85.50, 'status': 'pending'},
            {'date': '2024-01-16', 'label': 'TOTAL ESSENCE', 'amount': -55.00, 'status': 'pending'},
            {'date': '2024-01-17', 'label': 'AMAZON ACHAT', 'amount': -42.30, 'status': 'pending'}
        ])
        new_count1, skipped1 = save_transactions(df1)
        assert new_count1 == 3
        assert skipped1 == 0

        # Step 2: Second import with duplicates
        df2 = pd.DataFrame([
            {'date': '2024-01-15', 'label': 'COURSES CARREFOUR', 'amount': -85.50, 'status': 'pending'},  # Duplicate
            {'date': '2024-01-16', 'label': 'TOTAL ESSENCE', 'amount': -55.00, 'status': 'pending'},  # Duplicate
            {'date': '2024-01-18', 'label': 'NOUVEAU ACHAT', 'amount': -30.00, 'status': 'pending'}  # New
        ])
        new_count2, skipped2 = save_transactions(df2)

        # Verify duplicate detection
        assert skipped2 == 2  # Two duplicates detected
        assert new_count2 == 1  # One new transaction

        # Verify total count in DB
        df_all = get_all_transactions()
        assert len(df_all) == 4  # 3 from first import + 1 new from second

    def test_import_with_period_filter(self, temp_db, db_connection):
        """Test import workflow with year/month filtering."""
        # Import transactions from different months
        df = pd.DataFrame([
            {'date': '2024-01-15', 'label': 'JAN TX', 'amount': -50.00},
            {'date': '2024-02-15', 'label': 'FEB TX', 'amount': -60.00},
            {'date': '2024-03-15', 'label': 'MAR TX', 'amount': -70.00}
        ])
        save_transactions(df)

        # Filter by month (simulate UI behavior)
        df_all = get_all_transactions()
        df_all['date_dt'] = pd.to_datetime(df_all['date'])
        df_jan = df_all[df_all['date_dt'].dt.month == 1]
        df_feb = df_all[df_all['date_dt'].dt.month == 2]

        assert len(df_jan) == 1
        assert len(df_feb) == 1
        assert df_jan.iloc[0]['label'] == 'JAN TX'
        assert df_feb.iloc[0]['label'] == 'FEB TX'

    def test_import_with_account_attribution(self, temp_db, db_connection):
        """Test import with account label assignment."""
        # Import to different accounts
        df1 = pd.DataFrame([
            {'date': '2024-01-15', 'label': 'TX COMPTE 1', 'amount': -50.00, 'account_label': 'Compte Principal'}
        ])
        df2 = pd.DataFrame([
            {'date': '2024-01-16', 'label': 'TX COMPTE 2', 'amount': -60.00, 'account_label': 'Livret A'}
        ])

        save_transactions(df1)
        save_transactions(df2)

        # Verify account attribution
        df_all = get_all_transactions()
        assert df_all[df_all['label'] == 'TX COMPTE 1'].iloc[0]['account_label'] == 'Compte Principal'
        assert df_all[df_all['label'] == 'TX COMPTE 2'].iloc[0]['account_label'] == 'Livret A'


class TestOptimizationsWorkflow:
    """Test critical optimizations: compiled rules and batch operations."""

    def test_compiled_rules_performance(self, temp_db, db_connection):
        """Test that compiled rules cache works correctly."""
        from modules.db.rules import get_compiled_learning_rules
        from modules.cache_manager import invalidate_rule_caches

        # Step 1: Add multiple rules
        patterns = [
            ('CARREFOUR', 'Alimentation', 5),
            ('TOTAL', 'Transport', 5),
            ('AMAZON', 'Shopping', 5),
            ('SNCF', 'Transport', 5),
            ('UBER', 'Transport', 3)
        ]
        for pattern, category, priority in patterns:
            add_learning_rule(pattern, category, priority=priority)

        # Step 2: Get compiled rules (should cache)
        compiled_rules = get_compiled_learning_rules()
        assert len(compiled_rules) == 5

        # Verify all patterns are compiled
        for pattern_compiled, category, priority, pattern_str in compiled_rules:
            assert pattern_compiled is not None  # Should be compiled re.Pattern

        # Step 3: Verify cache works (second call should be instant)
        compiled_rules_2 = get_compiled_learning_rules()
        assert compiled_rules == compiled_rules_2  # Same data

        # Step 4: Add new rule and invalidate cache
        add_learning_rule('NETFLIX', 'Loisirs', priority=5)
        invalidate_rule_caches()

        # Step 5: Verify cache was invalidated
        compiled_rules_3 = get_compiled_learning_rules()
        assert len(compiled_rules_3) == 6  # New rule included

    def test_batch_operations_with_large_dataset(self, temp_db, db_connection):
        """Test batch insert optimization with many transactions."""
        # Create a large dataset (100 transactions)
        transactions = []
        for i in range(100):
            transactions.append({
                'date': f'2024-01-{(i % 28) + 1:02d}',
                'label': f'TRANSACTION {i}',
                'amount': -50.0 - (i % 50),
                'status': 'pending'
            })

        df = pd.DataFrame(transactions)

        # Import should use batch operations
        import time
        start = time.time()
        new_count, skipped = save_transactions(df)
        elapsed = time.time() - start

        # Verify all inserted
        assert new_count == 100
        assert skipped == 0

        # Performance check: should complete in reasonable time (< 2s)
        assert elapsed < 2.0, f"Batch import took {elapsed:.2f}s, expected < 2s"

        # Verify in DB
        df_all = get_all_transactions()
        assert len(df_all) == 100

    def test_categorization_with_compiled_rules(self, temp_db, db_connection):
        """Test that categorization uses compiled rules efficiently."""
        # Step 1: Add rules
        add_learning_rule('CARREFOUR', 'Alimentation', priority=5)
        add_learning_rule('AMAZON', 'Shopping', priority=5)

        # Step 2: Import many transactions
        transactions = []
        for i in range(50):
            label = 'CARREFOUR MARKET' if i % 2 == 0 else 'AMAZON.FR ACHAT'
            transactions.append({
                'date': f'2024-01-{(i % 28) + 1:02d}',
                'label': label,
                'amount': -50.0,
                'status': 'pending',
                'category_validated': 'Inconnu'
            })

        df = pd.DataFrame(transactions)
        save_transactions(df)

        # Step 3: Apply rules (should use compiled patterns)
        import time
        start = time.time()
        count = apply_rules_to_pending()
        elapsed = time.time() - start

        # Verify all categorized
        assert count == 50

        # Performance check: compiled rules should be fast (< 1s for 50 tx)
        assert elapsed < 1.0, f"Categorization took {elapsed:.2f}s, expected < 1s"

        # Verify categories
        cursor = db_connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE category_validated = 'Alimentation'")
        ali_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE category_validated = 'Shopping'")
        shop_count = cursor.fetchone()[0]

        assert ali_count == 25  # Half are CARREFOUR
        assert shop_count == 25  # Half are AMAZON


class TestValidationWorkflowAdvanced:
    """Test advanced validation features: bulk, undo, tags."""

    def test_validation_category_update(self, temp_db, db_connection):
        """Test category update during validation."""
        # Step 1: Import transaction
        df = pd.DataFrame([
            {'date': '2024-01-15', 'label': 'TEST TX', 'amount': -50.00, 'status': 'pending', 'category_validated': 'Inconnu'}
        ])
        save_transactions(df)

        df_all = get_all_transactions()
        tx_id = int(df_all.iloc[0]['id'])

        # Step 2: Validate and update category
        update_transaction_category(tx_id, 'Alimentation')

        # Verify update
        cursor = db_connection.cursor()
        cursor.execute("SELECT category_validated FROM transactions WHERE id = ?", (tx_id,))
        assert cursor.fetchone()[0] == 'Alimentation'

        # Step 3: Update again
        update_transaction_category(tx_id, 'Transport')

        # Verify second update
        cursor.execute("SELECT category_validated FROM transactions WHERE id = ?", (tx_id,))
        assert cursor.fetchone()[0] == 'Transport'

    def test_bulk_validation_with_member_and_tags(self, temp_db, db_connection):
        """Test bulk validation with member and tag assignment."""
        # Step 1: Add member
        add_member('Alice', 'HOUSEHOLD')

        # Step 2: Import multiple transactions
        df = pd.DataFrame([
            {'date': '2024-01-15', 'label': 'ACHAT 1', 'amount': -50.00, 'status': 'pending'},
            {'date': '2024-01-16', 'label': 'ACHAT 2', 'amount': -60.00, 'status': 'pending'},
            {'date': '2024-01-17', 'label': 'ACHAT 3', 'amount': -70.00, 'status': 'pending'}
        ])
        save_transactions(df)

        df_all = get_all_transactions()
        tx_ids = [int(x) for x in df_all['id'].tolist()]

        # Step 3: Bulk update with category, tags, and beneficiary
        bulk_update_transaction_status(tx_ids, 'Shopping', tags='Online,Urgent', beneficiary='Alice')

        # Step 4: Verify all updates
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT category_validated, tags, beneficiary, status
            FROM transactions
            WHERE id IN (?, ?, ?)
        """, tuple(tx_ids))

        for row in cursor.fetchall():
            category, tags, benef, status = row
            assert category == 'Shopping'
            assert 'online' in tags.lower()  # Tags normalized
            assert 'urgent' in tags.lower()
            assert benef == 'Alice'
            assert status == 'validated'

    def test_transaction_grouping_behavior(self, temp_db, db_connection):
        """Test that similar transactions can be identified for grouping."""
        # Step 1: Import similar transactions (would group)
        df = pd.DataFrame([
            {'date': '2024-01-15', 'label': 'RECURRING PAYMENT', 'amount': -50.00},
            {'date': '2024-01-16', 'label': 'RECURRING PAYMENT', 'amount': -50.00},
            {'date': '2024-01-17', 'label': 'RECURRING PAYMENT', 'amount': -50.00}
        ])
        save_transactions(df)

        df_all = get_all_transactions()
        assert len(df_all) == 3

        # All should have same label (for grouping)
        assert df_all['label'].nunique() == 1

        # Verify they can be grouped by label/amount
        grouped = df_all.groupby(['label', 'amount']).size()
        assert len(grouped) == 1
        assert grouped.iloc[0] == 3


class TestAnalyticsWorkflow:
    """Test analytics features: recurring, anomalies, trends."""

    def test_recurring_payment_detection(self, temp_db, db_connection):
        """Test detecting recurring payments."""
        from modules.analytics import detect_recurring_payments

        # Create recurring pattern (monthly)
        today = date.today()
        transactions = []
        for i in range(6):  # 6 months
            tx_date = today - timedelta(days=30 * i)
            transactions.append({
                'date': tx_date.strftime('%Y-%m-%d'),
                'label': 'NETFLIX SUBSCRIPTION',
                'amount': -12.99,
                'status': 'validated',
                'category_validated': 'Loisirs'
            })

        df = pd.DataFrame(transactions)
        save_transactions(df)

        # Detect recurring
        df_all = get_all_transactions()
        recurring_df = detect_recurring_payments(df_all)

        # Should find Netflix
        assert not recurring_df.empty
        netflix_row = recurring_df[recurring_df['label'].str.contains('NETFLIX', case=False)]
        assert not netflix_row.empty
        assert netflix_row.iloc[0]['frequency_label'] in ['Mensuel', 'Régulier']

    def test_anomaly_detection_workflow(self, temp_db, db_connection):
        """Test amount anomaly detection."""
        from modules.ai import detect_amount_anomalies

        # Create normal pattern + anomaly
        transactions = []
        for i in range(10):
            transactions.append({
                'date': f'2024-01-{i+1:02d}',
                'label': 'Carrefour Courses',
                'amount': -50.0,  # Normal
                'status': 'validated',
                'category_validated': 'Alimentation'
            })

        # Add anomaly
        transactions.append({
            'date': '2024-01-15',
            'label': 'CARREFOUR COURSES',
            'amount': -500.0,  # 10x normal!
            'status': 'validated',
            'category_validated': 'Alimentation'
        })

        df = pd.DataFrame(transactions)
        save_transactions(df)

        df_all = get_all_transactions()
        anomalies = detect_amount_anomalies(df_all)

        # Should detect the anomaly
        assert len(anomalies) > 0
        anom = anomalies[0]
        assert 'carrefour' in anom['label'].lower()
        assert anom.get('severity') in ['high', 'medium']


class TestConfigurationWorkflow:
    """Test configuration features: members, categories, merging."""

    def test_category_merge_workflow(self, temp_db, db_connection):
        """Test merging two categories."""
        from modules.db.categories import merge_categories

        # Step 1: Create transactions with old categories
        df = pd.DataFrame([
            {'date': '2024-01-15', 'label': 'TX 1', 'amount': -50.00, 'category_validated': 'Shopping'},
            {'date': '2024-01-16', 'label': 'TX 2', 'amount': -60.00, 'category_validated': 'Achats'}
        ])
        save_transactions(df)

        # Step 2: Merge 'Achats' into 'Shopping'
        merge_categories('Achats', 'Shopping')

        # Step 3: Verify all transactions now use 'Shopping'
        cursor = db_connection.cursor()
        cursor.execute("SELECT category_validated FROM transactions")
        categories = [row[0] for row in cursor.fetchall()]

        assert 'Achats' not in categories
        assert all(cat == 'Shopping' for cat in categories)

    def test_card_suffix_preservation(self, temp_db, db_connection):
        """Test that card_suffix is preserved during import."""
        from modules.db.members import add_member

        # Step 1: Add member
        add_member('Alice', 'HOUSEHOLD')

        # Step 2: Import transaction with card_suffix
        df = pd.DataFrame([
            {'date': '2024-01-15', 'label': 'ACHAT CB', 'amount': -50.00, 'card_suffix': '4242'}
        ])
        save_transactions(df)

        # Step 3: Verify card_suffix is preserved
        df_all = get_all_transactions()
        assert len(df_all) == 1
        assert df_all.iloc[0]['card_suffix'] == '4242'

    def test_category_usage_tracking(self, temp_db, db_connection):
        """Test that category usage can be tracked."""
        from modules.db.categories import get_categories

        # Step 1: Add transactions with different categories
        df = pd.DataFrame([
            {'date': '2024-01-15', 'label': 'TX 1', 'amount': -50.00, 'category_validated': 'Alimentation'},
            {'date': '2024-01-16', 'label': 'TX 2', 'amount': -60.00, 'category_validated': 'Transport'}
        ])
        save_transactions(df)

        # Step 2: Verify categories exist
        categories = get_categories()
        assert 'Alimentation' in categories
        assert 'Transport' in categories

        # Step 3: Count usage per category
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT category_validated, COUNT(*) as count
            FROM transactions
            GROUP BY category_validated
            ORDER BY count DESC
        """)
        usage = dict(cursor.fetchall())
        assert usage['Alimentation'] == 1
        assert usage['Transport'] == 1

    def test_orphan_member_cleanup(self, temp_db, db_connection):
        """Test detecting and fixing orphan member names."""
        from modules.db.members import get_orphan_labels, add_member, rename_member

        # Step 1: Add transaction with typo in member name
        df = pd.DataFrame([
            {'date': '2024-01-15', 'label': 'TX 1', 'amount': -50.00, 'member': 'Alic'},  # Typo
            {'date': '2024-01-16', 'label': 'TX 2', 'amount': -60.00, 'member': 'Alice'}  # Correct
        ])
        save_transactions(df)

        # Step 2: Add official member
        add_member('Alice', 'HOUSEHOLD')

        # Step 3: Detect orphans
        orphans = get_orphan_labels()
        assert 'Alic' in orphans  # Typo is orphan

        # Step 4: Fix by renaming transactions
        rename_member('Alic', 'Alice')

        # Step 5: Verify fixed
        orphans_after = get_orphan_labels()
        assert 'Alic' not in orphans_after

        cursor = db_connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE member = 'Alice'")
        assert cursor.fetchone()[0] == 2  # Both transactions now use 'Alice'


class TestRuleManagementWorkflow:
    """Test rule management: audit, conflicts, validation."""

    def test_rule_conflict_detection(self, temp_db, db_connection):
        """Test detecting conflicting rules (same pattern, different categories)."""
        from modules.ai.rules_auditor import analyze_rules_integrity

        # Step 1: Add conflicting rules
        add_learning_rule('AMAZON', 'Shopping', priority=5)
        add_learning_rule('AMAZON', 'Loisirs', priority=5)  # Conflict!

        # Step 2: Analyze
        df_rules = get_learning_rules()
        issues = analyze_rules_integrity(df_rules)

        # Should detect conflict
        assert len(issues['conflicts']) > 0
        conflict = issues['conflicts'][0]
        # Pattern might be normalized to lowercase
        assert 'amazon' in conflict['pattern'].lower()
        assert any('Shopping' in cat or 'shopping' in cat.lower() for cat in conflict['categories'])
        assert any('Loisirs' in cat or 'loisirs' in cat.lower() for cat in conflict['categories'])

    def test_rule_duplicate_detection(self, temp_db, db_connection):
        """Test detecting duplicate rules (same pattern, same category)."""
        from modules.ai.rules_auditor import analyze_rules_integrity

        # Step 1: Add duplicate rules
        add_learning_rule('CARREFOUR', 'Alimentation', priority=5)
        add_learning_rule('CARREFOUR', 'Alimentation', priority=5)  # Exact duplicate

        # Step 2: Analyze
        df_rules = get_learning_rules()
        issues = analyze_rules_integrity(df_rules)

        # Should detect duplicates or conflicts
        assert len(issues['duplicates']) > 0 or len(issues['conflicts']) > 0

    def test_invalid_regex_pattern_handling(self, temp_db, db_connection):
        """Test handling of invalid regex patterns."""
        from modules.db.rules import get_compiled_learning_rules

        # Step 1: Add invalid regex pattern
        add_learning_rule('[INVALID(', 'TestCategory', priority=5)

        # Step 2: Get compiled rules
        compiled = get_compiled_learning_rules()

        # Should handle gracefully (None for invalid patterns)
        invalid_rule = [r for r in compiled if r[3] == '[INVALID(']
        assert len(invalid_rule) == 1
        assert invalid_rule[0][0] is None  # pattern_compiled should be None
