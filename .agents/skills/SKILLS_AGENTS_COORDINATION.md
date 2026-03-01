# 🔄 Coordination Skills ↔ Agents ↔ Sous-Agents

> Document de liaison entre les skills globaux, les agents spécialisés et les sous-agents FinancePerso

---

## 🎯 Vue d'ensemble

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
│           └────────────────────┼────────────────────┘                       │
│                                ▼                                            │
│  AGENT ORCHESTRATOR (AGENT-000)                                             │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │  Route vers agents spécialisés selon le domaine                  │       │
│  └─────────────────────────────────────────────────────────────────┘       │
│                                │                                            │
│           ┌────────────────────┼────────────────────┐                       │
│           ▼                    ▼                    ▼                       │
│  SOUS-AGENTS (Spécialisés)                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                          │
│  │ AGENT-001   │  │ AGENT-009   │  │ AGENT-006   │                          │
│  │ Database    │  │ UI Component│  │ Analytics   │                          │
│  │ Architect   │  │ Architect   │  │ Dashboard   │                          │
│  └─────────────┘  └─────────────┘  └─────────────┘                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Matrice de Coordination

### Skill: `consistency-keeper`

**Rôle:** Gardien de la cohérence - vérifie DRY, doc sync, rangement, performance

**Quand l'invoquer:**
- Avant toute modification majeure
- Après refactoring
- Avant chaque merge/PR

**Agents à appeler:**

| Agent | Contexte d'appel | Action |
|-------|------------------|--------|
| **AGENT-000** (Orchestrator) | Toujours en premier | Coordination globale |
| **AGENT-012** (Test Automation) | Vérification DRY | Tests de non-régression |
| **AGENT-013** (QA Integration) | Validation finale | Check qualité globale |
| **AGENT-019** (Performance) | Si perf concernée | Audit performance |

**Protocole d'appel:**
```
1. consistency-keeper analyze
   └── Vérifie cohérence actuelle
   └── Identifie patterns à réutiliser
   
2. AGENT-000 route
   └── Détermine agents spécialisés nécessaires
   
3. [Agent(s) spécialisé(s)]
   └── Implémente la modification
   
4. consistency-keeper validate
   └── Vérifie DRY respecté
   └── Vérifie doc synchronisée
   └── Vérifie rangement OK
```

---

### Skill: `financeperso-specific`

**Rôle:** Conventions spécifiques au projet FinancePerso

**Quand l'invoquer:**
- TOUJOURS combiné avec un skill technique
- Pour toute modification dans le codebase FinancePerso

**Agents à appeler:**

| Agent | Contexte d'appel | Action |
|-------|------------------|--------|
| **AGENT-000** (Orchestrator) | Systématique | Coordination |
| **AGENT-001** (Database) | Si DB concernée | Patterns DB FinancePerso |
| **AGENT-004** (Transaction) | Si transactions | Patterns transactions |
| **AGENT-005** (Categorization) | Si catégorisation | Patterns IA |
| **AGENT-009** (UI Component) | Si UI concernée | Composants V5.5 |
| **AGENT-006** (Analytics) | Si dashboard | Patterns métriques |

**Protocole d'appel:**
```
1. financeperso-specific conventions
   └── Rappelle patterns spécifiques
   
2. [Skill technique] + financeperso-specific
   └── Audit/appli avec conventions
   
3. AGENT spécialisé FinancePerso
   └── Implémentation selon conventions
```

---

### Skill: `python-app-auditor`

**Rôle:** Audit technique Python générique

**Quand l'invoquer:**
- Audit de code Python
- Refactoring
- Review de qualité

**Agents à appeler:**

| Agent | Contexte d'appel | Action |
|-------|------------------|--------|
| **AGENT-000** (Orchestrator) | Systématique | Coordination |
| **AGENT-001** (Database) | Si models DB | Qualité couche données |
| **AGENT-004** (Transaction) | Si logique métier | Patterns métier |
| **AGENT-007** (AI Provider) | Si code IA | Patterns IA |
| **AGENT-012** (Test Automation) | Si tests manquants | Génération tests |

**Protocole d'appel:**
```
1. python-app-auditor analyze
   └── Audit qualité code Python
   
2. AGENT-000 route
   └── Détermine agents métier concernés
   
3. [Agents métier] + financeperso-specific
   └── Correction selon conventions
```

---

### Skill: `streamlit-app-auditor`

**Rôle:** Audit fonctionnel Streamlit

**Quand l'invoquer:**
- Test de l'app en conditions réelles
- Problèmes de performance runtime
- Audit UI/UX spécifique Streamlit

**Agents à appeler:**

| Agent | Contexte d'appel | Action |
|-------|------------------|--------|
| **AGENT-000** (Orchestrator) | Systématique | Coordination |
| **AGENT-009** (UI Component) | Si composants UI | Test composants V5.5 |
| **AGENT-010** (Navigation) | Si navigation | Test flux utilisateur |
| **AGENT-011** (Validation) | Si formulaires | Test validation |
| **AGENT-006** (Analytics) | Si dashboard | Test rendu KPIs |

**Protocole d'appel:**
```
1. streamlit-app-auditor launch
   └── Lance l'app en mode audit
   
2. AGENT-000 coordinate
   └── Agents UI/UX testent
   
3. [Agents UI] report
   └── Rapport des issues trouvées
```

---

## 📋 Scénarios d'utilisation

### Scénario 1: Nouvelle Feature (ex: KPI Cards V5.5)

```
1. consistency-keeper
   └── Analyse existant
   └── Identifie réutilisation possible
   
2. financeperso-specific + python-app-auditor
   └── Conventions + audit code
   
3. AGENT-000 route → AGENT-009 (UI Component)
   └── Spécialiste UI prend le relais
   
4. AGENT-009 implémente
   └── Crée KPICard selon maquettes
   └── Utilise tokens existants
   
5. AGENT-006 (Analytics) review
   └── Vérifie intégration dashboard
   
6. consistency-keeper validate
   └── Vérifie pas de duplication
   └── Vérifie doc à jour
   
7. streamlit-app-auditor test
   └── Test rendu réel
```

### Scénario 2: Refactoring Database

```
1. AGENT-000 notify
   └── Prévient tous les agents
   
2. AGENT-001 (Database) plan
   └── Planifie migration
   
3. consistency-keeper + python-app-auditor
   └── Vérifie impact sur code existant
   
4. AGENT-001 execute
   └── Applique migration
   
5. AGENT-004, 005, 006... update
   └── Chaque agent met à jour son domaine
   
6. AGENT-012 (Test Automation)
   └── Tests de non-régression
   
7. consistency-keeper validate
```

### Scénario 3: Bug Fix Production

```
1. AGENT-000 triage
   └── Détermine agent responsable
   
2. [Agent spécialisé] investigate
   └── Analyse root cause
   
3. python-app-auditor quick-check
   └── Vérifie pas d'impact négatif
   
4. [Agent] fix
   └── Applique correction
   
5. AGENT-013 (QA Integration)
   └── Validation rapide
   
6. consistency-keeper check
   └── Vérifie cohérence maintenue
```

---

## 🚨 Points d'attention

### 1. Ordre d'invocation OBLIGATOIRE

```
# ✅ CORRECT
1. consistency-keeper (check initial)
2. AGENT-000 (route)
3. [Agent spécialisé] (implémente)
4. consistency-keeper (validate)

# ❌ INCORRECT
1. [Agent spécialisé] directement
   └── Risque de duplication/pas DRY
   └── Risque de casser cohérence
```

### 2. Skills COMBINÉS obligatoires

```
# ✅ CORRECT
- python-app-auditor + financeperso-specific
- streamlit-app-auditor + financeperso-specific
- consistency-keeper seul (OK, c'est un meta-skill)

# ❌ INCORRECT
- python-app-auditor seul sur FinancePerso
   └── Ignore conventions projet
```

### 3. Communication inter-agents

Tous les agents doivent:
- **Signaler** leurs modifications à AGENT-000
- **Vérifier** dépendances avant modification
- **Respecter** les conventions de `financeperso-specific`

---

## 📝 Checklist de coordination

Avant de démarrer une tâche:

- [ ] **Skill adéquat** sélectionné
- [ ] **AGENT-000** notifié
- [ ] **consistency-keeper** invoqué en premier
- [ ] **Agents spécialisés** identifiés
- [ ] **Protocole** de coordination choisi

Après implémentation:

- [ ] **consistency-keeper** validation OK
- [ ] **Tests** passent (AGENT-012/013)
- [ ] **Documentation** à jour
- [ ] **AGENT-000** notification fin

---

## 🔗 Références

- [consistency-keeper](../../../../.config/agents/skills/consistency-keeper/SKILL.md)
- [financeperso-specific](financeperso-specific/SKILL.md)
- [AGENT-000 Orchestrator](../subagents/AGENT-000-Orchestrator.md)
- [Architecture agents](../subagents/AGENTS_COVERAGE_ANALYSIS.md)

---

**Dernière mise à jour:** 2026-03-01 (V5.5 Implementation)
