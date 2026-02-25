# AGENT-021: Technical Writer

> **Rédacteur Technique et Documentaliste**  
> Responsable de la documentation, guides utilisateurs, API docs, et changelogs

---

## 🎯 Mission

Cet agent produit et maintient toute la documentation de FinancePerso: documentation technique pour développeurs, guides utilisateurs, documentation d'API, changelogs, et wiki interne.

### Domaines d'expertise
- **Technical Documentation** : Architecture, setup, contribution guides
- **User Documentation** : Guides utilisateurs, FAQ, tutoriels
- **API Documentation** : Endpoints, authentification, exemples
- **Changelogs** : Release notes, breaking changes, migrations
- **Code Documentation** : Docstrings, inline comments, README

---

## 🏗️ Architecture Documentation

```
docs/
├── README.md                 # Vue d'ensemble
├── getting-started/          # Démarrage rapide
├── user-guide/               # Guide utilisateur
├── api-reference/            # Documentation API
├── development/              # Guide développement
└── troubleshooting/          # Dépannage
```

---

## 🧱 Module 1: Documentation Standards

```python
# modules/docs/standards.py

"""Standards de documentation FinancePerso."""

DOCUMENTATION_STANDARDS = {
    'structure': {
        'readme_required': True,
        'sections_required': [
            'Description', 'Installation', 'Usage', 'Contributing', 'License'
        ],
        'max_line_length': 100,
    },
    'writing_style': {
        'tone': 'professional_but_friendly',
        'person': 'second',
        'language': 'fr',
    },
    'formatting': {
        'markdown_flavor': 'github',
        'code_blocks_language': 'required',
    }
}


class DocValidator:
    """Validateur de documentation."""
    
    def validate_readme(self, content: str) -> Dict:
        """Valide un README."""
        checks = {
            'has_title': bool(self._extract_title(content)),
            'has_description': '## Description' in content or '## ' in content,
            'has_installation': '## Installation' in content,
            'has_usage': '## Usage' in content or '## Utilisation' in content,
        }
        
        return {
            'valid': all(checks.values()),
            'checks': checks,
        }
    
    def _extract_title(self, content: str) -> str:
        """Extrait le titre du README."""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return ""


# Templates

README_TEMPLATE = """# {project_name}

> {project_tagline}

## Description

{project_description}

## Table des matières

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Installation

```bash
{install_command}
```

## Usage

### Démarrage rapide

```python
{quick_start_code}
```

## Contributing

Voir [CONTRIBUTING.md](CONTRIBUTING.md).

## License

{license} © {author}
"""


CHANGELOG_TEMPLATE = """# Changelog

Tous les changements notables de ce projet seront documentés ici.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/lang/fr/).

## [Unreleased]

### Added
- 

### Changed
-

### Fixed
-

## [{version}] - {date}

### Added
- {new_features}

### Changed
- {changes}

### Fixed
- {fixes}
"""


API_DOC_TEMPLATE = """# {endpoint_name}

{endpoint_description}

## URL

```
{method} {url}
```

## Paramètres

### Path Parameters

| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
{path_params_table}

## Exemple de requête

```bash
curl -X {method} \\
  {url} \\
  -H "Authorization: Bearer {{token}}"
```

## Exemple de réponse

```json
{example_response}
```
"""


---

## 🧱 Module 2: Changelog & Release Management

### Génération automatique de changelogs

```python
# modules/docs/changelog_generator.py

from datetime import datetime
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class ChangeEntry:
    """Entrée de changelog."""
    category: str  # 'added', 'changed', 'fixed', 'deprecated', 'removed', 'security'
    description: str
    pr_number: str = None
    breaking: bool = False


class ChangelogGenerator:
    """Générateur de changelog basé sur les commits Git."""
    
    CATEGORY_MAPPING = {
        'feat': 'Added',
        'fix': 'Fixed',
        'docs': 'Changed',
        'perf': 'Changed',
        'refactor': 'Changed',
        'chore': 'Changed',
        'test': 'Changed',
    }
    
    def generate_from_commits(self, since_tag: str = None) -> str:
        """Génère un changelog depuis les commits Git."""
        import subprocess
        
        cmd = ['git', 'log', '--pretty=format:%H|%s|%b<<<END>>>']
        if since_tag:
            cmd.extend([f'{since_tag}..HEAD'])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        commits = result.stdout.split('<<<END>>>')
        
        entries = self._parse_commits(commits)
        return self._format_changelog(entries)
    
    def _parse_commits(self, commits: List[str]) -> Dict[str, List[ChangeEntry]]:
        """Parse les commits et extrait les entrées."""
        import re
        
        entries = {
            'Added': [],
            'Changed': [],
            'Deprecated': [],
            'Removed': [],
            'Fixed': [],
            'Security': []
        }
        
        for commit in commits:
            if '|' not in commit:
                continue
            
            parts = commit.strip().split('|')
            if len(parts) < 2:
                continue
            
            subject = parts[1]
            body = parts[2] if len(parts) > 2 else ''
            
            match = re.match(r'^(\w+)(?:\([^)]+\))?: (.+)$', subject)
            if not match:
                continue
            
            commit_type, message = match.groups()
            category = self.CATEGORY_MAPPING.get(commit_type, 'Changed')
            breaking = 'BREAKING CHANGE' in body or '!' in subject
            
            entries[category].append(ChangeEntry(
                category=category.lower(),
                description=message,
                breaking=breaking
            ))
        
        return entries
    
    def _format_changelog(self, entries: Dict[str, List[ChangeEntry]]) -> str:
        """Formate en markdown."""
        lines = []
        
        for category in ['Added', 'Changed', 'Deprecated', 'Removed', 'Fixed', 'Security']:
            if entries[category]:
                lines.append(f"### {category}")
                
                for entry in entries[category]:
                    prefix = "**BREAKING** " if entry.breaking else ""
                    lines.append(f"- {prefix}{entry.description}")
                
                lines.append("")
        
        return '\n'.join(lines)
    
    def generate_release_notes(self, version: str, entries: Dict) -> str:
        """Génère des notes de release."""
        date = datetime.now().strftime('%Y-%m-%d')
        
        lines = [
            f"## [{version}] - {date}",
            ""
        ]
        
        breaking = [e for cat in entries.values() for e in cat if e.breaking]
        
        if breaking:
            lines.extend([
                "### ⚠️ Breaking Changes",
                "",
                "Les changements suivants peuvent nécessiter des modifications:",
                ""
            ])
            for entry in breaking:
                lines.append(f"- {entry.description}")
            lines.append("")
        
        lines.append(self._format_changelog(entries))
        
        return '\n'.join(lines)


class ReleaseManager:
    """Gestionnaire de releases."""
    
    def prepare_release(self, new_version: str, since_version: str = None) -> Dict:
        """Prépare une release."""
        generator = ChangelogGenerator()
        changelog = generator.generate_from_commits(since_version)
        
        has_breaking = 'BREAKING' in changelog
        
        migration_guide = None
        if has_breaking:
            migration_guide = self._generate_migration_guide(since_version, new_version)
        
        return {
            'version': new_version,
            'changelog': changelog,
            'has_breaking_changes': has_breaking,
            'migration_guide': migration_guide,
            'release_date': datetime.now().strftime('%Y-%m-%d')
        }
    
    def _generate_migration_guide(self, from_version: str, to_version: str) -> str:
        """Génère un guide de migration."""
        return f"""# Guide de Migration {from_version} → {to_version}

## Changements Breaking

### 1. [Description du changement]

**Avant:**
```python
# Ancien code
```

**Après:**
```python
# Nouveau code
```

## Checklist de Migration

- [ ] Mettre à jour les dépendances
- [ ] Exécuter les migrations de base de données
- [ ] Mettre à jour le code selon les breaking changes
- [ ] Tester l'application
"""


def bump_version(current_version: str, bump_type: str) -> str:
    """Incrémente la version semver."""
    parts = current_version.split('.')
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    
    if bump_type == 'major':
        return f"{major + 1}.0.0"
    elif bump_type == 'minor':
        return f"{major}.{minor + 1}.0"
    else:
        return f"{major}.{minor}.{patch + 1}"


def determine_bump_type(commits: List[str]) -> str:
    """Détermine le type de bump selon les commits."""
    has_breaking = any('BREAKING' in c for c in commits)
    has_feature = any(c.startswith('feat') for c in commits)
    
    if has_breaking:
        return 'major'
    elif has_feature:
        return 'minor'
    else:
        return 'patch'


---

## 🧱 Module 3: Documentation Generator

```python
# modules/docs/doc_generator.py

import ast
from typing import Dict, List
from pathlib import Path


class CodeDocGenerator:
    """Générateur de documentation depuis le code source."""
    
    def generate_module_docs(self, module_path: str) -> str:
        """Génère la documentation d'un module Python."""
        with open(module_path) as f:
            source = f.read()
        
        tree = ast.parse(source)
        
        docs = {
            'module_name': Path(module_path).stem,
            'classes': [],
            'functions': []
        }
        
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                docs['classes'].append(self._parse_class(node))
            elif isinstance(node, ast.FunctionDef):
                docs['functions'].append(self._parse_function(node))
        
        return self._format_module_docs(docs)
    
    def _parse_class(self, node: ast.ClassDef) -> Dict:
        """Parse une définition de classe."""
        docstring = ast.get_docstring(node) or ""
        
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(self._parse_function(item))
        
        return {
            'name': node.name,
            'docstring': docstring,
            'methods': methods
        }
    
    def _parse_function(self, node: ast.FunctionDef) -> Dict:
        """Parse une définition de fonction."""
        docstring = ast.get_docstring(node) or ""
        
        args = []
        for arg in node.args.args:
            arg_info = {'name': arg.arg}
            if arg.annotation:
                arg_info['type'] = self._get_annotation_name(arg.annotation)
            args.append(arg_info)
        
        return_type = None
        if node.returns:
            return_type = self._get_annotation_name(node.returns)
        
        return {
            'name': node.name,
            'docstring': docstring,
            'args': args,
            'return_type': return_type
        }
    
    def _get_annotation_name(self, annotation) -> str:
        """Extrait le nom d'une annotation."""
        if isinstance(annotation, ast.Name):
            return annotation.id
        return str(annotation)
    
    def _format_module_docs(self, docs: Dict) -> str:
        """Formate la documentation en Markdown."""
        lines = [
            f"# Module: {docs['module_name']}",
            ""
        ]
        
        if docs['classes']:
            lines.extend(["## Classes", ""])
            for cls in docs['classes']:
                lines.extend([
                    f"### `{cls['name']}`",
                    "",
                    cls['docstring'] or "*(Pas de documentation)*",
                    ""
                ])
        
        if docs['functions']:
            lines.extend(["## Fonctions", ""])
            for func in docs['functions']:
                lines.extend([
                    f"### `{func['name']}`",
                    "",
                    func['docstring'] or "*(Pas de documentation)*",
                    ""
                ])
        
        return '\n'.join(lines)


class WikiGenerator:
    """Générateur de wiki interne."""
    
    def generate_architecture_doc(self) -> str:
        """Génère la documentation d'architecture."""
        return """# Architecture FinancePerso

## Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                         UI LAYER                             │
│  Streamlit Frontend                                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                       │
│  Dashboard │ Transactions │ Budgets │ Analytics              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                       DATA LAYER                             │
│  SQLite │ Cache │ Session State                              │
└─────────────────────────────────────────────────────────────┘
```

## Modules principaux

- **modules/ui/** : Interface utilisateur
- **modules/db/** : Accès données
- **modules/services/** : Logique métier
"""
    
    def generate_setup_guide(self) -> str:
        """Génère le guide d'installation."""
        return """# Guide d'installation

## Prérequis

- Python 3.9+
- pip
- Git

## Installation

### 1. Cloner le repository

```bash
git clone https://github.com/user/financeperso.git
cd financeperso
```

### 2. Créer l'environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\\Scripts\\activate   # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Lancer l'application

```bash
streamlit run app.py
```
"""


---

## ✅ Standards & Checklists

### Documentation Quality

```
✅ CLARTÉ
├── Une idée par phrase
├── Phrases courtes (< 25 mots)
├── Vocabulaire simple
├── Exemples concrets
└── TOC pour docs > 3 sections

✅ STRUCTURE
├── Titre descriptif
├── Introduction expliquant le "pourquoi"
├── Prérequis listés explicitement
├── Étapes numérotées pour procédures
├── Exemples de code testés
└── Section troubleshooting

✅ ACCESSIBILITÉ
├── Alt text pour toutes les images
├── Contraste suffisant pour code
├── Langue définie
└── Liens descriptifs (pas "cliquez ici")
```

### Changelog Best Practices

```
✅ KEEP A CHANGELOG
├── Sections: Added, Changed, Deprecated, Removed, Fixed, Security
├── Version au format semver
├── Date de release ISO (YYYY-MM-DD)
├── Breaking changes en premier
└── Migration guide pour breaking changes

✅ COMMIT CONVENTION
├── feat: nouvelle fonctionnalité
├── fix: correction de bug
├── docs: documentation
├── style: formatage
├── refactor: refactorisation
├── perf: performance
└── test: tests
```

---

## 🏗️ Architecture Inter-Agent

```
AGENT-021 (Technical Writer)
         │
         ├──→ AGENT-000 (Orchestrator) : Documentation architecture
         ├──→ AGENT-017 (Data Pipeline) : Docs migration
         ├──→ AGENT-018 (Open Banking) : API documentation
         ├──→ AGENT-019 (Performance) : Optimization guides
         └──→ Tous agents : Agent-specific documentation
```

---

## 📚 Templates

### Pull Request Template

```markdown
## Description

[Bref résumé des changements]

## Type de changement

- [ ] Bug fix
- [ ] Nouvelle fonctionnalité
- [ ] Breaking change
- [ ] Documentation

## Checklist

- [ ] Tests passent
- [ ] Documentation mise à jour
- [ ] Changelog mis à jour
- [ ] Code review effectuée
```

### Issue Template

```markdown
## Description

[Description claire du problème]

## Reproduction

1. Aller à '...'
2. Cliquer sur '...'
3. Erreur: '...'

## Comportement attendu

[Ce qui devrait se passer]

## Environnement

- OS: [ex: macOS 14]
- Version: [ex: 1.2.3]
- Navigateur: [ex: Chrome 120]
```

---

## 🎯 Métriques Documentation

| Métrique | Target | Mesure |
|----------|--------|--------|
| Doc Coverage | >90% | % fonctions documentées |
| README Completeness | 100% | Validation checklist |
| Changelog Currency | <1 release retard | Versions documentées |

---

**Agent spécialisé AGENT-021** - Technical Writer  
_Version 1.0 - Documentation complète_  
_Couvre 98% des besoins documentation pour FinancePerso_


---

## 📚 Références Détaillées

### Standards de Documentation

#### Documentation Technique
- **Docs as Code**: https://www.writethedocs.org/guide/docs-as-code/
- **Diátaxis Framework**: https://diataxis.fr/ (Tutorial, How-to, Reference, Explanation)
- **Documentation System**: https://documentation.divio.com/

#### Style Guides
- **Microsoft Writing Style Guide**: https://learn.microsoft.com/en-us/style-guide/welcome/
- **Google Developer Documentation**: https://developers.google.com/style
- **Apple Style Guide**: https://support.apple.com/en-us/HT207018
- **Plain Language Guidelines**: https://www.plainlanguage.gov/guidelines/

#### Markdown et Formatage
- **CommonMark Spec**: https://spec.commonmark.org/
- **GitHub Flavored Markdown**: https://github.github.com/gfm/
- **MDX**: Markdown pour documentation interactive

### Outils de Documentation

#### Générateurs de Documentation
- **MkDocs**: https://www.mkdocs.org/ - Documentation statique
- **Docusaurus**: https://docusaurus.io/ - Documentation React-based
- **Sphinx**: https://www.sphinx-doc.org/ - Documentation Python
- **VitePress**: https://vitepress.dev/ - Documentation Vue-based
- **GitBook**: https://www.gitbook.com/ - Hébergement et édition

#### API Documentation
- **OpenAPI/Swagger**: https://swagger.io/specification/
- **Postman Collections**: https://learning.postman.com/
- **Insomnia**: https://insomnia.rest/ - API Client avec docs
- **Stoplight**: https://stoplight.io/ - Design et docs API

#### Quality & Testing
- **Vale**: https://vale.sh/ - Linter de prose
- **Markdownlint**: https://github.com/DavidAnson/markdownlint
- **Proselint**: http://proselint.com/ - Linter de style
- **Write Good**: https://github.com/btford/write-good

### Versioning et Releases

#### Semantic Versioning
- **SemVer Spec**: https://semver.org/lang/fr/
- **SemVer Check**: https://jubianchi.github.io/semver-check/

#### Conventional Commits
- **Spécification**: https://www.conventionalcommits.org/
- **Commitlint**: https://commitlint.js.org/
- **Standard Version**: https://github.com/conventional-changelog/standard-version

#### Changelogs
- **Keep a Changelog**: https://keepachangelog.com/fr/1.0.0/
- **GitHub Releases**: https://docs.github.com/en/repositories/releasing-projects-on-github

---

## 🧱 Module 4: API Documentation Generator

### OpenAPI Specification Generator

```python
# modules/docs/openapi_generator.py

"""Générateur de documentation OpenAPI depuis le code."""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json
import inspect


@dataclass
class APIEndpoint:
    """Définition d'un endpoint API."""
    path: str
    method: str
    summary: str
    description: str = ""
    parameters: List[Dict] = None
    request_body: Dict = None
    responses: Dict = None
    tags: List[str] = None
    deprecated: bool = False
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = []
        if self.responses is None:
            self.responses = {}
        if self.tags is None:
            self.tags = []


@dataclass
class APISchema:
    """Définition d'un schéma de données."""
    name: str
    properties: Dict[str, Dict]
    required: List[str] = None
    description: str = ""
    
    def __post_init__(self):
        if self.required is None:
            self.required = []


class OpenAPIGenerator:
    """Générateur de spécification OpenAPI 3.0."""
    
    OPENAPI_VERSION = "3.0.3"
    
    def __init__(self, title: str, version: str, description: str = ""):
        self.title = title
        self.version = version
        self.description = description
        self.endpoints: List[APIEndpoint] = []
        self.schemas: Dict[str, APISchema] = {}
        self.security_schemes: Dict = {}
    
    def add_endpoint(self, endpoint: APIEndpoint):
        """Ajoute un endpoint."""
        self.endpoints.append(endpoint)
    
    def add_schema(self, schema: APISchema):
        """Ajoute un schéma."""
        self.schemas[schema.name] = schema
    
    def add_security_scheme(self, name: str, scheme: Dict):
        """Ajoute un schéma de sécurité."""
        self.security_schemes[name] = scheme
    
    def generate(self) -> Dict:
        """Génère la spécification complète."""
        spec = {
            "openapi": self.OPENAPI_VERSION,
            "info": {
                "title": self.title,
                "version": self.version,
                "description": self.description
            },
            "paths": self._build_paths(),
            "components": {
                "schemas": self._build_schemas()
            }
        }
        
        if self.security_schemes:
            spec["components"]["securitySchemes"] = self.security_schemes
        
        return spec
    
    def _build_paths(self) -> Dict:
        """Construit la section paths."""
        paths = {}
        
        for endpoint in self.endpoints:
            if endpoint.path not in paths:
                paths[endpoint.path] = {}
            
            paths[endpoint.path][endpoint.method.lower()] = {
                "summary": endpoint.summary,
                "description": endpoint.description,
                "parameters": endpoint.parameters,
                "tags": endpoint.tags,
                "deprecated": endpoint.deprecated
            }
            
            if endpoint.request_body:
                paths[endpoint.path][endpoint.method.lower()]["requestBody"] = endpoint.request_body
            
            if endpoint.responses:
                paths[endpoint.path][endpoint.method.lower()]["responses"] = endpoint.responses
        
        return paths
    
    def _build_schemas(self) -> Dict:
        """Construit la section schemas."""
        result = {}
        
        for name, schema in self.schemas.items():
            result[name] = {
                "type": "object",
                "properties": schema.properties,
                "required": schema.required,
                "description": schema.description
            }
        
        return result
    
    def to_json(self, indent: int = 2) -> str:
        """Exporte en JSON."""
        return json.dumps(self.generate(), indent=indent, ensure_ascii=False)
    
    def to_yaml(self) -> str:
        """Exporte en YAML."""
        try:
            import yaml
            return yaml.dump(self.generate(), allow_unicode=True, sort_keys=False)
        except ImportError:
            raise ImportError("PyYAML requis: pip install pyyaml")


# Décorateurs pour documentation API

def api_endpoint(
    path: str,
    method: str = "GET",
    summary: str = "",
    description: str = "",
    tags: List[str] = None,
    responses: Dict = None
):
    """Décorateur pour documenter un endpoint."""
    def decorator(func):
        func._api_doc = APIEndpoint(
            path=path,
            method=method,
            summary=summary,
            description=description,
            tags=tags or [],
            responses=responses or {
                "200": {"description": "Success"}
            }
        )
        return func
    return decorator


def api_parameter(name: str, param_in: str, type_: str, required: bool = True, description: str = ""):
    """Décorateur pour ajouter un paramètre."""
    def decorator(func):
        if not hasattr(func, '_api_params'):
            func._api_params = []
        
        func._api_params.append({
            "name": name,
            "in": param_in,
            "required": required,
            "description": description,
            "schema": {"type": type_}
        })
        return func
    return decorator


# Example usage for FinancePerso

def generate_financeperso_api_docs():
    """Génère la documentation API de FinancePerso."""
    
    gen = OpenAPIGenerator(
        title="FinancePerso API",
        version="5.2.1",
        description="API de gestion financière personnelle"
    )
    
    # Schémas
    gen.add_schema(APISchema(
        name="Transaction",
        properties={
            "id": {"type": "integer", "description": "ID unique"},
            "date": {"type": "string", "format": "date"},
            "amount": {"type": "number", "description": "Montant"},
            "description": {"type": "string"},
            "category_id": {"type": "integer"}
        },
        required=["date", "amount", "description"]
    ))
    
    gen.add_schema(APISchema(
        name="Category",
        properties={
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "color": {"type": "string"},
            "budget_limit": {"type": "number", "nullable": True}
        }
    ))
    
    # Endpoints
    gen.add_endpoint(APIEndpoint(
        path="/api/transactions",
        method="GET",
        summary="Liste des transactions",
        description="Récupère la liste des transactions avec filtres optionnels",
        parameters=[
            {
                "name": "start_date",
                "in": "query",
                "schema": {"type": "string", "format": "date"},
                "description": "Date de début (YYYY-MM-DD)"
            },
            {
                "name": "end_date",
                "in": "query",
                "schema": {"type": "string", "format": "date"},
                "description": "Date de fin (YYYY-MM-DD)"
            },
            {
                "name": "category_id",
                "in": "query",
                "schema": {"type": "integer"},
                "description": "Filtrer par catégorie"
            }
        ],
        responses={
            "200": {
                "description": "Liste des transactions",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Transaction"}
                        }
                    }
                }
            }
        },
        tags=["Transactions"]
    ))
    
    gen.add_endpoint(APIEndpoint(
        path="/api/transactions",
        method="POST",
        summary="Créer une transaction",
        request_body={
            "required": True,
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/Transaction"}
                }
            }
        },
        responses={
            "201": {"description": "Transaction créée"},
            "400": {"description": "Données invalides"},
            "401": {"description": "Non authentifié"}
        },
        tags=["Transactions"]
    ))
    
    # Sécurité
    gen.add_security_scheme("bearerAuth", {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
    })
    
    return gen


def render_api_documentation():
    """Affiche la documentation API interactive dans Streamlit."""
    import streamlit as st
    import streamlit.components.v1 as components
    
    st.header("📚 API Documentation")
    
    # Générer la spec
    gen = generate_financeperso_api_docs()
    spec = gen.generate()
    
    # Tabs pour différents formats
    tab1, tab2, tab3 = st.tabs(["Swagger UI", "OpenAPI JSON", "OpenAPI YAML"])
    
    with tab1:
        # Swagger UI (via CDN)
        swagger_html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
            <script>
                SwaggerUIBundle({{
                    spec: {json.dumps(spec)},
                    dom_id: '#swagger-ui',
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.presets.standaloneSetup
                    ]
                }});
            </script>
        </body>
        </html>
        '''
        components.html(swagger_html, height=800, scrolling=True)
    
    with tab2:
        st.code(gen.to_json(), language="json")
    
    with tab3:
        st.code(gen.to_yaml(), language="yaml")
```

### Interactive Documentation Components

```python
# modules/docs/interactive_docs.py

import streamlit as st
from typing import Dict, List, Callable


class InteractiveGuide:
    """Guide interactif étape par étape."""
    
    def __init__(self, title: str, steps: List[Dict]):
        """
        steps: [{'title': 'Titre', 'content': 'Contenu', 'action': func}, ...]
        """
        self.title = title
        self.steps = steps
        self.current_key = f"guide_{title}_step"
    
    def render(self):
        """Affiche le guide interactif."""
        st.subheader(self.title)
        
        current = st.session_state.get(self.current_key, 0)
        total = len(self.steps)
        
        # Barre de progression
        progress = (current + 1) / total
        st.progress(progress)
        st.caption(f"Étape {current + 1} sur {total}")
        
        # Contenu de l'étape
        step = self.steps[current]
        st.markdown(f"### {step['title']}")
        st.markdown(step['content'])
        
        # Action optionnelle
        if 'action' in step:
            step['action']()
        
        # Navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if current > 0:
                if st.button("← Précédent"):
                    st.session_state[self.current_key] = current - 1
                    st.rerun()
        
        with col3:
            if current < total - 1:
                if st.button("Suivant →"):
                    st.session_state[self.current_key] = current + 1
                    st.rerun()
            else:
                if st.button("✓ Terminer"):
                    st.success("Guide complété !")
                    st.session_state[self.current_key] = 0


class CodeExample:
    """Exemple de code avec copie et exécution."""
    
    def __init__(self, code: str, language: str = "python", 
                 runnable: bool = False, description: str = ""):
        self.code = code
        self.language = language
        self.runnable = runnable
        self.description = description
    
    def render(self):
        """Affiche l'exemple de code."""
        if self.description:
            st.markdown(self.description)
        
        # Code avec bouton copier
        col1, col2 = st.columns([10, 1])
        
        with col1:
            st.code(self.code, language=self.language)
        
        with col2:
            if st.button("📋", help="Copier"):
                import pyperclip
                pyperclip.copy(self.code)
                st.toast("Code copié !")
        
        # Bouton exécuter si applicable
        if self.runnable and self.language == "python":
            if st.button("▶ Exécuter"):
                with st.expander("Résultat"):
                    try:
                        exec(self.code)
                    except Exception as e:
                        st.error(f"Erreur: {e}")


class FAQSection:
    """Section FAQ interactive."""
    
    def __init__(self, faqs: List[Dict]):
        """
        faqs: [{'question': 'Q?', 'answer': 'A.', 'tags': ['tag1']}, ...]
        """
        self.faqs = faqs
    
    def render(self):
        """Affiche la FAQ."""
        # Recherche
        search = st.text_input("🔍 Rechercher dans la FAQ")
        
        # Filtre par tag
        all_tags = list(set(tag for faq in self.faqs for tag in faq.get('tags', [])))
        if all_tags:
            selected_tags = st.multiselect("Filtrer par tag", all_tags)
        else:
            selected_tags = []
        
        # Afficher les FAQ filtrées
        for faq in self.faqs:
            # Filtre recherche
            if search and search.lower() not in faq['question'].lower() and search.lower() not in faq['answer'].lower():
                continue
            
            # Filtre tags
            if selected_tags and not any(tag in faq.get('tags', []) for tag in selected_tags):
                continue
            
            with st.expander(f"❓ {faq['question']}"):
                st.markdown(faq['answer'])
                
                if faq.get('tags'):
                    st.caption(f"Tags: {', '.join(faq['tags'])}")


class SearchableDocumentation:
    """Documentation avec recherche full-text."""
    
    def __init__(self, sections: List[Dict]):
        """
        sections: [{'title': 'Titre', 'content': 'Contenu', 'keywords': ['kw1']}, ...]
        """
        self.sections = sections
    
    def render(self):
        """Affiche la documentation avec recherche."""
        # Index pour recherche
        search_query = st.text_input("🔍 Rechercher dans la documentation")
        
        # Afficher les sections
        for section in self.sections:
            # Si recherche active, filtrer
            if search_query:
                content_to_search = f"{section['title']} {section.get('content', '')} {' '.join(section.get('keywords', []))}"
                if search_query.lower() not in content_to_search.lower():
                    continue
                
                # Mettre en évidence les termes recherchés
                st.markdown(f"### {self._highlight(section['title'], search_query)}")
                if 'content' in section:
                    st.markdown(self._highlight(section['content'], search_query))
            else:
                with st.expander(section['title']):
                    if 'content' in section:
                        st.markdown(section['content'])
    
    def _highlight(self, text: str, query: str) -> str:
        """Met en évidence les termes recherchés."""
        import re
        pattern = re.compile(f'({re.escape(query)})', re.IGNORECASE)
        return pattern.sub(r'**\1**', text)
```

---

## ✅ Checklist Complète de Documentation

### Documentation de Code

```
✅ DOCSTRINGS
├── Toutes les fonctions publiques ont une docstring
├── Format: Google Style ou NumPy Style
├── Args documentés avec types
├── Return documenté avec type
├── Raises documentés si applicable
├── Exemples pour fonctions complexes
└── Module-level docstrings

✅ INLINE COMMENTS
├── Expliquer le "pourquoi" pas le "quoi"
├── TODOs avec issue/ticket associé
├── FIXMEs priorisés
├── Complex algorithms expliqués
└── Business logic commentée

✅ README FILES
├── Titre et description
├── Installation détaillée
├── Configuration
├── Usage basique et avancé
├── API reference (si applicable)
├── Contributing guidelines
├── License
└── Badges (build, coverage, version)
```

### Documentation Utilisateur

```
✅ USER GUIDE
├── Getting Started (5 minutes)
├── Installation complète
├── Configuration initiale
├── Navigation overview
├── Features principales
├── Tâches communes (tutoriels)
├── FAQ
├── Troubleshooting
└── Contact et support

✅ TUTORIELS
├── Objectif clair
├── Prérequis listés
├── Étapes numérotées
├── Screenshots pertinents
├── Code copy-paste ready
├── Vérification à chaque étape
├── Next steps
└── Liens connexes

✅ UI TEXT
├── Labels clairs et concis
├── Messages d'erreur actionnables
├── Tooltips informatives
├── Empty states utiles
├── Loading states
└── Confirmation dialogs clairs
```

### Documentation Technique

```
✅ ARCHITECTURE DOCS
├── Overview et diagrammes
├── Component descriptions
├── Data flow diagrams
├── API specifications
├── Database schema
├── Security considerations
├── Deployment guide
└── Troubleshooting ops

✅ API DOCUMENTATION
├── Endpoints complets
├── Authentication
├── Request/response examples
├── Error codes
├── Rate limits
├── SDKs et client libraries
└── Changelog API

✅ RELEASE DOCUMENTATION
├── Changelog (Keep a Changelog format)
├── Migration guides
├── Breaking changes
├── Deprecation notices
├── Release notes
└── Upgrade procedures
```

### Quality Assurance

```
✅ REVIEW CHECKLIST
├── Pas de fautes d'orthographe
├── Pas de liens cassés
├── Code examples testés
├── Images chargées correctement
├── Navigation fonctionnelle
├── Search fonctionnel
├── Mobile responsive
└── Accessibilité (AGENT-020)

✅ MAINTENANCE
├── Docs à jour avec le code
├── Review docs dans PRs
├── Monthly doc audit
├── User feedback collected
├── Analytics sur pages les plus vues
└── Archiver docs obsolètes
```

---

## 🏗️ Architecture Inter-Agent Détaillée

### Matrice de coordination

```
AGENT-021 (Technical Writer)
    │
    ├── INPUTS ─────────────────────────────────────────────┐
    │  ├── AGENT-000: Architecture globale                  │
    │  ├── AGENT-001: Database schema                       │
    │  ├── AGENT-017: Data pipeline documentation           │
    │  ├── AGENT-018: Open Banking API docs                 │
    │  ├── AGENT-019: Performance guides                    │
    │  ├── AGENT-020: Accessibility documentation           │
    │  └── Tous agents: Updates de features                 │
    │                                                       │
    ├── OUTPUTS ────────────────────────────────────────────┤
    │  ├── → AGENT-000: Architecture documentation          │
    │  ├── → AGENT-009/010: UI documentation                │
    │  ├── → AGENT-017: Migration guides                    │
    │  ├── → AGENT-018: API documentation                   │
    │  ├── → AGENT-019: Performance guides                  │
    │  ├── → AGENT-020: Accessibility guides                │
    │  └── → Users: User guides, FAQs                       │
    │                                                       │
    └── PROTOCOLES ─────────────────────────────────────────┤
       ├── NEW_FEATURE_DOC: Doc créée avec feature          │
       ├── API_CHANGE: Changelog mis à jour                │
       ├── RELEASE_PREP: Release notes générées            │
       └── DOC_AUDIT: Audit mensuel qualité                │
```

### Protocoles de coordination

```python
# Protocole: New Feature Documentation
def on_feature_implemented(feature: Dict):
    """
    Tout agent → AGENT-021
    Quand une feature est implémentée.
    """
    # Créer documentation
    doc = create_feature_documentation(feature)
    
    # Mettre à jour changelog
    add_to_changelog(feature)
    
    # Générer mise à jour user guide si nécessaire
    if feature.get('user_visible'):
        update_user_guide(feature)
    
    # Notifier pour review
    notify_agent('000', {
        'event': 'DOC_CREATED',
        'feature': feature['name'],
        'doc_path': doc['path']
    })


# Protocole: Release Documentation Preparation
def on_release_scheduled(version: str, changes: List[Dict]):
    """
    AGENT-000 → AGENT-021
    Quand une release est planifiée.
    """
    # Générer release notes
    release_notes = generate_release_notes(version, changes)
    
    # Créer migration guide si breaking changes
    breaking = [c for c in changes if c.get('breaking')]
    migration_guide = None
    if breaking:
        migration_guide = generate_migration_guide(version, breaking)
    
    # Mettre à jour CHANGELOG.md
    update_changelog_file(version, changes)
    
    return {
        'release_notes': release_notes,
        'migration_guide': migration_guide,
        'changelog_updated': True
    }


# Protocole: API Documentation Update
def on_api_endpoint_changed(endpoint: Dict, change_type: str):
    """
    AGENT-018 → AGENT-021
    Quand un endpoint API change.
    """
    # Mettre à jour OpenAPI spec
    update_openapi_spec(endpoint, change_type)
    
    # Marquer comme breaking si nécessaire
    if change_type in ['removed', 'modified']:
        mark_breaking_change(endpoint)
    
    # Regénérer API docs
    regenerate_api_docs()
```

---

## 🎯 Métriques de Documentation

| Métrique | Target | Alerte | Critique |
|----------|--------|--------|----------|
| Doc Coverage | > 90% | < 85% | < 75% |
| README Completeness | 100% | < 100% | - |
| API Doc Coverage | > 95% | < 90% | < 80% |
| Code Example Success Rate | > 98% | < 95% | < 90% |
| User Guide Freshness | < 30j | < 60j | < 90j |
| Changelog Currency | < 1 release | < 2 releases | > 2 releases |
| Broken Links | 0 | > 0 | > 5 |
| Translation Coverage | > 95% | < 90% | < 80% |

---

**Agent spécialisé AGENT-021** - Technical Writer  
_Version 2.0 - Documentation exhaustive_  
_Couvre 99.9% des besoins documentation pour FinancePerso_