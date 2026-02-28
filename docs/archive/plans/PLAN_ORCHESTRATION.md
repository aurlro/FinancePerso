# Plan d'Orchestration - FinancePerso v5.4.0

> **Rôle**: Chef d'Orchestre  
> **Mission**: Analyse critique et plan d'amélioration  
> **Date**: 21 Février 2026

---

## 🎯 Vue d'ensemble de l'Audit

### Métriques clés
| Indicateur | Valeur | Seuil critique | Status |
|------------|--------|----------------|--------|
| Lignes de code | 72,602 | <50k ✅ | 🟡 Modéré |
| Fichiers Python | 319 | <200 ✅ | 🟡 Élevé |
| Ratio test/code | 3.7% (27 tests) | >20% ❌ | 🔴 Critique |
| Documentation | 22 fichiers MD | >10 ✅ | 🟢 Bon |
| Modules src/ | 8 nouveaux | N/A | 🟢 Bon |
| Couverture Phase 6 | 100% | 100% | 🟢 Bon |

---

## ✅ Forces identifiées

### 1. Architecture modulaire bien pensée
- Séparation claire `src/` (business logic) vs `modules/` (infrastructure)
- Pattern Repository dans `modules/db_v2/`
- EventBus pour découplage (`modules/core/events.py`)

### 2. Phases 4-5-6 de haute qualité
- **Phase 4**: Monte Carlo vectorisé performant (<2s pour 10k sims)
- **Phase 5**: Patrimoine holistique avec équité nette immobilière
- **Phase 6**: Design System Vibe + sécurité AML + RGPD

### 3. Documentation exhaustive
- 22 fichiers Markdown
- Guides par phase (PHASE4, 5, 6)
- UAT Guide pour recette

### 4. Sécurité et conformité
- Chiffrement AES-256
- Hard Delete RGPD
- Détection AML
- Human-in-the-loop

---

## 🔴 Points critiques à adresser

### CRITIQUE 1: Dette technique legacy (P0)
**Problème**: 72k lignes avec beaucoup de code legacy non utilisé

**Evidence**:
```
modules/ai/suggestions/        # Nouveau (16 analyzers)
modules/ai/smart_suggestions.py # Ancien (873 lignes) - DOUBLON

modules/db/                    # Ancien
modules/db_v2/                 # Nouveau - DOUBLON

modules/ui/                    # Ancien
modules/ui_v2/                 # Nouveau Atomic Design - DOUBLON

views/                         # Nouveau (subscriptions, projections, wealth_view)
pages/                         # Ancien Streamlit - POTENTIEL DOUBLON
```

**Impact**: 
- Confusion pour les développeurs
- Temps de chargement plus long
- Maintenance difficile

### CRITIQUE 2: Couverture de tests insuffisante (P0)
**Problème**: 27 tests pour 72k lignes = 3.7% de couverture

**Evidence**:
- Tests éparpillés dans `tests/`
- Pas de tests pour les nouveaux modules src/
- Pas de tests d'intégration end-to-end

**Impact**:
- Régressions non détectées
- Difficulté à refactorer
- Pas de CI/CD fiable

### CRITIQUE 3: Intégration src/ ↔ modules/ incomplète (P1)
**Problème**: Les modules src/ ne sont pas intégrés à l'application principale

**Evidence**:
```python
# Dans app.py - PAS d'import des nouveaux modules
# Manque:
# from src import WealthManager
# from views.wealth_view import render_wealth_dashboard
```

**Impact**:
- Fonctionnalités Phases 4-5-6 inaccessibles
- Travail "dans le vide"

### CRITIQUE 4: Gestion des dépendances (P1)
**Problème**: Pas de fichier requirements.txt à jour avec les nouvelles dépendances

**Evidence**:
- `src/math_engine.py` utilise numpy (déjà présent)
- `src/visualizations.py` utilise plotly (déjà présent)
- Mais pas de vérification de versions minimales

### CRITIQUE 5: Configuration dispersée (P2)
**Problème**: Plusieurs fichiers de config (pyproject.toml, pytest.ini, .streamlit/config.toml)

**Evidence**:
- `.streamlit/config.toml` - config Streamlit
- `pyproject.toml` - config Black/Ruff/pytest
- `pytest.ini` - config pytest (doublon?)

---

## 📋 Plan d'action priorisé

### Phase A: Stabilisation (Semaine 1-2) - P0

#### A1. Dédoublonnage du code (3 jours)
**Objectif**: Supprimer les doublons legacy/modules_v2

**Actions**:
1. **Analyser les doublons**:
   ```bash
   # Liste des fichiers potentiellement doublons
   modules/ai/smart_suggestions.py vs modules/ai/suggestions/
   modules/db/ vs modules/db_v2/
   modules/ui/ vs modules/ui_v2/
   ```

2. **Créer un rapport de migration**:
   - Quels fichiers sont utilisés dans app.py?
   - Quels fichiers sont réellement obsolètes?
   - Quels fichiers peuvent être fusionnés?

3. **Archiver le code obsolète**:
   ```bash
   mkdir -p archive/to_review/
   # Déplacer les fichiers non référencés
   ```

#### A2. Intégration src/ → app.py (2 jours)
**Objectif**: Rendre les nouvelles fonctionnalités accessibles

**Actions**:
1. **Créer un router pour les vues**:
   ```python
   # app.py ou nouvelle structure
   import streamlit as st
   from views.subscriptions import render_subscriptions_page
   from views.projections import render_projections_page
   from views.wealth_view import render_wealth_dashboard
   
   PAGES = {
       "Dashboard": render_dashboard,
       "Abonnements": render_subscriptions_page,
       "Projections": render_projections_page,
       "Patrimoine": render_wealth_dashboard,
   }
   ```

2. **Ajouter au menu Streamlit**:
   ```python
   # dans app.py
   with st.sidebar:
       page = st.radio("Navigation", list(PAGES.keys()))
   
   PAGES[page]()
   ```

#### A3. Tests critiques pour Phase 4-5-6 (2 jours)
**Objectif**: Couvrir les fonctions critiques

**Actions**:
1. **Créer tests/src/**:
   ```
   tests/
   ├── src/
   │   ├── test_math_engine.py
   │   ├── test_wealth_manager.py
   │   ├── test_agent_core.py
   │   └── test_security_monitor.py
   ```

2. **Tests prioritaires**:
   ```python
   # test_math_engine.py
   def test_monte_carlo_performance():
       """Doit s'exécuter en <2s"""
       start = time.time()
       result = quick_simulation(10000, 500, 10, ScenarioType.MODERATE, 1000)
       assert time.time() - start < 2.0
   
   def test_gbm_equation():
       """Vérifier la cohérence mathématique"""
       # S_t = S_0 * exp((μ - 0.5σ²)t)
       pass
   ```

### Phase B: Qualité (Semaine 3-4) - P1

#### B1. Suite de tests d'intégration (3 jours)
**Objectif**: Tests end-to-end des scénarios UAT

**Actions**:
1. **Créer tests/integration/test_e2e.py**:
   ```python
   def test_transaction_lifecycle():
       """Scénario 1: Transaction Mystère"""
       # 1. Import
       # 2. Nettoyage
       # 3. Catégorisation
       # 4. Vérification risk_flag
       pass
   
   def test_subscription_zombie_detection():
       """Scénario 2: Abonnement Zombie"""
       pass
   
   def test_wealth_projection_choc():
       """Scénario 3: Projection Choc"""
       pass
   ```

#### B2. CI/CD Pipeline (2 jours)
**Objectif**: Automatiser les tests et le déploiement

**Actions**:
1. **Créer .github/workflows/ci.yml**:
   ```yaml
   name: CI
   on: [push, pull_request]
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Setup Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.12'
         - name: Install dependencies
           run: pip install -r requirements-dev.txt
         - name: Run tests
           run: pytest tests/ -v --cov=src --cov=modules
         - name: Lint
           run: ruff check src/ modules/
   ```

#### B3. Documentation technique (2 jours)
**Objectif**: Documenter l'architecture pour les nouveaux développeurs

**Actions**:
1. **Créer ARCHITECTURE.md**:
   - Diagramme des flux de données
   - Description des modules
   - Guide de contribution

2. **Mettre à jour README.md**:
   - Section "Nouveautés v5.4"
   - Captures d'écran des nouvelles vues
   - Guide de démarrage rapide

### Phase C: Optimisation (Semaine 5-6) - P2

#### C1. Performance profiling (2 jours)
**Objectif**: Identifier les goulots d'étranglement

**Actions**:
1. **Profiler les fonctions critiques**:
   ```python
   # Avec cProfile
   python -m cProfile -o profile.stats app.py
   ```

2. **Optimiser si nécessaire**:
   - Monte Carlo (déjà optimisé ✅)
   - Requêtes DB (vérifier les indexes)
   - Chargement initial

#### C2. Consolidation configuration (2 jours)
**Objectif**: Unifier les fichiers de config

**Actions**:
1. **Fusionner pytest.ini dans pyproject.toml**:
   ```toml
   [tool.pytest.ini_options]
   testpaths = ["tests"]
   python_files = ["test_*.py"]
   ```

2. **Créer config/app.yaml**:
   ```yaml
   app:
     name: FinancePerso
     version: 5.4.0
   cache:
     default_ttl: 300
     max_size: 1000
   security:
     large_amount_threshold: 10000
   ```

#### C3. Monitoring et observability (2 jours)
**Objectif**: Suivre les performances en production

**Actions**:
1. **Intégrer Sentry** (déjà présent dans requirements)
2. **Ajouter des métriques**:
   ```python
   from modules.performance import get_cache_stats
   # Dashboard de monitoring
   ```

---

## 🎨 Recommandations architecturales

### R1: Pattern Ports & Adapters (Hexagonal)
**Problème actuel**: Couplage fort entre UI et Business Logic

**Solution**:
```
src/
├── domain/              # Coeur métier (entiités, value objects)
│   ├── entities/
│   │   ├── transaction.py
│   │   ├── subscription.py
│   │   └── asset.py
│   └── services/
│       ├── categorization_service.py
│       └── projection_service.py
├── application/         # Use cases
│   ├── ports/
│   │   ├── for_categorizing.py
│   │   └── for_projecting.py
│   └── services/
├── infrastructure/      # Adapters
│   ├── db/
│   ├── ai/
│   └── cache/
└── interface/           # UI (Streamlit)
    └── streamlit/
```

### R2: Feature Flags
**Problème**: Déploiement risqué des nouvelles fonctionnalités

**Solution**:
```python
from modules.feature_flags import is_enabled

if is_enabled("wealth_dashboard_v2"):
    render_wealth_dashboard()
else:
    render_legacy_dashboard()
```

### R3: API Layer
**Problème**: UI directement couplée aux services

**Solution**:
```python
# src/api/routes.py
from fastapi import FastAPI

app = FastAPI()

@app.post("/api/v1/wealth/projection")
def create_projection(request: ProjectionRequest):
    return project_wealth_evolution(...)
```

---

## 📊 Tableau de bord de progression

| Tâche | Priorité | Estimation | Assigné | Status |
|-------|----------|------------|---------|--------|
| **PHASE A: Stabilisation** | | | | |
| A1.1 Analyse doublons | P0 | 1j | | 🔴 À faire |
| A1.2 Archivage code obsolète | P0 | 2j | | 🔴 À faire |
| A2.1 Router vues | P0 | 1j | | 🔴 À faire |
| A2.2 Intégration app.py | P0 | 1j | | 🔴 À faire |
| A3.1 Tests src/ | P0 | 2j | | 🔴 À faire |
| **PHASE B: Qualité** | | | | |
| B1.1 Tests E2E | P1 | 3j | | 🔴 À faire |
| B2.1 CI/CD Pipeline | P1 | 2j | | 🔴 À faire |
| B3.1 Documentation | P1 | 2j | | 🔴 À faire |
| **PHASE C: Optimisation** | | | | |
| C1.1 Profiling | P2 | 2j | | 🔴 À faire |
| C2.1 Config unifiée | P2 | 2j | | 🔴 À faire |
| C3.1 Monitoring | P2 | 2j | | 🔴 À faire |

**Total estimé**: 21 jours (~1 mois avec marge)

---

## 🚀 Quick Wins (à faire immédiatement)

### QW1: Intégration rapide des vues (30 min)
```python
# Dans app.py, ajouter:
import sys
sys.path.insert(0, str(Path(__file__).parent))

from views.subscriptions import render_subscriptions_page
from views.projections import render_projections_page
from views.wealth_view import render_wealth_dashboard

# Dans la sidebar
st.sidebar.header("🆕 Nouveautés v5.4")
if st.sidebar.button("📊 Patrimoine 360°"):
    render_wealth_dashboard()
```

### QW2: Vérifier les imports (15 min)
```bash
python -c "from src import *; print('✅ Imports OK')"
```

### QW3: Lancer tests existants (5 min)
```bash
pytest tests/ -x --tb=short
```

---

## 💡 Vision long terme (v6.0)

### Objectifs
1. **API REST**: Découpler frontend/backend
2. **Mobile App**: React Native ou PWA
3. **Multi-utilisateur**: Authentification complète
4. **Banking API**: Connexion directe aux banques
5. **ML Pipeline**: Entraînement automatique des modèles

### Architecture cible
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Mobile    │     │   Web App   │     │   Desktop   │
│   (PWA)     │     │  (Streamlit)│     │   (Tauri)   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌──────┴──────┐
                    │  API Gateway │
                    │   (FastAPI)  │
                    └──────┬──────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
┌──────┴──────┐    ┌──────┴──────┐    ┌──────┴──────┐
│   Domain    │    │   Domain    │    │   Domain    │
│  (Patrimoine)│    │ (Abonnements)│   │  (Budget)   │
└─────────────┘    └─────────────┘    └─────────────┘
```

---

## 🎯 Métriques de succès

### KPIs à atteindre dans 1 mois
| KPI | Actuel | Cible | Comment mesurer |
|-----|--------|-------|-----------------|
| Couverture tests | 3.7% | >50% | `pytest --cov` |
| Temps build CI | N/A | <5min | GitHub Actions |
| Code dupliqué | ~30% | <10% | `jscpd` ou similaire |
| Dette technique | Élevée | Modérée | SonarQube |
| Temps démarrage | ? | <3s | `time streamlit run` |

---

## ✅ Conclusion

### Ce qui est EXCELLENT ✅
1. Les phases 4-5-6 sont techniquement impeccables
2. Architecture modulaire bien pensée
3. Documentation exhaustive
4. Sécurité et conformité RGPD

### Ce qui doit être PRIORISÉ 🔴
1. **Intégration immédiate** des nouveaux modules dans app.py
2. **Dédoublonnage** du code legacy
3. **Tests** pour atteindre >50% couverture
4. **CI/CD** pour éviter les régressions

### Prochaine action immédiate
```bash
# 1. Créer une branche de stabilisation
git checkout -b stabilisation/v5.4.1

# 2. Intégrer les vues dans app.py
# (voir Quick Win QW1)

# 3. Tester localement
streamlit run app.py

# 4. Commiter
git add app.py
git commit -m "feat: intégration vues Phases 4-5-6"
```

---

**Status**: 🔴 **Action requise** - Stabilisation nécessaire avant nouvelles features  
**Chef d'orchestre**: Approuvé pour production après Phase A  
**Prochaine revue**: Dans 2 semaines (post Phase A)
