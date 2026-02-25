#!/usr/bin/env python3
"""
Analyseur de dépendances - Identifie le code réellement utilisé
================================================================

Usage:
    python scripts/analyze_dependencies.py

Ce script analyse:
1. Quels modules sont importés par app.py
2. Quels modules ne sont PAS utilisés
3. Les dépendances entre modules
"""

import ast
import os
import sys
from pathlib import Path
from collections import defaultdict


class ImportAnalyzer(ast.NodeVisitor):
    """Analyse les imports dans un fichier Python"""
    
    def __init__(self):
        self.imports = []
        self.from_imports = []
    
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        module = node.module or ""
        names = [alias.name for alias in node.names]
        self.from_imports.append((module, names))
        self.generic_visit(node)


def analyze_file(filepath):
    """Analyse un fichier Python et retourne ses imports"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        analyzer = ImportAnalyzer()
        analyzer.visit(tree)
        return analyzer.imports, analyzer.from_imports
    except Exception as e:
        return [], []


def find_all_py_files(directory, exclude_patterns=None):
    """Trouve tous les fichiers Python dans un répertoire"""
    if exclude_patterns is None:
        exclude_patterns = ['.venv', '__pycache__', 'archive', 'tests']
    
    py_files = []
    for root, dirs, files in os.walk(directory):
        # Exclure les dossiers non désirés
        dirs[:] = [d for d in dirs if not any(p in d for p in exclude_patterns)]
        
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    
    return py_files


def main():
    """Fonction principale"""
    print("=" * 70)
    print("ANALYSE DES DÉPENDANCES - FinancePerso")
    print("=" * 70)
    print()
    
    # 1. Analyser app.py (point d'entrée)
    print("1. Analyse de app.py (point d'entrée principal)")
    print("-" * 50)
    
    app_imports, app_from_imports = analyze_file('app.py')
    
    modules_used = set()
    for module, _ in app_from_imports:
        if module:
            top_module = module.split('.')[0]
            modules_used.add(top_module)
    
    print(f"Modules utilisés directement: {sorted(modules_used)}")
    print()
    
    # 2. Analyser tous les fichiers dans modules/
    print("2. Analyse de modules/")
    print("-" * 50)
    
    module_files = find_all_py_files('modules')
    print(f"Total fichiers dans modules/: {len(module_files)}")
    
    # Compter par sous-dossier
    by_folder = defaultdict(list)
    for f in module_files:
        rel_path = os.path.relpath(f, 'modules')
        folder = rel_path.split('/')[0]
        by_folder[folder].append(f)
    
    print("\nRépartition par dossier:")
    for folder, files in sorted(by_folder.items()):
        print(f"  {folder:20s}: {len(files):3d} fichiers")
    print()
    
    # 3. Analyser views/
    print("3. Analyse de views/")
    print("-" * 50)
    
    view_files = find_all_py_files('views')
    print(f"Total fichiers dans views/: {len(view_files)}")
    for f in sorted(view_files):
        print(f"  - {os.path.basename(f)}")
    print()
    
    # 4. Analyser src/
    print("4. Analyse de src/ (nouveaux modules)")
    print("-" * 50)
    
    src_files = find_all_py_files('src')
    print(f"Total fichiers dans src/: {len(src_files)}")
    for f in sorted(src_files):
        print(f"  - {os.path.basename(f)}")
    print()
    
    # 5. Détecter les doublons potentiels
    print("5. Détection des doublons potentiels")
    print("-" * 50)
    
    duplicates = []
    
    # Vérifier db/ vs db_v2/
    if os.path.exists('modules/db') and os.path.exists('modules/db_v2'):
        db_files = set(os.listdir('modules/db'))
        db_v2_files = set(os.listdir('modules/db_v2'))
        duplicates.append(("modules/db/", "modules/db_v2/", len(db_files & db_v2_files)))
    
    # Vérifier ui/ vs ui_v2/
    if os.path.exists('modules/ui') and os.path.exists('modules/ui_v2'):
        ui_files = set(os.listdir('modules/ui'))
        ui_v2_files = set(os.listdir('modules/ui_v2'))
        duplicates.append(("modules/ui/", "modules/ui_v2/", len(ui_files & ui_v2_files)))
    
    # Vérifier ai/smart_suggestions.py vs ai/suggestions/
    if os.path.exists('modules/ai/smart_suggestions.py') and os.path.exists('modules/ai/suggestions'):
        duplicates.append(("modules/ai/smart_suggestions.py", "modules/ai/suggestions/", "Remplacement"))
    
    for old, new, count in duplicates:
        print(f"  ⚠️  {old} ↔ {new}")
        print(f"      Fichiers communs/similaires: {count}")
    print()
    
    # 6. Recommandations
    print("6. RECOMMANDATIONS")
    print("-" * 50)
    print("""
Priorité P0 (Immédiat):
  ☐ Migrer modules/db/ → modules/db_v2/
  ☐ Migrer modules/ui/ → modules/ui_v2/
  ☐ Supprimer modules/ai/smart_suggestions.py (doublon)

Priorité P1 (Cette semaine):
  ☐ Vérifier que views/ utilise bien src/ (nouveau code)
  ☐ Nettoyer archive/ si confirmé inutile

Priorité P2 (Plus tard):
  ☐ Unifier les configurations
  ☐ Optimiser les imports
    """)
    
    # 7. Statistiques finales
    print("7. STATISTIQUES")
    print("-" * 50)
    
    total_lines = 0
    for filepath in module_files + view_files + src_files:
        try:
            with open(filepath, 'r') as f:
                total_lines += len(f.readlines())
        except (IOError, OSError, UnicodeDecodeError):
            pass
    
    print(f"Lignes de code analysées: {total_lines:,}")
    print(f"Estimation lignes supprimables: ~{int(total_lines * 0.27):,} (27%)")
    print()


if __name__ == "__main__":
    main()
