"""
Member management operations.
Handles members, member mappings (card suffixes), and member-related queries.
"""
import sqlite3
import pandas as pd
import unicodedata
import streamlit as st
from modules.db.connection import get_db_connection
from modules.logger import logger
from modules.constants import MemberType


def add_member(name: str, member_type: str = MemberType.HOUSEHOLD) -> bool:
    """
    Add a new member.

    Args:
        name: Member name (must be unique)
        member_type: MemberType.HOUSEHOLD or MemberType.EXTERNAL

    Returns:
        True if member was added, False if already exists
    """
    from modules.cache_manager import invalidate_member_caches

    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO members (name, member_type) VALUES (?, ?)",
                (name, member_type)
            )
            conn.commit()
            invalidate_member_caches()
            logger.info(f"Member added: {name} ({member_type})")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Member '{name}' already exists")
            return False


def update_member_type(member_id: int, member_type: str) -> None:
    """Update the type of a member (HOUSEHOLD or EXTERNAL)."""
    from modules.cache_manager import invalidate_member_caches

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE members SET member_type = ? WHERE id = ?", (member_type, member_id))
        conn.commit()
        invalidate_member_caches()


def delete_member(member_id: int) -> None:
    """Delete a member by ID."""
    from modules.cache_manager import invalidate_member_caches

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM members WHERE id = ?", (member_id,))
        conn.commit()

    invalidate_member_caches()


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_members() -> pd.DataFrame:
    """
    Get all members.
    
    Returns:
        DataFrame with columns: name, member_type
        
    Note:
        Cached for 5 minutes to improve performance
    """
    with get_db_connection() as conn:
        return pd.read_sql("SELECT * FROM members ORDER BY name", conn)


def rename_member(old_name: str, new_name: str) -> int:
    """
    Rename a member and propagate changes to transactions and mappings.
    
    Args:
        old_name: Current member name
        new_name: New member name
        
    Returns:
        Total number of affected transactions
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Update member table
        cursor.execute("UPDATE members SET name = ? WHERE name = ?", (new_name, old_name))
        
        # Update transactions (member field)
        cursor.execute("UPDATE transactions SET member = ? WHERE member = ?", (new_name, old_name))
        tx_count = cursor.rowcount
        
        # Update transactions (beneficiary field)
        cursor.execute("UPDATE transactions SET beneficiary = ? WHERE beneficiary = ?", (new_name, old_name))
        tx_count += cursor.rowcount
        
        # Update member mappings
        cursor.execute("UPDATE member_mappings SET member_name = ? WHERE member_name = ?", (new_name, old_name))

        conn.commit()

    # Invalidate both member and transaction caches since both are affected
    from modules.cache_manager import invalidate_member_caches, invalidate_transaction_caches
    invalidate_member_caches()
    invalidate_transaction_caches()

    logger.info(f"Renamed member '{old_name}' → '{new_name}': {tx_count} transactions updated")
    return tx_count


def get_orphan_labels() -> list[str]:
    """
    Find values in transactions that are NOT in the members table.
    
    Checks both the 'member' and 'beneficiary' fields for orphaned references.
    
    Returns:
        Sorted list of orphaned member/beneficiary names
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get official members
        cursor.execute("SELECT name FROM members")
        official_members = {r[0] for r in cursor.fetchall()}
        
        # Add reserved names
        official_members.update({'Maison', 'Famille', 'Inconnu', 'Anonyme', '', None})
        
        # Get unique values from transactions
        cursor.execute("SELECT DISTINCT member FROM transactions")
        txn_members = {r[0] for r in cursor.fetchall() if r[0]}
        
        cursor.execute("SELECT DISTINCT beneficiary FROM transactions")
        txn_benefs = {r[0] for r in cursor.fetchall() if r[0]}
        
        all_txn_values = txn_members.union(txn_benefs)
        orphans = all_txn_values - official_members
        
        return sorted(list(orphans))


def delete_and_replace_label(old_label: str, replacement_label: str = "Inconnu") -> int:
    """
    Replace a member label across all transactions and delete it.
    
    1. Updates all transactions using this label in member or beneficiary fields
    2. Deletes any member mapping for this label
    3. Deletes the member from the members table if it exists
    
    Args:
        old_label: Label to replace
        replacement_label: Replacement value (default: "Inconnu")
        
    Returns:
        Number of transactions updated
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Update transactions
        cursor.execute("UPDATE transactions SET member = ? WHERE member = ?", (replacement_label, old_label))
        count = cursor.rowcount
        cursor.execute("UPDATE transactions SET beneficiary = ? WHERE beneficiary = ?", (replacement_label, old_label))
        count += cursor.rowcount
        
        # Delete mappings
        cursor.execute("DELETE FROM member_mappings WHERE member_name = ?", (old_label,))
        
        # Delete from members table
        cursor.execute("DELETE FROM members WHERE name = ?", (old_label,))

        conn.commit()

    # Invalidate both member and transaction caches since both are affected
    from modules.cache_manager import invalidate_member_caches, invalidate_transaction_caches
    invalidate_member_caches()
    invalidate_transaction_caches()

    logger.info(f"Replaced label '{old_label}' → '{replacement_label}': {count} updates")
    return count


# --- Member Mapping Functions ---

def add_member_mapping(card_suffix: str, member_name: str) -> None:
    """
    Map a card suffix to a member name.

    Used for automatic member attribution during import based on card numbers.

    Args:
        card_suffix: Last 4 digits of card number
        member_name: Member to assign
    """
    from modules.cache_manager import invalidate_member_caches

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO member_mappings (card_suffix, member_name) VALUES (?, ?)",
            (card_suffix, member_name)
        )
        conn.commit()
        invalidate_member_caches()


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_member_mappings() -> dict[str, str]:
    """
    Get all member mappings (card suffix -> member name).
    
    Returns:
        Dict mapping card_suffix to member_name
        
    Note:
        Cached for 5 minutes to improve performance
    """
    with get_db_connection() as conn:
        df = pd.read_sql("SELECT card_suffix, member_name FROM member_mappings", conn)
        return dict(zip(df['card_suffix'], df['member_name']))


def delete_member_mapping(mapping_id: int) -> None:
    """Delete a member mapping by ID."""
    from modules.cache_manager import invalidate_member_caches

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM member_mappings WHERE id = ?", (mapping_id,))
        conn.commit()
        invalidate_member_caches()


def get_member_mappings_df() -> pd.DataFrame:
    """
    Get all member mappings as DataFrame.
    
    Returns:
        DataFrame with columns: id, card_suffix, member_name, created_at
    """
    with get_db_connection() as conn:
        return pd.read_sql("SELECT * FROM member_mappings", conn)


def get_unique_members() -> list[str]:
    """
    Get list of unique member names from members table or transactions.
    
    If members are configured in the database, uses that list (Managed Mode).
    Otherwise, discovers members from transactions (Legacy Mode).
    
    Returns:
        Sorted list of member names
    """
    def normalize(s):
        """Normalize a string for deduplication (remove accents, lowercase)."""
        if not s:
            return ""
        return "".join(
            c for c in unicodedata.normalize('NFD', str(s))
            if unicodedata.category(c) != 'Mn'
        ).lower()
    
    with get_db_connection() as conn:
        # 1. Official Members from config
        df_mem = pd.read_sql("SELECT name FROM members", conn)
        cfg_members = df_mem['name'].dropna().tolist()
        
        # If user has configured members, strictly follow that list (Managed Mode)
        if cfg_members:
            return sorted(list(set(cfg_members)))
        
        # 2. Fallback: Auto-discovery from transactions (Legacy/Unmanaged Mode)
        df_tx_m = pd.read_sql(
            "SELECT DISTINCT member FROM transactions "
            "WHERE member IS NOT NULL AND member != '' AND member != 'Inconnu'",
            conn
        )
        df_tx_b = pd.read_sql(
            "SELECT DISTINCT beneficiary FROM transactions "
            "WHERE beneficiary IS NOT NULL AND beneficiary != '' "
            "AND beneficiary != 'Famille' AND beneficiary != 'Maison'",
            conn
        )
        
        tx_names = set(df_tx_m['member'].dropna().tolist() + df_tx_b['beneficiary'].dropna().tolist())
        
        # Deduplicate using normalization
        seen = {}
        for name in tx_names:
            norm = normalize(name)
            if norm not in seen:
                seen[norm] = name
        
        return sorted(list(seen.values()))


def update_transaction_member(tx_id: int, new_member: str) -> None:
    """Update the member for a specific transaction."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE transactions SET member = ? WHERE id = ?", (new_member, tx_id))
        conn.commit()
