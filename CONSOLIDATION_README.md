# Consolidation FinancePerso - README

> **Mission**: Rationaliser le codebase de 72k à 45k lignes  
> **Approche**: Scripts automatisés + validation manuelle  
> **Durée**: 5 semaines

---

## 🚀 Démarrage rapide (5 minutes)

```bash
# 1. Voir l'état actuel
python scripts/analyze_dependencies.py

# 2. Lire la feuille de route
cat EXECUTION_ROADMAP.md

# 3. Commencer la Phase 2 (dedoublonnage)
python scripts/migrate_module.py --from modules/db --to modules/db_v2 --dry-run
```

---

## 📁 Structure des fichiers livrés

### Documentation stratégique
- **`PLAN_ORCHESTRATION_REVISED.md`** - Plan stratégique détaillé (5 phases)
- **`EXECUTION_ROADMAP.md`** - Feuille de route jour par jour (5 semaines)
- **`GUIDE_EXECUTIF_CONSOLIDATION.md`** - Guide pas à pas pour développeur
- **`CONSOLIDATION_REPORT.md`** - Rapport d'avancement et métriques

### Scripts d'automatisation
- **`scripts/analyze_dependencies.py`** - Analyse des dépendances entre modules
- **`scripts/migrate_module.py`** - Migration sécurisée avec backup
- **`scripts/create_tests_strategy.py`** - Génération des 10 tests stratégiques
- **`scripts/validate_consolidation.py`** - Validation finale complète

---

## 📊 État actuel

### ✅ Déjà fait (Phase 1)
- [x] Documentation consolidée: 23 → 4 fichiers
- [x] __pycache__ nettoyé: 1,061 → 0 dossiers
- [x] Validation imports: Tous les modules fonctionnent

### 🔴 À faire (Phases 2-5)
- [ ] Phase 2: Dédoublonage (-26% lignes)
- [ ] Phase 3: Tests rationalisés (10 tests)
- [ ] Phase 4: Intégration propre
- [ ] Phase 5: Validation finale

---

## 🎯 Objectifs chiffrés

| KPI | Actuel | Cible | Gain |
|-----|--------|-------|------|
| Lignes de code | 72,602 | ~45,000 | **-38%** |
| Fichiers Python | 319 | ~200 | **-37%** |
| Fichiers .md | 23 | 4 | **-83%** ✅ |
| Tests | 27 (dispersés) | 10 (stratégiques) | Qualité |
| Temps démarrage | ? | <3s | Performance |

---

## 🔴 Phase 2: Dédoublonage (Semaine 1-2)

### Doublons à traiter

```
modules/db/ (18 fichiers)      → modules/db_v2/ (14 fichiers)    [-3,000 lignes]
modules/ui/ (73 fichiers)      → modules/ui_v2/ (74 fichiers)    [-8,000 lignes]
cache_*.py (3 fichiers)        → performance/cache_advanced.py   [-1,500 lignes]
analytics*.py (2 fichiers)     → analytics_v2.py                [-800 lignes]
archive/legacy/ (17 fichiers)  → SUPPRESSION                    [-5,000 lignes]
                                                                      ─────────
TOTAL:                                                               [-18,900 lignes]
```

### Procédure pour chaque doublon

```bash
# 1. Analyser
python scripts/analyze_dependencies.py

# 2. Tester migration (dry-run)
python scripts/migrate_module.py \
  --from modules/db \
  --to modules/db_v2 \
  --dry-run

# 3. Exécuter si OK
python scripts/migrate_module.py \
  --from modules/db \
  --to modules/db_v2

# 4. Valider
python -c "from modules.db_v2 import *; print('✅ OK')"
```

---

## 🧪 Phase 3: Tests (Semaine 3)

### Générer les tests

```bash
python scripts/create_tests_strategy.py
```

Crée automatiquement:
- `tests/e2e/` (2 tests)
- `tests/integration/` (3 tests)
- `tests/unit/` (5 tests)

### Exécuter les tests

```bash
pytest tests/ -v --tb=short
```

---

## 🔧 Phase 4: Intégration (Semaine 4)

### Structure cible app.py

```python
import streamlit as st

# Core
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

---

## ✅ Phase 5: Validation (Semaine 5)

### Validation complète

```bash
python scripts/validate_consolidation.py
```

Vérifie:
1. ✅ Tous les imports fonctionnent
2. ✅ < 50,000 lignes de code
3. ✅ Pas de doublons
4. ✅ 10 tests présents et passants
5. ✅ Documentation consolidée
6. ✅ app.py propre et fonctionnel

---

## 🆘 Dépannage

### Si migration échoue

```bash
# Restaurer backup
cp -r backup/migration_YYYYMMDD_HHMMSS/modules/db modules/

# Ou avec git
git checkout -- modules/db
```

### Si besoin d'aide

1. Consulter `GUIDE_EXECUTIF_CONSOLIDATION.md`
2. Vérifier `EXECUTION_ROADMAP.md` pour la procédure détaillée
3. Lire les logs du script

---

## 📊 Suivi de progression

Mettre à jour ce tableau quotidiennement:

| Semaine | Objectif | Réalisé | Status |
|---------|----------|---------|--------|
| Semaine 1 | Migration DB | | 🔴 |
| Semaine 2 | Migration UI + Cache | | 🔴 |
| Semaine 3 | 10 tests créés | | 🔴 |
| Semaine 4 | app.py unifié | | 🔴 |
| Semaine 5 | Release v5.5 | | 🔴 |

---

## 🎯 Validation finale

Cochez quand tout est terminé:

- [ ] `modules/db/` supprimé (db_v2 renommé)
- [ ] `modules/ui/` supprimé (ui_v2 renommé)
- [ ] Doublons secondaires supprimés
- [ ] 10 tests créés et passants
- [ ] `app.py` utilise uniquement `src/` propre
- [ ] Application démarre sans erreur
- [ ] `validate_consolidation.py` passe
- [ ] < 50,000 lignes de code
- [ ] Documentation à jour (4 fichiers)

---

**Chef d'orchestre**: ✅ Plan approuvé et outils livrés  
**Prochaine étape**: Exécuter Phase 2 (Dédoublonage)
