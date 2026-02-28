#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Documentation - FinancePerso

Ce script est appelé automatiquement après chaque changement majeur
du code pour maintenir la documentation à jour.

Usage:
    python .agents/doc_agent.py --check     # Vérifie la cohérence doc/code
    python .agents/doc_agent.py --update    # Met à jour la documentation
    python .agents/doc_agent.py --generate  # Génère nouvelle documentation
"""

import argparse
import os
import re
from datetime import datetime
from pathlib import Path


class DocumentationAgent:
    """Agent responsable de maintenir la documentation à jour."""
    
    def __init__(self):
        self.project_root = Path("/Users/aurelien/Documents/Projets/FinancePerso")
        self.docs_dir = self.project_root / "docs"
        self.changes_log = []
    
    def check_consistency(self) -> dict:
        """Vérifie la cohérence entre le code et la documentation."""
        issues = []
        
        # Vérifier que AGENTS.md existe
        agents_md = self.project_root / "AGENTS.md"
        if not agents_md.exists():
            issues.append("❌ AGENTS.md manquant")
        else:
            # Vérifier que la version dans AGENTS.md correspond
            content = agents_md.read_text()
            if "modules/notifications" in content and "notifications V3" not in content:
                issues.append("⚠️ AGENTS.md: notifications V3 non documenté")
        
        # Vérifier que le CHANGELOG existe
        changelog = self.project_root / "CHANGELOG.md"
        if not changelog.exists():
            issues.append("❌ CHANGELOG.md manquant")
        
        # Vérifier que les migrations sont documentées
        migrations = list((self.project_root / "migrations").glob("*.sql"))
        migration_doc = self.docs_dir / "MIGRATIONS.md"
        if not migration_doc.exists() and len(migrations) > 5:
            issues.append("⚠️ Documentation des migrations manquante")
        
        # Vérifier la documentation des modules
        modules_dir = self.project_root / "modules"
        for module_path in modules_dir.iterdir():
            if module_path.is_dir() and not (module_path / "README.md").exists():
                if module_path.name in ["notifications", "ai", "db"]:
                    issues.append(f"⚠️ README.md manquant pour {module_path.name}/")
        
        return {
            "status": "ok" if not issues else "issues_found",
            "issues": issues,
            "checked_files": len(list(self.docs_dir.rglob("*.md")))
        }
    
    def update_changelog(self, change_type: str, description: str) -> bool:
        """Ajoute une entrée au CHANGELOG."""
        changelog = self.project_root / "CHANGELOG.md"
        
        if not changelog.exists():
            return False
        
        today = datetime.now().strftime("%Y-%m-%d")
        entry = f"\n- [{change_type}] {description} ({today})"
        
        # Lire et insérer après la ligne "## Unreleased"
        content = changelog.read_text()
        if "## Unreleased" in content:
            content = content.replace(
                "## Unreleased\n",
                f"## Unreleased\n{entry}"
            )
            changelog.write_text(content)
            return True
        return False
    
    def update_agents_md(self, section: str, content: str) -> bool:
        """Met à jour une section de AGENTS.md."""
        agents_md = self.project_root / "AGENTS.md"
        
        if not agents_md.exists():
            return False
        
        # TODO: Implémenter la mise à jour de section
        return True
    
    def generate_module_doc(self, module_name: str) -> str:
        """Génère la documentation pour un module."""
        module_path = self.project_root / "modules" / module_name
        
        if not module_path.exists():
            return ""
        
        # Compter les lignes de code
        total_lines = 0
        py_files = list(module_path.rglob("*.py"))
        
        for f in py_files:
            try:
                total_lines += len(f.read_text().splitlines())
            except:
                pass
        
        # Générer README
        readme_content = f"""# Module {module_name}

**Généré le:** {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Vue d'ensemble

- **Fichiers:** {len(py_files)}
- **Lignes de code:** ~{total_lines}

## Structure

"""
        
        for f in sorted(py_files):
            rel_path = f.relative_to(module_path)
            readme_content += f"- `{rel_path}`\n"
        
        readme_content += "\n## Usage\n\n```python\n"
        readme_content += f"from modules.{module_name} import ...\n"
        readme_content += "```\n"
        
        return readme_content
    
    def run_full_check(self) -> str:
        """Exécute une vérification complète."""
        result = self.check_consistency()
        
        report = f"""
{'='*60}
📚 RAPPORT DE VÉRIFICATION DOCUMENTATION
{'='*60}

Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

RÉSULTAT: {result['status'].upper()}

Fichiers vérifiés: {result['checked_files']}

"""
        
        if result['issues']:
            report += "\nPROBLÈMES DÉTECTÉS:\n"
            for issue in result['issues']:
                report += f"  {issue}\n"
        else:
            report += "\n✅ Tous les contrôles sont passés !\n"
        
        report += "\n" + "="*60 + "\n"
        
        return report


def main():
    parser = argparse.ArgumentParser(description="Agent Documentation")
    parser.add_argument("--check", action="store_true", help="Vérifie la cohérence")
    parser.add_argument("--update", action="store_true", help="Met à jour la documentation")
    parser.add_argument("--generate", metavar="MODULE", help="Génère la doc pour un module")
    
    args = parser.parse_args()
    
    agent = DocumentationAgent()
    
    if args.check:
        print(agent.run_full_check())
    
    elif args.update:
        print(agent.run_full_check())
        print("\n📝 Mise à jour de la documentation...")
        # TODO: Implémenter les mises à jour automatiques
        print("✅ Terminé")
    
    elif args.generate:
        module = args.generate
        doc = agent.generate_module_doc(module)
        output_path = agent.project_root / "modules" / module / "README.md"
        output_path.write_text(doc)
        print(f"✅ Documentation générée: {output_path}")
    
    else:
        # Mode par défaut: vérification rapide
        print(agent.run_full_check())


if __name__ == "__main__":
    main()
