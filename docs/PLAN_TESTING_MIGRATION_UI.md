# Plan d'Action : Tests 50% + Migration UI Unifiée

**Date** : 14 mars 2026  
**Version** : 5.6.0  
**Objectifs** :
1. Atteindre 50% de couverture de tests (vs ~20% actuel)
2. Planifier et démarrer la migration UI unifiée (V5.5/V5.6)

---

## 📊 ÉTAT ACTUEL

### Tests
- **Modules Python** : 287
- **Fichiers de test** : 54
- **Fonctions de test** : ~340
- **Couverture estimée** : ~20-25%

### Architecture UI
```
modules/ui/
├── components/          # Legacy V5.0 (~25 composants)
├── dashboard/           # Legacy V5.0 (~10 composants)
├── v5_5/                # Nouveau Design System (~20 composants)
│   ├── components/      # Atomes/Molécules V5.5
│   ├── dashboard/       # Dashboard V5.5
│   └── pages/           # Controllers V5.5
├── atoms/               # Design System atomic (~5 composants)
├── molecules/           # Design System (~3 composants)
└── ...
```

**Problème** : Double système parallèle avec duplication logique

---

## 🎯 PARTIE 1 : AUGMENTER COUVERTURE TESTS À 50%

### Modules critiques SANS tests (Priorité 1)

| Module | Priorité | Complexité | Estimation |
|--------|----------|------------|------------|
| `modules/cashflow/` | High | Medium | 2 jours |
| `modules/wealth/` | High | Medium | 2 jours |
| `modules/ai/suggestions/` | High | High | 3 jours |
| `modules/open_banking/` | High | High | 3 jours |
| `modules/notifications/` | High | Medium | 2 jours |
| `modules/gamification/` | Medium | Medium | 2 jours |
| `modules/couple/` | Medium | Low | 1 jour |
| `modules/ingestion/` | Medium | Medium | 2 jours |
| `modules/categorization.py` | High | High | 3 jours |
| `modules/ai_manager.py` | High | High | 3 jours |

**Total Priorité 1** : ~23 jours → **Objectif : 15 jours** (focus sur les plus critiques)

### Modules avec tests insuffisants (Priorité 2)

| Module | Tests existants | Couverture | Action |
|--------|-----------------|------------|--------|
| `modules/db/` | 11 fichiers | ~60% | Compléter edge cases |
| `modules/ui/v5_5/` | 3 fichiers | ~15% | Tests composants |
| `modules/cache_*.py` | 1 fichier | ~30% | Tests multi-threading |
| `modules/export/` | 0 fichier | 0% | Tests PDF/CSV/Excel |

### Plan de bataille Tests (5 semaines)

#### Semaine 1 : Fondations métier
```
Jour 1-2 : modules/categorization.py + categorization_cascade.py
Jour 3-4 : modules/ai_manager.py (mock providers)
Jour 5   : modules/ingestion/ (parsing CSV)
```
**Tests à créer** : ~80

#### Semaine 2 : Modules avancés
```
Jour 1-2 : modules/cashflow/ (prédictions)
Jour 3-4 : modules/wealth/ (patrimoine)
Jour 5   : modules/couple/ (membres, prêts)
```
**Tests à créer** : ~60

#### Semaine 3 : IA et notifications
```
Jour 1-3 : modules/ai/suggestions/ (analyzers)
Jour 4-5 : modules/notifications/ (V3)
```
**Tests à créer** : ~70

#### Semaine 4 : Open Banking et exports
```
Jour 1-3 : modules/open_banking/
Jour 4-5 : modules/export/ + gamification/
```
**Tests à créer** : ~60

#### Semaine 5 : UI V5.5 et E2E
```
Jour 1-3 : modules/ui/v5_5/components/
Jour 4-5 : Tests E2E critiques (parcoures utilisateur)
```
**Tests à créer** : ~50

**Total prévu** : ~320 nouveaux tests + 340 existants = **~660 tests**  
**Objectif couverture** : 50%

---

## 🎨 PARTIE 2 : MIGRATION UI UNIFIÉE

### Analyse de la duplication

#### Composants Legacy (V5.0) à migrer
| Composant Legacy | Équivalent V5.5 | Status |
|------------------|-----------------|--------|
| `ui/components/loading_states.py` | `ui/v5_5/components/loader.py` | ❌ Manquant |
| `ui/components/empty_states.py` | `ui/molecules/empty_state.py` | ⚠️ Partiel |
| `ui/components/pagination.py` | - | ❌ Pas de remplacement |
| `ui/dashboard/kpi_cards.py` | `ui/v5_5/components/kpi_card.py` | ✅ Existe |
| `ui/dashboard/category_charts.py` | `ui/v5_5/components/charts/` | ⚠️ Partiel |

#### Architecture cible (Design System Atomic)
```
modules/ui/
├── tokens/              # Couleurs, spacing, typography, radius
├── atoms/               # Boutons, icônes, badges (bas niveau)
├── molecules/           # Cards, empty states, metrics (composés)
├── organisms/           # Header, sidebar, formulaires complexes
├── templates/           # Layouts de page
└── pages/               # Controllers spécifiques aux pages
```

### Plan de migration (4 phases)

#### Phase 1 : Fondations (Semaine 6)
```
Jour 1-2 : Finaliser le Design System
  - Compléter atoms/ (manque: tooltip, divider)
  - Compléter molecules/ (manque: modal, toast)
  
Jour 3-4 : Créer les composants manquants dans v5_5/
  - Pagination
  - Loading states
  - File upload
  
Jour 5 : Documentation du Design System
```

#### Phase 2 : Migration Dashboard (Semaine 7-8)
```
Semaine 7 :
  - Migrer dashboard/legacy → dashboard_v5.py
  - Remplacer kpi_cards.py
  - Remplacer category_charts.py
  
Semaine 8 :
  - Migrer evolution_chart.py
  - Migrer budget_tracker.py
  - Tests visuels (screenshots)
```

#### Phase 3 : Migration Pages (Semaine 9)
```
Jour 1-2 : Page Import (ui/importing/)
Jour 3-4 : Page Validation (ui/validation/)
Jour 5   : Page Configuration (ui/config/)
```

#### Phase 4 : Nettoyage (Semaine 10)
```
Jour 1-2 : Marquer composants legacy @deprecated
Jour 3-4 : Migrer pages restantes
Jour 5   : Suppression composants legacy (après validation)
```

---

## 📋 TÂCHES DÉTAILLÉES

### Tâche 1.1 : Tests Categorization
```python
# tests/test_categorization.py
class TestCategorizationCascade:
    """Tests la cascade de catégorisation."""
    
    def test_rule_exact_match(self, temp_db):
        """Règle exacte prioritaire."""
        pass
    
    def test_rule_pattern_match(self, temp_db):
        """Pattern matching partiel."""
        pass
    
    def test_ml_local_fallback(self, temp_db):
        """Fallback ML local."""
        pass
    
    def test_ai_cloud_fallback(self, temp_db, mock_ai):
        """Fallback IA cloud avec mock."""
        pass
```

### Tâche 1.2 : Tests AI Manager
```python
# tests/test_ai_manager.py
class TestAIManager:
    """Tests le gestionnaire IA unifié."""
    
    def test_provider_gemini(self, mock_gemini):
        """Provider Gemini fonctionne."""
        pass
    
    def test_provider_ollama(self, mock_ollama):
        """Provider Ollama fonctionne."""
        pass
    
    def test_fallback_chain(self):
        """Chaîne de fallback fonctionne."""
        pass
    
    def test_circuit_breaker(self):
        """Circuit breaker s'active après erreurs."""
        pass
```

### Tâche 2.1 : Composant Pagination V5.5
```python
# modules/ui/molecules/pagination.py
"""
Pagination molecule for the Design System.

Props:
    total_items: int
    items_per_page: int = 20
    current_page: int = 1
    on_page_change: Callable[[int], None]
    max_visible_pages: int = 5
"""
```

### Tâche 2.2 : Migration Dashboard Controller
```python
# modules/ui/pages/dashboard.py (nouveau)
"""
Unified dashboard controller using Design System V5.5.

Replaces:
    - modules/ui/dashboard/customizable_dashboard.py
    - modules/ui/v5_5/pages/dashboard_controller.py
"""
```

---

## 📈 MÉTRIQUES DE SUCCÈS

### Tests
| Métrique | Avant | Après (Objectif) |
|----------|-------|------------------|
| Fichiers de test | 54 | 85+ |
| Fonctions de test | 340 | 660+ |
| Couverture lignes | ~25% | 50% |
| Couverture branches | ~20% | 45% |
| Tests E2E | 3 | 10+ |

### UI
| Métrique | Avant | Après (Objectif) |
|----------|-------|------------------|
| Composants legacy | ~40 | 0 |
| Composants Design System | ~25 | 50+ |
| Duplication code UI | 30% | <10% |
| Temps chargement dashboard | ? | <1s |

---

## 🛠️ RESSOURCES NÉCESSAIRES

### Tests
- **Temps** : 5 semaines (1 développeur)
- **Outils** : pytest, pytest-cov, pytest-mock, freezegun
- **Infrastructure** : CI/GitHub Actions (déjà en place)

### UI
- **Temps** : 4 semaines (1 développeur)
- **Outils** : Playwright (tests visuels), Storybook (documentation)
- **Design** : Figma/Wireframes (si modifications UX)

---

## ⚠️ RISQUES ET MITIGATIONS

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Tests cassent CI | High | `continue-on-error` temporaire, puis rendre strict |
| Régression UI | High | Tests visuels Playwright avant/après |
| Migration trop longue | Medium | Approche par étapes, feature flags |
| Couverture 50% non atteinte | Low | Prioriser modules critiques d'abord |

---

## ✅ PROCHAINES ACTIONS IMMÉDIATES

1. **Aujourd'hui** : Créer les fichiers de test pour `categorization.py`
2. **Demain** : Implémenter `test_ai_manager.py` avec mocks
3. **Cette semaine** : Finaliser Design System (atoms/manquants)
4. **Semaine prochaine** : Démarrer migration Dashboard

---

*Document créé le 14/03/2026 - À mettre à jour chaque semaine avec l'avancement*
