"""
Tests for UI validation grouping logic.
"""
import pytest
import pandas as pd
from modules.ui.validation.grouping import get_smart_groups, calculate_group_stats, get_group_transactions


class TestGetSmartGroups:
    """Tests for transaction grouping algorithm."""
    
    def test_basic_grouping(self):
        """Test that identical labels are grouped together."""
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'label': ['CARREFOUR CB*6759', 'CARREFOUR CB*6759', 'AUCHAN CB*1234'],
            'amount': [-50.0, -50.0, -30.0],
            'is_manually_ungrouped': [0, 0, 0]
        })
        
        result = get_smart_groups(df)
        
        assert 'clean_group' in result.columns
        
        # First two should be in same group
        group1 = result.iloc[0]['clean_group']
        group2 = result.iloc[1]['clean_group']
        group3 = result.iloc[2]['clean_group']
        
        assert group1 == group2
        assert group1 != group3
    
    def test_cheque_grouping_by_amount(self):
        """Test that cheques are grouped by label + amount."""
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'label': ['CHQ 12345', 'CHQ 12345', 'CHQ 67890'],
            'amount': [-100.0, -100.0, -200.0],
            'is_manually_ungrouped': [0, 0, 0]
        })
        
        result = get_smart_groups(df)
        
        # Same cheque number, same amount -> same group
        assert result.iloc[0]['clean_group'] == result.iloc[1]['clean_group']
        
        # Different cheque number OR different amount -> different group
        assert result.iloc[0]['clean_group'] != result.iloc[2]['clean_group']
    
    def test_manually_ungrouped_transactions(self):
        """Test that manually ungrouped transactions stay isolated."""
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'label': ['CARREFOUR CB*6759', 'CARREFOUR CB*6759', 'CARREFOUR CB*6759'],
            'amount': [-50.0, -50.0, -50.0],
            'is_manually_ungrouped': [0, 1, 0]
        })
        
        result = get_smart_groups(df)
        
        # Transaction 2 should be in single group
        assert result.iloc[1]['clean_group'].startswith('single_')
        
        # Transactions 1 and 3 should be grouped together
        assert result.iloc[0]['clean_group'] == result.iloc[2]['clean_group']
        assert not result.iloc[0]['clean_group'].startswith('single_')
    
    def test_excluded_ids_parameter(self):
        """Test that excluded IDs are kept as single groups."""
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'label': ['CARREFOUR CB*6759', 'CARREFOUR CB*6759', 'CARREFOUR CB*6759'],
            'amount': [-50.0, -50.0, -50.0],
            'is_manually_ungrouped': [0, 0, 0]
        })
        
        # Exclude transaction 2
        result = get_smart_groups(df, excluded_ids={2})
        
        # Transaction 2 should be single
        assert result.iloc[1]['clean_group'] == 'single_2'
        
        # Transactions 1 and 3 grouped
        assert result.iloc[0]['clean_group'] == result.iloc[2]['clean_group']


class TestCalculateGroupStats:
    """Tests for group statistics calculation."""
    
    def test_group_stats_calculation(self):
        """Test that group stats are calculated correctly."""
        df = pd.DataFrame({
            'id': [1, 2, 3, 4],
            'clean_group': ['GROUP_A', 'GROUP_A', 'GROUP_B', 'single_4'],
            'date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04'],
            'amount': [-50.0, -60.0, -30.0, -100.0]
        })
        
        stats = calculate_group_stats(df)
        
        # Check columns
        assert all(col in stats.columns for col in ['clean_group', 'count', 'max_date', 'max_amount', 'is_single'])
        
        # Check GROUP_A stats
        group_a = stats[stats['clean_group'] == 'GROUP_A'].iloc[0]
        assert group_a['count'] == 2
        assert group_a['max_date'] == '2024-01-02'
        assert group_a['max_amount'] == 60.0  # abs(max)
        assert group_a['is_single'] == 0
        
        # Check single transaction
        single = stats[stats['clean_group'] == 'single_4'].iloc[0]
        assert single['count'] == 1
        assert single['is_single'] == 1
    
    def test_max_amount_uses_absolute_values(self):
        """Test that max_amount uses absolute values."""
        df = pd.DataFrame({
            'id': [1, 2],
            'clean_group': ['GROUP_A', 'GROUP_A'],
            'date': ['2024-01-01', '2024-01-02'],
            'amount': [-100.0, 50.0]  # negative and positive
        })
        
        stats = calculate_group_stats(df)
        
        # Should be 100.0 (abs of -100.0)
        assert stats.iloc[0]['max_amount'] == 100.0


class TestGetGroupTransactions:
    """Tests for retrieving transactions by group."""
    
    def test_get_group_transactions(self):
        """Test retrieving transactions from a specific group."""
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'clean_group': ['GROUP_A', 'GROUP_A', 'GROUP_B'],
            'amount': [-50.0, -60.0, -30.0]
        })
        
        group_a_txs = get_group_transactions(df, 'GROUP_A')
        
        assert len(group_a_txs) == 2
        assert list(group_a_txs['id']) == [1, 2]
    
    def test_get_nonexistent_group(self):
        """Test retrieving a group that doesn't exist."""
        df = pd.DataFrame({
            'id': [1, 2],
            'clean_group': ['GROUP_A', 'GROUP_A']
        })
        
        result = get_group_transactions(df, 'GROUP_NONEXISTENT')
        
        assert len(result) == 0
