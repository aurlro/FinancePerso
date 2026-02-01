#!/usr/bin/env python3
"""Script de migration: remplace print() par logger dans les fichiers modules."""

import re
import sys
from pathlib import Path

# Fichiers à exclure (CLI tools, scripts de debug)
EXCLUDE = [
    "cache_monitor.py",
    "benchmark.py",
    "profile_db.py",
    "check_models.py",
    "versioning.py",
    "audit_redux.py",
    "test_*.py",
]

def should_process(filepath: Path) -> bool:
    """Vérifie si le fichier doit être traité."""
    name = filepath.name
    for pattern in EXCLUDE:
        if pattern.endswith("*.py"):
            if name.startswith(pattern.replace("*.py", "")):
                return False
        elif name == pattern:
            return False
    return True

def migrate_file(filepath: Path) -> int:
    """Migre un fichier: remplace print() par logger."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    changes = 0
    
    # Vérifier si déjà importé
    has_logger_import = 'from modules.logger import' in content or 'import modules.logger' in content
    
    # Regex pour trouver print() en début de ligne (pas dans une string/docstring)
    # Capture les patterns: print(f"..."), print("..."), print('...'), print(var)
    print_pattern = r'^(\s*)print\((.+?)\)$'
    
    lines = content.split('\n')
    new_lines = []
    in_multiline_string = False
    string_delimiter = None
    
    for i, line in enumerate(lines):
        # Détection basique des multiline strings
        if '"""' in line or "'''" in line:
            in_multiline_string = not in_multiline_string
        
        if in_multiline_string:
            new_lines.append(line)
            continue
        
        match = re.match(print_pattern, line)
        if match:
            indent = match.group(1)
            args = match.group(2)
            
            # Déterminer le niveau de log
            lower_args = args.lower()
            if any(word in lower_args for word in ['error', 'erreur', 'exception', 'failed', 'echec']):
                level = 'error'
            elif any(word in lower_args for word in ['warning', 'warn', 'attention', 'alert']):
                level = 'warning'
            else:
                level = 'info'
            
            # Remplacer
            new_line = f'{indent}logger.{level}({args})'
            new_lines.append(new_line)
            changes += 1
        else:
            new_lines.append(line)
    
    if changes > 0 and not has_logger_import:
        # Ajouter l'import après les autres imports
        content = '\n'.join(new_lines)
        # Trouver la ligne pour insérer l'import
        import_idx = 0
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                import_idx = i + 1
        
        lines.insert(import_idx, 'from modules.logger import logger')
        content = '\n'.join(lines)
    else:
        content = '\n'.join(new_lines)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return changes

def main():
    modules_dir = Path('modules')
    total_changes = 0
    files_modified = 0
    
    for pyfile in modules_dir.rglob('*.py'):
        if should_process(pyfile):
            changes = migrate_file(pyfile)
            if changes > 0:
                print(f"✓ {pyfile}: {changes} print() migré(s)")
                total_changes += changes
                files_modified += 1
    
    print(f"\n{'='*50}")
    print(f"Migration terminée!")
    print(f"Fichiers modifiés: {files_modified}")
    print(f"Total print() → logger: {total_changes}")

if __name__ == '__main__':
    main()
