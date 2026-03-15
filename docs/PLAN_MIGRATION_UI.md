# Plan de Migration UI Unifiée

**Objectif** : Unifier les deux systèmes UI (Legacy V5.0 + V5.5) sous le Design System Atomic

**Durée estimée** : 4 semaines
**Date de début** : Semaine 6 (après les 5 semaines de tests)

---

## 📊 ANALYSE DE L'EXISTANT

### Architecture Legacy (V5.0)
```
modules/ui/
├── components/          # 25+ composants (legacy)
│   ├── loading_states.py
│   ├── empty_states.py
│   ├── pagination.py
│   ├── filters.py
│   └── ...
├── dashboard/           # 10+ composants
│   ├── kpi_cards.py
│   ├── category_charts.py
│   ├── evolution_chart.py
│   └── ...
└── ...
```

### Architecture V5.5 (Design System)
```
modules/ui/
├── tokens/              # Design tokens (couleurs, spacing, typography)
├── atoms/               # Composants atomiques (bas niveau)
├── molecules/           # Composants moléculaires
└── v5_5/                # Implémentation V5.5
    ├── components/
    ├── dashboard/
    └── pages/
```

### Problèmes identifiés

1. **Duplication** : `kpi_cards.py` (legacy) vs `kpi_card.py` (v5_5)
2. **Manquants** : Pagination, loading states dans V5.5
3. **Incohérence** : Styles et comportements différents
4. **Dette technique** : Double maintenance

---

## 🎯 ARCHITECTURE CIBLE

### Design System Atomic complet
```
modules/ui/
├── tokens/              # Constantes de design
│   ├── colors.py        # Palette de couleurs
│   ├── spacing.py       # Espacements
│   ├── typography.py    # Polices et tailles
│   └── radius.py        # Border radius
│
├── atoms/               # Éléments de base
│   ├── button.py        # Boutons
│   ├── icon.py          # Icônes
│   ├── badge.py         # Badges
│   ├── input.py         # Champs de saisie
│   ├── select.py        # Sélecteurs
│   └── tooltip.py       # Infobulles
│
├── molecules/           # Composants composés
│   ├── card.py          # Cartes
│   ├── empty_state.py   # États vides
│   ├── metric.py        # Métriques/KPI
│   ├── pagination.py    # Pagination (NOUVEAU)
│   ├── modal.py         # Modales
│   └── toast.py         # Notifications toast
│
├── organisms/           # Composants complexes
│   ├── header.py        # Header de page
│   ├── sidebar.py       # Navigation latérale
│   ├── transaction_form.py
│   └── filter_panel.py
│
├── templates/           # Layouts
│   ├── page_layout.py   # Layout standard
│   ├── dashboard_layout.py
│   └── wizard_layout.py
│
└── pages/               # Controllers de pages
    ├── dashboard.py     # Dashboard unifié
    ├── import_page.py   # Import transactions
    ├── validation_page.py
    └── settings_page.py
```

---

## 📅 PHASES DE MIGRATION

### Phase 1 : Fondations (Semaine 6)

#### Jour 1-2 : Compléter le Design System
- [ ] Créer `modules/ui/atoms/tooltip.py`
- [ ] Créer `modules/ui/atoms/divider.py`
- [ ] Créer `modules/ui/atoms/switch.py`
- [ ] Documenter les atoms dans `docs/DESIGN_SYSTEM.md`

#### Jour 3-4 : Créer les molécules manquantes
- [ ] Créer `modules/ui/molecules/pagination.py`
- [ ] Créer `modules/ui/molecules/modal.py`
- [ ] Créer `modules/ui/molecules/toast.py`
- [ ] Créer `modules/ui/molecules/loader.py`

**Spécification Pagination** :
```python
@dataclass
class PaginationProps:
    total_items: int
    items_per_page: int = 20
    current_page: int = 1
    on_page_change: Callable[[int], None]
    max_visible_pages: int = 5
```

#### Jour 5 : Documentation
- [ ] Créer `docs/UI_COMPONENTS.md`
- [ ] Documenter chaque composant avec exemples
- [ ] Créer guide d'utilisation

---

### Phase 2 : Migration Dashboard (Semaine 7-8)

#### Semaine 7 : Core Dashboard

**Tâches** :
1. **Remplacer `dashboard/kpi_cards.py`**
   - Utiliser `v5_5/components/kpi_card.py`
   - Adapter l'interface si nécessaire
   - Tests visuels

2. **Remplacer `dashboard/category_charts.py`**
   - Utiliser `v5_5/components/charts/`
   - Migrer vers Plotly/D3 unifié
   - Préserver les fonctionnalités

3. **Créer `pages/dashboard.py` (unifié)**
   ```python
   # modules/ui/pages/dashboard.py
   """
   Dashboard controller unifié.
   
   Remplace:
       - modules/ui/dashboard/customizable_dashboard.py
       - modules/ui/v5_5/pages/dashboard_controller.py
   """
   ```

#### Semaine 8 : Features avancées

**Tâches** :
1. Migrer `evolution_chart.py`
2. Migrer `budget_tracker.py`
3. Migrer `smart_recommendations.py`
4. Tests E2E dashboard (Playwright)

---

### Phase 3 : Migration Pages Majeures (Semaine 9)

#### Jour 1-2 : Page Import
```
modules/ui/importing/main.py → modules/ui/pages/import_page.py
```
- Conserver la logique métier
- Remplacer les composants UI
- Tests fonctionnels

#### Jour 3-4 : Page Validation
```
modules/ui/validation/main.py → modules/ui/pages/validation_page.py
```
- Migrer le grouping
- Migrer le row_view
- Conserver la logique de validation

#### Jour 5 : Page Configuration
```
modules/ui/config/ → modules/ui/pages/settings_page.py
```
- Unifier la gestion des paramètres
- Migrer chaque section

---

### Phase 4 : Nettoyage (Semaine 10)

#### Jour 1-2 : Déprécation
- [ ] Ajouter `@deprecated` aux composants legacy
- [ ] Logger warnings quand utilisés
- [ ] Créer liste de migration

#### Jour 3-4 : Migration pages restantes
- [ ] Intelligence
- [ ] Budgets
- [ ] Audit
- [ ] Assistant

#### Jour 5 : Suppression
- [ ] Supprimer `modules/ui/components/` (legacy)
- [ ] Supprimer `modules/ui/dashboard/` (legacy)
- [ ] Mettre à jour les imports
- [ ] Tests complets

---

## 🗺️ MAPPING DES COMPOSANTS

### Table de correspondance

| Legacy (V5.0) | V5.5 / Cible | Status |
|---------------|--------------|--------|
| `components/loading_states.py` | `molecules/loader.py` | À créer |
| `components/empty_states.py` | `molecules/empty_state.py` | Existe |
| `components/pagination.py` | `molecules/pagination.py` | À créer |
| `components/filters.py` | `organisms/filter_panel.py` | À créer |
| `components/tag_selector.py` | `molecules/tag_selector.py` | Existe |
| `dashboard/kpi_cards.py` | `v5_5/components/kpi_card.py` | Existe |
| `dashboard/category_charts.py` | `v5_5/components/charts/` | Existe |
| `dashboard/evolution_chart.py` | `v5_5/components/charts/line.py` | À créer |
| `couple/dashboard.py` | `pages/couple_dashboard.py` | À créer |

---

## 🧪 STRATÉGIE DE TESTS

### Tests visuels (Playwright)
```python
# tests/ui/visual/test_dashboard_migration.py

def test_dashboard_v5_5_renders(page):
    """Le nouveau dashboard s'affiche correctement."""
    page.goto("/dashboard")
    
    # Screenshot de référence
    expect(page).to_have_screenshot("dashboard-v5_5.png")

def test_pagination_component(page):
    """La pagination fonctionne."""
    page.goto("/transactions")
    page.click("[data-testid=pagination-next]")
    
    expect(page.locator("[data-testid=page-number]")).to_have_text("2")
```

### Tests composants
```python
# tests/ui/components/test_pagination.py

class TestPagination:
    def test_renders_correct_number_of_pages(self):
        pagination = Pagination(total_items=100, items_per_page=20)
        assert pagination.total_pages == 5
    
    def test_calls_callback_on_page_change(self):
        callback = Mock()
        pagination = Pagination(
            total_items=100,
            on_page_change=callback
        )
        pagination.go_to_page(3)
        callback.assert_called_with(3)
```

---

## 📋 CHECKLIST DE MIGRATION

### Pour chaque composant
- [ ] Analyser le composant legacy
- [ ] Vérifier si équivalent existe dans V5.5
- [ ] Créer/adapter le composant cible
- [ ] Migrer les usages
- [ ] Tests unitaires
- [ ] Tests visuels
- [ ] Documentation
- [ ] Marquer legacy comme @deprecated

### Validation finale
- [ ] Tous les imports legacy remplacés
- [ ] Tests E2E passent
- [ ] Screenshots comparatifs validés
- [ ] Performance maintenue/améliorée
- [ ] Documentation à jour

---

## ⚠️ RISQUES ET MITIGATIONS

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Régression fonctionnelle | High | Feature flags, tests E2E complets |
| Performance dégradée | Medium | Benchmarks avant/après, lazy loading |
| Incompréhension équipe | Low | Documentation, workshop Design System |
| Migration trop longue | Medium | Sprints 2 semaines, livraisons incrémentales |

---

## 📈 MÉTRIQUES DE SUCCÈS

### Avant migration
- Composants legacy : ~40
- Composants V5.5 : ~25
- Duplication estimée : 30%

### Après migration (objectif)
- Composants unifiés : ~50
- Duplication : <10%
- Temps chargement dashboard : <1s
- Cohérence visuelle : 100%

---

## 🚀 PROCHAINES ACTIONS

1. **Cette semaine** : Valider ce plan avec l'équipe
2. **Semaine 6 J1** : Commencer Phase 1 (atoms manquants)
3. **Semaine 6 J3** : Créer composant Pagination
4. **Semaine 7 J1** : Démarrer migration Dashboard

---

*Document créé le 14/03/2026 - Dernière mise à jour: 14/03/2026*
