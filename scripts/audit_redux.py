import sys
import os
import pandas as pd
import sqlite3
from collections import Counter

# Set up project root in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from modules.data_manager import get_db_connection

def full_audit():
    print("🚀 Starting Comprehensive Audit (Fixed Path)...\n")
    
    with get_db_connection() as conn:
        # 1. CATEGORIES AUDIT
        print("--- 1. CATEGORIES ---")
        official_df = pd.read_sql("SELECT name FROM categories", conn)
        official_cats = set(official_df['name'].tolist())
        print(f"✅ {len(official_cats)} Official Categories")
        
        # Check for Ghosts
        used_cats_df = pd.read_sql("SELECT DISTINCT category_validated FROM transactions WHERE category_validated IS NOT NULL AND category_validated != 'Inconnu'", conn)
        used_cats = set(used_cats_df['category_validated'].tolist())
        
        ghosts = used_cats - official_cats
        if ghosts:
            print(f"❌ {len(ghosts)} Ghost Categories Found:")
            for g in ghosts:
                count = pd.read_sql(f"SELECT COUNT(*) as c FROM transactions WHERE category_validated = ?", conn, params=(g,)).iloc[0]['c']
                print(f"   - '{g}' ({count} transactions)")
        else:
            print("✨ No Ghost Categories found.")

        # 2. TAGS AUDIT
        print("\n--- 2. TAGS ---")
        tags_df = pd.read_sql("SELECT category_validated, tags FROM transactions WHERE tags IS NOT NULL AND tags != ''", conn)
        
        all_tags = []
        tag_cat_map = {} # tag -> set(categories)
        
        for _, row in tags_df.iterrows():
            cat = row['category_validated']
            if not cat: continue
            
            row_tags = [t.strip() for t in str(row['tags']).split(',') if t.strip()]
            all_tags.extend(row_tags)
            
            for t in row_tags:
                if t not in tag_cat_map: tag_cat_map[t] = set()
                tag_cat_map[t].add(cat)
                
        unique_tags = set(all_tags)
        print(f"🏷️  {len(unique_tags)} Unique Tags in use.")
        
        # Cross-Category Tags
        multi_cat_tags = {t: cats for t, cats in tag_cat_map.items() if len(cats) > 1}
        if multi_cat_tags:
            print(f"⚠️ {len(multi_cat_tags)} Tags used in MULTIPLE Categories (Potential Ambiguity)")
        else:
            print("✅ Tags strictly separated per category.")

        # 3. DATA COMPLETENESS
        print("\n--- 3. DATA COMPLETENESS ---")
        total_tx = pd.read_sql("SELECT COUNT(*) as c FROM transactions", conn).iloc[0]['c']
        pending = pd.read_sql("SELECT COUNT(*) as c FROM transactions WHERE status='pending'", conn).iloc[0]['c']
        print(f"📊 Total Transactions: {total_tx}")
        print(f"⏳ Pending Validation: {pending}")

if __name__ == "__main__":
    full_audit()
