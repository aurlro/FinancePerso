# 🚀 Roadmap FinancePerso Electron

> Migration depuis Streamlit vers Electron + React + FastAPI

---

## 📊 État Actuel

### ✅ Phase 0 - Fondation (TERMINÉE)
- [x] Architecture Electron + Vite + React + TypeScript
- [x] SQLite local avec sqlite3
- [x] Design System Tailwind + shadcn/ui
- [x] Navigation React Router
- [x] IPC communication (main ↔ renderer)

### ✅ Phase 1 - Core (TERMINÉE)
- [x] Dashboard basique (KPIs)
- [x] Transactions CRUD
- [x] Import CSV natif
- [x] Catégories (structure)

---

## 🎯 Phase 2 - Parité Streamlit (En cours)

### 2.1 Visualisations 📊 
**Agent:** AGENT-006 (Analytics Dashboard) + AGENT-009 (UI Component)

- [ ] Intégrer Recharts/Plotly.js
- [ ] Graphique dépenses par catégorie (pie)
- [ ] Graphique tendances mensuelles (line)
- [ ] Histogramme dépenses quotidiennes
- [ ] Vue "Reste à vivre" ( comme Streamlit )

**Fichiers:**
- `src/components/charts/ExpenseChart.tsx`
- `src/components/charts/TrendChart.tsx`
- `src/hooks/useCharts.ts`

---

### 2.2 Budgets & Alertes 💰
**Agent:** AGENT-014 (Budget Wealth Manager)

- [ ] CRUD Budgets par catégorie
- [ ] Barre de progression budget
- [ ] Alertes dépassement (80%, 100%)
- [ ] Prédictions simples (tendance linéaire)

**Pages:**
- `src/pages/Budgets.tsx`

---

### 2.3 Validation & Audit 🔍
**Agent:** AGENT-011 (Data Validation) + AGENT-005 (Categorization AI)

- [ ] Page validation batch
- [ ] Regroupement transactions similaires
- [ ] Détection doublons
- [ ] Suggestions catégorisation basiques

**Pages:**
- `src/pages/Validation.tsx`

---

### 2.4 Assistant IA 🤖
**Agent:** AGENT-007 (AI Provider Manager) + AGENT-008 (AI Features)

- [ ] Intégration API Gemini/OpenAI
- [ ] Chat interface (similaire Streamlit)
- [ ] Categorization cloud
- [ ] Anomalies detection

**Pages:**
- `src/pages/Assistant.tsx`

---

## 🚀 Phase 3 - Features Avancées

### 3.1 Multi-membres 👥
**Agent:** AGENT-015 (Member Management)

- [ ] Gestion membres du foyer
- [ ] Attribution transactions par membre
- [ ] Vue filtrée par membre
- [ ] Couleurs/types différents

### 3.2 Recherche Globale 🔎
**Agent:** AGENT-010 (Navigation Experience)

- [ ] Barre recherche globale (Cmd+K)
- [ ] Filtres avancés (date, montant, catégorie)
- [ ] Historique recherche

### 3.3 Patrimoine & Projections 📈
**Agent:** AGENT-014 (Budget Wealth Manager)

- [ ] Suivi patrimoine
- [ ] Objectifs épargne
- [ ] Projections simples

### 3.4 Abonnements 🔄
**Agent:** AGENT-004 (Transaction Engine)

- [ ] Détection auto abonnements
- [ ] Liste abonnements
- [ ] Alertes renouvellement

---

## 🔧 Phase 4 - Architecture Backend

### 4.1 FastAPI Backend 🐍
**Agent:** AGENT-023 (FastAPI Architect)

- [ ] Setup FastAPI + SQLAlchemy 2.0
- [ ] Endpoints REST (comme spec Fusion)
- [ ] Migrations Alembic
- [ ] WebSocket pour temps réel

### 4.2 Python Bridge 🌉
**Agent:** AGENT-025 (Electron Desktop)

- [ ] Spawn FastAPI depuis Electron
- [ ] Communication IPC/HTTP hybride
- [ ] Packaging Python avec app

---

## 🎨 Phase 5 - UX/UI Polish

### 5.1 Design System Complet
**Agent:** AGENT-009 (UI Component Architect)

- [ ] Empty states
- [ ] Loading skeletons
- [ ] Error boundaries
- [ ] Animations transitions

### 5.2 Mobile Responsive 📱
**Agent:** AGENT-020 (Accessibility Specialist)

- [ ] Bottom navigation mobile
- [ ] Swipe actions transactions
- [ ] Touch-friendly inputs
- [ ] Responsive breakpoints

### 5.3 Accessibilité ♿
- [ ] ARIA labels
- [ ] Keyboard navigation
- [ ] Screen reader support
- [ ] Color contrast

---

## 🧪 Phase 6 - Qualité

### 6.1 Tests
**Agent:** AGENT-012 (Test Automation) + AGENT-013 (QA Integration)

- [ ] Tests unitaires (Vitest)
- [ ] Tests E2E (Playwright)
- [ ] Tests IPC
- [ ] Coverage > 80%

### 6.2 Documentation
**Agent:** AGENT-021 (Technical Writer)

- [ ] Storybook composants
- [ ] API documentation
- [ ] User guide

---

## 📅 Planning Suggéré

| Phase | Durée | Agents Principaux |
|-------|-------|-------------------|
| 2.1 - Charts | 2-3 jours | AGENT-006, 009 |
| 2.2 - Budgets | 2-3 jours | AGENT-014 |
| 2.3 - Validation | 3-4 jours | AGENT-011, 005 |
| 2.4 - AI | 3-4 jours | AGENT-007, 008 |
| 3.x - Avancé | 1-2 semaines | AGENT-015, 010 |
| 4.x - Backend | 1-2 semaines | AGENT-023 |
| 5.x - Polish | 1 semaine | AGENT-009, 020 |
| 6.x - Tests | 1 semaine | AGENT-012, 013 |

**Total estimé:** 6-8 semaines pour parité complète avec Streamlit

---

## 🎯 Priorités Recommandées

### P0 (Immédiat)
1. **Charts** - Essentiel pour dashboard utile
2. **Budgets** - Feature clé utilisée quotidiennement
3. **Validation batch** - Workflow import essentiel

### P1 (Court terme)
4. **AI Categorization** - Gain de temps majeur
5. **Multi-membres** - Pour couples
6. **Recherche** - UX améliorée

### P2 (Moyen terme)
7. **FastAPI backend** - Architecture scalable
8. **Patrimoine** - Feature avancée
9. **Gamification** - Engagement

---

## 🔄 Stratégie de Migration

### Option A: Feature Parity (Recommandé)
Tout recréer 1:1 puis ajouter nouvelles features

### Option B: MVP Minimal
Se concentrer sur le core (Dashboard + Import + Validation) pour release rapide

### Option C: Hybrid
Utiliser FastAPI comme bridge pour réutiliser modules Python existants

---

## 📚 Ressources

- [AGENTS.md](/Users/aurelien/Documents/Projets/FinancePerso/AGENTS.md) - Guide agents
- [docs/PLANNING/fusion/](/Users/aurelien/Documents/Projets/FinancePerso/docs/PLANNING/fusion/) - Specs Fusion
- [Version Streamlit](/Users/aurelien/Documents/Projets/FinancePerso/pages/) - Référence features

---

*Dernière mise à jour: 2025-03-13*
*Prochaine review: Après Phase 2.1 (Charts)*
