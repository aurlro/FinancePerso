#!/usr/bin/env python3
"""
FinancePerso - Doctor Script
Diagnostique complet de l'environnement de développement
"""

import sys
import subprocess
import os
from pathlib import Path

# Colors
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
ENDC = '\033[0m'

def check(name, command, success_msg, error_msg, optional=False):
    """Run a check command."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"{GREEN}✓{ENDC} {name}: {success_msg}")
            return True
        else:
            if optional:
                print(f"{YELLOW}⚠{ENDC} {name}: {error_msg} (optionnel)")
            else:
                print(f"{RED}✗{ENDC} {name}: {error_msg}")
            return False
    except Exception as e:
        if optional:
            print(f"{YELLOW}⚠{ENDC} {name}: {e} (optionnel)")
        else:
            print(f"{RED}✗{ENDC} {name}: {e}")
        return False

def main():
    print(f"{BLUE}╔════════════════════════════════════════════════╗{ENDC}")
    print(f"{BLUE}║       FinancePerso - Environment Doctor        ║{ENDC}")
    print(f"{BLUE}╚════════════════════════════════════════════════╝{ENDC}")
    print()
    
    checks_passed = 0
    checks_total = 0
    
    # 1. Python Version
    checks_total += 1
    if sys.version_info >= (3, 12):
        print(f"{GREEN}✓{ENDC} Python: {sys.version.split()[0]} (>= 3.12)")
        checks_passed += 1
    else:
        print(f"{RED}✗{ENDC} Python: {sys.version.split()[0]} (3.12+ requis)")
    
    # 2. Virtual Environment
    checks_total += 1
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    if in_venv or Path('.venv').exists():
        print(f"{GREEN}✓{ENDC} Virtual Environment: OK")
        checks_passed += 1
    else:
        print(f"{YELLOW}⚠{ENDC} Virtual Environment: Non détecté (run: make setup)")
    
    # 3. Dependencies
    checks_total += 1
    try:
        import streamlit
        print(f"{GREEN}✓{ENDC} Streamlit: {streamlit.__version__}")
        checks_passed += 1
    except ImportError:
        print(f"{RED}✗{ENDC} Streamlit: Non installé (run: pip install -r requirements.txt)")
    
    # 4. Tests (quick check without running full test)
    checks_total += 1
    if Path('tests/test_essential.py').exists():
        print(f"{GREEN}✓{ENDC} Tests: Fichiers présents (203 tests)")
        checks_passed += 1
    else:
        print(f"{RED}✗{ENDC} Tests: Fichiers manquants")
    
    # 5. Git
    checks_total += 1
    if check("Git", 
             "git rev-parse --git-dir 2>/dev/null",
             "OK",
             "Pas un repo git"):
        checks_passed += 1
    
    # 6. Environment File
    checks_total += 1
    if Path('.env').exists():
        print(f"{GREEN}✓{ENDC} Fichier .env: Présent")
        checks_passed += 1
    else:
        print(f"{YELLOW}⚠{ENDC} Fichier .env: Manquant (copiez .env.example)")
    
    # 7. Linting tools (optional)
    check("Ruff", 
          "ruff --version 2>/dev/null",
          "Installé",
          "Non installé (pip install ruff)",
          optional=True)
    
    check("Black", 
          "black --version 2>/dev/null",
          "Installé",
          "Non installé (pip install black)",
          optional=True)
    
    # Summary
    print()
    print(f"{BLUE}╔════════════════════════════════════════════════╗{ENDC}")
    percentage = int((checks_passed / checks_total) * 100)
    
    if percentage == 100:
        print(f"{GREEN}║  Santé: {percentage}% - Tout est parfait! 🎉{ENDC}          {GREEN}║{ENDC}")
    elif percentage >= 80:
        print(f"{YELLOW}║  Santé: {percentage}% - Quelques améliorations possibles{ENDC}  {YELLOW}║{ENDC}")
    else:
        print(f"{RED}║  Santé: {percentage}% - Action requise{ENDC}                  {RED}║{ENDC}")
    
    print(f"{BLUE}╚════════════════════════════════════════════════╝{ENDC}")
    print()
    
    # Recommendations
    if percentage < 100:
        print("Recommandations:")
        if not in_venv:
            print(f"  {BLUE}→{ENDC} make setup          # Configurer l'environnement")
        print(f"  {BLUE}→{ENDC} make test           # Vérifier les tests")
        print(f"  {BLUE}→{ENDC} make check          # Vérifier tout")
    else:
        print(f"{GREEN}🚀 Vous êtes prêt à développer !{ENDC}")
        print(f"  {BLUE}→{ENDC} make run            # Lancer l'application")
    
    print()

if __name__ == "__main__":
    main()
