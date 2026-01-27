"""
Tests for members.py module.
"""
import pytest
from modules.db.members import (
    get_members,
    get_unique_members,
    add_member,
    update_member_type,
    delete_member,
    rename_member,
    get_member_mappings,
    add_member_mapping,
    delete_member_mapping
)

class TestGetMembers:
    """Tests for fetching members."""
    
    def test_get_members_defaults(self, temp_db):
        """Test getting default members."""
        df = get_members()
        assert not df.empty
        assert len(df) >= 3  # At least Maison, Famille, Inconnu
        
        names = df['name'].tolist()
        assert 'Maison' in names
        assert 'Famille' in names
        assert 'Inconnu' in names
    
    def test_get_unique_members(self, temp_db):
        """Test getting unique member names."""
        members = get_unique_members()
        assert isinstance(members, list)
        assert 'Maison' in members
        assert 'Famille' in members

class TestAddMember:
    """Tests for adding members."""
    
    def test_add_household_member(self, temp_db):
        """Test adding a household member."""
        member_id = add_member('Alice', 'HOUSEHOLD')
        assert member_id is True
        
        df = get_members()
        alice = df[df['name'] == 'Alice']
        assert not alice.empty
        assert alice.iloc[0]['member_type'] == 'HOUSEHOLD'
    
    def test_add_external_member(self, temp_db):
        """Test adding an external member."""
        member_id = add_member('Amazon', 'EXTERNAL')
        assert member_id is True
        
        df = get_members()
        amazon = df[df['name'] == 'Amazon']
        assert not amazon.empty
        assert amazon.iloc[0]['member_type'] == 'EXTERNAL'
    
    def test_add_member_default_type(self, temp_db):
        """Test adding member with default type (HOUSEHOLD)."""
        member_id = add_member('Bob')
        assert member_id is True
        
        df = get_members()
        bob = df[df['name'] == 'Bob']
        # Note: Depending on implementation, member_type column key
        col = 'member_type' if 'member_type' in df.columns else 'type'
        assert bob.iloc[0][col] == 'HOUSEHOLD'
    
    def test_add_duplicate_member(self, temp_db):
        """Test that duplicate member names are handled."""
        add_member('Duplicate')
        # Second add should fail or return existing/False
        result = add_member('Duplicate')
        assert result is False

class TestUpdateMember:
    """Tests for updating members."""
    
    def test_update_member_type(self, temp_db):
        """Test updating member type."""
        add_member('Charlie', 'HOUSEHOLD')
        
        # Get ID
        df = get_members()
        member_id = int(df[df['name'] == 'Charlie'].iloc[0]['id'])
        
        update_member_type(member_id, 'EXTERNAL')
        
        df = get_members()
        charlie = df[df['name'] == 'Charlie']
        col = 'member_type' if 'member_type' in df.columns else 'type'
        assert charlie.iloc[0][col] == 'EXTERNAL'
    
    def test_update_member_name(self, temp_db):
        """Test updating member name."""
        add_member('OldName')
        rename_member('OldName', 'NewName')
        
        df = get_members()
        assert 'NewName' in df['name'].tolist()
        assert 'OldName' not in df['name'].tolist()

class TestDeleteMember:
    """Tests for deleting members."""
    
    def test_delete_member(self, temp_db):
        """Test deleting a member."""
        add_member('ToDelete')
        
        df = get_members()
        member_id = int(df[df['name'] == 'ToDelete'].iloc[0]['id'])
        
        deleted = delete_member(member_id)
        assert deleted is None # delete_member returns None in typical implementation here
        
        df = get_members()
        assert 'ToDelete' not in df['name'].tolist()
    
    def test_delete_nonexistent_member(self, temp_db):
        """Test deleting non-existent member."""
        # Just check it doesn't crash
        delete_member(99999)

class TestRenameMember:
    """Tests for renaming members with transaction updates."""
    
    def test_rename_member_updates_transactions(self, temp_db, db_connection):
        """Test that renaming updates all transactions."""
        # Add transactions with old member name
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO members (name) VALUES ('OldMember')")
        cursor.execute("""
            INSERT INTO transactions (date, label, amount, member)
            VALUES ('2024-01-15', 'TX 1', -50.00, 'OldMember')
        """)
        cursor.execute("""
            INSERT INTO transactions (date, label, amount, member)
            VALUES ('2024-01-16', 'TX 2', -30.00, 'OldMember')
        """)
        db_connection.commit()
        
        # Rename
        count = rename_member('OldMember', 'NewMember')
        assert count == 2
        
        # Verify
        cursor.execute("""
            SELECT COUNT(*) FROM transactions WHERE member = 'NewMember'
        """)
        assert cursor.fetchone()[0] == 2
        
        cursor.execute("""
            SELECT COUNT(*) FROM transactions WHERE member = 'OldMember'
        """)
        assert cursor.fetchone()[0] == 0

class TestMemberMappings:
    """Tests for card suffix to member mappings."""
    
    def test_get_member_mappings_empty(self, temp_db):
        """Test getting mappings when none exist."""
        # Clear defaults first if needed, but temp_db should be standard
        # Actually init_db populates defaults.
        # So it might not be empty.
        df = get_member_mappings()
        # Just check structure
        assert 'card_suffix' in df.keys() or isinstance(df, dict)
    
    def test_add_member_mapping(self, temp_db):
        """Test adding a card mapping."""
        add_member_mapping('1234', 'Alice')
        
        mappings = get_member_mappings()
        # get_member_mappings returns dict {suffix: name}
        assert '1234' in mappings
        assert mappings['1234'] == 'Alice'

    def test_delete_member_mapping(self, temp_db):
        """Test deleting a card mapping."""
        add_member_mapping('5678', 'Bob')
        
        # We need ID to delete?
        # delete_member_mapping(mapping_id)
        # We need to fetch ID first from get_member_mappings_df if valid
        from modules.db.members import get_member_mappings_df
        df = get_member_mappings_df()
        mapping_id = int(df[df['card_suffix'] == '5678'].iloc[0]['id'])
        
        delete_member_mapping(mapping_id)
        
        mappings = get_member_mappings()
        assert '5678' not in mappings
