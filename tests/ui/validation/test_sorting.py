"""
Tests for UI validation sorting logic.
"""
import pytest
import pandas as pd
from modules.ui.validation.sorting import sort_groups, get_sort_options, SortStrategy


class TestSortGroups:
    """Tests for group sorting functionality."""
    
    @pytest.fixture
    def sample_group_stats(self):
        """Sample group statistics for testing."""
        return pd.DataFrame({
            'clean_group': ['GROUP_A', 'GROUP_B', 'GROUP_C', 'single_1'],
            'count': [5, 2, 10, 1],
            'max_date': ['2024-01-05', '2024-01-03', '2024-01-10', '2024-01-01'],
            'max_amount': [100.0, 50.0, 200.0, 25.0],
            'is_single': [0, 0, 0, 1]
        })
    
    def test_sort_by_count_descending(self, sample_group_stats):
        """Test sorting by count (largest groups first)."""
        result = sort_groups(sample_group_stats, SortStrategy.COUNT, max_groups=10)
        
        # Groups should come before singles
        assert 'GROUP_C' in result
        assert result[0] == 'GROUP_C'  # count=10
        assert result[1] == 'GROUP_A'  # count=5
        assert result[2] == 'GROUP_B'  # count=2
        assert result[3] == 'single_1'  # single last
    
    def test_sort_by_date_recent(self, sample_group_stats):
        """Test sorting by most recent date."""
        result = sort_groups(sample_group_stats, SortStrategy.DATE_RECENT, max_groups=10)
        
        # Most recent date first (groups before singles)
        non_singles = [g for g in result if not g.startswith('single_')]
        assert non_singles[0] == 'GROUP_C'  # 2024-01-10
    
    def test_sort_by_date_old(self, sample_group_stats):
        """Test sorting by oldest date."""
        result = sort_groups(sample_group_stats, SortStrategy.DATE_OLD, max_groups=10)
        
        # Oldest date first (groups before singles)
        non_singles = [g for g in result if not g.startswith('single_')]
        assert non_singles[0] == 'GROUP_B'  # 2024-01-03
    
    def test_sort_by_amount_descending(self, sample_group_stats):
        """Test sorting by largest amount."""
        result = sort_groups(sample_group_stats, SortStrategy.AMOUNT_DESC, max_groups=10)
        
        # Largest amount first
        non_singles = [g for g in result if not g.startswith('single_')]
        assert non_singles[0] == 'GROUP_C'  # 200.0
    
    def test_sort_by_amount_ascending(self, sample_group_stats):
        """Test sorting by smallest amount."""
        result = sort_groups(sample_group_stats, SortStrategy.AMOUNT_ASC, max_groups=10)
        
        # Smallest amount first
        non_singles = [g for g in result if not g.startswith('single_')]
        assert non_singles[0] == 'GROUP_B'  # 50.0
    
    def test_max_groups_limit(self, sample_group_stats):
        """Test that max_groups parameter limits results."""
        result = sort_groups(sample_group_stats, SortStrategy.COUNT, max_groups=2)
        
        assert len(result) == 2
        # Should return top 2 by count
        assert result[0] == 'GROUP_C'
        assert result[1] == 'GROUP_A'
    
    def test_singles_always_after_groups(self, sample_group_stats):
        """Test that single transactions always appear after groups."""
        result = sort_groups(sample_group_stats, SortStrategy.COUNT, max_groups=10)
        
        # Find index of first single
        single_idx = next(i for i, g in enumerate(result) if g.startswith('single_'))
        
        # All groups should come before singles
        for i in range(single_idx):
            assert not result[i].startswith('single_')
    
    def test_invalid_sort_key_defaults_to_count(self, sample_group_stats):
        """Test that invalid sort key defaults to COUNT."""
        result = sort_groups(sample_group_stats, "invalid_key", max_groups=10)
        
        # Should behave like COUNT sort
        assert result[0] == 'GROUP_C'


class TestGetSortOptions:
    """Tests for sort options helper."""
    
    def test_get_sort_options_returns_dict(self):
        """Test that get_sort_options returns a dictionary."""
        options = get_sort_options()
        
        assert isinstance(options, dict)
        assert len(options) == 5
    
    def test_sort_options_keys_are_user_friendly(self):
        """Test that keys are human-readable."""
        options = get_sort_options()
        
        assert "Gros groupes (Défaut)" in options
        assert "Plus récentes" in options
        assert "Plus anciennes" in options
    
    def test_sort_options_values_are_strategies(self):
        """Test that values are SortStrategy constants."""
        options = get_sort_options()
        
        assert options["Gros groupes (Défaut)"] == SortStrategy.COUNT
        assert options["Plus récentes"] == SortStrategy.DATE_RECENT
        assert options["Plus anciennes"] == SortStrategy.DATE_OLD
        assert options["Montant (Décroissant)"] == SortStrategy.AMOUNT_DESC
        assert options["Montant (Croissant)"] == SortStrategy.AMOUNT_ASC


class TestSortStrategy:
    """Tests for SortStrategy constants."""
    
    def test_strategy_constants_exist(self):
        """Test that all strategy constants are defined."""
        assert hasattr(SortStrategy, 'COUNT')
        assert hasattr(SortStrategy, 'DATE_RECENT')
        assert hasattr(SortStrategy, 'DATE_OLD')
        assert hasattr(SortStrategy, 'AMOUNT_DESC')
        assert hasattr(SortStrategy, 'AMOUNT_ASC')
    
    def test_strategy_constants_are_strings(self):
        """Test that strategy constants are strings."""
        assert isinstance(SortStrategy.COUNT, str)
        assert isinstance(SortStrategy.DATE_RECENT, str)
