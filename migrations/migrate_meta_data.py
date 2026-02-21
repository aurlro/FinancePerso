"""
Script de migration pour ajouter le champ meta_data aux transactions.
=====================================================================

Usage:
    python migrations/migrate_meta_data.py

Ce script:
1. Vérifie si la colonne meta_data existe
2. L'ajoute si nécessaire
3. Migre les données existantes (category_validated, ai_confidence)
4. Génère un rapport
"""

import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.db.connection import get_db_connection
from modules.logger import logger


def check_column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    """Vérifie si une colonne existe dans une table."""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [info[1] for info in cursor.fetchall()]
    return column in columns


def add_meta_data_column(conn: sqlite3.Connection) -> bool:
    """Ajoute la colonne meta_data à la table transactions."""
    try:
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE transactions ADD COLUMN meta_data TEXT")
        conn.commit()
        logger.info("✅ Colonne meta_data ajoutée avec succès")
        return True
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            logger.info("ℹ️ Colonne meta_data existe déjà")
            return True
        logger.error(f"❌ Erreur lors de l'ajout de la colonne: {e}")
        return False


def migrate_existing_data(conn: sqlite3.Connection) -> dict:
    """Migre les données existantes vers le nouveau format meta_data."""
    cursor = conn.cursor()
    
    # Récupérer les transactions sans meta_data mais avec category_validated
    cursor.execute(
        """
        SELECT id, category_validated, ai_confidence, status
        FROM transactions
        WHERE meta_data IS NULL
        AND category_validated IS NOT NULL
        """
    )
    
    transactions = cursor.fetchall()
    migrated_count = 0
    error_count = 0
    
    for tx_id, category, confidence, status in transactions:
        try:
            # Déterminer la méthode basée sur les données existantes
            if status == "validated":
                method = "MANUAL" if confidence is None else "AI"
            else:
                method = "LEGACY"
            
            # Créer les métadonnées
            meta_data = {
                "categorization": {
                    "method": method,
                    "confidence_score": confidence or 0.8,
                    "timestamp": datetime.now().isoformat(),
                    "version": "1.0",
                },
                "migrated": True,
                "migration_date": datetime.now().isoformat(),
            }
            
            # Mettre à jour la transaction
            cursor.execute(
                "UPDATE transactions SET meta_data = ? WHERE id = ?",
                (json.dumps(meta_data), tx_id)
            )
            migrated_count += 1
            
        except Exception as e:
            logger.error(f"Erreur lors de la migration de la transaction {tx_id}: {e}")
            error_count += 1
    
    conn.commit()
    
    return {
        "migrated": migrated_count,
        "errors": error_count,
        "total_processed": len(transactions),
    }


def generate_report(conn: sqlite3.Connection) -> dict:
    """Génère un rapport sur l'état de la migration."""
    cursor = conn.cursor()
    
    # Statistiques générales
    cursor.execute("SELECT COUNT(*) FROM transactions")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE meta_data IS NOT NULL")
    with_meta = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE meta_data IS NULL")
    without_meta = cursor.fetchone()[0]
    
    return {
        "total_transactions": total,
        "with_metadata": with_meta,
        "without_metadata": without_meta,
        "coverage_percent": round(with_meta / total * 100, 2) if total > 0 else 0,
    }


def main():
    """Point d'entrée principal du script de migration."""
    logger.info("🚀 Démarrage de la migration meta_data")
    
    try:
        with get_db_connection() as conn:
            # Étape 1: Vérifier et ajouter la colonne
            if not check_column_exists(conn, "transactions", "meta_data"):
                logger.info("📦 Ajout de la colonne meta_data...")
                if not add_meta_data_column(conn):
                    logger.error("❌ Impossible d'ajouter la colonne. Arrêt.")
                    return 1
            else:
                logger.info("ℹ️ Colonne meta_data déjà présente")
            
            # Étape 2: Migrer les données existantes
            logger.info("🔄 Migration des données existantes...")
            migration_result = migrate_existing_data(conn)
            logger.info(f"✅ {migration_result['migrated']} transactions migrées")
            if migration_result['errors'] > 0:
                logger.warning(f"⚠️ {migration_result['errors']} erreurs lors de la migration")
            
            # Étape 3: Générer le rapport
            logger.info("📊 Génération du rapport...")
            report = generate_report(conn)
            
            print("\n" + "=" * 60)
            print("RAPPORT DE MIGRATION")
            print("=" * 60)
            print(f"Total transactions: {report['total_transactions']}")
            print(f"Avec métadonnées: {report['with_metadata']}")
            print(f"Sans métadonnées: {report['without_metadata']}")
            print(f"Couverture: {report['coverage_percent']}%")
            print("=" * 60)
            
            logger.info("✅ Migration terminée avec succès!")
            return 0
            
    except Exception as e:
        logger.error(f"❌ Erreur fatale lors de la migration: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
