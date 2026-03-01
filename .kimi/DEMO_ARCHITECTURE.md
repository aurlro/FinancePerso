# 🎬 Démonstration Architecture - Feature Réelle

> Feature choisie : **"Ajouter un indicateur de budget dépassé sur les KPI Cards"**

---

## 🎯 Contexte

**Feature demandée :** Sur le dashboard V5.5, les KPI Cards doivent afficher une alerte visuelle quand le budget mensuel d'une catégorie est dépassé (>100%).

**Composants concernés :**
- `modules/ui/v5_5/components/kpi_card.py` (existant)
- `modules/ui/v5_5/dashboard/kpi_grid.py` (existant)
- Base de données : tables `budgets` et `transactions`

---

## 🔄 Déroulement selon l'architecture

### PHASE 1: consistency-keeper (Analyse initiale)

```
🔍 Analyse de la cohérence existante...

✅ Patterns identifiés à réutiliser:
   - KPICard dans modules/ui/v5_5/components/kpi_card.py
   - Thème Emerald avec tokens CSS existants
   - Composant Alert déjà existant dans feedback.py

✅ Vérification DRY:
   - Pas de composant budget-alert existant → création nécessaire
   - KPI Card déjà factorisé → étendre plutôt que dupliquer

✅ Documentation:
   - AGENTS.md mentionne les composants V5.5
   - Pas de doc spécifique sur KPI Cards → ajouter exemple

📋 Résultat: Peut étendre KPICard, pas besoin de nouveau composant
```

---

### PHASE 2: Skills techniques + financeperso-specific

```
🔍 Audit python-app-auditor + financeperso-specific

✅ Code existant analysé:
   - kpi_card.py: 89 lignes, bien structuré
   - Propriétés: title, value, trend, icon, color
   
✅ Conventions FinancePerso à respecter:
   - Widget keys: f"kpi_{category}_{timestamp}"
   - Messages en français
   - Utiliser theme.py pour couleurs
   - @st.cache_data pour requêtes budget

✅ Patterns DB identifiés:
   from modules.db.connection import get_db_connection
   with get_db_connection() as conn:
       cursor.execute("SELECT...")

📋 Résultat: Extension propre possible, respects conventions OK
```

---

### PHASE 3: AGENT-000 (Orchestration)

```
🎯 AGENT-000 analyse la demande:

Domaines concernés:
   1. UI Component (modification KPICard) → AGENT-009
   2. Analytics (calcul budget vs réel) → AGENT-006
   3. Database (requête budgets) → AGENT-001 (conseil)
   4. Tests (validation) → AGENT-012

Plan d'exécution:
   Étape 1: AGENT-009 étend KPICard avec prop `budget_status`
   Étape 2: AGENT-006 ajoute calcul budget/réel dans kpi_grid.py
   Étape 3: AGENT-012 teste avec MCP playwright
   
Dépendances: AGENT-009 → AGENT-006 → AGENT-012
```

---

### PHASE 4: Exécution par agents spécialisés

#### Étape 4.1: AGENT-009 (UI Component Architect)

**MCP utilisés:**
- `filesystem/read_file`: Lire `kpi_card.py` existant
- `filesystem/read_file`: Lire `theme.py` pour tokens couleurs

**Action:**
```python
# Extension de KPICard
class KPICard:
    def __init__(self, title, value, trend=None, icon=None, 
                 color=None, budget_status=None):  # ← AJOUT
        ...
        self.budget_status = budget_status  # 'under', 'warning', 'over'
    
    def render(self):
        # Logique existante...
        
        # AJOUT: Indicateur budget
        if self.budget_status == 'over':
            st.markdown(f"""
                <div class="kpi-alert kpi-alert-danger">
                    🔴 Budget dépassé de {self.budget_pct}%
                </div>
            """, unsafe_allow_html=True)
        elif self.budget_status == 'warning':
            st.markdown(f"""
                <div class="kpi-alert kpi-alert-warning">
                    ⚠️ Budget à {self.budget_pct}%
                </div>
            """, unsafe_allow_html=True)
```

**Résultat:** ✅ Composant étendu, CSS ajouté dans `theme.py`

---

#### Étape 4.2: AGENT-006 (Analytics Dashboard Engineer)

**MCP utilisés:**
- `sqlite/read_query`: Calcul budget vs réel
- `filesystem/read_file`: Lire `kpi_grid.py`

**Requête SQL (via MCP sqlite):**
```sql
SELECT 
    t.category_validated,
    SUM(ABS(t.amount)) as depense_mois,
    b.amount as budget_mois,
    ROUND(SUM(ABS(t.amount)) / b.amount * 100, 1) as pourcentage
FROM transactions t
JOIN budgets b ON t.category_validated = b.category
WHERE t.amount < 0 
    AND t.status = 'validated'
    AND strftime('%Y-%m', t.date) = strftime('%Y-%m', 'now')
GROUP BY t.category_validated
HAVING pourcentage > 80  -- Seulement si >80% pour optimisation
```

**Action dans `kpi_grid.py`:**
```python
@st.cache_data(ttl=300)
def get_budget_status():
    # Résultat de la requête MCP sqlite...
    return {
        'Alimentation': {'status': 'over', 'pct': 110},
        'Loisirs': {'status': 'warning', 'pct': 85},
        ...
    }

# Dans la boucle de rendu des KPIs
budget_info = budget_status.get(category)
kpi = KPICard(
    title=category,
    value=montant,
    budget_status=budget_info['status'] if budget_info else None,
    budget_pct=budget_info['pct'] if budget_info else None
)
```

**Résultat:** ✅ Intégration complète, cache ajouté

---

#### Étape 4.3: AGENT-012 (Test Automation Engineer)

**MCP utilisés:**
- `playwright/navigate`: Lancer app
- `playwright/take_screenshot`: Capturer dashboard

**Actions:**
```python
# Test E2E avec Playwright
playwright/navigate: {"url": "http://localhost:8501"}
playwright/wait_for: {"text": "Dashboard"}
playwright/take_screenshot: {"filename": "test_budget_alert.png"}

# Assertions visuelles:
# - KPI Card "Alimentation" doit avoir classe "kpi-alert-danger"
# - KPI Card "Loisirs" doit avoir classe "kpi-alert-warning"
# - KPI Card avec budget OK ne doit pas avoir d'alerte
```

**Résultat:** ✅ Screenshots capturés, alertes visuelles OK

---

### PHASE 5: consistency-keeper (Validation finale)

```
✅ Validation post-implémentation:

DRY Check:
   ✓ Pas de duplication de code
   ✓ Réutilisation de KPICard existant
   ✓ CSS ajouté dans theme.py (pas de nouveau fichier)

Doc Sync:
   ✓ CHANGELOG.md mis à jour (feature budget alert)
   ✓ AGENTS.md - section UI V5.5 enrichie
   ✓ Docstring ajoutée à KPICard.render()

Rangement:
   ✓ Fichiers au bon endroit
   ✓ Pas de fichiers temporaires
   ✓ Imports propres (pas circulaires)

Performance:
   ✓ Requête SQL optimisée (HAVING >80%)
   ✓ Cache @st.cache_data utilisé
   ✓ Pas de requête N+1
```

---

## 📊 Résumé de la démonstration

| Phase | Durée estimée | Résultat |
|-------|---------------|----------|
| consistency-keeper (analyse) | 2 min | Patterns identifiés, DRY OK |
| Skills audit | 3 min | Conventions validées |
| AGENT-000 routing | 1 min | Plan à 3 étapes |
| AGENT-009 (UI) | 10 min | Composant étendu |
| AGENT-006 (Analytics) | 10 min | Intégration + SQL |
| AGENT-012 (Tests) | 5 min | Screenshots validés |
| consistency-keeper (validation) | 2 min | Tous checks OK |
| **TOTAL** | **~33 min** | Feature livrée, testée, documentée |

---

## ✅ Ce qui a bien fonctionné

1. **consistency-keeper** a évité la création d'un nouveau composant inutile
2. **MCP sqlite** a permis de tester la requête SQL directement
3. **MCP playwright** a validé le rendu visuel sans code de test complexe
4. **AGENT-000** a coordonné les dépendances entre agents
5. **financeperso-specific** a garanti le respect des conventions

---

## 🎓 Apprentissages

**Ce pattern est applicable à:**
- Toute modification UI V5.5
- Features avec calculs métier (utiliser sqlite MCP)
- Features nécessitant validation visuelle (utiliser playwright MCP)

**Éviter quand:**
- Hotfix urgent (raccourcir le workflow)
- Modification triviale (< 5 lignes)
- Pas d'impact UI ni DB

---

**Démonstration réalisée le:** 2026-03-01
