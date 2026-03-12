#!/usr/bin/env python3
"""Migration des données Streamlit → React v6.0

Ce script migre les données de l'ancienne base SQLite (modules/db/)
vers la nouvelle structure server/app/database.db
"""

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# Chemins
OLD_DB = Path("Data/finance.db")
NEW_DB = Path("server/finance_v6.db")
BACKUP_DIR = Path("backups/migration_v6")


def backup_old_db():
    """Sauvegarde la base existante."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"finance_backup_{timestamp}.db"
    
    if OLD_DB.exists():
        shutil.copy2(OLD_DB, backup_path)
        print(f"✅ Sauvegarde créée: {backup_path}")
        return backup_path
    else:
        print(f"⚠️ Base source non trouvée: {OLD_DB}")
        return None


def get_old_transactions():
    """Récupère les transactions de l'ancienne base."""
    if not OLD_DB.exists():
        return []
    
    with sqlite3.connect(OLD_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, date, label, amount, category, account, 
                   status, member, beneficiary, notes, tx_hash
            FROM transactions
            WHERE deleted = 0 OR deleted IS NULL
        """)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_old_categories():
    """Récupère les catégories."""
    if not OLD_DB.exists():
        return []
    
    with sqlite3.connect(OLD_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, emoji, is_fixed FROM categories")
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_old_accounts():
    """Récupère les comptes."""
    if not OLD_DB.exists():
        return []
    
    with sqlite3.connect(OLD_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, account_type, owner FROM accounts")
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def migrate_to_new_db():
    """Migration principale."""
    print("🚀 Migration FinancePerso v5 → v6")
    print("=" * 50)
    
    # 1. Sauvegarde
    backup_path = backup_old_db()
    if not backup_path:
        print("❌ Impossible de continuer sans base source")
        return False
    
    # 2. Stats avant
    old_tx = get_old_transactions()
    old_cat = get_old_categories()
    old_acc = get_old_accounts()
    
    print(f"\n📊 Données à migrer:")
    print(f"   - Transactions: {len(old_tx)}")
    print(f"   - Catégories: {len(old_cat)}")
    print(f"   - Comptes: {len(old_acc)}")
    
    # 3. Créer la nouvelle base si elle n'existe pas
    if not NEW_DB.exists():
        print(f"\n⚠️ Nouvelle base non initialisée: {NEW_DB}")
        print("   Exécutez d'abord: cd server && python init_db.py")
        return False
    
    # 4. Migration
    print(f"\n📝 Migration en cours...")
    
    with sqlite3.connect(NEW_DB) as conn:
        cursor = conn.cursor()
        
        # Vider les tables existantes
        cursor.execute("DELETE FROM transactions")
        cursor.execute("DELETE FROM categories")
        cursor.execute("DELETE FROM accounts")
        
        # Migrer catégories
        for cat in old_cat:
            cursor.execute("""
                INSERT INTO categories (id, name, emoji, is_fixed)
                VALUES (?, ?, ?, ?)
            """, (cat.get('id'), cat.get('name'), cat.get('emoji'), 
                  cat.get('is_fixed', 0)))
        
        # Migrer comptes
        for acc in old_acc:
            cursor.execute("""
                INSERT INTO accounts (id, name, account_type, owner)
                VALUES (?, ?, ?, ?)
            """, (acc.get('id'), acc.get('name'), acc.get('account_type'),
                  acc.get('owner')))
        
        # Migrer transactions
        migrated = 0
        for tx in old_tx:
            try:
                cursor.execute("""
                    INSERT INTO transactions 
                    (id, date, label, amount, category_id, account_id,
                     status, member_id, beneficiary, notes, hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tx.get('id'),
                    tx.get('date'),
                    tx.get('label'),
                    tx.get('amount'),
                    tx.get('category'),
                    tx.get('account'),
                    tx.get('status', 'pending'),
                    tx.get('member'),
                    tx.get('beneficiary'),
                    tx.get('notes'),
                    tx.get('tx_hash')
                ))
                migrated += 1
            except Exception as e:
                print(f"   ⚠️ Erreur transaction {tx.get('id')}: {e}")
        
        conn.commit()
    
    print(f"\n✅ Migration terminée!")
    print(f"   - Transactions migrées: {migrated}/{len(old_tx)}")
    print(f"   - Catégories migrées: {len(old_cat)}")
    print(f"   - Comptes migrés: {len(old_acc)}")
    
    # Rapport
    report = {
        "date": datetime.now().isoformat(),
        "source": str(OLD_DB),
        "destination": str(NEW_DB),
        "stats": {
            "transactions_total": len(old_tx),
            "transactions_migrated": migrated,
            "categories": len(old_cat),
            "accounts": len(old_acc)
        }
    }
    
    report_path = BACKUP_DIR / f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📝 Rapport sauvegardé: {report_path}")
    return True


if __name__ == "__main__":
    success = migrate_to_new_db()
    sys.exit(0 if success else 1)
