"""
Member management operations.
Handles members, member mappings (card suffixes), and member-related queries.
"""

import sqlite3
import unicodedata

import pandas as pd
import streamlit as st

from modules.constants import MemberType
from modules.core.events import EventBus
from modules.db.connection import get_db_connection
from modules.logger import logger


def add_member(name: str, member_type: str = MemberType.HOUSEHOLD) -> bool:
    """
    Add a new member.

    Args:
        name: Member name (must be unique)
        member_type: MemberType.HOUSEHOLD or MemberType.EXTERNAL

    Returns:
        True if member was added, False if already exists
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO members (name, member_type) VALUES (?, ?)", (name, member_type)
            )
            conn.commit()
            logger.info(f"Member added: {name} ({member_type})")
            EventBus.emit("members.changed", action="added")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Member '{name}' already exists")
            return False


def update_member_type(member_id: int, member_type: str) -> None:
    """Update the type of a member (HOUSEHOLD or EXTERNAL)."""

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE members SET member_type = ? WHERE id = ?", (member_type, member_id))
        conn.commit()
    # Clear cache to ensure fresh data on next read
    try:
        st.cache_data.clear()
    except Exception:
        pass
    EventBus.emit("members.changed")


def delete_member(member_id: int) -> None:
    """Delete a member by ID."""

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM members WHERE id = ?", (member_id,))
        conn.commit()

    # Clear cache to ensure fresh data
    get_members.clear()
    
    EventBus.emit("members.changed")


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
        cursor.execute(
            "UPDATE transactions SET beneficiary = ? WHERE beneficiary = ?", (new_name, old_name)
        )
        tx_count += cursor.rowcount

        # Update member mappings
        cursor.execute(
            "UPDATE member_mappings SET member_name = ? WHERE member_name = ?", (new_name, old_name)
        )

        conn.commit()

    # Invalidate both member and transaction caches since both are affected
    EventBus.emit("members.changed")
    EventBus.emit("transactions.changed")

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
        official_members.update({"Maison", "Famille", "Inconnu", "Anonyme", "", None})

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
        cursor.execute(
            "UPDATE transactions SET member = ? WHERE member = ?", (replacement_label, old_label)
        )
        count = cursor.rowcount
        cursor.execute(
            "UPDATE transactions SET beneficiary = ? WHERE beneficiary = ?",
            (replacement_label, old_label),
        )
        count += cursor.rowcount

        # Delete mappings
        cursor.execute("DELETE FROM member_mappings WHERE member_name = ?", (old_label,))

        # Delete from members table
        cursor.execute("DELETE FROM members WHERE name = ?", (old_label,))

        conn.commit()

    # Invalidate both member and transaction caches since both are affected
    EventBus.emit("members.changed")
    EventBus.emit("transactions.changed")

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

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO member_mappings (card_suffix, member_name) VALUES (?, ?)",
            (card_suffix, member_name),
        )
        conn.commit()
    EventBus.emit("members.changed")


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
        return dict(zip(df["card_suffix"], df["member_name"]))


def delete_member_mapping(mapping_id: int) -> None:
    """Delete a member mapping by ID."""

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM member_mappings WHERE id = ?", (mapping_id,))
        conn.commit()
    EventBus.emit("members.changed")


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
            c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn"
        ).lower()

    with get_db_connection() as conn:
        # 1. Official Members from config
        df_mem = pd.read_sql("SELECT name FROM members", conn)
        cfg_members = df_mem["name"].dropna().tolist()

        # If user has configured members, strictly follow that list (Managed Mode)
        if cfg_members:
            return sorted(list(set(cfg_members)))

        # 2. Fallback: Auto-discovery from transactions (Legacy/Unmanaged Mode)
        df_tx_m = pd.read_sql(
            "SELECT DISTINCT member FROM transactions "
            "WHERE member IS NOT NULL AND member != '' AND member != 'Inconnu'",
            conn,
        )
        df_tx_b = pd.read_sql(
            "SELECT DISTINCT beneficiary FROM transactions "
            "WHERE beneficiary IS NOT NULL AND beneficiary != '' "
            "AND beneficiary != 'Famille' AND beneficiary != 'Maison'",
            conn,
        )

        tx_names = set(
            df_tx_m["member"].dropna().tolist() + df_tx_b["beneficiary"].dropna().tolist()
        )

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


def get_all_member_names() -> list[str]:
    """Get all unique member names from the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM members")
        return [row[0] for row in cursor.fetchall()]


@st.cache_data(ttl=300)
def get_member_detection_data() -> tuple[dict[str, str], list[str], dict[str, str]]:
    """
    Charge en une fois toutes les données nécessaires à la détection de membre.
    
    Cette fonction est utilisée pour éviter le problème N+1 lors de l'import
    de transactions en masse.
    
    Returns:
        Tuple contenant:
        - mappings: dict[card_suffix -> member_name]
        - all_members: list[str] des noms de membres
        - account_maps: dict[account_label -> member_name]
    """
    return (
        get_member_mappings(),
        get_all_member_names(),
        get_account_member_mappings()
    )


def detect_member_from_content(
    label: str,
    card_suffix: str = None,
    account_label: str = None,
    cached_data: tuple[dict[str, str], list[str], dict[str, str]] | None = None
) -> str:
    """
    Detect member based on label, card suffix, and account.

    Uses a cascading detection strategy:
    1. Card suffix mapping (highest priority - most reliable)
    2. Member names found in transaction label
    3. Account-based mappings
    4. Default member (configurable, replaces 'Inconnu')

    Args:
        label: Transaction label
        card_suffix: Detected card suffix (e.g. 6759)
        account_label: Bank account label
        cached_data: Optional pre-loaded data to avoid N+1 queries.
                     Tuple of (mappings, all_members, account_maps).
                     If not provided, data will be loaded from cache.

    Returns:
        Member name. Never returns 'Inconnu' if force_member_identification is enabled.
    """
    from modules.db.settings import get_default_member, get_force_member_identification

    label_upper = label.upper()

    # Utiliser les données fournies ou charger depuis le cache
    if cached_data is not None:
        mappings, all_members, account_maps = cached_data
    else:
        mappings, all_members, account_maps = get_member_detection_data()

    # 1. Check card suffix mapping (highest priority)
    if card_suffix:
        if card_suffix in mappings:
            return mappings[card_suffix]

    # 2. Check for member names in label
    # We fetch all member names
    for member in all_members:
        # Search for exact name in label (with boundaries or common formats)
        if member.upper() in label_upper:
            return member

    # 3. Special cases / Heuristics
    if "PAULINE" in label_upper:
        # Add more specific patterns here as needed
        pass

    # 4. Account-based defaults (if account belongs to one person)
    if account_label:
        account_label.upper()

        # Check explicit mapping table first
        if account_label in account_maps:
            return account_maps[account_label]

        # Fallback to heuristics on account label
        # Add account-specific mappings here as needed

    # 5. Default member (replaces 'Inconnu' if configured)
    default_member = get_default_member()
    force_id = get_force_member_identification()

    if force_id or default_member != "Inconnu":
        return default_member

    return "Inconnu"


# --- Account Mapping Functions ---


def add_account_member_mapping(account_label: str, member_name: str) -> None:
    """Map a bank account label to a default member name."""

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO account_member_mappings (account_label, member_name) VALUES (?, ?)",
            (account_label, member_name),
        )
        conn.commit()
    EventBus.emit("members.changed")


@st.cache_data(ttl=300)
def get_account_member_mappings() -> dict[str, str]:
    """Get all account-member mappings."""
    with get_db_connection() as conn:
        try:
            df = pd.read_sql("SELECT account_label, member_name FROM account_member_mappings", conn)
            return dict(zip(df["account_label"], df["member_name"]))
        except Exception:
            # Fallback if table doesn't exist yet
            return {}


def get_account_member_mappings_df() -> pd.DataFrame:
    """Get all account-member mappings as DataFrame."""
    with get_db_connection() as conn:
        try:
            return pd.read_sql("SELECT * FROM account_member_mappings", conn)
        except Exception:
            return pd.DataFrame()


def delete_account_member_mapping(mapping_id: int) -> None:
    """Delete an account-member mapping by ID."""

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM account_member_mappings WHERE id = ?", (mapping_id,))
        conn.commit()
    EventBus.emit("members.changed")


# ============================================================================
# UNKNOWN MEMBER ANALYSIS & REPAIR
# ============================================================================


def get_unknown_member_stats() -> dict:
    """
    Get statistics about transactions with unknown members.

    Returns:
        Dict with:
        - count: Total number of 'Inconnu' transactions
        - percentage: Percentage of total transactions
        - by_account: Breakdown by account label
        - by_label: Most common labels with unknown members
    """
    from modules.db.settings import get_default_member

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Total unknown count
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE member = 'Inconnu'")
        unknown_count = cursor.fetchone()[0]

        # Total transactions
        cursor.execute("SELECT COUNT(*) FROM transactions")
        total_count = cursor.fetchone()[0]

        percentage = (unknown_count / total_count * 100) if total_count > 0 else 0

        # Breakdown by account
        cursor.execute(
            """
            SELECT account_label, COUNT(*) as cnt 
            FROM transactions 
            WHERE member = 'Inconnu' 
            GROUP BY account_label 
            ORDER BY cnt DESC
        """
        )
        by_account = {row[0] or "Unknown": row[1] for row in cursor.fetchall()}

        # Most common labels
        cursor.execute(
            """
            SELECT label, COUNT(*) as cnt 
            FROM transactions 
            WHERE member = 'Inconnu' 
            GROUP BY label 
            ORDER BY cnt DESC 
            LIMIT 10
        """
        )
        by_label = [{"label": row[0], "count": row[1]} for row in cursor.fetchall()]

        return {
            "count": unknown_count,
            "total": total_count,
            "percentage": round(percentage, 2),
            "by_account": by_account,
            "by_label": by_label,
            "default_member": get_default_member(),
        }


def repair_unknown_members(dry_run: bool = False) -> dict:
    """
    Repair transactions with 'Inconnu' member by applying the default member.

    Args:
        dry_run: If True, only returns what would be changed without making changes

    Returns:
        Dict with repair results:
        - repaired_count: Number of transactions repaired
        - default_member: The member used for repair
        - sample_repaired: Sample of repaired transaction IDs
    """
    from modules.db.settings import get_default_member

    default_member = get_default_member()

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get count and sample
        cursor.execute(
            """
            SELECT id, label, account_label 
            FROM transactions 
            WHERE member = 'Inconnu'
            ORDER BY date DESC
        """
        )
        rows = cursor.fetchall()

        if not rows:
            return {
                "repaired_count": 0,
                "default_member": default_member,
                "sample_repaired": [],
                "message": "Aucune transaction 'Inconnu' à réparer",
            }

        tx_ids = [row[0] for row in rows]
        sample = [{"id": row[0], "label": row[1], "account": row[2]} for row in rows[:5]]

        if not dry_run:
            # Perform the repair
            placeholders = ",".join(["?" for _ in tx_ids])
            cursor.execute(
                f"""
                UPDATE transactions 
                SET member = ? 
                WHERE id IN ({placeholders})
            """,
                [default_member] + tx_ids,
            )

            conn.commit()
            logger.info(f"Repaired {len(tx_ids)} transactions: 'Inconnu' → '{default_member}'")

    EventBus.emit("transactions.changed")

    return {
        "repaired_count": len(tx_ids),
        "default_member": default_member,
        "sample_repaired": sample,
        "dry_run": dry_run,
        "message": f"{'Simulé' if dry_run else 'Réparé'}: {len(tx_ids)} transactions 'Inconnu' → '{default_member}'",
    }


def analyze_unknown_patterns() -> list[dict]:
    """
    Analyze patterns in transactions with unknown members to suggest improvements.

    This helps identify:
    - Common card suffixes not mapped
    - Account labels that could have default mappings
    - Label patterns that could indicate specific members

    Returns:
        List of suggestions for improving member detection
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        suggestions = []

        # 1. Find common card suffixes in unknown transactions
        cursor.execute(
            """
            SELECT card_suffix, COUNT(*) as cnt 
            FROM transactions 
            WHERE member = 'Inconnu' 
            AND card_suffix IS NOT NULL 
            AND card_suffix != ''
            GROUP BY card_suffix 
            ORDER BY cnt DESC 
            LIMIT 5
        """
        )

        for row in cursor.fetchall():
            suggestions.append(
                {
                    "type": "card_suffix",
                    "value": row[0],
                    "count": row[1],
                    "action": f"Mapper le suffixe de carte '{row[0]}' à un membre",
                    "sql_check": f"SELECT label FROM transactions WHERE card_suffix = '{row[0]}' LIMIT 3",
                }
            )

        # 2. Find account labels with many unknowns
        cursor.execute(
            """
            SELECT account_label, COUNT(*) as cnt 
            FROM transactions 
            WHERE member = 'Inconnu' 
            AND account_label IS NOT NULL 
            AND account_label != ''
            GROUP BY account_label 
            HAVING cnt > 5
            ORDER BY cnt DESC
        """
        )

        for row in cursor.fetchall():
            suggestions.append(
                {
                    "type": "account",
                    "value": row[0],
                    "count": row[1],
                    "action": f"Créer un mapping compte→membre pour '{row[0]}'",
                    "example": f"add_account_member_mapping('{row[0]}', 'VOTRE_NOM')",
                }
            )

        return suggestions


def ensure_no_unknown_members() -> dict:
    """
    Ensure no transactions have 'Inconnu' as member.

    This is a comprehensive function that:
    1. Enables force_member_identification
    2. Repairs all existing unknown transactions
    3. Returns a summary of actions taken

    Returns:
        Summary of actions taken
    """
    from modules.db.settings import get_default_member, set_force_member_identification

    # Step 1: Enable force identification
    set_force_member_identification(True)

    # Step 2: Repair existing
    repair_result = repair_unknown_members(dry_run=False)

    return {
        "force_identification_enabled": True,
        "default_member": get_default_member(),
        "repaired_count": repair_result["repaired_count"],
        "message": (
            f"✅ Identification forcée activée\n"
            f"✅ {repair_result['repaired_count']} transactions réparées\n"
            f"✅ Toutes les nouvelles transactions utiliseront '{get_default_member()}' par défaut"
        ),
    }
