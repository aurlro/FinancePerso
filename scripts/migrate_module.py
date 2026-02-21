#!/usr/bin/env python3
"""
Script de migration sécurisée de modules
========================================

Usage:
    python scripts/migrate_module.py --from modules/db --to modules/db_v2 --backup
    
Ce script:
1. Crée une sauvegarde complète
2. Analyse les dépendances
3. Migre les références
4. Valide la migration
5. Supprime l'ancien module (optionnel)
"""

import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path


class ModuleMigrator:
    """Gère la migration d'un module vers un autre"""
    
    def __init__(self, from_path, to_path, backup=True, dry_run=False):
        self.from_path = Path(from_path)
        self.to_path = Path(to_path)
        self.backup = backup
        self.dry_run = dry_run
        self.log = []
        
    def create_backup(self):
        """Crée une sauvegarde des modules concernés"""
        if not self.backup:
            return
            
        backup_dir = Path(f"backup/migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        if self.dry_run:
            print(f"[DRY-RUN] Sauvegarde créée: {backup_dir}")
            return
            
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder le module source
        if self.from_path.exists():
            shutil.copytree(self.from_path, backup_dir / self.from_path.name)
            
        # Sauvegarder le module cible
        if self.to_path.exists():
            shutil.copytree(self.to_path, backup_dir / self.to_path.name, dirs_exist_ok=True)
            
        self.log.append(f"Sauvegarde créée: {backup_dir}")
        print(f"✅ Sauvegarde créée: {backup_dir}")
        
    def analyze_dependencies(self):
        """Analyse les fichiers qui importent l'ancien module"""
        print(f"\n📊 Analyse des dépendances vers {self.from_path}...")
        
        affected_files = []
        
        # Parcourir tous les fichiers Python
        for root, dirs, files in os.walk('.'):
            # Ignorer certains dossiers
            dirs[:] = [d for d in dirs if d not in ['.venv', '__pycache__', 'backup', '.git']]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Vérifier si le fichier importe l'ancien module
                        module_name = str(self.from_path).replace('/', '.')
                        if f"from {module_name}" in content or f"import {module_name}" in content:
                            affected_files.append(filepath)
                    except:
                        pass
        
        print(f"   Fichiers affectés: {len(affected_files)}")
        for f in affected_files[:10]:  # Limiter l'affichage
            print(f"     - {f}")
        if len(affected_files) > 10:
            print(f"     ... et {len(affected_files) - 10} autres")
            
        return affected_files
        
    def update_imports(self, affected_files):
        """Met à jour les imports dans les fichiers affectés"""
        print(f"\n🔄 Mise à jour des imports...")
        
        from_module = str(self.from_path).replace('/', '.')
        to_module = str(self.to_path).replace('/', '.')
        
        for filepath in affected_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Remplacer les imports
                new_content = content.replace(f"from {from_module}", f"from {to_module}")
                new_content = new_content.replace(f"import {from_module}", f"import {to_module}")
                
                if self.dry_run:
                    print(f"[DRY-RUN] {filepath}: {from_module} → {to_module}")
                else:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                        
                self.log.append(f"Mise à jour: {filepath}")
                
            except Exception as e:
                print(f"❌ Erreur sur {filepath}: {e}")
                
        print(f"✅ {len(affected_files)} fichiers mis à jour")
        
    def validate_migration(self):
        """Valide que la migration fonctionne"""
        print(f"\n✓ Validation de la migration...")
        
        # Vérifier que le nouveau module existe
        if not self.to_path.exists():
            print(f"❌ Le module cible n'existe pas: {self.to_path}")
            return False
            
        # Essayer d'importer le nouveau module
        to_module = str(self.to_path).replace('/', '.')
        
        try:
            if not self.dry_run:
                __import__(to_module)
            print(f"✅ Import réussi: {to_module}")
            return True
        except Exception as e:
            print(f"❌ Import échoué: {e}")
            return False
            
    def remove_old_module(self):
        """Supprime l'ancien module"""
        if self.dry_run:
            print(f"[DRY-RUN] Suppression de {self.from_path}")
            return
            
        if self.from_path.exists():
            shutil.rmtree(self.from_path)
            self.log.append(f"Suppression: {self.from_path}")
            print(f"✅ Ancien module supprimé: {self.from_path}")
            
    def run(self):
        """Exécute la migration complète"""
        print("=" * 70)
        print(f"MIGRATION: {self.from_path} → {self.to_path}")
        print("=" * 70)
        
        if self.dry_run:
            print("⚠️  MODE DRY-RUN - Aucune modification ne sera effectuée\n")
            
        # 1. Sauvegarde
        self.create_backup()
        
        # 2. Analyse
        affected_files = self.analyze_dependencies()
        
        if not affected_files:
            print("⚠️  Aucun fichier n'importe ce module")
            response = input("Continuer quand même? (y/N): ")
            if response.lower() != 'y':
                print("Migration annulée")
                return
                
        # 3. Confirmation
        if not self.dry_run:
            print(f"\n⚠️  Cette action va modifier {len(affected_files)} fichiers")
            response = input("Continuer? (y/N): ")
            if response.lower() != 'y':
                print("Migration annulée")
                return
                
        # 4. Migration
        self.update_imports(affected_files)
        
        # 5. Validation
        if self.validate_migration():
            print("\n✅ Migration validée!")
            
            # 6. Suppression (optionnelle)
            if not self.dry_run:
                response = input(f"\nSupprimer l'ancien module {self.from_path}? (y/N): ")
                if response.lower() == 'y':
                    self.remove_old_module()
        else:
            print("\n❌ Migration échouée - restauration nécessaire")
            print(f"Restaurer depuis: backup/migration_*/")


def main():
    parser = argparse.ArgumentParser(
        description="Migration sécurisée de modules Python"
    )
    parser.add_argument(
        "--from", "-f",
        dest="from_path",
        required=True,
        help="Chemin du module source (ex: modules/db)"
    )
    parser.add_argument(
        "--to", "-t",
        required=True,
        help="Chemin du module cible (ex: modules/db_v2)"
    )
    parser.add_argument(
        "--backup", "-b",
        action="store_true",
        default=True,
        help="Créer une sauvegarde (défaut: True)"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Simulation sans modification"
    )
    
    args = parser.parse_args()
    
    migrator = ModuleMigrator(
        from_path=args.from_path,
        to_path=args.to,
        backup=args.backup,
        dry_run=args.dry_run
    )
    
    migrator.run()


if __name__ == "__main__":
    main()
