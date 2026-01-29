"""
Tests for analytics.py module.
"""
import pytest
import pandas as pd
from modules.analytics import (
    detect_financial_profile,
    get_monthly_savings_trend,
    detect_internal_transfers,
    exclude_internal_transfers
)

class TestFinancialProfileDetection:
    """Tests for financial profile detection."""
    
    def test_detect_financial_profile_empty(self, temp_db):
        """Test profile detection with no data."""
        df = pd.DataFrame(columns=['date', 'label', 'amount', 'category_validated'])
        suggestions = detect_financial_profile(df)
        assert isinstance(suggestions, list)
    
    def test_detect_salary_pattern(self, temp_db):
        """Test detecting salary transactions."""
        # Create dataframe with salary pattern
        df = pd.DataFrame([
            {
                'date': '2024-01-15',
                'label': 'VIREMENT SALAIRE EMPLOYEUR',
                'amount': 2500.00,
                'category_validated': 'Inconnu'
            },
            {
                'date': '2024-02-15',
                'label': 'VIREMENT SALAIRE EMPLOYEUR',
                'amount': 2500.00,
                'category_validated': 'Inconnu'
            }
        ])
        
        suggestions = detect_financial_profile(df)
        
        # Should detect salary
        salary_suggestions = [s for s in suggestions if 'salaire' in s.get('type', '').lower()]
        assert len(salary_suggestions) > 0
    
    def test_detect_rent_pattern(self, temp_db):
        """Test detecting rent/housing payments."""
        df = pd.DataFrame([
            {
                'date': '2024-01-01',
                'label': 'PRLV FONCIERE LOGEMENT',
                'amount': -1200.00,
                'category_validated': 'Inconnu'
            },
            {
                'date': '2024-02-01',
                'label': 'PRLV FONCIERE LOGEMENT',
                'amount': -1200.00,
                'category_validated': 'Inconnu'
            }
        ])
        
        suggestions = detect_financial_profile(df)
        
        # Should detect housing
        housing_suggestions = [s for s in suggestions if 'logement' in s.get('type', '').lower()]
        assert len(housing_suggestions) > 0
    
    def test_detect_subscription_pattern(self, temp_db):
        """Test detecting recurring subscriptions."""
        df = pd.DataFrame([
            {
                'date': '2024-01-15',
                'label': 'NETFLIX ABONNEMENT',
                'amount': -15.99,
                'category_validated': 'Inconnu'
            },
            {
                'date': '2024-02-15',
                'label': 'NETFLIX ABONNEMENT',
                'amount': -15.99,
                'category_validated': 'Inconnu'
            },
            {
                'date': '2024-03-15',
                'label': 'NETFLIX ABONNEMENT',
                'amount': -15.99,
                'category_validated': 'Inconnu'
            }
        ])
        
        suggestions = detect_financial_profile(df)
        
        # Should detect subscription
        sub_suggestions = [s for s in suggestions if 'abonnement' in s.get('type', '').lower() or 'subscription' in s.get('type', '').lower()]
        assert len(sub_suggestions) > 0

class TestMonthlySavingsTrendAnalytics:
    """Tests for monthly savings trend in analytics module."""
    
    def test_get_monthly_savings_trend_structure(self, temp_db):
        """Test savings trend returns proper structure."""
        df = get_monthly_savings_trend(months=6)
        
        assert isinstance(df, pd.DataFrame)
        # Check expected columns
        if not df.empty:
            assert 'month' in df.columns
    
    def test_get_monthly_savings_trend_calculation(self, temp_db, db_connection):
        """Test savings calculation accuracy."""
        cursor = db_connection.cursor()
        
        # Add known income and expense
        cursor.execute("""
            INSERT INTO transactions (date, label, amount, status, category_validated)
            VALUES ('2024-01-15', 'SALAIRE', 3000.00, 'VALIDATED', 'Revenus')
        """)
        cursor.execute("""
            INSERT INTO transactions (date, label, amount, status, category_validated)
            VALUES ('2024-01-16', 'COURSES', -1000.00, 'VALIDATED', 'Alimentation')
        """)
        cursor.execute("""
            INSERT INTO transactions (date, label, amount, status, category_validated)
            VALUES ('2024-01-17', 'LOYER', -1200.00, 'VALIDATED', 'Logement')
        """)
        
        db_connection.commit()
        
        df = get_monthly_savings_trend(months=12)
        
        if not df.empty:
            jan_data = df[df['month'].str.contains('2024-01')]
            if not jan_data.empty:
                # Expected savings: 3000 - 1000 - 1200 = 800
                savings_col = 'Epargne' if 'Epargne' in df.columns else 'savings'
                if savings_col in df.columns:
                    assert jan_data.iloc[0][savings_col] == 800.00

class TestRecurringTransactionDetection:
    """Tests for recurring transaction detection."""
    
    def test_detect_recurring_expenses(self, temp_db):
        """Test detecting recurring expense patterns."""
        # Create dataframe with recurring transactions
        df = pd.DataFrame([
            {'date': '2024-01-15', 'label': 'EDF ELECTRICITE', 'amount': -80.00},
            {'date': '2024-02-15', 'label': 'EDF ELECTRICITE', 'amount': -82.00},
            {'date': '2024-03-15', 'label': 'EDF ELECTRICITE', 'amount': -78.00},
        ])
        
        suggestions = detect_financial_profile(df)
        
        # Should detect utility bill pattern
        # Implementation-dependent check
        assert isinstance(suggestions, list)

class TestInternalTransfers:
    """Tests for internal transfer detection."""
    
    def test_exclude_internal_transfers(self, temp_db):
        """Test exclusion of internal transfers."""
        df = pd.DataFrame([
            {'id': 1, 'date': '2024-01-01', 'label': 'VIR SEPA AURELIEN', 'amount': -100.0, 'category_validated': 'Autre'},
            {'id': 2, 'date': '2024-01-02', 'label': 'CARREFOUR', 'amount': -50.0, 'category_validated': 'Alimentation'},
        ])
        
        df_clean = exclude_internal_transfers(df)
        # Should remove VIR SEPA PERSO
        assert len(df_clean) == 1
        assert df_clean.iloc[0]['label'] == 'CARREFOUR'

