# 🧹 Commandes de nettoyage GitHub

> Exécuter ces commandes si vous avez `gh` (GitHub CLI) installé et authentifié

## 1. Supprimer les branches obsolètes sur GitHub

```bash
# Se connecter à GitHub (si pas déjà fait)
gh auth login

# Supprimer la branche Design
git push origin --delete Design

# Supprimer toutes les branches dependabot mergées
git branch -r --merged origin/main | grep "origin/dependabot/" | sed 's/origin\///' | xargs -I {} git push origin --delete {}
```

## 2. Fermer les PRs dependabot ouvertes (10 PRs)

```bash
# Fermer toutes les PRs dependabot ouvertes
gh pr list --author dependabot[bot] --state open --json number | jq -r '.[].number' | xargs -I {} gh pr close {} --delete-branch
```

Ou manuellement via l'interface web :
- https://github.com/aurlro/FinancePerso/pulls
- Cliquer sur chaque PR dependabot → "Close pull request"

## 3. Vérifier le résultat

```bash
# Lister les branches restantes
git branch -a

# Lister les PRs ouvertes
gh pr list --state open
```

## 4. Configurer dependabot (déjà fait via .github/dependabot.yml)

La configuration limite maintenant à **5 PRs max** avec **grouping** des mises à jour.

---

## ✅ Ce qui a déjà été nettoyé

| Élément | Statut |
|---------|--------|
| Branche Design locale | ✅ Supprimée |
| Branches dependabot mergées (2) | ✅ Supprimées |
| Workflows (v6 → v4/v5) | ✅ Corrigés |
| Configuration dependabot | ✅ Créée |
| Script cleanup_github.sh | ✅ Créé |

## 📊 Branches restantes à nettoyer

```
remotes/origin/Design  # À supprimer (déjà mergée)
remotes/origin/dependabot/github_actions/actions/github-script-8
remotes/origin/dependabot/github_actions/actions/setup-python-6
remotes/origin/dependabot/github_actions/actions/upload-artifact-7
remotes/origin/dependabot/github_actions/codecov/codecov-action-5
remotes/origin/dependabot/github_actions/docker/build-push-action-6
remotes/origin/dependabot/github_actions/docker/login-action-4
remotes/origin/dependabot/github_actions/docker/metadata-action-6
remotes/origin/dependabot/github_actions/docker/setup-buildx-action-4
remotes/origin/dependabot/github_actions/docker/setup-qemu-action-4
remotes/origin/dependabot/pip/black-26.1.0
remotes/origin/dependabot/pip/black-26.3.0
remotes/origin/dependabot/pip/cryptography-44.0.3
remotes/origin/dependabot/pip/pandas-2.3.3
remotes/origin/dependabot/pip/plotly-6.5.2
remotes/origin/dependabot/pip/plotly-6.6.0
remotes/origin/dependabot/pip/pydantic-2.12.5
remotes/origin/dependabot/pip/pytest-9.0.2
remotes/origin/dependabot/pip/python-dotenv-1.2.1
remotes/origin/dependabot/pip/python-dotenv-1.2.2
remotes/origin/dependabot/pip/ruff-0.15.4
remotes/origin/dependabot/pip/ruff-0.15.5
remotes/origin/dependabot/pip/sentry-sdk-2.53.0
remotes/origin/dependabot/pip/sentry-sdk-2.54.0
remotes/origin/dependabot/pip/streamlit-1.55.0
```

**Total: 24 branches à nettoyer + 10 PRs ouvertes**
