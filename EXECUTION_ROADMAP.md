# Feuille de Route d'Exécution - Consolidation FinancePerso

> **Version**: 1.0  
> **Durée**: 5 semaines  
> **Objectif**: Passer de 72k à 45k lignes (-38%)

---

## 📋 Vue d'ensemble des 5 Phases

```
Semaine 1-2: DÉDOUBLONNAGE          (-26% lignes)
Semaine 3:   TESTS RATIONALISÉS     (10 tests stratégiques)
Semaine 4:   INTÉGRATION PROPRE     (app.py unifié)
Semaine 5:   VALIDATION FINALE      (Release v5.5)
```

---

## 🚀 Phase 1: Documentation (✅ FAITE)

**Résultat**: 23 → 4 fichiers MD (-83%)

### Actions déjà effectuées:
- ✅ Archivage 19 fichiers MD dans `docs/archive/`
- ✅ Conservation 4 fichiers essentiels
- ✅ Création `docs/ARCHITECTURE.md` et `docs/USER_GUIDE.md`
- ✅ Nettoyage 1,061 dossiers `__pycache__`

---

## 🔴 Phase 2: Dédoublonage (Semaine 1-2)

### Objectif: Supprimer ~18,900 lignes de doublons

#### Jour 1: Analyse
```bash
# Analyser les dépendances
python scripts/analyze_dependencies.py

# Identifier quels fichiers utilisent modules/db/
grep -r "from modules.db" --include="*.py" . | grep -v __pycache__
```

#### Jour 2: Migration DB (mode test)
```bash
# Dry-run pour voir ce qui va changer
python scripts/migrate_module.py \
  --from modules/db \
  --to modules/db_v2 \
  --dry-run

# Vérifier le backup créé
ls -la backup/migration_*/
```

#### Jour 3: Migration DB (exécution)
```bash
# Exécuter la migration réelle
python scripts/migrate_module.py \
  --from modules/db \
  --to modules/db_v2

# Tester
python -c "from modules.db_v2 import *; print('✅ OK')"

# Si OK, supprimer l'ancien
rm -rf modules/db
```

#### Jour 4: Migration UI (même procédure)
```bash
python scripts/migrate_module.py \
  --from modules/ui \
  --to modules/ui_v2

# Renommer pour simplicité
mv modules/ui_v2 modules/ui
```

#### Jour 5: Fusion modules secondaires
```bash
# Analyser les fichiers cache
python -c "
import ast
import os

cache_files = [
    'modules/cache_manager.py',
    'modules/cache_monitor.py', 
    'modules/cache_multitier.py'
]

for f in cache_files:
    if os.path.exists(f):
        with open(f) as file:
            tree = ast.parse(file.read())
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        print(f'{f}: {classes}')
"

# Garder uniquement modules/performance/cache_advanced.py
# Supprimer les anciens si non utilisés
```

#### Validation Phase 2:
```bash
# Compter les lignes
find src modules views -name "*.py" | xargs wc -l | tail -1
# Objectif: < 55,000 lignes
```

---

## 🧪 Phase 3: Tests Rationalisés (Semaine 3)

### Objectif: 10 tests stratégiques vs 27 tests dispersés

#### Jour 1: Créer structure
```bash
# Générer les tests
python scripts/create_tests_strategy.py

# Structure créée:
tests/
├── e2e/              (2 tests)
├── integration/      (3 tests)
└── unit/             (5 tests)
```

#### Jour 2: Implémenter tests E2E
```python
# tests/e2e/test_transaction_lifecycle.py
# → Compléter le test import → nettoyage → catégorisation

# tests/e2e/test_wealth_projection.py
# → Compléter le test patrimoine → projection → résultats
```

#### Jour 3: Implémenter tests Intégration
```python
# tests/integration/test_performance.py
# → Vérifier Monte Carlo < 2s

# tests/integration/test_security.py
# → Vérifier détection AML

# tests/integration/test_compliance.py
# → Vérifier Hard Delete RGPD
```

#### Jour 4: Implémenter tests Unit
```python
# tests/unit/test_data_cleaning.py
# tests/unit/test_subscriptions.py
# tests/unit/test_wealth.py
# tests/unit/test_cache.py
# tests/unit/test_ui.py
```

#### Jour 5: Exécuter et corriger
```bash
# Exécuter tous les tests
pytest tests/ -v --tb=short

# Si échecs, corriger
# Objectif: 10/10 tests passent
```

---

## 🔧 Phase 4: Intégration Propre (Semaine 4)

### Objectif: Une seule codebase fonctionnelle

#### Jour 1: Refactor app.py
```python
# app.py - Structure cible
import streamlit as st

# Imports core
from modules.db import get_db
from modules.ui import apply_vibe_theme

# Business logic (src/)
from src import (
    clean_transaction_label,
    SubscriptionDetector,
    MonteCarloSimulator,
    WealthManager,
)

# Views
from views.subscriptions import render_subscriptions
from views.projections import render_projections
from views.wealth import render_wealth

# Router
PAGES = {
    "Dashboard": render_dashboard,
    "Abonnements": render_subscriptions,
    "Projections": render_projections,
    "Patrimoine": render_wealth,
}
```

#### Jour 2: Nettoyer imports
```bash
# Optimiser les imports
python -m isort app.py src/ modules/ views/

# Vérifier imports non utilisés
python -m vulture app.py src/ modules/ --min-confidence 80
```

#### Jour 3: Intégrer vues
```bash
# Vérifier que les vues fonctionnent
python -c "
from views.subscriptions import render_subscriptions_page
from views.projections import render_projections_page
from views.wealth_view import render_wealth_dashboard
print('✅ Toutes les vues importables')
"
```

#### Jour 4: Test intégration
```bash
# Démarrer l'application
streamlit run app.py &

# Vérifier health
sleep 5
curl -s http://localhost:8501/_stcore/health | grep -q "200\|307" && echo "✅ OK"
```

#### Jour 5: Documentation
```bash
# Mettre à jour README
# Ajouter section "Nouveautés v5.5"
# Décrire la consolidation
```

---

## ✅ Phase 5: Validation Finale (Semaine 5)

### Objectif: Release candidate validée

#### Jour 1: Exécuter validation complète
```bash
python scripts/validate_consolidation.py
```

#### Jour 2: Performance checks
```bash
# Benchmark Monte Carlo
python -c "
import time
from src import quick_simulation, ScenarioType

start = time.time()
quick_simulation(10000, 500, 10, ScenarioType.MODERATE, 1000)
elapsed = time.time() - start

print(f'Monte Carlo 1000 sims: {elapsed:.2f}s')
assert elapsed < 2.0, 'Trop lent!'
print('✅ Performance OK')
"
```

#### Jour 3: Lint et formatage
```bash
# Formater
black src/ modules/ views/ --line-length 100

# Linter
ruff check src/ modules/ views/ --fix

# Types
mypy src/ --ignore-missing-imports
```

#### Jour 4: Tests finaux
```bash
# Tous les tests
pytest tests/ -v --cov=src --cov=modules --cov-report=html

# Vérifier couverture > 60%
```

#### Jour 5: Release
```bash
# Tag version
git tag -a v5.5.0 -m "Consolidation: -38% lignes de code"

# Créer release notes
cat > RELEASE_NOTES.md << 'EOF'
# FinancePerso v5.5.0

## 🎯 Consolidation majeure

### Changements
- Documentation: 23 → 4 fichiers (-83%)
- Code: 72k → 45k lignes (-38%)
- Tests: 27 dispersés → 10 stratégiques
- Architecture: Unifiée et simplifiée

### Performance
- Démarrage: <3s
- Monte Carlo: <2s pour 1000 sims
- Cache hit rate: >80%

### Prochaines étapes
- API REST (v6.0)
- Mobile App
EOF
```

---

## 📊 Checklist de validation

### Phase 2 (Dédoublonage)
- [ ] `modules/db/` migré vers `modules/db_v2/`
- [ ] `modules/ui/` migré vers `modules/ui_v2/`
- [ ] Doublons cache supprimés
- [ ] `archive/legacy/` supprimé
- [ ] < 55,000 lignes

### Phase 3 (Tests)
- [ ] 10 tests créés
- [ ] Tests E2E passent
- [ ] Tests intégration passent
- [ ] Tests unit passent

### Phase 4 (Intégration)
- [ ] `app.py` utilise uniquement `src/`
- [ ] Pas d'imports doublons
- [ ] Application démarre
- [ ] Navigation fonctionne

### Phase 5 (Release)
- [ ] `validate_consolidation.py` passe
- [ ] Performance < 2s (Monte Carlo)
- [ ] Lint: 0 erreur
- [ ] Tests: >60% couverture

---

## 🆘 Support et dépannage

### Si la migration échoue
```bash
# Restaurer depuis backup
cp -r backup/migration_YYYYMMDD_HHMMSS/modules/db modules/

# Ou restaurer tout
git checkout -- modules/db
```

### Si tests échouent
```bash
# Voir détails
pytest tests/ -v --tb=long

# Debug un test spécifique
pytest tests/unit/test_data_cleaning.py -v --pdb
```

### Si app.py ne démarre pas
```bash
# Vérifier imports
python -c "import app"

# Voir erreur complète
streamlit run app.py 2>&1 | head -50
```

---

## 📞 Ressources

| Ressource | Fichier |
|-----------|---------|
| Plan stratégique | `PLAN_ORCHESTRATION_REVISED.md` |
| Guide exécutif | `GUIDE_EXECUTIF_CONSOLIDATION.md` |
| Analyse dépendances | `scripts/analyze_dependencies.py` |
| Migration | `scripts/migrate_module.py` |
| Création tests | `scripts/create_tests_strategy.py` |
| Validation | `scripts/validate_consolidation.py` |

---

## ✅ Sign-off

| Phase | Responsable | Date | Signature |
|-------|-------------|------|-----------|
| Phase 2: Dédoublonage | | | |
| Phase 3: Tests | | | |
| Phase 4: Intégration | | | |
| Phase 5: Validation | | | |

---

**Début**: Aujourd'hui  
**Fin estimée**: 5 semaines  
**Validation**: Chef d'orchestre
