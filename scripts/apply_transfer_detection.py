# -*- coding: utf-8 -*-
"""
Script d'application de la détection des transferts sur les données existantes.

Ce script permet d'appliquer la nouvelle logique de détection des transferts
sur toutes les transactions existantes dans la base de données.

Usage:
    python scripts/apply_transfer_detection.py [--dry-run] [--reset]

Options:
    --dry-run   Affiche les changements sans les appliquer
    --reset     Réinitialise les catégories des transferts existants avant application
"""

import argparse
import sys

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, "/Users/aurelien/Documents/Projets/FinancePerso")

from modules.db.connection import get_db_connection
from modules.db.migrations import init_db
from modules.db.transactions import bulk_update_transaction_status
from modules.logger import logger
from modules.transfer_detection import detect_transfer_type, get_transfer_summary


def get_affected_transactions(reset: bool = False):
    """
    Récupère les transactions qui seront affectées par la détection.
    
    Args:
        reset: Si True, inclut aussi les transactions déjà catégorisées comme transferts
        
    Returns:
        Liste des transactions à traiter
    """
    with get_db_connection() as conn:
        if reset:
            # Inclut les transactions déjà marquées comme transferts
            query = """
                SELECT id, label, account_label, category_validated
                FROM transactions
                WHERE label IS NOT NULL
                AND category_validated NOT IN ('Hors Budget', 'Inconnu')
            """
        else:
            # Exclut les transactions déjà catégorisées comme transferts
            query = """
                SELECT id, label, account_label, category_validated
                FROM transactions
                WHERE category_validated NOT IN ('Virement Interne', 'Contribution Partenaire', 'Hors Budget')
                AND label IS NOT NULL
            """
        
        import pandas as pd
        return pd.read_sql(query, conn)


def apply_detection(dry_run: bool = False, reset: bool = False):
    """
    Applique la détection des transferts sur toutes les transactions.
    
    Args:
        dry_run: Si True, affiche les changements sans les appliquer
        reset: Si True, réinitialise les catégories des transferts existants
    """
    print("=" * 60)
    print("Application de la détection des transferts")
    print("=" * 60)
    
    if dry_run:
        print("\n⚠️  MODE DRY-RUN : Aucune modification ne sera appliquée\n")
    
    # Récupère les transactions à traiter
    df = get_affected_transactions(reset=reset)
    
    if df.empty:
        print("Aucune transaction à traiter.")
        return
    
    print(f"\n{len(df)} transactions à analyser...")
    
    # Analyse chaque transaction
    changes = []
    
    for _, row in df.iterrows():
        detected = detect_transfer_type(row["label"], row.get("account_label"))
        current_cat = row["category_validated"]
        
        if detected and detected != current_cat:
            changes.append({
                "id": row["id"],
                "label": row["label"][:50],  # Truncate for display
                "current": current_cat,
                "new": detected,
            })
    
    if not changes:
        print("\n✅ Aucune modification nécessaire.")
        return
    
    # Affiche les changements
    print(f"\n{len(changes)} transactions seront modifiées :\n")
    print(f"{'ID':<8} {'Label':<50} {'Actuel':<25} {'Nouveau':<25}")
    print("-" * 110)
    
    for change in changes:
        print(f"{change['id']:<8} {change['label']:<50} {change['current']:<25} {change['new']:<25}")
    
    # Applique les changements
    if not dry_run:
        print("\n📝 Application des changements...")
        
        # Groupe par catégorie pour mise à jour en batch
        by_category = {}
        for change in changes:
            cat = change["new"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(change["id"])
        
        total_updated = 0
        for category, tx_ids in by_category.items():
            try:
                bulk_update_transaction_status(tx_ids, category)
                total_updated += len(tx_ids)
                print(f"  ✓ {len(tx_ids):4d} transactions → {category}")
            except Exception as e:
                logger.error(f"Erreur lors de la mise à jour en batch pour {category}: {e}")
                print(f"  ✗ Erreur pour {category}: {e}")
        
        print(f"\n✅ {total_updated} transactions mises à jour avec succès.")
    else:
        print(f"\n💡 Mode dry-run : {len(changes)} transactions auraient été modifiées.")
    
    # Affiche le résumé des transferts
    print("\n" + "=" * 60)
    print("Résumé des transferts après application")
    print("=" * 60)
    
    summary = get_transfer_summary()
    print(f"\nVirements internes      : {len(summary['internal_transfers'])} transactions")
    print(f"Contributions partenaire : {len(summary['partner_contributions'])} transactions")
    print(f"\nMontant total virements internes : {summary['total_internal']:,.2f} €")
    print(f"Montant total contributions      : {summary['total_contributions']:,.2f} €")


def main():
    parser = argparse.ArgumentParser(
        description="Applique la détection des transferts sur les transactions existantes"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Affiche les changements sans les appliquer",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Réinitialise les catégories des transferts existants avant application",
    )
    
    args = parser.parse_args()
    
    # Initialise la base de données (crée les nouvelles catégories si nécessaire)
    print("Initialisation de la base de données...")
    init_db()
    
    # Applique la détection
    apply_detection(dry_run=args.dry_run, reset=args.reset)


if __name__ == "__main__":
    main()
