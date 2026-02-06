"""
Script de réparation des hash de transactions manquants.
Recalcule le hash universel (Date|Label|Amount|Index) pour les transactions anciennes.
"""
import sqlite3
import hashlib
import os
import sys
from collections import defaultdict

# Setup paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
DB_PATH = os.path.join(PROJECT_ROOT, "Data", "finance.db")

def calculate_universal_hash(date, label, amount, index):
    norm_label = str(label).strip().upper()
    # Universal Signature: date|label|amount|index
    # Note: excluding account for universality
    base = f"{date}|{norm_label}|{amount}|{index}"
    return hashlib.sha256(base.encode()).hexdigest()[:16]

def repair_hashes():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all transactions with empty or NULL hash
    query = "SELECT id, date, label, amount FROM transactions WHERE tx_hash IS NULL OR tx_hash = '' OR tx_hash = 'None' ORDER BY date, id"
    rows = cursor.execute(query).fetchall()
    
    if not rows:
        print("✅ No broken hashes found.")
        conn.close()
        return

    print(f"🔧 Found {len(rows)} transactions with missing hashes. Repairing...")
    
    # We need to track local occurrence index to match ingestion logic
    # (date, label, amount) -> current_count
    occurrence_map = defaultdict(int)
    
    updated_count = 0
    
    for row in rows:
        tx_id, date, label, amount = row
        
        # Determine index for this specific transaction signature
        key = (date, label, amount)
        index = occurrence_map[key]
        occurrence_map[key] += 1
        
        new_hash = calculate_universal_hash(date, label, amount, index)
        
        try:
            cursor.execute("UPDATE transactions SET tx_hash = ? WHERE id = ?", (new_hash, tx_id))
            updated_count += 1
        except sqlite3.IntegrityError:
            # If hash collision (very rare unless duplicate exists), try with higher index
            # This is a fallback repair
            occurrence_map[key] += 1
            index = occurrence_map[key]
            new_hash = calculate_universal_hash(date, label, amount, index)
            cursor.execute("UPDATE transactions SET tx_hash = ? WHERE id = ?", (new_hash, tx_id))
            print(f"⚠️ Collision handling for ID {tx_id}: index bumped to {index}")

    conn.commit()
    conn.close()
    print(f"✅ Repaired {updated_count} hashes.")

if __name__ == "__main__":
    repair_hashes()
