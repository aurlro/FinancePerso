#!/usr/bin/env python3
"""
Audit complet de la codebase FinancePerso.
Génère un rapport de santé détaillé.
Usage: python scripts/audit_codebase.py
"""
import os
import re
import sys
from pathlib import Path
from collections import defaultdict
import ast

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
IGNORE_DIRS = {'.venv', '__pycache__', '.git', 'legacy', 'node_modules'}
MAX_FILE_LINES = 150

class CodebaseAuditor:
    """Auditeur complet de la codebase."""
    
    def __init__(self):
        self.issues = defaultdict(list)
        self.metrics = {}
        
    def run_full_audit(self):
        """Lance l'audit complet."""
        print("🔍 Audit de la codebase FinancePerso")
        print("=" * 70)
        
        self._audit_backup_files()
        self._audit_python_files()
        self._audit_imports()
        self._audit_session_state()
        self._audit_file_sizes()
        self._audit_tests()
        
        self._print_report()
        return len(self.issues) == 0
    
    def _audit_backup_files(self):
        """Détecte les fichiers backup."""
        backups = list(PROJECT_ROOT.rglob("*.backup*"))
        backups.extend(PROJECT_ROOT.rglob("*backup*.py"))
        
        self.metrics['backup_files'] = len(backups)
        if backups:
            self.issues['backup_files'] = [str(b.relative_to(PROJECT_ROOT)) for b in backups[:10]]
    
    def _audit_python_files(self):
        """Audit des fichiers Python."""
        py_files = list(PROJECT_ROOT.rglob("*.py"))
        py_files = [f for f in py_files if not any(ign in str(f) for ign in IGNORE_DIRS)]
        
        self.metrics['python_files'] = len(py_files)
        
        # Fichiers avec imports inline
        inline_imports = []
        for f in py_files:
            content = f.read_text(encoding='utf-8')
            if re.search(r'^(\s+)(import|from)\s+', content, re.MULTILINE):
                inline_imports.append(f.relative_to(PROJECT_ROOT))
        
        self.metrics['inline_imports'] = len(inline_imports)
        if inline_imports:
            self.issues['inline_imports'] = [str(p) for p in inline_imports[:10]]
    
    def _audit_imports(self):
        """Audit des imports circulaires potentiels."""
        circular_suspects = []
        
        # Détection simple : fichiers qui s'importent mutuellement
        imports_map = defaultdict(list)
        
        for py_file in PROJECT_ROOT.rglob("*.py"):
            if any(ign in str(py_file) for ign in IGNORE_DIRS):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                imports = re.findall(r'from modules\.(\w+)\.', content)
                for imp in imports:
                    imports_map[py_file.stem].append(imp)
            except:
                continue
        
        # Chercher les cycles simples A -> B -> A
        for file_a, imports_a in imports_map.items():
            for imp in imports_a:
                if imp in imports_map and file_a in imports_map[imp]:
                    circular_suspects.append(f"{file_a} <-> {imp}")
        
        self.metrics['circular_imports'] = len(circular_suspects)
        if circular_suspects:
            self.issues['circular_imports'] = list(set(circular_suspects))[:5]
    
    def _audit_session_state(self):
        """Audit des clés de session state."""
        session_keys = set()
        
        for py_file in PROJECT_ROOT.rglob("*.py"):
            if any(ign in str(py_file) for ign in IGNORE_DIRS):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                # Détecte st.session_state['key'] ou st.session_state.get('key')
                keys = re.findall(r"session_state\[['\"]([^'\"]+)['\"]\]", content)
                keys.extend(re.findall(r"session_state\.get\(['\"]([^'\"]+)['\"]", content))
                session_keys.update(keys)
            except:
                continue
        
        self.metrics['session_state_keys'] = len(session_keys)
        
        # Clés problématiques (non préfixées)
        bad_keys = [k for k in session_keys if not any(k.startswith(p) for p in ['audit_', 'dashboard_', 'chat_', 'config_'])]
        if bad_keys:
            self.issues['unprefixed_session_keys'] = bad_keys[:10]
    
    def _audit_file_sizes(self):
        """Audit des tailles de fichiers."""
        large_files = []
        
        for py_file in PROJECT_ROOT.rglob("*.py"):
            if any(ign in str(py_file) for ign in IGNORE_DIRS):
                continue
            if 'pages/' not in str(py_file):  # Les pages peuvent être grandes
                continue
            
            try:
                lines = len(py_file.read_text(encoding='utf-8').splitlines())
                if lines > MAX_FILE_LINES:
                    large_files.append((py_file.relative_to(PROJECT_ROOT), lines))
            except:
                continue
        
        self.metrics['large_files'] = len(large_files)
        if large_files:
            self.issues['large_files'] = [f"{f[0]}: {f[1]} lignes" for f in sorted(large_files, key=lambda x: x[1], reverse=True)[:5]]
    
    def _audit_tests(self):
        """Audit des tests."""
        test_files = list((PROJECT_ROOT / "tests").rglob("test_*.py"))
        
        self.metrics['test_files'] = len(test_files)
        
        # Vérifier la présence de conftest.py
        has_conftest = (PROJECT_ROOT / "tests" / "conftest.py").exists()
        self.metrics['has_conftest'] = has_conftest
        
        if not has_conftest:
            self.issues['missing_conftest'] = ["tests/conftest.py manquant"]
    
    def _print_report(self):
        """Affiche le rapport final."""
        print("\n📊 MÉTRIQUES")
        print("-" * 70)
        for key, value in self.metrics.items():
            status = "✅" if self._is_metric_good(key, value) else "⚠️"
            print(f"{status} {key.replace('_', ' ').title()}: {value}")
        
        if self.issues:
            print("\n❌ PROBLÈMES DÉTECTÉS")
            print("-" * 70)
            for category, items in self.issues.items():
                print(f"\n{category.replace('_', ' ').title()} ({len(items)} items):")
                for item in items[:5]:  # Limiter l'affichage
                    print(f"  • {item}")
                if len(items) > 5:
                    print(f"  ... et {len(items) - 5} autres")
        else:
            print("\n✅ Aucun problème majeur détecté!")
        
        # Score global
        score = self._calculate_score()
        print(f"\n🏆 Score de santé: {score}/100")
        
        if score >= 80:
            print("🟢 Excellente santé")
        elif score >= 60:
            print("🟡 Santé acceptable - Améliorations possibles")
        else:
            print("🔴 Santé préoccupante - Action requise")
    
    def _is_metric_good(self, key, value):
        """Détermine si une métrique est bonne."""
        thresholds = {
            'backup_files': (0, 0),
            'inline_imports': (0, 10),
            'circular_imports': (0, 0),
            'large_files': (0, 5),
            'has_conftest': (True, True),
        }
        
        if key in thresholds:
            min_good, max_acceptable = thresholds[key]
            if isinstance(value, bool):
                return value == min_good
            return min_good <= value <= max_acceptable
        return True
    
    def _calculate_score(self):
        """Calcule un score global de santé."""
        score = 100
        
        # Pénalités
        score -= min(self.metrics.get('backup_files', 0) * 2, 30)
        score -= min(self.metrics.get('inline_imports', 0), 20)
        score -= self.metrics.get('circular_imports', 0) * 10
        score -= min(self.metrics.get('large_files', 0) * 2, 20)
        
        if not self.metrics.get('has_conftest', False):
            score -= 10
        
        return max(0, score)


def main():
    auditor = CodebaseAuditor()
    success = auditor.run_full_audit()
    
    # Générer un fichier de rapport
    report_path = PROJECT_ROOT / "logs" / "audit_report.txt"
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, 'w') as f:
        f.write("Audit Report - FinancePerso\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Score: {auditor._calculate_score()}/100\n\n")
        f.write("Metrics:\n")
        for key, value in auditor.metrics.items():
            f.write(f"  {key}: {value}\n")
        f.write("\nIssues:\n")
        for category, items in auditor.issues.items():
            f.write(f"\n{category}:\n")
            for item in items:
                f.write(f"  - {item}\n")
    
    print(f"\n📝 Rapport sauvegardé dans: {report_path}")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
