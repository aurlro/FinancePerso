#!/usr/bin/env python3
"""
Script de test MCP pour FinancePerso
Teste la connexion et exécute quelques requêtes de base
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "Data" / "finance.db"

def test_connection():
    """Teste la connexion à la base de données"""
    print(f"📁 Base de données : {DB_PATH}")
    print(f"   Existe : {DB_PATH.exists()}")
    
    if not DB_PATH.exists():
        print("❌ Base de données non trouvée !")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Test 1: Liste des tables
        print("\n📋 Tables dans la base :")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            print(f"   - {table[0]}")
        
        # Test 2: Stats transactions
        print("\n📊 Stats transactions :")
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as actives,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending
            FROM transactions
        """)
        stats = cursor.fetchone()
        print(f"   Total : {stats[0]}")
        print(f"   Actives : {stats[1]}")
        print(f"   Pending : {stats[2]}")
        
        # Test 3: Dernières transactions
        print("\n📝 5 dernières transactions :")
        cursor.execute("""
            SELECT date, label, amount, category_validated, status
            FROM transactions
            ORDER BY date DESC
            LIMIT 5
        """)
        for row in cursor.fetchall():
            label = row[1] or ""
            print(f"   {row[0]} | {label[:30]:30} | {row[2]:>8.2f}€ | {row[3] or 'N/A'} | {row[4]}")
        
        conn.close()
        print("\n✅ Connexion réussie !")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
