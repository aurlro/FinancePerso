"""
Script de nettoyage des doublons inter-comptes.
Garde 1 seule transaction par groupe (Date, Montant, Libellé).
Priorise les comptes 'connus' vs 'Unknown'.
"""
import sqlite3
import pandas as pd
import os
import sys
import shutil
from datetime import datetime

# Setup paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
DB_PATH = os.path.join(PROJECT_ROOT, "Data", "finance.db")

def backup_db():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{DB_PATH}.{timestamp}.bak"
    shutil.copy2(DB_PATH, backup_path)
    print(f"✅ Backup created: {backup_path}")

def clean_duplicates():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Find Duplicate Groups
    query = """
        SELECT date, label, amount, COUNT(*) as count, GROUP_CONCAT(id) as ids
        FROM transactions
        GROUP BY date, label, amount
        HAVING count > 1
    """
    duplicates = pd.read_sql(query, conn)
    
    if duplicates.empty:
        print("✨ No duplicates found. Database is clean!")
        return

    print(f"🔍 Found {len(duplicates)} groups of duplicates.")
    
    total_deleted = 0
    
    for _, row in duplicates.iterrows():
        # Get all distinct IDs for this group
        # Note: GROUP_CONCAT might return comma sep string
        group_ids = row['ids'].split(',')
        
        # Get details to decide which one to keep
        placeholders = ','.join('?' * len(group_ids))
        details_query = f"SELECT id, account_label, category_validated as category, tx_hash FROM transactions WHERE id IN ({placeholders})"
        details = pd.read_sql(details_query, conn, params=group_ids)
        
        # Sorting logic to keep the 'best' one:
        # 1. Prefer defined account over 'Unknown'
        # 2. Prefer categorized over uncategorized (not 'Inconnu')
        # 3. Prefer ID (keep oldest imported? or newest?) -> Let's keep oldest ID (lowest number) usually implies first import
        
        def score_row(r):
            score = 0
            if r['account_label'] and r['account_label'] != 'Unknown':
                score += 10
            if r['category'] and r['category'] != 'Inconnu':
                score += 5
            return score
            
        details['score'] = details.apply(score_row, axis=1)
        
        # Sort by score DESC, then ID ASC (keep oldest)
        details = details.sort_values(by=['score', 'id'], ascending=[False, True])
        
        # Keep the first one
        to_keep_id = details.iloc[0]['id']
        to_delete_ids = details.iloc[1:]['id'].tolist()
        
        print(f"   Group: {row['date']} | {row['label']} | {row['amount']}€")
        print(f"     ✅ Keeping: {details.iloc[0]['account_label']} (ID: {to_keep_id})")
        print(f"     🗑️ Deleting: {len(to_delete_ids)} duplicates")
        
        for did in to_delete_ids:
            cursor.execute("DELETE FROM transactions WHERE id = ?", (did,))
            total_deleted += 1

    conn.commit()
    conn.close()
    
    print("-" * 30)
    print(f"✅ Cleanup Complete! Deleted {total_deleted} duplicate transactions.")

if __name__ == "__main__":
    backup_db()
    clean_duplicates()
