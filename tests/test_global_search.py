# -*- coding: utf-8 -*-
"""
Tests for the global search module.
"""
import pytest
import pandas as pd
from datetime import date, datetime
from unittest.mock import patch, MagicMock


class TestGlobalSearchBasic:
    """Test suite for GlobalSearch basic functionality."""
    
    @pytest.fixture
    def search_instance(self):
        """Create GlobalSearch instance with mocked session state."""
        with patch('modules.ui.global_search.st') as mock_st:
            mock_st.session_state = {}
            from modules.ui.global_search import GlobalSearch
            return GlobalSearch()
    
    def test_init_session_state(self, search_instance):
        """Test that session state is initialized correctly."""
        # Vérifier que l'initialisation ne plante pas
        assert search_instance is not None
    
    def test_search_transactions_empty_query(self, search_instance):
        """Test search with empty query returns empty DataFrame."""
        result = search_instance.search_transactions("")
        assert isinstance(result, pd.DataFrame)
        assert result.empty
    
    def test_search_transactions_short_query(self, search_instance):
        """Test search with short query (< 2 chars) returns empty DataFrame."""
        result = search_instance.search_transactions("a")
        assert isinstance(result, pd.DataFrame)
        assert result.empty
    
    def test_search_transactions_no_data(self, search_instance):
        """Test search when no transactions in database."""
        with patch('modules.ui.global_search.get_all_transactions', return_value=pd.DataFrame()):
            result = search_instance.search_transactions("test")
            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestGlobalSearchWithData:
    """Test suite for GlobalSearch with sample data."""
    
    @pytest.fixture
    def sample_df(self):
        """Create sample transaction DataFrame."""
        return pd.DataFrame({
            'id': [1, 2, 3, 4],
            'date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18'],
            'label': ['CARREFOUR MARKET', 'SALAIRE JANVIER', 'TOTAL STATION', 'NETFLIX'],
            'amount': [-45.50, 2500.00, -60.00, -12.99],
            'category_validated': ['Alimentation', 'Revenus', 'Transport', 'Loisirs'],
            'category_predicted': ['Alimentation', 'Revenus', 'Transport', 'Loisirs'],
            'member': ['Maison', 'Maison', 'Maison', 'Alice'],
            'tags': ['courses', 'salaire', 'essence', 'streaming']
        })
    
    @pytest.fixture
    def search_instance(self):
        """Create GlobalSearch instance."""
        with patch('modules.ui.global_search.st') as mock_st:
            mock_st.session_state = {}
            from modules.ui.global_search import GlobalSearch
            return GlobalSearch()
    
    def test_search_by_label(self, search_instance, sample_df):
        """Test searching by transaction label."""
        with patch('modules.ui.global_search.get_all_transactions', return_value=sample_df):
            result = search_instance.search_transactions("CARREFOUR")
            assert len(result) == 1
            assert result.iloc[0]['label'] == 'CARREFOUR MARKET'
    
    def test_search_by_category(self, search_instance, sample_df):
        """Test searching by category."""
        with patch('modules.ui.global_search.get_all_transactions', return_value=sample_df):
            result = search_instance.search_transactions("Alimentation")
            assert len(result) >= 1
            assert 'Alimentation' in result['category_validated'].values
    
    def test_search_by_amount_exact(self, search_instance, sample_df):
        """Test searching by exact amount."""
        with patch('modules.ui.global_search.get_all_transactions', return_value=sample_df):
            result = search_instance.search_transactions("-45.50")
            assert len(result) == 1
            assert result.iloc[0]['amount'] == -45.50
    
    def test_search_by_amount_integer(self, search_instance, sample_df):
        """Test searching by integer amount."""
        with patch('modules.ui.global_search.get_all_transactions', return_value=sample_df):
            result = search_instance.search_transactions("2500")
            assert len(result) == 1
            assert result.iloc[0]['amount'] == 2500.00
    
    def test_search_by_member(self, search_instance, sample_df):
        """Test searching by member name."""
        with patch('modules.ui.global_search.get_all_transactions', return_value=sample_df):
            result = search_instance.search_transactions("Alice")
            assert len(result) == 1
            assert result.iloc[0]['member'] == 'Alice'
    
    def test_search_case_insensitive(self, search_instance, sample_df):
        """Test search is case insensitive."""
        with patch('modules.ui.global_search.get_all_transactions', return_value=sample_df):
            result_lower = search_instance.search_transactions("carrefour")
            result_upper = search_instance.search_transactions("CARREFOUR")
            assert len(result_lower) == len(result_upper)
    
    def test_search_limit(self, search_instance, sample_df):
        """Test search respects limit parameter."""
        with patch('modules.ui.global_search.get_all_transactions', return_value=sample_df):
            result = search_instance.search_transactions("a", limit=2)  # 'a' matches multiple
            assert len(result) <= 2
    
    def test_search_no_results(self, search_instance, sample_df):
        """Test search with no matching results."""
        with patch('modules.ui.global_search.get_all_transactions', return_value=sample_df):
            result = search_instance.search_transactions("XYZ123NONEXISTENT")
            assert result.empty


class TestGlobalSearchCategories:
    """Test suite for category search."""
    
    @pytest.fixture
    def search_instance(self):
        """Create GlobalSearch instance."""
        with patch('modules.ui.global_search.st') as mock_st:
            mock_st.session_state = {}
            from modules.ui.global_search import GlobalSearch
            return GlobalSearch()
    
    def test_search_categories_empty_query(self, search_instance):
        """Test category search with empty query."""
        result = search_instance.search_categories("")
        assert result == []
    
    def test_search_categories_with_data(self, search_instance):
        """Test category search returns results."""
        mock_categories = {
            'Alimentation': '🛒',
            'Transport': '🚗',
            'Loisirs': '🎮'
        }
        with patch('modules.ui.global_search.get_categories_with_emojis', return_value=mock_categories):
            result = search_instance.search_categories("Ali")
            assert len(result) == 1
            assert result[0]['name'] == 'Alimentation'
    
    def test_search_categories_case_insensitive(self, search_instance):
        """Test category search is case insensitive."""
        mock_categories = {'Alimentation': '🛒'}
        with patch('modules.ui.global_search.get_categories_with_emojis', return_value=mock_categories):
            result_lower = search_instance.search_categories("ali")
            result_upper = search_instance.search_categories("ALI")
            assert len(result_lower) == len(result_upper)
    
    def test_search_categories_limit(self, search_instance):
        """Test category search respects limit."""
        mock_categories = {
            f'Category{i}': '🏷️' for i in range(10)
        }
        with patch('modules.ui.global_search.get_categories_with_emojis', return_value=mock_categories):
            result = search_instance.search_categories("Category")
            assert len(result) <= 5  # Limite par défaut


class TestGlobalSearchFormat:
    """Test suite for result formatting."""
    
    @pytest.fixture
    def search_instance(self):
        """Create GlobalSearch instance."""
        with patch('modules.ui.global_search.st') as mock_st:
            mock_st.session_state = {}
            from modules.ui.global_search import GlobalSearch
            return GlobalSearch()
    
    def test_format_transaction_result_positive(self, search_instance):
        """Test formatting positive amount transaction."""
        row = pd.Series({
            'date': '2024-01-15',
            'label': 'SALAIRE',
            'amount': 2500.00,
            'category_validated': 'Revenus'
        })
        result = search_instance.format_transaction_result(row)
        assert '📅' in result
        assert 'SALAIRE' in result
        assert 'green' in result.lower()
    
    def test_format_transaction_result_negative(self, search_instance):
        """Test formatting negative amount transaction."""
        row = pd.Series({
            'date': '2024-01-15',
            'label': 'CARREFOUR',
            'amount': -45.50,
            'category_validated': 'Alimentation'
        })
        result = search_instance.format_transaction_result(row)
        assert '📅' in result
        assert 'CARREFOUR' in result
        assert 'red' in result.lower()
    
    def test_format_transaction_result_long_label(self, search_instance):
        """Test formatting truncates long labels."""
        row = pd.Series({
            'date': '2024-01-15',
            'label': 'A' * 100,
            'amount': -10.00,
            'category_validated': 'Test'
        })
        result = search_instance.format_transaction_result(row)
        assert '...' in result


class TestGlobalSearchIntegration:
    """Integration tests with real database."""
    
    def test_search_with_real_transactions(self, temp_db, sample_transactions):
        """Test search with actual database transactions."""
        from modules.ui.global_search import GlobalSearch
        from modules.db.transactions import save_transactions
        import pandas as pd
        
        # Sauvegarder des transactions
        df = pd.DataFrame(sample_transactions)
        save_transactions(df)
        
        with patch('modules.ui.global_search.st') as mock_st:
            mock_st.session_state = {}
            search = GlobalSearch()
            
            # Rechercher
            result = search.search_transactions("CARREFOUR")
            assert isinstance(result, pd.DataFrame)


class TestGlobalSearchEdgeCases:
    """Test suite for edge cases and error handling."""
    
    @pytest.fixture
    def search_instance(self):
        """Create GlobalSearch instance."""
        with patch('modules.ui.global_search.st') as mock_st:
            mock_st.session_state = {}
            from modules.ui.global_search import GlobalSearch
            return GlobalSearch()
    
    def test_search_with_special_characters(self, search_instance):
        """Test search handles special characters gracefully."""
        df = pd.DataFrame({
            'id': [1],
            'date': ['2024-01-15'],
            'label': ['Test [Special] (Chars)'],
            'amount': [-10.00],
            'category_validated': ['Test']
        })
        with patch('modules.ui.global_search.get_all_transactions', return_value=df):
            result = search_instance.search_transactions("[Special]")
            # Ne devrait pas planter
            assert isinstance(result, pd.DataFrame)
    
    def test_search_with_invalid_amount(self, search_instance):
        """Test search handles invalid amount strings."""
        df = pd.DataFrame({
            'id': [1],
            'date': ['2024-01-15'],
            'label': ['Test'],
            'amount': [-10.00],
            'category_validated': ['Test']
        })
        with patch('modules.ui.global_search.get_all_transactions', return_value=df):
            # "abc" n'est pas un montant valide, mais ne doit pas planter
            result = search_instance.search_transactions("abc")
            assert isinstance(result, pd.DataFrame)
    
    def test_search_database_error(self, search_instance):
        """Test search handles database errors gracefully."""
        with patch('modules.ui.global_search.get_all_transactions', side_effect=Exception("DB Error")):
            result = search_instance.search_transactions("test")
            assert isinstance(result, pd.DataFrame)
            assert result.empty
