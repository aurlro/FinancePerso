"""
Tests for category charts component.
Focus on testable logic: data preparation and aggregation.
"""
import pytest
import pandas as pd
from modules.ui.dashboard.category_charts import prepare_expense_dataframe

class TestPrepareExpenseDataframe:
    """Tests for expense dataframe preparation."""
    
    def test_prepare_expense_dataframe_basic(self):
        """Test basic expense dataframe preparation."""
        df = pd.DataFrame([
            {
                'amount': -100.00,
                'category_validated': 'Alimentation',
                'original_category': 'Food'
            },
            {
                'amount': -50.00,
                'category_validated': 'Transport',
                'original_category': 'Car'
            },
            {
                'amount': 500.00,  # Income, should be excluded
                'category_validated': 'Revenus',
                'original_category': 'Salary'
            }
        ])
        
        cat_emoji_map = {
            'Alimentation': '🛒',
            'Transport': '🚗',
            'Revenus': '💰'
        }
        
        df_exp = prepare_expense_dataframe(df, cat_emoji_map)
        
        # Should only have expenses (negative amounts)
        assert len(df_exp) == 2
        assert all(df_exp['amount'] > 0)  # Converted to positive
        
        # Check categories with emojis
        assert '🛒 Alimentation' in df_exp['Catégorie'].values
        assert '🚗 Transport' in df_exp['Catégorie'].values
    
    def test_prepare_expense_dataframe_uses_validated_category(self):
        """Test that validated category is preferred over original."""
        df = pd.DataFrame([
            {
                'amount': -100.00,
                'category_validated': 'Alimentation',
                'original_category': 'Inconnu'
            }
        ])
        
        cat_emoji_map = {'Alimentation': '🛒', 'Inconnu': '❓'}
        
        df_exp = prepare_expense_dataframe(df, cat_emoji_map)
        
        # Should use validated category
        assert '🛒 Alimentation' in df_exp['Catégorie'].values
        assert '❓ Inconnu' not in df_exp['Catégorie'].values
    
    def test_prepare_expense_dataframe_fallback_to_original(self):
        """Test fallback to original category when validated is 'Inconnu'."""
        df = pd.DataFrame([
            {
                'amount': -100.00,
                'category_validated': 'Inconnu',
                'original_category': 'Alimentation'
            }
        ])
        
        cat_emoji_map = {'Alimentation': '🛒', 'Inconnu': '❓'}
        
        df_exp = prepare_expense_dataframe(df, cat_emoji_map)
        
        # Should fallback to original category
        assert '🛒 Alimentation' in df_exp['Catégorie'].values
    
    def test_prepare_expense_dataframe_emoji_missing(self):
        """Test handling of categories without emojis."""
        df = pd.DataFrame([
            {
                'amount': -100.00,
                'category_validated': 'Unknown Category',
                'original_category': 'Unknown'
            }
        ])
        
        cat_emoji_map = {}  # No emojis
        
        df_exp = prepare_expense_dataframe(df, cat_emoji_map)
        
        # Should still work, maybe with default emoji
        assert len(df_exp) == 1
        assert 'Unknown Category' in df_exp['Catégorie'].values[0]

class TestCategoryAggregation:
    """Tests for category aggregation logic (implicit in prepare)."""
    
    def test_aggregation_by_category(self):
        """Test that same categories are aggregated."""
        df = pd.DataFrame([
            {'amount': -100.00, 'category_validated': 'Alimentation', 'original_category': 'Food'},
            {'amount': -50.00, 'category_validated': 'Alimentation', 'original_category': 'Food'},
            {'amount': -80.00, 'category_validated': 'Transport', 'original_category': 'Car'}
        ])
        
        cat_emoji_map = {'Alimentation': '🛒', 'Transport': '🚗'}
        
        df_exp = prepare_expense_dataframe(df, cat_emoji_map)
        
        # All three rows should be present (prepare doesn't aggregate, just transforms)
        assert len(df_exp) == 3
        
        # But if we aggregate manually
        grouped = df_exp.groupby('Catégorie')['amount'].sum()
        assert grouped['🛒 Alimentation'] == 150.00
        assert grouped['🚗 Transport'] == 80.00
