# 🔧 Plan Expert - Remise en Ordre du Projet

## 📋 Situation Actuelle

✅ **Bonne nouvelle** : Le projet est **fonctionnel et stable**
- 203 tests passent
- Application Streamlit tourne parfaitement
- Code quality: 96/100

⚠️ **Le problème** : C'est le **développement local** qui est confus
- Pas d'environnement virtuel standardisé
- Commandes dispersées (ruff, pytest, etc.)
- CI/CD fonctionne mais pas intuitif

---

## 🎯 Plan d'Action (30 minutes)

### Étape 1 : Setup Unique (10 min)

```bash
# Une seule commande pour tout configurer
cd /Users/aurelien/Documents/Projets/FinancePerso
make setup
```

Ce que ça fait :
1. ✅ Crée `.venv/` (environnement isolé)
2. ✅ Installe toutes les dépendances
3. ✅ Configure les git hooks (pre-commit)
4. ✅ Crée `.env` si absent

### Étape 2 : Commandes Standardisées (5 min)

Après `make setup`, utilisez **uniquement** ces commandes :

| Commande | Quand l'utiliser | Temps |
|----------|------------------|-------|
| `make run` | Lancer l'app | instant |
| `make test` | Avant chaque commit | 5s |
| `make check` | Avant push | 30s |
| `make lint` | Vérifier style | 2s |
| `make format` | Formater code | 3s |
| `make clean` | Nettoyer cache | 1s |

**Plus besoin de se souvenir de `pytest`, `ruff`, `black` !**

### Étape 3 : Vérification (2 min)

```bash
# Vérifiez que tout est OK
python3 scripts/doctor.py
```

Objectif : **100% de santé**

### Étape 4 : GitHub Actions (Déjà fait ✅)

Le CI/CD est **déjà configuré** et fonctionne :
- `.github/workflows/ci.yml` - Tests & Lint
- `.github/workflows/release.yml` - Releases

**Pour voir les exécutions** :
1. Allez sur https://github.com/[user]/FinancePerso/actions
2. Voyez l'historique des runs

---

## 📁 Nouveaux Fichiers Créés

```
FinancePerso/
├── Makefile                    # Commandes standardisées ⭐
├── PROJECT_STATUS.md           # État du projet
├── PLAN_EXPERT.md             # Ce fichier
├── scripts/
│   ├── setup_dev_env.sh       # Setup automatique ⭐
│   └── doctor.py              # Diagnostic santé ⭐
├── .github/workflows/ci.yml    # CI amélioré
└── tests/README.md            # Stratégie de tests
```

---

## 🎓 Workflow Quotidien Recommandé

### Développement Normal

```bash
# 1. Activez l'environnement (une fois par session)
source .venv/bin/activate

# 2. Travaillez sur le code...
# ...

# 3. Testez rapidement (avant chaque commit)
make test

# 4. Commit
git commit -am "feat: ma feature"

# 5. Vérification complète (avant push)
make check

# 6. Push
git push origin ma-branche
```

### Résolution de Problèmes

```bash
# Si les tests échouent
make clean        # Nettoyer cache
make test         # Réessayer

# Si imports cassés
source .venv/bin/activate  # Vérifier env activé
pip install -r requirements.txt  # Réinstaller deps

# Si CI échoue en local
make ci           # Exécute exactement comme GitHub Actions
```

---

## 🔍 Architecture CI/CD Clarifiée

```
Push/PR sur main
       │
       ▼
┌─────────────────┐
│  1. Code Quality │  ← Ruff + Black
│     (30s)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. Tests        │  ← 203 tests
│     (2min)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. Security     │  ← Bandit scan
│     (30s)       │
└────────┬────────┘
         │
         ▼
     ✅ Merge OK
```

**Le CI fonctionne en 3 jobs parallèles** : Lint → Test → Security

---

## 📊 Matrice des Environnements

| Environnement | Python | Tests | Lint | Usage |
|---------------|--------|-------|------|-------|
| Local Dev | 3.12 | `make test` | `make lint` | Développement |
| CI/CD | 3.11, 3.12 | `pytest` | `ruff` | Validation |
| Production | 3.12 | - | - | Runtime Streamlit |

---

## ✅ Checklist Migration

- [ ] Lancer `make setup` (une fois)
- [ ] Vérifier `python3 scripts/doctor.py` = 100%
- [ ] Tester `make run` → App démarre
- [ ] Tester `make test` → Tous passent
- [ ] Commit les nouveaux fichiers
- [ ] Push → Vérifier CI vert sur GitHub

---

## 🆘 Support

| Problème | Solution |
|----------|----------|
| "Command not found: make" | `brew install make` (macOS) ou utiliser `./scripts/setup_dev_env.sh` |
| Tests lents | Utiliser `make test` (essentiels uniquement) |
| Erreurs d'import | Vérifier `source .venv/bin/activate` |
| CI rouge | Lire le log sur GitHub Actions |

---

## 🎯 Résumé

**Avant** : Commandes dispersées, confusion  
**Après** : `make setup` puis `make [commande]`

Le projet est **déjà bien structuré**, il manquait juste :
1. Un setup automatique ✅
2. Des commandes standardisées ✅
3. Un diagnostic santé ✅

**Prochaine étape** : Lancer `make setup` ! 🚀
