"""
Tests for tags.py module.
"""
import pytest
import pandas as pd
from modules.db.tags import (
    get_all_tags,
    remove_tag_from_all_transactions,
    normalize_tags_for_transaction
)
from modules.db.transactions import (
    save_transactions,
    update_transaction_category,
    get_all_transactions
)

class TestGetTags:
    """Tests for fetching tags."""
    
    def test_get_all_tags_empty(self, temp_db):
        """Test getting tags when none exist."""
        tags = get_all_tags()
        assert isinstance(tags, list)
    
    def test_get_all_tags_with_data(self, temp_db, db_connection):
        """Test getting all unique tags."""
        # Add transactions with tags
        df = pd.DataFrame([
            {'date': '2024-01-15', 'label': 'TX1', 'amount': -50.0, 'tags': 'tag1,tag2'},
            {'date': '2024-01-16', 'label': 'TX2', 'amount': -30.0, 'tags': 'tag2,tag3'}
        ])
        save_transactions(df)
        
        tags = get_all_tags()
        assert 'tag1' in tags
        assert 'tag2' in tags
        assert 'tag3' in tags

class TestTagOperations:
    """Tests for tag operations."""
    
    def _add_tx(self, tags=None, label='TX'):
        df = pd.DataFrame([
            {'date': '2024-01-15', 'label': label, 'amount': -50.0, 'tags': tags}
        ])
        save_transactions(df)
        df_all = get_all_transactions()
        # Find the one we just added (last one with matching label)
        return int(df_all[df_all['label'] == label].iloc[0]['id'])

    def test_add_tag_via_update(self, temp_db):
        """Test adding tag via update_transaction_category."""
        tx_id = self._add_tx()
        
        # update tags
        update_transaction_category(tx_id, 'Inconnu', tags='newtag')
        
        df = get_all_transactions()
        tx = df[df['id'] == tx_id].iloc[0]
        assert 'newtag' in tx['tags']
    
    def test_remove_tag_from_all_transactions(self, temp_db):
        """Test removing a tag globally."""
        self._add_tx(tags='delete_me,keep', label='TX1')
        self._add_tx(tags='delete_me,other', label='TX2')
        
        count = remove_tag_from_all_transactions('delete_me')
        assert count == 2
        
        df = get_all_transactions()
        for _, tx in df.iterrows():
            if tx['tags']:
                assert 'delete_me' not in tx['tags']
                
class TestNormalizeTags:
    """Tests for tag normalization."""
    
    def test_normalize_tags(self, temp_db):
        """Test normalization."""
        normalized = normalize_tags_for_transaction('Tag1, TAG2, tag1 ')
        tags = [t.strip() for t in normalized.split(',')]
        assert 'tag1' in tags
        assert 'tag2' in tags
        assert len(tags) == 2
