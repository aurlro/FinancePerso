# 🧪 Guide d'Exécution des Tests - FinancePerso

## ⚠️ Problème macOS .DS_Store

À cause de la protection SIP (System Integrity Protection) de macOS, pytest ne peut pas scanner les fichiers `.DS_Store` du projet, ce qui bloque l'exécution.

## ✅ Solutions

### Solution 1: Script de Test (RECOMMANDÉ)

Utilisez le script fourni qui contourne automatiquement le problème :

```bash
cd tests
./run_tests.sh
```

**Options** :
```bash
./run_tests.sh                    # Tous les tests
./run_tests.sh db/               # Tests DB uniquement
./run_tests.sh ui/               # Tests UI uniquement
./run_tests.sh test_integration.py  # Tests d'intégration
./run_tests.sh -k "transaction"  # Tests contenant "transaction"
```

### Solution 2: Supprimer .DS_Store Manuellement

```bash
# Depuis la racine du projet
find . -name ".DS_Store" -delete

# Puis lancer les tests
cd tests
python3 -m pytest -v
```

### Solution 3: Utiliser --ignore

```bash
cd tests
python3 -m pytest --ignore=../.DS_Store --ignore=.DS_Store -v
```

### Solution 4: Exécuter Tests Individuellement

```bash
# Tester un module spécifique (évite le scan du projet)
python3 -m pytest db/test_transactions.py -v
python3 -m pytest ui/test_filters.py -v
python3 -m pytest test_integration.py -v
```

---

## 📊 Commandes de Test

### Tests par Catégorie

```bash
# Tous les tests (189 tests)
./run_tests.sh

# DB uniquement (108 tests)
./run_tests.sh db/

# UI uniquement (54 tests)  
./run_tests.sh ui/

# Integration (9 tests)
./run_tests.sh test_integration.py

# Logic (28 tests)
./run_tests.sh test_grouping.py test_sorting.py
```

### Tests Spécifiques

```bash
# Une classe de tests
./run_tests.sh db/test_transactions.py::TestGetTransactions

# Un test précis
./run_tests.sh db/test_transactions.py::TestGetTransactions::test_get_all_transactions_empty

# Par mot-clé
./run_tests.sh -k "duplicate"
./run_tests.sh -k "budget"
```

### Options Utiles

```bash
# Arrêter au premier échec
./run_tests.sh -x

# Voir les print()
./run_tests.sh -s

# Mode verbose
./run_tests.sh -vv

# Résumé court
./run_tests.sh --tb=short

# Coverage HTML
./run_tests.sh --cov=modules --cov-report=html
```

---

## 🎯 Tests Disponibles

| Catégorie | Fichiers | Tests | Description |
|-----------|----------|-------|-------------|
| **DB** | 10 | 108 | CRUD, validation, audit |
| **UI** | 6 | 54 | Components, filters, logic |
| **Integration** | 1 | 9 | End-to-end workflows |
| **Logic** | 2 | 28 | Grouping, sorting |
| **TOTAL** | **19** | **199** | Full test suite |

---

## ⚡ Tests Rapides

```bash
# Test rapide (quelques tests pour vérifier)
./run_tests.sh db/test_budgets.py -v

# Test complet avec résumé
./run_tests.sh --tb=line

# Only failed tests from last run
./run_tests.sh --lf
```

---

## 🐛 Debugging

Si les tests échouent :

1. **Vérifier la DB de test**
```bash
# S'assurer qu'aucune DB de test ne traine
rm -f /tmp/test_*.db
```

2. **Réinstaller dépendances**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

3. **Vérifier pytest**
```bash
python3 -m pytest --version
# Devrait afficher: pytest 8.4.2
```

4. **Mode debug**
```bash
./run_tests.sh --pdb  # Drop into debugger on failure
./run_tests.sh -vv --tb=long  # Maximum verbosity
```

---

## 📝 Exemple de Sortie Réussie

```
🧪 FinancePerso Test Runner
================================

Lancement des tests...
========================= test session starts ==========================
platform darwin -- Python 3.12.2, pytest-8.4.2
rootdir: /Users/aurelien/Documents/Projets/FinancePerso
plugins: cov-7.0.0

db/test_transactions.py::TestGetTransactions::test_get_all ✓
db/test_categories.py::TestGetCategories::test_get_all ✓
...
========================= 199 passed in 5.23s ==========================
```

---

## 💡 Astuce

Ajoutez un alias dans votre `.zshrc` :

```bash
alias test-finance='cd ~/Documents/Projets/FinancePerso/tests && ./run_tests.sh'
```

Puis simplement :
```bash
test-finance
```
