# 🏗️ Architecture d'Orchestration Complète - FinancePerso

> Organisation hiérarchique : **Outils natifs** → **MCP Servers** → **Skills** → **Agents** → **Sous-Agents**

---

## 📊 Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         ARCHITECTURE 5 COUCHES                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  COUCHE 1: OUTILS NATIFS (Kimi Core)                                            │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐                   │
│  │ReadFile │ │WriteFile│ │ Shell   │ │ Grep    │ │ Glob    │  ... (20+ outils) │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘                   │
│                                                                                  │
│  COUCHE 2: MCP SERVERS (Extensions)                                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐                   │
│  │ sqlite  │ │filesystem│ │ fetch   │ │ github  │ │playwright│  ...             │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘                   │
│                                                                                  │
│  COUCHE 3: SKILLS (Connaissances & Conventions)                                 │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐                   │
│  │consistency-     │ │python-app-      │ │streamlit-app-   │  ...               │
│  │keeper           │ │auditor          │ │auditor          │                   │
│  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘                   │
│           │                   │                   │                             │
│           └───────────────────┼───────────────────┘                             │
│                               ▼                                                 │
│  COUCHE 4: AGENT ORCHESTRATOR (AGENT-000)                                       │
│  ┌─────────────────────────────────────────────────────────────────┐           │
│  │  Routeur central - Coordonne tous les agents spécialisés         │           │
│  │  • Notifie les modifications                                     │           │
│  │  • Gère les dépendances                                          │           │
│  │  • Planifie l'ordre d'exécution                                  │           │
│  └────────────────────────┬────────────────────────────────────────┘           │
│                           │                                                     │
│           ┌───────────────┼───────────────┐                                     │
│           ▼               ▼               ▼                                     │
│  COUCHE 5: SOUS-AGENTS (Spécialisés par domaine)                                │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐                   │
│  │AGENT-001│ │AGENT-004│ │AGENT-009│ │AGENT-012│ │AGENT-019│  ... (22 agents)  │
│  │Database │ │Transac- │ │   UI    │ │  Tests  │ │  Perf   │                   │
│  │Architect│ │ tions   │ │Component│ │Automation│ │Engineer │                   │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘                   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Principes d'Utilisation

### Quand utiliser chaque couche ?

| Couche | Cas d'usage | Exemple |
|--------|-------------|---------|
| **Outils natifs** | Actions directes, simples, rapides | Lire un fichier, exécuter une commande shell |
| **MCP Servers** | Capacités spécialisées, état persistant | SQL sur la base, navigation fichiers avancée |
| **Skills** | Connaissances contextuelles, audit | Vérifier DRY, conventions projet |
| **AGENT-000** | Coordination multi-agents | Démarrer une feature complexe |
| **Sous-Agents** | Exécution spécialisée | Implémenter un composant UI V5.5 |

---

## 🔧 Couche 1: Outils Natifs vs MCP

### Outils Natifs (disponibles immédiatement)

```python
# ✅ Utiliser pour: Actions simples et directes
ReadFile(path="modules/ui/feedback.py")
Shell(command="pytest tests/test_essential.py")
Grep(pattern="def validate", path="modules/")
WriteFile(path="docs/guide.md", content="...")
```

### MCP Servers (à configurer)

```python
# ✅ Utiliser pour: Capacités spécialisées avec état

# MCP SQLite - Analytics et debug base de données
sqlite/read_query: "SELECT COUNT(*) FROM transactions WHERE status='pending'"

# MCP Filesystem - Exploration avancée
filesystem/read_file: {"path": "/modules/ui/v5_5/theme.py"}
filesystem/list_directory: {"path": "/modules"}

# MCP Fetch - Requêtes API/web
fetch/fetch: {"url": "https://api.github.com/repos/user/repo/issues"}

# MCP GitHub - Gestion repo
github/create_issue: {"owner": "...", "repo": "...", "title": "..."}

# MCP Playwright - Tests navigateur
playwright/navigate: {"url": "http://localhost:8501"}
playwright/take_screenshot: {}
```

### Matrice de décision

| Besoin | Outil natif | MCP Server | Raison |
|--------|-------------|------------|--------|
| Lire un fichier connu | ✅ ReadFile | ❌ | Plus rapide, pas de config |
| Requête SQL complexe | ❌ | ✅ sqlite | Capacité dédiée, réutilisable |
| Explorer arborescence | ❌ | ✅ filesystem | Navigation récursive |
| Appel API externe | ❌ | ✅ fetch | Gestion headers, retry |
| Exécuter commande shell | ✅ Shell | ❌ | Flexibilité maximale |
| Screenshot navigateur | ❌ | ✅ playwright | Automatisation complète |
| Créer issue GitHub | ❌ | ✅ github | API structurée |

---

## 🧠 Couche 3: Skills - Quand les invoquer

### Hiérarchie des Skills

```
skills-orchestrator (meta - coordonne les autres)
    │
    ├── consistency-keeper (garde-fou - TOUJOURS en 1er)
    │
    ├── python-app-auditor (audit code Python)
    ├── streamlit-app-auditor (audit fonctionnel Streamlit)
    ├── ux-product-designer (design/UX)
    ├── project-auditor (audit global projet)
    │
    └── financeperso-specific (conventions projet - COMBINÉ)
```

### Protocole d'invocation

```
# 1. TOUJOURS commencer par consistency-keeper
consistency-keeper analyze
    └── Identifie patterns existants
    └── Vérifie cohérence actuelle
    └── Liste les fichiers à réutiliser

# 2. COMBINER avec skill technique + projet
python-app-auditor + financeperso-specific
    └── Audit qualité + conventions projet

# 3. streamlit-app-auditor (si test runtime)
streamlit-app-auditor + financeperso-specific
    └── Test app lancée + conventions UI

# 4. CONCLURE avec consistency-keeper
consistency-keeper validate
    └── Vérifie DRY respecté
    └── Vérifie doc synchronisée
```

### Règles ABSOLUES

1. **consistency-keeper** = TOUJOURS en PREMIER et en DERNIER
2. **financeperso-specific** = TOUJOURS COMBINÉ (jamais seul)
3. **skills-orchestrator** = Si plusieurs skills en parallèle nécessaires

---

## 🤖 Couche 4-5: Agents - Workflow

### AGENT-000 (Orchestrator) - OBLIGATOIRE

**Rôle:** Routeur central - Aucun sous-agent ne doit être appelé directement

```
Utilisateur demande:
"Crée un nouveau composant KPI Card pour le dashboard"

    ↓

AGENT-000 reçoit la demande
    ├── Analyse le domaine (UI ? DB ? IA ? Tests ?)
    ├── Identifie agent(s) spécialisé(s)
    ├── Vérifie dépendances entre agents
    └── Planifie séquence d'exécution

    ↓

AGENT-000 délègue à AGENT-009 (UI Component Architect)
    └── Spécialiste UI implémente le composant

    ↓

AGENT-000 notifie AGENT-006 (Analytics Dashboard)
    └── Vérifie intégration dashboard

    ↓

AGENT-000 coordonne AGENT-012 (Test Automation)
    └── Génère tests pour le composant

    ↓

AGENT-000 retourne rapport final à l'utilisateur
```

### Mapping Domaine → Agent

| Domaine | Agent | MCP Utiles |
|---------|-------|------------|
| Base de données | AGENT-001 | sqlite, filesystem |
| Sécurité | AGENT-002 | github (secrets scanning) |
| DevOps/Docker | AGENT-003 | filesystem, shell |
| Transactions | AGENT-004 | sqlite |
| Catégorisation IA | AGENT-005 | sqlite, context7 |
| Analytics/Dashboard | AGENT-006 | sqlite, playwright |
| Providers IA | AGENT-007 | fetch, context7 |
| Features IA | AGENT-008 | sqlite, context7 |
| UI Components | AGENT-009 | filesystem, playwright |
| Navigation UX | AGENT-010 | playwright |
| Validation Data | AGENT-011 | sqlite |
| Tests | AGENT-012 | playwright, shell |
| QA | AGENT-013 | playwright, github |
| Budgets | AGENT-014 | sqlite |
| Membres | AGENT-015 | sqlite |
| Notifications | AGENT-016 | sqlite |
| Data Pipeline | AGENT-017 | sqlite, filesystem |
| Open Banking | AGENT-018 | fetch |
| Performance | AGENT-019 | playwright, sqlite |
| Accessibilité | AGENT-020 | playwright |
| Documentation | AGENT-021 | filesystem |

---

## 🔄 Workflow Complet Exemple

### Scénario: "Ajouter un graphique dépenses par catégorie"

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ÉTAPE 1: ANALYSE (consistency-keeper)                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Vérifie si graphique similaire existe déjà                               │
│ • Liste composants charts existants (modules/ui/v5_5/dashboard/)           │
│ • Identifie patterns à réutiliser                                          │
│ • Documente: "Utiliser plotly comme les autres graphs"                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ ÉTAPE 2: AUDIT (python-app-auditor + financeperso-specific)                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Analyse qualité code existant                                            │
│ • Vérifie conventions FinancePerso:                                        │
│   - Session state correctement initialisé                                  │
│   - Cache @st.cache_data utilisé                                           │
│   - Clés widgets format f"type_{id}"                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ ÉTAPE 3: ROUTAGE (AGENT-000)                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│ AGENT-000 analyse la demande:                                              │
│   • Domaine: UI + Analytics                                                │
│   • Agents concernés: AGENT-009 + AGENT-006                                │
│   • Dépendances: Nécessite d'abord AGENT-009 (UI) puis AGENT-006 (intégr)  │
│                                                                              │
│ Plan: 1. AGENT-009 → 2. AGENT-006 → 3. AGENT-012 (tests)                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ ÉTAPE 4: IMPLÉMENTATION UI (AGENT-009)                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ AGENT-009 utilise:                                                          │
│   • MCP filesystem: Lire modules/ui/v5_5/components/ existants             │
│   • Outil natif ReadFile: Étudier patterns V5.5                            │
│   • Skill financeperso-specific: Conventions composants                    │
│                                                                              │
│ Crée: modules/ui/v5_5/components/category_chart.py                         │
│   - Style cohérent avec KPICard                                            │
│   - Utilise theme.py pour couleurs                                         │
│   - Props: data, title, height                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ ÉTAPE 5: INTÉGRATION DASHBOARD (AGENT-006)                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ AGENT-006 utilise:                                                          │
│   • MCP sqlite: Requête agrégation par catégorie                           │
│     "SELECT category, SUM(amount) FROM transactions GROUP BY category"     │
│   • Outil natif ReadFile: dashboard_v5.py                                  │
│   • MCP filesystem: Vérifier layout existant                               │
│                                                                              │
│ Intègre: Ajoute le graphique dans la grille KPI                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ ÉTAPE 6: TESTS (AGENT-012)                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ AGENT-012 utilise:                                                          │
│   • Outil natif Shell: pytest tests/ui/test_components.py                  │
│   • MCP playwright: Screenshot du rendu graphique                          │
│                                                                              │
│ Vérifie: Rendu correct, données affichées, responsive                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ ÉTAPE 7: VALIDATION (consistency-keeper)                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Vérifie pas de duplication avec autres graphs                            │
│ • Vérifie AGENTS.md à jour si nouveau pattern                              │
│ • Vérifie imports propres (pas circulaires)                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ ÉTAPE 8: TEST FONCTIONNEL (streamlit-app-auditor)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Lance app: streamlit run app.py                                          │
│ • MCP playwright: Navigate + screenshot                                    │
│ • Vérifie: Graphique s'affiche, données correctes, pas d'erreurs           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ MCP Servers - Guide d'utilisation par Agent

### MCP SQLite (AGENT-001, 004, 006, 011, 014, 015, 016)

```python
# Cas d'usage:
- Debug: "Pourquoi cette transaction n'apparaît pas ?"
- Analytics: "Top 10 catégories ce mois"
- Validation: "Y a-t-il des doublons ?"
- Migration: "Vérifier cohérence après migration"

# Exemples de requêtes:
"SELECT status, COUNT(*) FROM transactions GROUP BY status"
"SELECT * FROM transactions WHERE label LIKE '%Amazon%' ORDER BY date DESC"
"SELECT category, SUM(ABS(amount)) FROM transactions WHERE amount < 0 GROUP BY category"
```

### MCP Filesystem (AGENT-009, 021)

```python
# Cas d'usage:
- Explorer structure modules/ui/v5_5/
- Trouver tous les fichiers CSS
- Lister composants disponibles
- Vérifier pas de fichiers orphelins

# Exemples:
filesystem/list_directory: {"path": "/modules/ui/v5_5/components"}
filesystem/read_file: {"path": "/modules/constants.py"}
```

### MCP Playwright (AGENT-010, 012, 013, 019, 020)

```python
# Cas d'usage:
- Tester rendu UI V5.5
- Valider navigation entre pages
- Screenshot pour comparaison maquettes
- Tester responsive mobile

# Exemples:
playwright/navigate: {"url": "http://localhost:8501"}
playwright/take_screenshot: {"fullPage": true}
playwright/click: {"element": "Bouton Importer", "ref": "btn_import"}
```

### MCP GitHub (AGENT-003, 013)

```python
# Cas d'usage:
- Créer issue pour bug détecté
- Créer PR après feature
- Lister PRs en attente de review
- Vérifier status CI

# Exemples:
github/create_issue: {"title": "Bug: KPI Card dépassement budget", "labels": ["bug", "v5.5"]}
github/create_pull_request: {"title": "Feat: Nouveau graphique catégories", "base": "main"}
```

---

## 🎯 Checklist avant chaque intervention

### Pour une nouvelle feature :

- [ ] **consistency-keeper** - Analyse existant et patterns
- [ ] **AGENT-000** - Notification orchestrateur
- [ ] **Skill technique** + **financeperso-specific** - Audit
- [ ] **Agent spécialisé** - Implémentation
- [ ] **consistency-keeper** - Validation finale
- [ ] **MCP Tests** (playwright) - Test fonctionnel si UI

### Pour un bug fix :

- [ ] **AGENT-000** - Triage et routage
- [ ] **Agent concerné** - Investigation
- [ ] **MCP SQLite** - Debug données si nécessaire
- [ ] **Skill audit** - Vérifier pas d'impact négatif
- [ ] **AGENT-012** - Test de non-régression

### Pour un refactor :

- [ ] **consistency-keeper** - Baseline avant refactor
- [ ] **python-app-auditor** - Plan de refactor
- [ ] **AGENT-000** - Coordonne agents impactés
- [ ] **Agents concernés** - Adaptent leur domaine
- [ ] **consistency-keeper** - Compare avec baseline
- [ ] **AGENT-012/013** - Tests complets

---

## 🚀 Exemples de prompts utilisateur

### ✅ Prompts bien formulés :

```
"Analyse la cohérence du projet avec consistency-keeper, puis 
 route vers AGENT-009 pour créer un composant Card selon les 
 maquettes V5.5"

"AGENT-000: Bug détecté dans la catégorisation. Route vers 
 l'agent approprié pour investigation. Utilise MCP sqlite si 
 besoin de debug la base."

"Audit complet: consistency-keeper + python-app-auditor + 
 financeperso-specific sur modules/categorization.py"

"Test fonctionnel avec streamlit-app-auditor + playwright 
 de la page dashboard V5.5"
```

### ❌ Prompts à éviter :

```
"AGENT-009 crée un composant"  # ← Manque consistency-keeper avant
"Fix ce bug dans transactions"  # ← Manque AGENT-000 pour triage
"Audit le code"  # ← Trop vague, pas de skill spécifié
```

---

## 📋 Récapitulatif visuel

```
┌─────────────────────────────────────────────────────────────────┐
│                    ORDRE D'INVOCATION                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. consistency-keeper analyze                                   │
│     └── Check cohérence, identifie patterns                     │
│                                                                  │
│  2. [Skill technique] + financeperso-specific                    │
│     └── Audit avec conventions projet                           │
│                                                                  │
│  3. AGENT-000 route                                              │
│     └── Détermine agents spécialisés                            │
│                                                                  │
│  4. [Agent spécialisé]                                           │
│     └── Utilise MCP si pertinent:                               │
│         • sqlite → Analytics/DB                                 │
│         • filesystem → Exploration                              │
│         • playwright → Test UI                                  │
│         • fetch → API externes                                  │
│         • github → Gestion repo                                 │
│                                                                  │
│  5. consistency-keeper validate                                  │
│     └── Vérifie DRY, doc sync, rangement                        │
│                                                                  │
│  6. [Tests/QA] (AGENT-012/013)                                   │
│     └── Validation finale                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

**Document créé le:** 2026-03-01  
**Version:** 1.0 - Architecture complète avec MCP
