"""
Data quality audit and cleanup operations.
Handles data integrity checks, duplicate detection, and automatic fixes.
"""

import re
from pathlib import Path

import pandas as pd

from modules.core.events import EventBus
from modules.db.connection import get_db_connection
from modules.logger import logger


def auto_fix_common_inconsistencies() -> int:
    """
    Magic Fix 5.1: Rapprochement & Alias Normalization.

    Performs:
    1. Member fixes (accents, re-attribution)
    2. SMART TAGGING: Refunds, keyword heuristics
    3. COLLECTIVE INTELLIGENCE: propagate tags from identical labels
    4. RAPPROCHEMENT INTER-COMPTES: Match mirror transfers (Version 5.1 New)
    5. ALIAS NORMALIZATION: Apply beneficiary aliases (Version 5.1 New)
    6. WITHDRAWAL & LABEL FIXES: Retraits DAB, normalization
    7. Deduplication & Integrity

    Returns:
        Number of fixes applied
    """
    total_fixed = 0
    from modules.db.members import detect_member_from_content
    from modules.db.tags import learn_tags_from_history
    from modules.utils import clean_label

    # 0. Boostrap learning
    learn_tags_from_history()

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1. Member Consistency (common typo fixes)
        fixes = {"Anonyme": "Inconnu"}
        for wrong, right in fixes.items():
            cursor.execute("UPDATE transactions SET member = ? WHERE member = ?", (right, wrong))
            total_fixed += cursor.rowcount
            cursor.execute(
                "UPDATE transactions SET beneficiary = ? WHERE beneficiary = ?", (right, wrong)
            )
            total_fixed += cursor.rowcount

        # Smart Re-attribution
        cursor.execute(
            """
            SELECT id, label, card_suffix, account_label, member 
            FROM transactions 
            WHERE member = 'Inconnu' OR member LIKE 'Carte %' OR member IS NULL
        """
        )
        rows = cursor.fetchall()
        member_updates = []
        for tx_id, label, suffix, account, current_m in rows:
            detected_m = detect_member_from_content(label, suffix, account)
            if detected_m != current_m and detected_m != "Inconnu":
                member_updates.append((detected_m, tx_id))
        if member_updates:
            cursor.executemany("UPDATE transactions SET member = ? WHERE id = ?", member_updates)
            total_fixed += len(member_updates)

        # 2. COLLECTIVE INTELLIGENCE: Propagate tags
        cursor.execute(
            """
            SELECT label, tags, COUNT(*) as count
            FROM transactions 
            WHERE tags IS NOT NULL AND tags != ''
            GROUP BY label, tags
            ORDER BY label, count DESC
        """
        )
        tag_clouds = cursor.fetchall()
        label_to_best_tags = {}
        processed_labels = set()
        for label, tags, count in tag_clouds:
            if label not in processed_labels:
                label_to_best_tags[label] = tags
                processed_labels.add(label)

        cursor.execute("SELECT id, label FROM transactions WHERE (tags IS NULL OR tags = '')")
        untagged = cursor.fetchall()
        propagate_updates = []
        for tx_id, label in untagged:
            if label in label_to_best_tags:
                propagate_updates.append((label_to_best_tags[label], tx_id))
        if propagate_updates:
            cursor.executemany("UPDATE transactions SET tags = ? WHERE id = ?", propagate_updates)
            total_fixed += len(propagate_updates)

        # 3. RAPPROCHEMENT INTER-COMPTES (Version 5.1 New)
        # Find transactions with same amount, opposite sign, different accounts, within ±2 days
        cursor.execute(
            """
            SELECT t1.id, t2.id, t1.tags
            FROM transactions t1
            JOIN transactions t2 ON abs(t1.amount) = abs(t2.amount)
            WHERE t1.amount = -t2.amount
              AND t1.account_label != t2.account_label
              AND abs(julianday(t1.date) - julianday(t2.date)) <= 2
              AND t1.id < t2.id
        """
        )
        match_rows = cursor.fetchall()
        match_updates = []
        for id1, id2, current_tags in match_rows:
            tags = set([t.strip().lower() for t in (current_tags or "").split(",") if t.strip()])
            if "rapproché" not in tags:
                tags.add("rapproché")
                new_tags = ", ".join(sorted(list(tags)))
                match_updates.append((new_tags, id1))
                match_updates.append((new_tags, id2))

        if match_updates:
            # We use redundant updates but it's okay for consistency
            cursor.executemany(
                "UPDATE transactions SET tags = ?, category_validated = 'Virement Interne', status = 'validated' WHERE id = ?",
                match_updates,
            )
            total_fixed += len(match_updates) // 2

        # 4. ALIAS NORMALIZATION (Version 5.1 New)
        cursor.execute("SELECT alias, normalized_name FROM beneficiary_aliases")
        aliases = cursor.fetchall()

        # Batch alias updates
        alias_updates = [(normalized, alias, f"%{alias}%") for alias, normalized in aliases]
        if alias_updates:
            cursor.executemany(
                """
                UPDATE transactions 
                SET beneficiary = ? 
                WHERE (beneficiary = ? OR label LIKE ?)
            """,
                alias_updates,
            )
            # executemany doesn't return rowcount for each, so we estimate
            total_fixed += len(alias_updates)

        # 5. SMART TAGGING & Keywords
        cursor.execute("SELECT id, label, amount, tags, category_validated FROM transactions")
        tag_updates = []
        keywords = {
            "PAYPAL": "achat en ligne",
            "AMAZON": "online",
            "SNCF": "train",
            "TRAIN": "train",
            "RETRAIT DAB": "espèces",
            "UBER": "vTC",
            "DELIVEROO": "repas midi",
            "LECLERC": "courses",
            "SUPER U": "courses",
            "CARREFOUR": "courses",
            "BOULANGERIE": "boulangerie",
            "DARTY": "équipement",
            "FNAC": "culture",
        }
        expense_cats = [
            "Alimentation",
            "Transport",
            "Logement",
            "Santé",
            "Loisirs",
            "Achats",
            "Restaurants",
            "Auto",
            "Enfants",
            "Cadeaux",
            "Assurances",
            "Impôts",
            "Services",
            "Abonnements",
        ]

        for tx_id, label, amount, tags, cat in cursor.fetchall():
            label_upper = label.upper()
            current_tags = set([t.strip().lower() for t in (tags or "").split(",") if t.strip()])
            orig_len = len(current_tags)
            for kw, tag in keywords.items():
                if kw in label_upper:
                    current_tags.add(tag)
            if "AVOIR" in label_upper or (cat in expense_cats and amount > 0):
                current_tags.add("remboursement")
            if len(current_tags) > orig_len:
                tag_updates.append((", ".join(sorted(list(current_tags))), tx_id))

        if tag_updates:
            cursor.executemany("UPDATE transactions SET tags = ? WHERE id = ?", tag_updates)
            total_fixed += len(tag_updates)

        # 6. WITHDRAWAL & LABEL FIXES
        cursor.execute(
            "UPDATE transactions SET category_validated = 'Loisirs' WHERE category_validated = 'Inconnu' AND UPPER(label) LIKE '%RETRAIT DAB%'"
        )
        total_fixed += cursor.rowcount

        cursor.execute("SELECT id, label FROM transactions")
        label_updates = []
        for tx_id, label in cursor.fetchall():
            cleaned = clean_label(label)
            if cleaned and cleaned != label and len(cleaned) > 2:
                label_updates.append((cleaned, tx_id))
        if label_updates:
            cursor.executemany("UPDATE transactions SET label = ? WHERE id = ?", label_updates)
            total_fixed += len(label_updates)

        # 7. Integrity & Deduplication
        cursor.execute("DELETE FROM learning_rules WHERE pattern = '' OR pattern IS NULL")
        total_fixed += cursor.rowcount

        # Link Integrity Reporting
        broken = verify_link_integrity()
        if broken:
            logger.warning(f"⚠️  {len(broken)} broken links detected during audit!")
            for b in broken:
                logger.error(f"   - In {b['file']}: target '{b['target']}' is missing")

        cursor.execute(
            """
            SELECT tx_hash, GROUP_CONCAT(id) as ids
            FROM transactions
            WHERE tx_hash IS NOT NULL AND tx_hash != ''
            GROUP BY tx_hash
            HAVING COUNT(*) > 1
        """
        )
        # Collect all duplicate IDs to delete (keep the first one)
        ids_to_delete = []
        for row in cursor.fetchall():
            ids = [int(x) for x in row[1].split(",")]
            ids_to_delete.extend(ids[1:])  # Keep first, delete rest

        # Batch delete duplicates
        if ids_to_delete:
            placeholders = ",".join(["?"] * len(ids_to_delete))
            cursor.execute(f"DELETE FROM transactions WHERE id IN ({placeholders})", ids_to_delete)
            total_fixed += len(ids_to_delete)

        conn.commit()

    # Final refresh: Re-apply valid rules
    try:
        from modules.categorization import apply_rules

        with get_db_connection() as conn:
            pending_df = pd.read_sql(
                "SELECT id, label FROM transactions WHERE status='pending'", conn
            )
            cursor = conn.cursor()

            # Collect updates for batch execution
            rule_updates = []
            for _, row in pending_df.iterrows():
                cat, conf = apply_rules(row["label"])
                if cat and cat != "Inconnu":
                    rule_updates.append((cat, row["id"]))

            # Batch update
            if rule_updates:
                cursor.executemany(
                    "UPDATE transactions SET category_validated = ?, status = 'validated' WHERE id = ?",
                    rule_updates,
                )
                total_fixed += len(rule_updates)
            conn.commit()
    except Exception as e:
        logger.error(f"Error re-applying rules in magic fix: {e}")

    if total_fixed > 0:
        EventBus.emit("transactions.batch_changed", action="magic_fix")
        EventBus.emit("categories.changed", action="magic_fix")
        EventBus.emit("members.changed", action="magic_fix")

    logger.info(f"Magic Fix 5.1 applied {total_fixed} corrections")
    return total_fixed


def get_suggested_mappings() -> pd.DataFrame:
    """
    Identify recurring card suffixes that are not yet mapped.

    Returns:
        DataFrame with columns: card_suffix, occurrence, example_label
        Sorted by frequency (most common first)
    """
    with get_db_connection() as conn:
        query = """
            SELECT card_suffix, COUNT(*) as occurrence, MAX(label) as example_label
            FROM transactions
            WHERE card_suffix IS NOT NULL 
              AND card_suffix NOT IN (SELECT card_suffix FROM member_mappings)
            GROUP BY card_suffix
            HAVING occurrence >= 2
            ORDER BY occurrence DESC
        """
        return pd.read_sql(query, conn)


def whitelist_transfer_label(label: str) -> bool:
    """Whitelist a label to prevent it from appearing in transfer audit inconsistencies."""
    from modules.db.settings import add_verified_transfer_label

    return add_verified_transfer_label(label)


def get_transfer_inconsistencies() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Identify potentially miscategorized internal transfers.

    Returns:
        Tuple of (missing_transfers, wrong_transfers)
        - missing_transfers: Transactions with transfer keywords but not categorized as such
        - wrong_transfers: Transactions categorized as transfers but lacking transfer keywords
    """
    from modules.db.settings import (
        get_internal_transfer_keywords,
        get_internal_transfer_targets,
        get_verified_transfer_labels,
    )

    with get_db_connection() as conn:
        # 1. Build detection pattern from keywords and targets
        keywords = get_internal_transfer_keywords()
        targets = get_internal_transfer_targets()
        all_patterns = sorted(list(set(keywords + targets)))

        # Build parameterized LIKE clauses
        likes_placeholders = " OR ".join(["upper(label) LIKE ?" for _ in all_patterns])
        # Add wildcards to patterns for SQL parameters
        pattern_params = [f"%{k}%" for k in all_patterns]

        # 2. Get whitelist
        whitelist = get_verified_transfer_labels()
        whitelist_clause = ""
        whitelist_params = []
        if whitelist:
            placeholders = ", ".join(["?"] * len(whitelist))
            whitelist_clause = f"AND label NOT IN ({placeholders})"
            whitelist_params = list(whitelist)

        # 3. Missing transfers: have keywords but wrong category
        if likes_placeholders:
            query_missing = f"""
                SELECT * FROM transactions 
                WHERE ({likes_placeholders})
                AND category_validated NOT IN ('Virement Interne', 'Hors Budget') 
                AND (
                    status = 'pending'
                    OR category_validated IN ('Virements', 'Virements reçus', 'Inconnu')
                )
            """
            missing_params = pattern_params
        else:
            # No patterns configured - return empty
            query_missing = "SELECT * FROM transactions WHERE 1=0"
            missing_params = []

        # 4. Wrong transfers: categorized as transfer but no keywords AND not whitelisted
        if likes_placeholders:
            query_wrong = f"""
                SELECT * FROM transactions 
                WHERE category_validated = 'Virement Interne' 
                AND NOT ({likes_placeholders})
                {whitelist_clause}
            """
            wrong_params = pattern_params + whitelist_params
        else:
            # No patterns configured - all transfers might be wrong
            query_wrong = f"""
                SELECT * FROM transactions 
                WHERE category_validated = 'Virement Interne'
                {whitelist_clause}
            """
            wrong_params = whitelist_params

        missing = pd.read_sql(
            query_missing, conn, params=missing_params if missing_params else None
        )
        wrong = pd.read_sql(query_wrong, conn, params=wrong_params if wrong_params else None)
        return missing, wrong


def verify_link_integrity() -> list[dict]:
    """
    Exhaustive scan of Python files for broken st.switch_page or st.page_link calls.
    Returns a list of dicts with file path and target.
    """
    base_dir = Path(__file__).parent.parent.parent
    pages_dir = base_dir / "pages"

    # Regex for finding Streamlit page navigation
    page_nav_regex = re.compile(
        r'st\.(?:switch_page|page_link)\(\s*(?:f?["\'](pages\/[^"\']+)["\']|["\'](pages\/[^"\']+)["\']\.format)'
    )

    existing_pages = {f"pages/{p.name}" for p in pages_dir.glob("*.py")}
    broken_links = []

    # Scan app.py, modules/ and pages/
    search_paths = [base_dir / "app.py", base_dir / "modules", base_dir / "pages"]

    for search_path in search_paths:
        if not search_path.exists():
            continue

        files = [search_path] if search_path.is_file() else list(search_path.rglob("*.py"))

        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8")
                matches = [m[0] or m[1] for m in page_nav_regex.findall(content)]

                for target in matches:
                    if "{" in target or "%" in target:
                        continue  # Skip dynamic
                    if target not in existing_pages:
                        broken_links.append(
                            {"file": str(file_path.relative_to(base_dir)), "target": target}
                        )
            except Exception:
                continue

    return broken_links


def get_old_pending_transactions(days: int = 30) -> pd.DataFrame:
    """
    Get pending transactions older than specified days.
    
    Args:
        days: Number of days to consider as "old" (default: 30)
        
    Returns:
        DataFrame with old pending transactions
    """
    from datetime import datetime, timedelta
    
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    with get_db_connection() as conn:
        query = """
            SELECT * FROM transactions 
            WHERE status != 'validated' 
            AND date < ?
            ORDER BY date DESC
        """
        return pd.read_sql(query, conn, params=(cutoff_date,))


def validate_transactions_by_ids(tx_ids: list[int]) -> int:
    """
    Validate multiple transactions by their IDs.
    
    Args:
        tx_ids: List of transaction IDs to validate
        
    Returns:
        Number of transactions validated
    """
    if not tx_ids:
        return 0
        
    with get_db_connection() as conn:
        cursor = conn.cursor()
        placeholders = ",".join(["?"] * len(tx_ids))
        cursor.execute(
            f"""UPDATE transactions 
                SET status = 'validated', 
                    category_validated = CASE 
                        WHEN category_validated IS NULL OR category_validated = '' 
                        THEN 'Inconnu' 
                        ELSE category_validated 
                    END
                WHERE id IN ({placeholders})""",
            list(tx_ids)
        )
        conn.commit()
        return cursor.rowcount


def ignore_transactions(tx_ids: list[int]) -> int:
    """
    Mark transactions as ignored by setting a special tag.
    
    Args:
        tx_ids: List of transaction IDs to ignore
        
    Returns:
        Number of transactions updated
    """
    if not tx_ids:
        return 0
        
    with get_db_connection() as conn:
        cursor = conn.cursor()
        placeholders = ",".join(["?"] * len(tx_ids))
        
        # Get current tags
        cursor.execute(
            f"SELECT id, tags FROM transactions WHERE id IN ({placeholders})",
            list(tx_ids)
        )
        rows = cursor.fetchall()
        
        updates = []
        for tx_id, current_tags in rows:
            new_tags = "ignored"
            if current_tags and current_tags.strip():
                if "ignored" not in current_tags.lower():
                    new_tags = f"{current_tags},ignored"
                else:
                    continue
            updates.append((new_tags, tx_id))
        
        if updates:
            cursor.executemany(
                "UPDATE transactions SET tags = ? WHERE id = ?",
                updates
            )
        conn.commit()
        return len(updates)


def get_duplicate_transactions() -> pd.DataFrame:
    """
    Get detailed information about duplicate transactions.
    
    Returns:
        DataFrame with duplicate groups and their transaction IDs
    """
    with get_db_connection() as conn:
        query = """
            SELECT 
                date, label, amount,
                COUNT(*) as duplicate_count,
                GROUP_CONCAT(id) as ids,
                GROUP_CONCAT(account_label) as accounts
            FROM transactions 
            GROUP BY date, label, amount 
            HAVING COUNT(*) > 1
            ORDER BY duplicate_count DESC, date DESC
        """
        return pd.read_sql(query, conn)


def merge_duplicate_transactions(date: str, label: str, amount: float) -> dict:
    """
    Merge duplicate transactions by keeping the most complete one and deleting others.
    
    Args:
        date: Transaction date
        label: Transaction label
        amount: Transaction amount
        
    Returns:
        Dict with result info: {"kept_id": int, "deleted_ids": list, "success": bool}
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get all duplicates
        cursor.execute(
            """SELECT id, category_validated, status, tags, beneficiary, notes, member
               FROM transactions 
               WHERE date = ? AND label = ? AND amount = ?
               ORDER BY 
                   CASE WHEN status = 'validated' THEN 0 ELSE 1 END,
                   CASE WHEN category_validated IS NOT NULL AND category_validated != 'Inconnu' THEN 0 ELSE 1 END,
                   LENGTH(COALESCE(tags, '')),
                   LENGTH(COALESCE(notes, '')),
                   id DESC""",
            (date, label, amount)
        )
        rows = cursor.fetchall()
        
        if len(rows) <= 1:
            return {"kept_id": None, "deleted_ids": [], "success": False, "message": "Pas de doublons"}
        
        # Keep the first (most complete) one
        kept_id = rows[0][0]
        deleted_ids = [r[0] for r in rows[1:]]
        
        # Delete duplicates
        placeholders = ",".join(["?"] * len(deleted_ids))
        cursor.execute(
            f"DELETE FROM transactions WHERE id IN ({placeholders})",
            deleted_ids
        )
        conn.commit()
        
        # Clear caches
        from modules.db.connection import clear_db_cache
        clear_db_cache()
        
        return {
            "kept_id": kept_id,
            "deleted_ids": deleted_ids,
            "success": True,
            "message": f"{len(deleted_ids)} doublon(s) supprimé(s), ID conservé: {kept_id}"
        }


def get_rule_overlaps_with_details() -> list[dict]:
    """
    Get detailed information about rule overlaps with affected transactions.
    
    Returns:
        List of dicts with overlap details and sample affected transactions
    """
    from modules.ai.rules_auditor import analyze_rules_integrity
    from modules.db.rules import get_learning_rules
    
    rules_df = get_learning_rules()
    if rules_df.empty:
        return []
    
    audit = analyze_rules_integrity(rules_df)
    overlaps = audit.get("overlaps", [])
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        for overlap in overlaps:
            # Get sample transactions that would match the shorter pattern
            shorter_pattern = overlap["shorter_pattern"]
            cursor.execute(
                """SELECT id, label, category_validated, date 
                   FROM transactions 
                   WHERE label LIKE ? 
                   LIMIT 3""",
                (f"%{shorter_pattern}%",)
            )
            overlap["sample_transactions"] = [
                dict(zip(["id", "label", "category", "date"], row))
                for row in cursor.fetchall()
            ]
            
            # Count affected transactions
            cursor.execute(
                "SELECT COUNT(*) FROM transactions WHERE label LIKE ?",
                (f"%{shorter_pattern}%",)
            )
            overlap["affected_count"] = cursor.fetchone()[0]
    
    return overlaps
