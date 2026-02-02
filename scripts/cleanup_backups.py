#!/usr/bin/env python3
"""
Script de nettoyage des fichiers backup.
Déplace les backups dans legacy/ ou les supprime si identiques.
Usage: python scripts/cleanup_backups.py [--dry-run] [--force]
"""
import os
import sys
import shutil
import filecmp
import argparse
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
LEGACY_DIR = PROJECT_ROOT / "legacy" / "backups"


def find_backup_files():
    """Trouve tous les fichiers backup."""
    patterns = ['*.backup*', '*_backup*', '*.bak', '*~']
    backups = []
    
    for pattern in patterns:
        backups.extend(PROJECT_ROOT.rglob(pattern))
    
    # Exclure les dossiers spéciaux
    exclude_dirs = {'.venv', '__pycache__', '.git', 'legacy', 'node_modules', '.pytest_cache'}
    backups = [b for b in backups if not any(ex in str(b) for ex in exclude_dirs)]
    
    return sorted(set(backups))


def get_original_file(backup_path):
    """Tente de trouver le fichier original correspondant au backup."""
    name = backup_path.name
    parent = backup_path.parent
    
    # Patterns possibles : file.py.backup, file_backup.py, file.py.bak, file~
    if '.backup' in name:
        original_name = name.split('.backup')[0]
    elif '_backup' in name:
        original_name = name.replace('_backup', '').replace('__', '_')
    elif name.endswith('.bak'):
        original_name = name[:-4]
    elif name.endswith('~'):
        original_name = name[:-1]
    else:
        return None
    
    original = parent / original_name
    if original.exists():
        return original
    
    # Essayer avec .py si pas d'extension
    if not original_name.endswith('.py'):
        original = parent / (original_name + '.py')
        if original.exists():
            return original
    
    return None


def analyze_backup(backup_path):
    """Analyse un fichier backup et retourne la recommandation."""
    original = get_original_file(backup_path)
    
    if not original:
        return {
            'status': 'orphan',
            'action': 'archive',  # Pas de fichier original trouvé
            'reason': f"Fichier original non trouvé pour {backup_path.name}"
        }
    
    if filecmp.cmp(str(backup_path), str(original), shallow=False):
        return {
            'status': 'identical',
            'action': 'delete',
            'reason': f"Identique à {original.name}"
        }
    
    # Comparer les dates
    backup_mtime = datetime.fromtimestamp(backup_path.stat().st_mtime)
    original_mtime = datetime.fromtimestamp(original.stat().st_mtime)
    
    if backup_mtime > original_mtime:
        return {
            'status': 'newer',
            'action': 'review',  # Le backup est plus récent !
            'reason': f"⚠️  PLUS RÉCENT que {original.name} ({backup_mtime} vs {original_mtime})"
        }
    
    return {
        'status': 'older',
        'action': 'archive',
        'reason': f"Version ancienne de {original.name}"
    }


def main():
    parser = argparse.ArgumentParser(
        description='Nettoie les fichiers backup du projet'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Affiche ce qui serait fait sans exécuter'
    )
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Exécute sans confirmation'
    )
    parser.add_argument(
        '--archive-only',
        action='store_true',
        help='Archive uniquement, ne supprime jamais'
    )
    
    args = parser.parse_args()
    
    print("🧹 Nettoyage des fichiers backup")
    print("=" * 70)
    
    # Trouver tous les backups
    backups = find_backup_files()
    
    if not backups:
        print("✅ Aucun fichier backup trouvé!")
        return 0
    
    print(f"📁 {len(backups)} fichier(s) backup trouvé(s)\n")
    
    # Analyser chaque backup
    analysis = []
    for backup in backups:
        info = analyze_backup(backup)
        info['path'] = backup
        info['relative'] = backup.relative_to(PROJECT_ROOT)
        analysis.append(info)
    
    # Grouper par action
    to_delete = [a for a in analysis if a['action'] == 'delete']
    to_archive = [a for a in analysis if a['action'] == 'archive']
    to_review = [a for a in analysis if a['action'] == 'review']
    
    # Afficher le rapport
    if to_delete:
        print(f"🗑️  {len(to_delete)} fichier(s) à SUPPRIMER (identiques):")
        for item in to_delete:
            print(f"   • {item['relative']}")
            print(f"     → {item['reason']}")
        print()
    
    if to_archive:
        print(f"📦 {len(to_archive)} fichier(s) à ARCHIVER:")
        for item in to_archive:
            print(f"   • {item['relative']}")
            print(f"     → {item['reason']}")
        print()
    
    if to_review:
        print(f"⚠️  {len(to_review)} fichier(s) à VÉRIFIER (backup plus récent!):")
        for item in to_review:
            print(f"   • {item['relative']}")
            print(f"     → {item['reason']}")
        print()
    
    if args.dry_run:
        print("🔍 Mode DRY-RUN - Aucune action effectuée")
        return 0
    
    # Confirmation
    if not args.force:
        response = input("\nContinuer? [o/N]: ").lower().strip()
        if response not in ['o', 'oui', 'y', 'yes']:
            print("❌ Annulé")
            return 1
    
    # Exécution
    print("\n🚀 Exécution...")
    
    # Créer le dossier legacy s'il n'existe pas
    if not args.dry_run:
        LEGACY_DIR.mkdir(parents=True, exist_ok=True)
    
    deleted_count = 0
    archived_count = 0
    errors = []
    
    # Traiter les suppressions
    for item in to_delete:
        if args.archive_only:
            # Archiver au lieu de supprimer
            try:
                dest = LEGACY_DIR / item['path'].name
                shutil.move(str(item['path']), str(dest))
                archived_count += 1
                print(f"📦 Archivé: {item['relative']}")
            except Exception as e:
                errors.append(f"Erreur archivage {item['relative']}: {e}")
        else:
            # Supprimer
            try:
                item['path'].unlink()
                deleted_count += 1
                print(f"🗑️  Supprimé: {item['relative']}")
            except Exception as e:
                errors.append(f"Erreur suppression {item['relative']}: {e}")
    
    # Traiter les archivages
    for item in to_archive:
        try:
            dest = LEGACY_DIR / item['path'].name
            # Gérer les collisions de noms
            counter = 1
            while dest.exists():
                stem = item['path'].stem
                suffix = item['path'].suffix
                dest = LEGACY_DIR / f"{stem}_{counter}{suffix}"
                counter += 1
            
            shutil.move(str(item['path']), str(dest))
            archived_count += 1
            print(f"📦 Archivé: {item['relative']}")
        except Exception as e:
            errors.append(f"Erreur archivage {item['relative']}: {e}")
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ")
    print(f"   🗑️  Supprimés: {deleted_count}")
    print(f"   📦 Archivés: {archived_count}")
    print(f"   ⚠️  À vérifier manuellement: {len(to_review)}")
    
    if errors:
        print(f"\n❌ {len(errors)} erreur(s):")
        for error in errors:
            print(f"   • {error}")
        return 1
    
    if to_review:
        print(f"\n⚠️  {len(to_review)} fichier(s) nécessitent une vérification manuelle.")
        print("   Ils sont plus récents que les fichiers originaux!")
        print(f"   Vérifiez dans: {LEGACY_DIR}")
    
    print("\n✅ Terminé!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
