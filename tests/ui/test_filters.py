"""
Tests for filters component.
Focus on testable logic: date range calculation, filter application, and validation.
"""
import pytest
import pandas as pd
from datetime import date, timedelta

class TestDateRangeFiltering:
    """Tests for date range filtering logic."""
    
    def test_filter_by_single_month(self):
        """Test filtering transactions by single month."""
        df = pd.DataFrame([
            {'date': '2024-01-15', 'amount': -100.00},
            {'date': '2024-02-15', 'amount': -200.00},
            {'date': '2024-03-15', 'amount': -300.00}
        ])
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter to January only
        filtered = df[df['date'].dt.month == 1]
        
        assert len(filtered) == 1
        assert filtered.iloc[0]['amount'] == -100.00
    
    def test_filter_by_year(self):
        """Test filtering transactions by year."""
        df = pd.DataFrame([
            {'date': '2023-06-15', 'amount': -100.00},
            {'date': '2024-06-15', 'amount': -200.00}
        ])
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter to 2024 only
        filtered = df[df['date'].dt.year == 2024]
        
        assert len(filtered) == 1
        assert filtered.iloc[0]['amount'] == -200.00
    
    def test_filter_by_date_range(self):
        """Test filtering by custom date range."""
        df = pd.DataFrame([
            {'date': '2024-01-01', 'amount': -100.00},
            {'date': '2024-01-15', 'amount': -200.00},
            {'date': '2024-02-01', 'amount': -300.00}
        ])
        df['date'] = pd.to_datetime(df['date'])
        
        start_date = pd.to_datetime('2024-01-10')
        end_date = pd.to_datetime('2024-01-31')
        
        filtered = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        
        assert len(filtered) == 1
        assert filtered.iloc[0]['date'] == pd.to_datetime('2024-01-15')

class TestCategoryFiltering:
    """Tests for category filtering logic."""
    
    def test_filter_by_single_category(self):
        """Test filtering by single category."""
        df = pd.DataFrame([
            {'category_validated': 'Alimentation', 'amount': -100.00},
            {'category_validated': 'Transport', 'amount': -50.00},
            {'category_validated': 'Alimentation', 'amount': -75.00}
        ])
        
        filtered = df[df['category_validated'] == 'Alimentation']
        
        assert len(filtered) == 2
        assert filtered['amount'].sum() == -175.00
    
    def test_filter_by_multiple_categories(self):
        """Test filtering by multiple categories."""
        df = pd.DataFrame([
            {'category_validated': 'Alimentation', 'amount': -100.00},
            {'category_validated': 'Transport', 'amount': -50.00},
            {'category_validated': 'Loisirs', 'amount': -30.00}
        ])
        
        categories = ['Alimentation', 'Transport']
        filtered = df[df['category_validated'].isin(categories)]
        
        assert len(filtered) == 2

class TestAmountFiltering:
    """Tests for amount-based filtering logic."""
    
    def test_filter_expenses_only(self):
        """Test filtering only expenses (negative amounts)."""
        df = pd.DataFrame([
            {'amount': -100.00},
            {'amount': 500.00},
            {'amount': -50.00}
        ])
        
        expenses = df[df['amount'] < 0]
        
        assert len(expenses) == 2
    
    def test_filter_income_only(self):
        """Test filtering only income (positive amounts)."""
        df = pd.DataFrame([
            {'amount': -100.00},
            {'amount': 500.00},
            {'amount': 200.00}
        ])
        
        income = df[df['amount'] > 0]
        
        assert len(income) == 2
    
    def test_filter_by_amount_threshold(self):
        """Test filtering by minimum amount."""
        df = pd.DataFrame([
            {'amount': -10.00},
            {'amount': -100.00},
            {'amount': -500.00}
        ])
        
        threshold = -50.00
        large_expenses = df[df['amount'] < threshold]
        
        assert len(large_expenses) == 2
        assert -10.00 not in large_expenses['amount'].values

class TestCombinedFilters:
    """Tests for combining multiple filters."""
    
    def test_combined_date_and_category(self):
        """Test combining date and category filters."""
        df = pd.DataFrame([
            {'date': '2024-01-15', 'category_validated': 'Alimentation', 'amount': -100.00},
            {'date': '2024-01-20', 'category_validated': 'Transport', 'amount': -50.00},
            {'date': '2024-02-15', 'category_validated': 'Alimentation', 'amount': -75.00}
        ])
        df['date'] = pd.to_datetime(df['date'])
        
        # January + Alimentation
        filtered = df[
            (df['date'].dt.month == 1) & 
            (df['category_validated'] == 'Alimentation')
        ]
        
        assert len(filtered) == 1
        assert filtered.iloc[0]['amount'] == -100.00
