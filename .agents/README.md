# 🤖 Agents - FinancePerso

Ce répertoire contient les agents automatisés utilisés pour maintenir et améliorer la qualité du projet FinancePerso.

## 📋 Agents disponibles

### `doc_agent.py` - Agent de Documentation

Agent responsable de maintenir la cohérence entre le code et la documentation du projet.

#### Usage

```bash
# Vérifier la cohérence documentation/code
python .agents/doc_agent.py --check

# Mettre à jour la documentation automatiquement
python .agents/doc_agent.py --update

# Générer la documentation pour un module spécifique
python .agents/doc_agent.py --generate <module_name>
```

#### Quand l'utiliser ?

| Moment | Commande | Raison |
|--------|----------|--------|
| Avant chaque commit | `--check` | Vérifie que la doc est à jour (hook pre-commit) |
| Après modification majeure | `--update` | Met à jour le CHANGELOG et AGENTS.md |
| Nouveau module | `--generate <module>` | Crée la documentation initiale |
| CI/CD | `--check` | Bloque les PR avec documentation obsolète |

#### Fonctionnement

L'agent analyse :

1. **AGENTS.md** - Vérifie que tous les modules sont documentés
2. **CHANGELOG.md** - Vérifie que les changements récents sont listés
3. **docs/** - Vérifie que chaque module a sa documentation
4. **migrations/** - Vérifie que les migrations SQL sont documentées

#### Intégration dans le workflow

##### Hook Pre-commit (automatique)

Le hook est installé dans `.git/hooks/pre-commit`. Il vérifie automatiquement la documentation avant chaque commit.

```bash
# Pour contourner temporairement le hook
git commit --no-verify -m "message"
```

##### Makefile

```bash
make doc-check     # Vérification rapide
make doc-update    # Mise à jour automatique
make doc-generate MODULE=notifications  # Génération module
```

##### CI/CD GitHub Actions

Le workflow `.github/workflows/documentation.yml` s'exécute sur :
- Push sur `main`/`develop`
- Pull requests modifiant la documentation ou le code

## 📁 Structure

```
.agents/
├── doc_agent.py              # Agent de documentation
├── README.md                 # Ce fichier
├── skills/                   # Skills pour les agents
│   └── financeperso-specific/
│       ├── SKILL.md
│       └── references/
└── subagents/               # Spécifications des sous-agents
    ├── AGENT-000-Orchestrator.md
    ├── AGENT-001-Database-Architect.md
    └── ...
```

## 🔧 Configuration

### Activer/Désactiver le hook pre-commit

```bash
# Rendre exécutable (activer)
chmod +x .git/hooks/pre-commit

# Désactiver temporairement
chmod -x .git/hooks/pre-commit
```

### Désactiver la vérification pour un commit

```bash
git commit --no-verify -m "message"
```

## 📝 Bonnes pratiques

1. **Toujours vérifier avant de push** : `make doc-check`
2. **Mettre à jour après changements majeurs** : `make doc-update`
3. **Documenter les nouveaux modules** : `make doc-generate MODULE=nom`
4. **Ne pas ignorer les erreurs de doc** en CI/CD

## 🐛 Dépannage

### Le hook pre-commit échoue

```bash
# Voir les détails
python .agents/doc_agent.py --check

# Corriger automatiquement
python .agents/doc_agent.py --update
```

### doc_agent.py non trouvé

Vérifiez que vous êtes à la racine du projet :

```bash
cd /Users/aurelien/Documents/Projets/FinancePerso
python .agents/doc_agent.py --check
```

---

*Dernière mise à jour : 2026-02-28*
