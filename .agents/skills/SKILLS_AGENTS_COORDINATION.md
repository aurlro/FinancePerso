# 🔄 Coordination Skills ↔ Agents ↔ Sous-Agents

> Document de liaison entre les skills globaux, les agents spécialisés et les sous-agents FinancePerso  
> **Mise à jour:** Mars 2026 - Architecture Dual-Stack (Streamlit + Electron)

---

## 🎯 Vue d'ensemble

### Architecture Dual-Stack

```
FinancePerso/
├── [RACINE]                    # Application Streamlit (Legacy - maintenance)
│   ├── app.py
│   ├── pages/01_*.py
│   ├── modules/
│   └── tests/
│
└── financeperso-electron/      # Application Electron (Nouveau - actif)
    ├── src/main.js
    ├── src/pages/
    └── tests/e2e/
```

### Système de Coordination

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COORDINATION SYSTEM                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  SKILLS (Globaux)                                                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │ consistency-    │  │ python-app-     │  │ streamlit-app-  │             │
│  │ keeper          │  │ auditor         │  │ auditor         │             │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘             │
│           │                    │                    │                       │
│  ┌────────┴────────────────────┴────────────────────┴─────────────────┐    │
│  │                    financeperso-specific (DUAL)                    │    │
│  │              Supporte Streamlit ET Electron                        │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│  ┌─────────────────────────────────┴─────────────────────────────────┐      │
│  │                                                                   │      │
│  │  electron-vite-expert + financeperso-electron-specific            │      │
│  │  (Pour le projet financeperso-electron/)                          │      │
│  │                                                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                    │                                        │
│  AGENT ORCHESTRATOR (AGENT-000)                                             │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │  Route vers agents spécialisés selon le domaine ET la stack      │       │
│  └─────────────────────────────────────────────────────────────────┘       │
│                                │                                            │
│         ┌──────────────────────┼──────────────────────┐                     │
│         ▼                      ▼                      ▼                     │
│  SOUS-AGENTS STREAMLIT    SOUS-AGENTS ELECTRON      SOUS-AGENTS COMMUNS    │
│  ┌─────────────┐          ┌─────────────┐          ┌─────────────┐          │
│  │ AGENT-001   │          │ AGENT-025   │          │ AGENT-014   │          │
│  │ Database    │          │ Electron    │          │ Budget      │          │
│  │ Architect   │          │ Desktop     │          │ Wealth      │          │
│  └─────────────┘          └─────────────┘          └─────────────┘          │
│  ┌─────────────┐          ┌─────────────┐          ┌─────────────┐          │
│  │ AGENT-005   │          │ AGENT-009   │          │ AGENT-015   │          │
│  │ Categoriza- │          │ UI Component│          │ Member      │          │
│  │ tion AI     │          │ Architect   │          │ Management  │          │
│  └─────────────┘          └─────────────┘          └─────────────┘          │
│  ┌─────────────┐          ┌─────────────┐          ┌─────────────┐          │
│  │ AGENT-006   │          │ AGENT-012   │          │ AGENT-007   │          │
│  │ Analytics   │          │ Test Auto   │          │ AI Provider │          │
│  │ Dashboard   │          │             │          │ Manager     │          │
│  └─────────────┘          └─────────────┘          └─────────────┘          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Skills disponibles

| Skill | Stack | Usage |
|-------|-------|-------|
| `consistency-keeper` | Global | Vérification cohérence avant/après |
| `financeperso-specific` | Dual | Conventions communes Streamlit + Electron |
| `python-app-auditor` | Streamlit | Audit code Python |
| `streamlit-app-auditor` | Streamlit | Audit fonctionnel Streamlit |
| `electron-vite-expert` | Electron | Configuration Electron + Vite |
| `financeperso-electron-specific` | Electron | Conventions projet Electron |

---

## 🔄 Matrice de Coordination

### Skill: `consistency-keeper`

**Rôle:** Gardien de la cohérence - vérifie DRY, doc sync, rangement, performance

**Quand l'invoquer:**
- Avant toute modification majeure
- Après refactoring
- Avant chaque merge/PR
- **Pour les DEUX stacks (Streamlit ET Electron)**

**Agents à appeler:**

| Agent | Contexte | Action |
|-------|----------|--------|
| **AGENT-000** (Orchestrator) | Toujours | Coordination globale |
| **AGENT-012** (Test Automation) | Vérification | Tests E2E Playwright (Electron) ou pytest (Streamlit) |
| **AGENT-013** (QA Integration) | Validation finale | Check qualité globale |
| **AGENT-019** (Performance) | Si perf concernée | Audit performance |
| **AGENT-025** (Electron) | Si Electron concerné | Validation build/packaging |

---

### Skill: `financeperso-specific` (DUAL STACK)

**Rôle:** Conventions spécifiques au projet FinancePerso (Streamlit + Electron)

**⚠️ IMPORTANT:** Ce skill couvre **LES DEUX applications** :
- Application Streamlit (racine)
- Application Electron (financeperso-electron/)

**Quand l'invoquer:**
- TOUJOURS combiné avec un skill technique
- Pour toute modification dans **l'une ou l'autre** application

**Agents à appeler selon la stack:**

#### Pour Streamlit:
| Agent | Contexte | Action |
|-------|----------|--------|
| **AGENT-000** | Systématique | Coordination |
| **AGENT-001** | DB | Patterns DB FinancePerso |
| **AGENT-004** | Transactions | Patterns transactions |
| **AGENT-005** | IA | Patterns IA |
| **AGENT-009** | UI V5.5 | Composants V5.5 |
| **AGENT-006** | Dashboard | Patterns métriques |

#### Pour Electron:
| Agent | Contexte | Action |
|-------|----------|--------|
| **AGENT-000** | Systématique | Coordination |
| **AGENT-025** | Electron | Architecture main/renderer |
| **AGENT-009** | UI React | Composants shadcn/ui |
| **AGENT-010** | Navigation | Command Palette, routing |
| **AGENT-012** | Tests | Tests Playwright |
| **AGENT-014** | Budgets/Wealth | Logique métier |
| **AGENT-015** | Members | Multi-membres |

#### Communs:
| Agent | Contexte | Action |
|-------|----------|--------|
| **AGENT-007** | AI Provider | APIs Gemini/OpenAI |
| **AGENT-008** | AI Features | Chat IA |

---

### Skill: `electron-vite-expert`

**Rôle:** Configuration robuste Electron + Vite + SQLite

**Quand l'invoquer:**
- Configuration build Electron
- Problèmes IPC/main process
- SQLite integration
- Packaging/distribution

**Agents à appeler:**

| Agent | Contexte | Action |
|-------|----------|--------|
| **AGENT-000** | Systématique | Coordination |
| **AGENT-025** (Electron) | Architecture | Configuration main/renderer |
| **AGENT-012** (Test) | Validation | Tests E2E |
| **AGENT-003** (DevOps) | CI/CD | GitHub Actions |

---

### Skill: `financeperso-electron-specific`

**Rôle:** Conventions spécifiques au projet financeperso-electron

**Quand l'invoquer:**
- Nouvelle feature dans Electron
- Refactoring Electron
- Nouvelle page/composant
- Tests E2E

**Agents à appeler:**

| Agent | Contexte | Action |
|-------|----------|--------|
| **AGENT-000** | Systématique | Coordination |
| **AGENT-025** | Architecture | Review architecture |
| **AGENT-009** | UI | Composants shadcn/ui |
| **AGENT-012** | Tests | Tests Playwright |
| **AGENT-010** | Navigation | UX routing |

---

### Skill: `python-app-auditor` (STREAMLIT ONLY)

**Rôle:** Audit technique Python générique

**⚠️ ATTENTION:** Uniquement pour l'application Streamlit (racine)

**Agents à appeler:**

| Agent | Contexte | Action |
|-------|----------|--------|
| **AGENT-000** | Systématique | Coordination |
| **AGENT-001** | Database | Qualité couche données |
| **AGENT-004** | Transaction | Patterns métier |
| **AGENT-007** | AI | Patterns IA |
| **AGENT-012** | Tests | Génération tests pytest |

---

### Skill: `streamlit-app-auditor` (STREAMLIT ONLY)

**Rôle:** Audit fonctionnel Streamlit

**⚠️ ATTENTION:** Uniquement pour l'application Streamlit (racine)

**Agents à appeler:**

| Agent | Contexte | Action |
|-------|----------|--------|
| **AGENT-000** | Systématique | Coordination |
| **AGENT-009** | UI V5.5 | Test composants |
| **AGENT-010** | Navigation | Test flux utilisateur |
| **AGENT-011** | Validation | Test formulaires |
| **AGENT-006** | Analytics | Test rendu KPIs |

---

## 📋 Scénarios d'utilisation

### Scénario 1: Nouvelle Feature Electron (ex: Page Settings)

```
1. consistency-keeper
   └── Analyse pages existantes
   └── Identifie patterns à réutiliser
   
2. electron-vite-expert + financeperso-electron-specific
   └── Conventions Electron + patterns projet
   
3. AGENT-000 route → AGENT-025 (Electron) + AGENT-009 (UI)
   └── Spécialistes Electron et UI
   
4. AGENT-025 crée structure
   └── Handler IPC
   └── Route
   
5. AGENT-009 implémente UI
   └── Composants shadcn/ui
   └── Hooks React
   
6. AGENT-012 (Test) ajoute tests E2E
   └── Test Playwright
   
7. consistency-keeper validate
   └── Vérifie DRY respecté
   └── Vérifie doc à jour
   
8. Build test
   └── npm run build (OK)
```

### Scénario 2: Bug Fix Streamlit (Maintenance legacy)

```
1. AGENT-000 triage
   └── Détermine c'est Streamlit (legacy)
   
2. python-app-auditor + financeperso-specific
   └── Audit code Python + conventions
   
3. AGENT-000 route → AGENT-004 (Transaction)
   └── Spécialiste transactions
   
4. AGENT-004 investigate
   └── Analyse root cause
   
5. AGENT-004 fix
   └── Applique correction
   
6. AGENT-012 (Test Automation)
   └── Tests pytest de non-régression
   
7. consistency-keeper check
   └── Vérifie cohérence maintenue
```

### Scénario 3: Migration Feature Streamlit → Electron

```
1. AGENT-000 coordination
   └── Plan de migration
   
2. financeperso-specific (analyse Streamlit)
   └── Comprend feature existante
   
3. electron-vite-expert + financeperso-electron-specific
   └── Conventions cible Electron
   
4. AGENT-000 route → AGENT-014 (Budget/Wealth)
   └── Spécialiste métier
   
5. AGENT-025 (Electron) crée structure
   └── Database service
   └── IPC handlers
   
6. AGENT-009 (UI) implémente React
   └── Components
   └── Hooks
   └── Page
   
7. AGENT-012 (Test) tests E2E
   └── Tests Playwright complets
   
8. consistency-keeper validate
   └── Parité feature vérifiée
   └── Doc mise à jour
```

---

## 🚨 Points d'attention

### 1. Sélection de la bonne stack

```
# ✅ SI le user parle de "financeperso-electron/" → Electron
skills: electron-vite-expert + financeperso-electron-specific
agents: AGENT-025, AGENT-009, AGENT-012

# ✅ SI le user parle de "app.py" ou "pages/01_*.py" → Streamlit  
skills: python-app-auditor/streamlit-app-auditor + financeperso-specific
agents: AGENT-001, AGENT-004, AGENT-005

# ✅ SI ambiguous → Demander clarification
"Tu veux modifier l'application Streamlit ou l'application Electron ?"
```

### 2. Ordre d'invocation OBLIGATOIRE

```
# ✅ CORRECT (Electron)
1. consistency-keeper (check)
2. electron-vite-expert (config)
3. financeperso-electron-specific (conventions)
4. AGENT-000 (route)
5. AGENT-025 + AGENT-009 (implémente)
6. consistency-keeper (validate)

# ✅ CORRECT (Streamlit)
1. consistency-keeper (check)
2. python-app-auditor (audit)
3. financeperso-specific (conventions)
4. AGENT-000 (route)
5. AGENT-001/004/005 (implémente)
6. consistency-keeper (validate)
```

### 3. Skills COMBINÉS obligatoires

```
# ✅ CORRECT (Electron)
- electron-vite-expert + financeperso-electron-specific
- financeperso-specific seul (OK pour overview)

# ✅ CORRECT (Streamlit)
- python-app-auditor + financeperso-specific
- streamlit-app-auditor + financeperso-specific

# ❌ INCORRECT
- electron-vite-expert seul sur FinancePerso
  └── Ignore conventions projet
```

---

## 📝 Checklist de coordination

### Avant de démarrer:

- [ ] **Stack identifiée** (Streamlit ou Electron)
- [ ] **Skill(s) adéquat(s)** sélectionné(s)
- [ ] **AGENT-000** notifié
- [ ] **consistency-keeper** invoqué en premier
- [ ] **Agents spécialisés** identifiés selon stack

### Après implémentation:

- [ ] **consistency-keeper** validation OK
- [ ] **Tests** passent (pytest pour Streamlit, Playwright pour Electron)
- [ ] **Build** OK (npm run build pour Electron)
- [ ] **Documentation** à jour
- [ ] **AGENT-000** notification fin

---

## 🔗 Références

### Skills
- [consistency-keeper](consistency-keeper/SKILL.md)
- [financeperso-specific](financeperso-specific/SKILL.md) - **DUAL STACK**
- [electron-vite-expert](electron-vite-expert/SKILL.md) - **ELECTRON**
- [financeperso-electron-specific](financeperso-electron/SKILL.md) - **ELECTRON**

### Agents
- [AGENT-000 Orchestrator](../subagents/AGENT-000-Orchestrator.md)
- [AGENT-025 Electron Desktop](../subagents/AGENT-025-Electron-Desktop-Architect.md) - **NOUVEAU**

### Projets
- `financeperso-electron/PROJECT_COMPLETION_REPORT.md` - État Electron
- `financeperso-electron/ROADMAP.md` - Roadmap Electron

---

**Dernière mise à jour:** 2026-03-13 (Architecture Dual-Stack v1.0.0)
