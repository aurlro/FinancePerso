# AGENT-021: Documentation & Technical Writer

## 🎯 Mission

Rédacteur technique et créateur de documentation pour FinancePerso. Responsable de la documentation utilisateur, de la documentation API, des guides d'onboarding, et de la maintenance du changelog. Garant de la qualité et de la clarté de toute la documentation du projet.

---

## 📚 Contexte: Architecture Documentaire

### Philosophie
> "Un code bien documenté est un code maintenable. La documentation est aussi importante que le code."

### Structure de Documentation

```
docs/
├── 📖 ACTIVE/                    # Documentation maintenue
│   ├── user-guide/
│   │   ├── getting-started.md   # Guide démarrage rapide
│   │   ├── import.md            # Guide import CSV
│   │   ├── validation.md        # Guide validation
│   │   ├── budgets.md           # Guide budgets
│   │   └── faq.md               # FAQ
│   ├── development/
│   │   ├── setup.md             # Setup environnement
│   │   ├── architecture.md      # Architecture technique
│   │   └── contributing.md      # Guide contribution
│   └── api/
│       └── api-reference.md     # Référence API
│
├── 🎯 PLANNING/                  # Spécifications futures
│   ├── roadmap.md               # Roadmap produit
│   └── features/                # Specs features
│
├── 📋 REFERENCE/                 # Documentation stable
│   ├── adr/                     # Architecture Decision Records
│   ├── architecture/
│   │   ├── v5-current.md
│   │   └── v6-target.md
│   └── personas/
│       └── user-personas.md
│
└── 📦 archive/                   # Documentation historique
```

---

## 🏗️ Module 1: Générateur de Documentation

```python
# modules/docs/__init__.py
"""
Documentation Generator Module.
Génération automatique de documentation.
"""

from .generators import (
    ChangelogGenerator,
    APIDocumentationGenerator,
    UserGuideGenerator,
    OnboardingGuideGenerator
)
from .templates import DocumentTemplates
from .validators import DocumentationValidator

__all__ = [
    'ChangelogGenerator',
    'APIDocumentationGenerator',
    'UserGuideGenerator',
    'OnboardingGuideGenerator',
    'DocumentTemplates',
    'DocumentationValidator'
]
```

---

## 🧱 Module 2: Générateur de Changelog

```python
# modules/docs/changelog_generator.py

import re
import subprocess
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import json

from modules.logger import logger


class ChangeType(Enum):
    """Types de changements (Conventional Commits)."""
    FEATURE = "feat"
    FIX = "fix"
    DOCS = "docs"
    STYLE = "style"
    REFACTOR = "refactor"
    PERF = "perf"
    TEST = "test"
    CHORE = "chore"
    BREAKING = "BREAKING CHANGE"


@dataclass
class ChangeEntry:
    """Entrée de changelog."""
    type: ChangeType
    scope: Optional[str]
    description: str
    breaking: bool
    commit_hash: str
    author: str
    date: datetime


class ChangelogGenerator:
    """
    Générateur de changelog automatique.
    
    Parse les commits git et génère un CHANGELOG.md structuré.
    """
    
    # Sections du changelog
    SECTIONS = {
        ChangeType.BREAKING: "### ⚠️ BREAKING CHANGES",
        ChangeType.FEATURE: "### 🚀 Nouvelles Fonctionnalités",
        ChangeType.FIX: "### 🐛 Corrections de Bugs",
        ChangeType.PERF: "### ⚡ Performance",
        ChangeType.REFACTOR: "### 🔧 Refactoring",
        ChangeType.DOCS: "### 📚 Documentation",
        ChangeType.TEST: "### 🧪 Tests",
        ChangeType.CHORE: "### 🏗️ Maintenance",
        ChangeType.STYLE: "### 💄 Style"
    }
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
    
    def generate(
        self,
        since_tag: Optional[str] = None,
        to_tag: Optional[str] = None,
        output_path: str = "CHANGELOG.md"
    ) -> str:
        """
        Génère le changelog entre deux tags.
        
        Args:
            since_tag: Tag de départ (ex: "v5.5.0")
            to_tag: Tag de fin (ex: "v5.6.0")
            output_path: Chemin de sortie
            
        Returns:
            Contenu du changelog généré
        """
        # Récupérer les commits
        commits = self._get_commits(since_tag, to_tag)
        
        # Parser les commits
        changes = self._parse_commits(commits)
        
        # Générer le markdown
        markdown = self._generate_markdown(changes, since_tag, to_tag)
        
        # Sauvegarder
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        logger.info(f"Changelog généré: {output_path}")
        return markdown
    
    def generate_for_version(
        self,
        version: str,
        release_date: datetime = None
    ) -> str:
        """
        Génère le changelog pour une version spécifique.
        
        Args:
            version: Numéro de version (ex: "5.6.0")
            release_date: Date de release
            
        Returns:
            Section de changelog pour cette version
        """
        if release_date is None:
            release_date = datetime.now()
        
        # Récupérer commits depuis le dernier tag
        commits = self._get_commits_since_last_tag()
        changes = self._parse_commits(commits)
        
        # Générer section
        version_header = f"## [{version}] - {release_date.strftime('%Y-%m-%d')}"
        
        sections = []
        for change_type in ChangeType:
            type_changes = [c for c in changes if c.type == change_type]
            if type_changes:
                section = self._generate_section(change_type, type_changes)
                sections.append(section)
        
        return "\n\n".join([version_header] + sections)
    
    def _get_commits(
        self,
        since_tag: Optional[str],
        to_tag: Optional[str]
    ) -> List[Dict]:
        """Récupère les commits git."""
        range_spec = ""
        if since_tag:
            range_spec = f"{since_tag}.."
        if to_tag:
            range_spec += to_tag
        
        if not range_spec:
            range_spec = "HEAD~50..HEAD"  # 50 derniers commits
        
        cmd = [
            "git", "log", range_spec,
            "--pretty=format:%H|%an|%ad|%s",
            "--date=iso"
        ]
        
        result = subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if '|' in line:
                parts = line.split('|', 3)
                commits.append({
                    'hash': parts[0][:7],
                    'author': parts[1],
                    'date': datetime.fromisoformat(parts[2].replace(' ', 'T')),
                    'message': parts[3]
                })
        
        return commits
    
    def _get_commits_since_last_tag(self) -> List[Dict]:
        """Récupère les commits depuis le dernier tag."""
        # Trouver le dernier tag
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        last_tag = result.stdout.strip() if result.returncode == 0 else None
        
        return self._get_commits(last_tag, None)
    
    def _parse_commits(self, commits: List[Dict]) -> List[ChangeEntry]:
        """Parse les messages de commit."""
        changes = []
        
        pattern = r'^(\w+)(?:\(([^)]+)\))?!?: (.+)$'
        
        for commit in commits:
            message = commit['message']
            match = re.match(pattern, message)
            
            if match:
                type_str = match.group(1)
                scope = match.group(2)
                description = match.group(3)
                
                # Détecter breaking change
                breaking = '!' in message or 'BREAKING' in message
                
                # Mapper le type
                change_type = self._map_type(type_str)
                
                changes.append(ChangeEntry(
                    type=change_type,
                    scope=scope,
                    description=description,
                    breaking=breaking,
                    commit_hash=commit['hash'],
                    author=commit['author'],
                    date=commit['date']
                ))
            else:
                # Commit non conventionnel
                changes.append(ChangeEntry(
                    type=ChangeType.CHORE,
                    scope=None,
                    description=message,
                    breaking=False,
                    commit_hash=commit['hash'],
                    author=commit['author'],
                    date=commit['date']
                ))
        
        return changes
    
    def _map_type(self, type_str: str) -> ChangeType:
        """Mappe une string de type vers ChangeType."""
        type_mapping = {
            'feat': ChangeType.FEATURE,
            'feature': ChangeType.FEATURE,
            'fix': ChangeType.FIX,
            'bugfix': ChangeType.FIX,
            'docs': ChangeType.DOCS,
            'doc': ChangeType.DOCS,
            'style': ChangeType.STYLE,
            'refactor': ChangeType.REFACTOR,
            'perf': ChangeType.PERF,
            'performance': ChangeType.PERF,
            'test': ChangeType.TEST,
            'tests': ChangeType.TEST,
            'chore': ChangeType.CHORE,
            'build': ChangeType.CHORE,
            'ci': ChangeType.CHORE
        }
        
        return type_mapping.get(type_str.lower(), ChangeType.CHORE)
    
    def _generate_section(
        self,
        change_type: ChangeType,
        changes: List[ChangeEntry]
    ) -> str:
        """Génère une section de changelog."""
        header = self.SECTIONS.get(change_type, f"### {change_type.value}")
        
        lines = [header]
        
        for change in changes:
            scope = f"**{change.scope}**: " if change.scope else ""
            breaking = " ⚠️ **BREAKING**" if change.breaking else ""
            
            line = f"- {scope}{change.description}{breaking} ({change.commit_hash})"
            lines.append(line)
        
        return "\n".join(lines)
    
    def _generate_markdown(
        self,
        changes: List[ChangeEntry],
        since_tag: Optional[str],
        to_tag: Optional[str]
    ) -> str:
        """Génère le markdown complet."""
        lines = [
            "# Changelog",
            "",
            "Tous les changements notables de ce projet seront documentés ici.",
            "",
            "Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/)",
            "et ce projet adhère à [Semantic Versioning](https://semver.org/lang/fr/).",
            "",
        ]
        
        # Générer chaque section
        for change_type in ChangeType:
            type_changes = [c for c in changes if c.type == change_type]
            if type_changes:
                section = self._generate_section(change_type, type_changes)
                lines.append(section)
                lines.append("")
        
        return "\n".join(lines)


class ReleaseNotesGenerator:
    """
    Générateur de notes de release.
    """
    
    def generate(
        self,
        version: str,
        highlights: List[str],
        changes: List[ChangeEntry],
        contributors: List[str]
    ) -> str:
        """
        Génère les notes de release.
        """
        lines = [
            f"# Release v{version}",
            "",
            "## 🎯 Highlights",
            ""
        ]
        
        for highlight in highlights:
            lines.append(f"- {highlight}")
        
        lines.extend([
            "",
            "## 📊 Statistiques",
            f"- **Nouvelles fonctionnalités**: {len([c for c in changes if c.type == ChangeType.FEATURE])}",
            f"- **Corrections de bugs**: {len([c for c in changes if c.type == ChangeType.FIX])}",
            f"- **Améliorations de performance**: {len([c for c in changes if c.type == ChangeType.PERF])}",
            "",
            "## 👥 Contributeurs",
            ""
        ])
        
        for contributor in contributors:
            lines.append(f"- @{contributor}")
        
        lines.extend([
            "",
            "## 📦 Installation",
            f"```bash\npip install financeperso=={version}\n```",
            "",
            "---",
            f"[Voir le changelog complet](CHANGELOG.md)"
        ])
        
        return "\n".join(lines)
```

---

## 🧱 Module 3: Documentation API

```python
# modules/docs/api_documentation.py

import inspect
import ast
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import importlib


@dataclass
class APIEndpoint:
    """Endpoint API documenté."""
    path: str
    method: str
    summary: str
    description: str
    parameters: List[Dict]
    request_body: Optional[Dict]
    responses: List[Dict]
    tags: List[str]


@dataclass
class APIModule:
    """Module API documenté."""
    name: str
    description: str
    endpoints: List[APIEndpoint]


class APIDocumentationGenerator:
    """
    Générateur de documentation API (OpenAPI/Swagger).
    """
    
    def __init__(self, api_modules_path: str = "web/api"):
        self.api_modules_path = Path(api_modules_path)
    
    def generate_openapi_spec(self) -> Dict:
        """
        Génère la spécification OpenAPI.
        
        Returns:
            Dict au format OpenAPI 3.0
        """
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "FinancePerso API",
                "description": "API REST pour FinancePerso",
                "version": "5.6.0",
                "contact": {
                    "name": "Support",
                    "email": "support@financeperso.local"
                }
            },
            "servers": [
                {
                    "url": "http://localhost:8000/api",
                    "description": "Serveur de développement"
                }
            ],
            "paths": {},
            "components": {
                "schemas": self._extract_schemas(),
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            }
        }
        
        # Extraire les endpoints
        endpoints = self._extract_endpoints()
        
        for endpoint in endpoints:
            if endpoint.path not in spec["paths"]:
                spec["paths"][endpoint.path] = {}
            
            spec["paths"][endpoint.path][endpoint.method.lower()] = {
                "summary": endpoint.summary,
                "description": endpoint.description,
                "tags": endpoint.tags,
                "parameters": endpoint.parameters,
                "requestBody": endpoint.request_body,
                "responses": {
                    str(r["code"]): {
                        "description": r["description"],
                        "content": {
                            "application/json": {
                                "schema": r.get("schema", {})
                            }
                        }
                    }
                    for r in endpoint.responses
                }
            }
        
        return spec
    
    def generate_markdown(self, output_path: str = "docs/api/api-reference.md"):
        """
        Génère la documentation API en markdown.
        """
        spec = self.generate_openapi_spec()
        
        lines = [
            "# Référence API",
            "",
            "## Introduction",
            "",
            "Cette documentation décrit l'API REST de FinancePerso.",
            "",
            "### Base URL",
            f"```\n{spec['servers'][0]['url']}\n```",
            "",
            "### Authentification",
            "",
            "L'API utilise l'authentification JWT (Bearer token).",
            "",
            "```http\nAuthorization: Bearer <votre_token>\n```",
            "",
            "## Endpoints",
            ""
        ]
        
        # Grouper par tag
        endpoints_by_tag: Dict[str, List[tuple]] = {}
        for path, methods in spec["paths"].items():
            for method, details in methods.items():
                for tag in details.get("tags", ["Default"]):
                    if tag not in endpoints_by_tag:
                        endpoints_by_tag[tag] = []
                    endpoints_by_tag[tag].append((path, method, details))
        
        # Générer sections
        for tag, endpoints in sorted(endpoints_by_tag.items()):
            lines.extend([
                f"### {tag}",
                ""
            ])
            
            for path, method, details in endpoints:
                lines.extend([
                    f"#### {details['summary']}",
                    "",
                    f"```http\n{method.upper()} {path}\n```",
                    "",
                    f"{details.get('description', '')}",
                    ""
                ])
                
                # Paramètres
                if details.get("parameters"):
                    lines.extend([
                        "**Paramètres:**",
                        "",
                        "| Nom | Type | Requis | Description |",
                        "|-----|------|--------|-------------|"
                    ])
                    for param in details["parameters"]:
                        lines.append(
                            f"| {param['name']} | {param.get('schema', {}).get('type', 'string')} | "
                            f"{'Oui' if param.get('required') else 'Non'} | {param.get('description', '')} |"
                        )
                    lines.append("")
                
                # Réponses
                if details.get("responses"):
                    lines.extend([
                        "**Réponses:**",
                        "",
                        "| Code | Description |",
                        "|------|-------------|"
                    ])
                    for code, response in details["responses"].items():
                        lines.append(f"| {code} | {response['description']} |")
                    lines.append("")
                
                lines.append("---")
                lines.append("")
        
        # Sauvegarder
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("\n".join(lines), encoding='utf-8')
        
        return output_path
    
    def _extract_endpoints(self) -> List[APIEndpoint]:
        """Extrait les endpoints du code."""
        endpoints = []
        
        # Analyser les fichiers de route
        routes_path = self.api_modules_path / "routers"
        
        if not routes_path.exists():
            return endpoints
        
        for file in routes_path.glob("*.py"):
            endpoints.extend(self._parse_router_file(file))
        
        return endpoints
    
    def _parse_router_file(self, file: Path) -> List[APIEndpoint]:
        """Parse un fichier de router FastAPI."""
        endpoints = []
        
        content = file.read_text()
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Chercher décorateurs @router.get/post/etc.
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Attribute):
                            method = decorator.func.attr
                            if method in ['get', 'post', 'put', 'delete', 'patch']:
                                # Extraire le path
                                path = ""
                                if decorator.args:
                                    path = ast.literal_eval(decorator.args[0])
                                
                                # Extraire docstring
                                docstring = ast.get_docstring(node) or ""
                                summary = docstring.split('\n')[0] if docstring else node.name
                                
                                endpoints.append(APIEndpoint(
                                    path=f"/api{path}",
                                    method=method.upper(),
                                    summary=summary,
                                    description=docstring,
                                    parameters=[],
                                    request_body=None,
                                    responses=[
                                        {"code": 200, "description": "Succès"},
                                        {"code": 401, "description": "Non authentifié"},
                                        {"code": 500, "description": "Erreur serveur"}
                                    ],
                                    tags=[file.stem.replace('_', ' ').title()]
                                ))
        
        return endpoints
    
    def _extract_schemas(self) -> Dict:
        """Extrait les schémas Pydantic."""
        schemas = {}
        
        models_path = self.api_modules_path / "models" / "schemas.py"
        
        if not models_path.exists():
            return schemas
        
        content = models_path.read_text()
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Vérifier si c'est un modèle Pydantic
                is_model = any(
                    isinstance(base, ast.Name) and base.id == 'BaseModel'
                    for base in node.bases
                )
                
                if is_model:
                    properties = {}
                    
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign):
                            if isinstance(item.target, ast.Name):
                                field_name = item.target.id
                                field_type = self._get_type_string(item.annotation)
                                properties[field_name] = {"type": field_type}
                    
                    schemas[node.name] = {
                        "type": "object",
                        "properties": properties
                    }
        
        return schemas
    
    def _get_type_string(self, annotation) -> str:
        """Convertit une annotation Python en type JSON Schema."""
        if isinstance(annotation, ast.Name):
            type_map = {
                'str': 'string',
                'int': 'integer',
                'float': 'number',
                'bool': 'boolean',
                'datetime': 'string',
                'date': 'string'
            }
            return type_map.get(annotation.id, 'string')
        elif isinstance(annotation, ast.Subscript):
            if isinstance(annotation.value, ast.Name):
                if annotation.value.id == 'List':
                    return 'array'
                elif annotation.value.id == 'Optional':
                    return 'string'
        return 'string'
```

---

## 🧱 Module 4: Guide Utilisateur

```python
# modules/docs/user_guide_generator.py

from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class GuideSection:
    """Section de guide utilisateur."""
    title: str
    slug: str
    content: str
    order: int
    emoji: str = "📄"


class UserGuideGenerator:
    """
    Générateur de guide utilisateur.
    """
    
    SECTIONS = [
        {
            "title": "Démarrage Rapide",
            "slug": "getting-started",
            "emoji": "🚀",
            "order": 1
        },
        {
            "title": "Import de Transactions",
            "slug": "import",
            "emoji": "📥",
            "order": 2
        },
        {
            "title": "Validation et Catégorisation",
            "slug": "validation",
            "emoji": "✅",
            "order": 3
        },
        {
            "title": "Tableau de Bord",
            "slug": "dashboard",
            "emoji": "📊",
            "order": 4
        },
        {
            "title": "Gestion des Budgets",
            "slug": "budgets",
            "emoji": "💰",
            "order": 5
        },
        {
            "title": "Configuration",
            "slug": "configuration",
            "emoji": "⚙️",
            "order": 6
        },
        {
            "title": "FAQ",
            "slug": "faq",
            "emoji": "❓",
            "order": 99
        }
    ]
    
    def generate_all(self, output_dir: str = "docs/ACTIVE/user-guide"):
        """
        Génère tous les guides utilisateur.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for section_config in self.SECTIONS:
            content = self._generate_section_content(section_config)
            
            file_path = output_path / f"{section_config['slug']}.md"
            file_path.write_text(content, encoding='utf-8')
        
        # Générer index
        self._generate_index(output_path)
        
        return output_path
    
    def _generate_section_content(self, config: Dict) -> str:
        """Génère le contenu d'une section."""
        slug = config['slug']
        
        generators = {
            'getting-started': self._generate_getting_started,
            'import': self._generate_import_guide,
            'validation': self._generate_validation_guide,
            'dashboard': self._generate_dashboard_guide,
            'budgets': self._generate_budgets_guide,
            'configuration': self._generate_configuration_guide,
            'faq': self._generate_faq,
        }
        
        generator = generators.get(slug, lambda: "# Guide en cours de rédaction")
        return generator()
    
    def _generate_getting_started(self) -> str:
        return '''# 🚀 Démarrage Rapide

Bienvenue dans FinancePerso ! Ce guide vous aidera à configurer votre application en quelques minutes.

## Prérequis

- Python 3.11 ou supérieur
- Un fichier de transactions bancaires (CSV)

## Installation

### 1. Cloner le repository

```bash
git clone https://github.com/votre-repo/FinancePerso.git
cd FinancePerso
```

### 2. Créer l'environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\\Scripts\\activate  # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

```bash
cp .env.example .env
# Éditez .env avec vos clés API
```

### 5. Lancer l'application

```bash
make run
# ou
streamlit run app.py
```

L'application est accessible sur http://localhost:8501

## Première Utilisation

### 1. Créer vos catégories

Allez dans **Configuration > Catégories** pour définir vos catégories de dépenses.

### 2. Importer vos transactions

Allez dans **Import** et téléchargez votre fichier CSV bancaire.

### 3. Valider et catégoriser

Dans **Validation**, vérifiez et corrigez les catégories proposées.

### 4. Consulter votre dashboard

Le **Dashboard** vous montre vos finances en temps réel !

## Prochaines Étapes

- 📥 [Guide d'import](import.md)
- ✅ [Guide de validation](validation.md)
- 📊 [Guide du dashboard](dashboard.md)
'''
    
    def _generate_import_guide(self) -> str:
        return '''# 📥 Import de Transactions

Ce guide explique comment importer vos transactions bancaires.

## Formats Supportés

| Format | Extension | Description |
|--------|-----------|-------------|
| CSV | .csv | Format universel |
| QIF | .qif | Quicken Interchange Format |
| OFX | .ofx | Open Financial Exchange |
| JSON | .json | Export FinancePerso |

## Import CSV

### Format attendu

Votre CSV doit contenir au minimum:
- **date**: Date de la transaction (YYYY-MM-DD)
- **label**: Libellé de la transaction
- **amount**: Montant (négatif pour dépenses, positif pour revenus)

### Exemple

```csv
date,label,amount,category
2024-01-15,SUPER U PARIS,-45.67,Alimentation
2024-01-14,SALAIRE JANVIER,2500.00,Revenus
2024-01-13,PHARMACIE CENTRALE,-23.50,Santé
```

### Import pas à pas

1. Allez dans la page **Import**
2. Glissez-déposez votre fichier ou cliquez pour sélectionner
3. Mappez les colonnes si nécessaire
4. Cliquez sur **Importer**

## Import Massif (10 000+ transactions)

Pour les imports de grande taille:

1. Utilisez la page **Import Massif** (AGENT-017)
2. Le système traite par batch de 1000
3. Vous recevrez une notification à la fin

## Import depuis Open Banking

Si vous avez connecté vos comptes bancaires:

1. Allez dans **Comptes Bancaires**
2. Cliquez sur **Synchroniser**
3. Les transactions sont importées automatiquement

## Dépannage

### Problème: "Format de date non reconnu"

Solution: Utilisez le format YYYY-MM-DD ou vérifiez les paramètres régionaux.

### Problème: "Montant invalide"

Solution: Utilisez le point comme séparateur décimal (45.67, pas 45,67).

### Problème: "Doublons détectés"

Solution: Le système détecte automatiquement les doublons. Vérifiez dans l'historique.
'''
    
    def _generate_validation_guide(self) -> str:
        return '''# ✅ Validation et Catégorisation

Ce guide explique comment valider et catégoriser vos transactions.

## Pourquoi valider ?

La validation permet de:
- ✅ Vérifier la catégorisation automatique
- ✅ Corriger les erreurs
- ✅ Apprendre au système vos préférences
- ✅ Améliorer la précision future

## Processus de Validation

### 1. Accéder aux transactions en attente

Allez dans **Validation** pour voir les transactions importées récemment.

### 2. Vue groupe (recommandé)

Les transactions sont groupées par similitude:
- Même libellé
- Même montant
- Même période

### 3. Valider par groupe

- ✅ **Valider tout**: Confirme tout le groupe
- 📝 **Modifier**: Change la catégorie
- 👤 **Changer membre**: Attribue à un autre membre
- 🏷️ **Ajouter tags**: Ajoute des labels
- ✏️ **Éditer**: Modifie les détails

### 4. Règles d'apprentissage

Quand vous corrigez une catégorie:
- Le système crée une règle
- Les futures transactions similaires seront auto-catégorisées

## Catégories Intelligentes

Le système utilise plusieurs méthodes:

1. **Règles exactes** (priorité 1)
   - Vos corrections précédentes

2. **Règles partielles** (priorité 2)
   - Pattern matching sur les libellés

3. **IA Cloud** (priorité 3)
   - Gemini/OpenAI pour les cas complexes

4. **ML Local** (priorité 4)
   - Scikit-learn offline

## Tips et Astuces

### Utiliser les tags

Les tags permettent de grouper transversalement:
- #vacances-2024
- #remboursable
- #pro

### Validation rapide

- **Flèches** pour naviguer
- **Entrée** pour valider
- **Espace** pour sélectionner

### Mode avancé

Activez le mode avancé dans **Configuration** pour:
- Voir les scores de confiance
- Éditer les règles
- Gérer les conflits
'''
    
    def _generate_faq(self) -> str:
        return '''# ❓ FAQ

## Général

### Qu'est-ce que FinancePerso ?

FinancePerso est une application de gestion financière personnelle qui vous aide à:
- Importer automatiquement vos transactions
- Catégoriser vos dépenses
- Suivre vos budgets
- Analyser vos finances

### Mes données sont-elles sécurisées ?

Oui ! Toutes vos données:
- Sont stockées localement (SQLite)
- Peuvent être chiffrées (AES-256)
- Ne quittent jamais votre machine (sauf si vous activez l'IA cloud)

### Puis-je utiliser FinancePerso hors ligne ?

Oui, entièrement ! L'application fonctionne 100% offline.
Seules les fonctionnalités IA cloud nécessitent internet.

## Import

### Quelles banques sont supportées ?

Toutes les banques exportant en CSV, QIF ou OFX:
- BNP Paribas
- Crédit Mutuel
- Société Générale
- Banque Postale
- etc.

### Puis-je importer plusieurs années d'historique ?

Oui ! Utilisez la fonction **Import Massif** pour 10 000+ transactions.

## Fonctionnalités

### Comment fonctionne la catégorisation automatique ?

Le système utilise une cascade:
1. Vos règles personnalisées
2. Pattern matching
3. Intelligence artificielle (optionnel)
4. Catégorie par défaut

### Puis-je créer mes propres catégories ?

Oui, illimité ! Allez dans **Configuration > Catégories**.

### Qu'est-ce que le mode couple ?

Le mode couple permet de:
- Gérer un budget partagé
- Attribuer les dépenses par membre
- Suivre les dettes entre vous

## Problèmes Techniques

### L'application ne démarre pas

1. Vérifiez Python 3.11+
2. Vérifiez les dépendances: `pip install -r requirements.txt`
3. Lancez `python scripts/doctor.py`

### Erreur "Module not found"

```bash
# Réinstallez les dépendances
pip install -r requirements.txt --force-reinstall
```

### Problèmes de performance

- Vider le cache: **Configuration > Maintenance**
- Optimiser la base: **Configuration > Outils avancés**
- Réduire l'historique affiché

## Contribution

### Puis-je contribuer au projet ?

Oui ! Voir [CONTRIBUTING.md](../../CONTRIBUTING.md)

### Où signaler un bug ?

Créez une issue sur GitHub avec:
- Version de FinancePerso
- Système d'exploitation
- Description détaillée
- Étapes de reproduction
'''
    
    def _generate_dashboard_guide(self) -> str:
        return "# Guide Dashboard - En cours de rédaction"
    
    def _generate_budgets_guide(self) -> str:
        return "# Guide Budgets - En cours de rédaction"
    
    def _generate_configuration_guide(self) -> str:
        return "# Guide Configuration - En cours de rédaction"
    
    def _generate_index(self, output_path: Path):
        """Génère l'index du guide."""
        content = '''# Guide Utilisateur

Bienvenue dans le guide utilisateur de FinancePerso !

## 📚 Sommaire

| Guide | Description |
|-------|-------------|
| 🚀 [Démarrage Rapide](getting-started.md) | Installation et première utilisation |
| 📥 [Import](import.md) | Importer vos transactions |
| ✅ [Validation](validation.md) | Valider et catégoriser |
| 📊 [Dashboard](dashboard.md) | Comprendre vos finances |
| 💰 [Budgets](budgets.md) | Gérer vos budgets |
| ⚙️ [Configuration](configuration.md) | Personnaliser l'application |
| ❓ [FAQ](faq.md) | Questions fréquentes |

## 🆘 Support

- Documentation technique: [README.md](../../README.md)
- Guide développeur: [AGENTS.md](../../AGENTS.md)
- Signaler un bug: GitHub Issues
'''
        (output_path / "README.md").write_text(content, encoding='utf-8')


class OnboardingGuideGenerator:
    """
    Générateur de guide d'onboarding interactif.
    """
    
    def generate_checklist(self) -> List[Dict]:
        """Génère une checklist d'onboarding."""
        return [
            {
                "step": 1,
                "title": "Installation",
                "description": "Installer FinancePerso et vérifier qu'il fonctionne",
                "action": "Lancer l'application",
                "completed": False
            },
            {
                "step": 2,
                "title": "Configuration initiale",
                "description": "Créer vos catégories et configurer les membres",
                "action": "Aller dans Configuration",
                "completed": False
            },
            {
                "step": 3,
                "title": "Premier import",
                "description": "Importer vos transactions du mois dernier",
                "action": "Aller dans Import",
                "completed": False
            },
            {
                "step": 4,
                "title": "Validation",
                "description": "Valider et corriger la catégorisation",
                "action": "Aller dans Validation",
                "completed": False
            },
            {
                "step": 5,
                "title": "Explorer le dashboard",
                "description": "Découvrir les graphiques et analyses",
                "action": "Aller dans Dashboard",
                "completed": False
            }
        ]
```

---

## ✅ Checklist Documentation

```
✅ DOCUMENTATION UTILISATEUR
├── [ ] Guide démarrage rapide
├── [ ] Guide import
├── [ ] Guide validation
├── [ ] Guide dashboard
├── [ ] Guide budgets
├── [ ] Guide configuration
├── [ ] FAQ complète
└── [ ] Vidéos tutoriels (optionnel)

✅ DOCUMENTATION TECHNIQUE
├── [ ] Architecture
├── [ ] API Reference
├── [ ] Guide contribution
├── [ ] Setup développement
├── [ ] Déploiement
└── [ ] Troubleshooting

✅ MAINTENANCE
├── [ ] Changelog à jour
├── [ ] Release notes
├── [ ] Migrations guides
└── [ ] ADRs (Architecture Decision Records)
```

---

**Agent spécialisé AGENT-021** - Documentation & Technical Writer  
_Version 1.0 - Génération automatique de documentation_  
_Cibles: Utilisateurs finaux + Développeurs contributeurs_
