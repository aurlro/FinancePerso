# Guide Exécutif - Consolidation FinancePerso

> **Pour**: Développeur en charge de la consolidation  
> **Objectif**: Passer de 72k à 45k lignes en 5 semaines  
> **Méthode**: Scripts automatisés + validation manuelle

---

## 📊 État actuel (post Quick Wins)

### ✅ Déjà fait
- [x] Documentation: 23 → 4 fichiers MD (-83%)
- [x] __pycache__: 1,061 → 0 dossiers (-100%)
- [x] Validation imports: Tous les modules src/ fonctionnent

### 🔴 À faire (priorisé)

| Doublon | Fichiers | Lignes estimées | Action |
|---------|----------|-----------------|--------|
| modules/db/ vs modules/db_v2/ | 18 vs 14 | ~3,000 | **Migrer db → db_v2** |
| modules/ui/ vs modules/ui_v2/ | 73 vs 74 | ~8,000 | **Migrer ui → ui_v2** |
| cache_*.py (3 fichiers) | 3 | ~1,500 | **Fusionner** |
| analytics.py vs analytics_v2.py | 2 | ~800 | **Migrer** |
| notifications.py vs notifications_realtime.py | 2 | ~600 | **Fusionner** |
| archive/legacy_v5/ | 17 fichiers | ~5,000 | **Supprimer** |
| **TOTAL** | | **~18,900 lignes** | **-26%** |

---

## 🚀 Phase 2: Dédoublonage (Semaine 1-2)

### Jour 1-2: Migration DB

```bash
# Étape 1: Analyser les dépendances
python scripts/analyze_dependencies.py

# Étape 2: Vérifier ce qui utilise modules/db/
grep -r "from modules.db" --include="*.py" . | grep -v __pycache__ | head -20

# Étape 3: Migrer en mode dry-run
python scripts/migrate_module.py \
  --from modules/db \
  --to modules/db_v2 \
  --dry-run

# Étape 4: Si OK, exécuter la migration réelle
python scripts/migrate_module.py \
  --from modules/db \
  --to modules/db_v2

# Étape 5: Tester
python -c "from modules.db_v2 import *; print('✅ OK')"
```

### Jour 3-4: Migration UI

```bash
# Même procédure pour UI
python scripts/migrate_module.py \
  --from modules/ui \
  --to modules/ui_v2 \
  --dry-run

# Après validation
python scripts/migrate_module.py \
  --from modules/ui \
  --to modules/ui_v2
```

### Jour 5: Fusion modules secondaires

```bash
# Fusionner les caches
# modules/cache_manager.py + cache_monitor.py + cache_multitier.py → modules/performance/cache_advanced.py

# Vérifier quel fichier est utilisé
grep -r "cache_manager\|cache_monitor\|cache_multitier" --include="*.py" app.py pages/

# Si peu utilisé, supprimer et utiliser uniquement performance/cache_advanced.py
```

---

## 🧪 Phase 3: Tests rationalisés (Semaine 3)

### Structure cible

```
tests/
├── conftest.py                    # Fixtures
├── e2e/                          # 2 tests
│   ├── test_transaction_lifecycle.py
│   └── test_wealth_projection.py
├── integration/                   # 3 tests
│   ├── test_performance.py
│   ├── test_security.py
│   └── test_compliance.py
└── unit/                         # 5 tests
    ├── test_data_cleaning.py
    ├── test_subscriptions.py
    ├── test_wealth.py
    ├── test_cache.py
    └── test_ui.py
```

### Tests à créer

```python
# tests/e2e/test_transaction_lifecycle.py
def test_full_transaction_flow():
    """Test E2E: Import → Nettoyage → Catégorisation → Stockage"""
    # 1. Importer transaction brute
    # 2. Vérifier nettoyage
    # 3. Vérifier catégorisation
    # 4. Vérifier stockage
    pass

# tests/integration/test_performance.py  
def test_monte_carlo_speed():
    """Test: 1000 simulations en <2s"""
    import time
    start = time.time()
    quick_simulation(10000, 500, 10, ScenarioType.MODERATE, 1000)
    assert time.time() - start < 2.0
```

---

## 🔧 Phase 4: Intégration propre (Semaine 4)

### Vérifier l'intégration app.py

```python
# app.py - Structure simplifiée idéale
import streamlit as st

# Core (léger)
from modules.db import get_db
from modules.ui import apply_vibe_theme
from modules.logger import logger

# Business Logic (src/)
from src import (
    clean_transaction_label,
    SubscriptionDetector,
    MonteCarloSimulator,
    WealthManager,
)

# Views
from views.dashboard import render_dashboard
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

page = st.sidebar.radio("Navigation", list(PAGES.keys()))
PAGES[page]()
```

### Nettoyer les imports

```bash
# Vérifier les imports non utilisés
python -m vulture app.py modules/ src/ --min-confidence 80

# Optimiser les imports
isort app.py modules/ src/
```

---

## ✅ Phase 5: Validation (Semaine 5)

### Checklist finale

```bash
# 1. Tous les tests passent
pytest tests/ -x --tb=short

# 2. Pas d'erreurs de lint
ruff check src/ modules/

# 3. Application démarre
streamlit run app.py &
sleep 5
curl -s http://localhost:8501/_stcore/health | grep -q "200\|307" && echo "✅ OK"

# 4. Métriques
find src modules -name "*.py" | xargs wc -l | tail -1
# Objectif: < 50,000 lignes
```

---

## 📁 Scripts fournis

| Script | Usage | Quand l'utiliser |
|--------|-------|------------------|
| `scripts/analyze_dependencies.py` | Analyse des dépendances | Avant chaque migration |
| `scripts/migrate_module.py` | Migration sécurisée | Phase 2 |
| `scripts/quick_integrate.py` | Intégration rapide vues | Phase 4 |
| `scripts/run_production.sh` | Lancement production | Phase 5 |

---

## 🚨 Risques et mitigations

| Risque | Mitigation |
|--------|------------|
| Casse fonctionnalité | Backup avant chaque migration + tests |
| Perde du code utile | Analyse des dépendances avant suppression |
| Trop long | Approche incrémentale (une migration par jour) |
| Régression perf | Benchmarks avant/après |

---

## 📞 Support

Si bloqué:
1. Vérifier le backup dans `backup/`
2. Restaurer: `cp -r backup/migration_*/modules/db .`
3. Consulter `docs/archive/` pour l'historique
4. Lire `PLAN_ORCHESTRATION_REVISED.md` pour le contexte

---

## ✅ Sign-off checklist

- [ ] DB migré: modules/db/ → modules/db_v2/
- [ ] UI migré: modules/ui/ → modules/ui_v2/
- [ ] Doublons secondaires supprimés
- [ ] 10 tests créés et passants
- [ ] app.py intègre uniquement src/ + modules/ propres
- [ ] Application démarre sans erreur
- [ ] < 50,000 lignes de code

---

**Début**: Aujourd'hui  
**Fin estimée**: Dans 5 semaines  
**Validation finale**: Chef d'orchestre
