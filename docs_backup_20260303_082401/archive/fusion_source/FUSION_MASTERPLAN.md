# 🔄 Plan de Fusion : FinancePerso + FinCouple

> **Document de référence pour la convergence des deux projets**  
> **Version:** 1.0  
> **Date:** 2026-03-02  
> **Horizon:** 6-12 mois  
> **Architecture cible:** Hybride (React + Streamlit) + SQLite locale

---

## 📋 Table des matières

1. [Executive Summary](#1-executive-summary)
2. [Analyse comparative des projets](#2-analyse-comparative-des-projets)
3. [Vision de la fusion](#3-vision-de-la-fusion)
4. [Architecture cible](#4-architecture-cible)
5. [Plan de migration (6-12 mois)](#5-plan-de-migration-6-12-mois)
6. [Matrice des fonctionnalités](#6-matrice-des-fonctionnalités)
7. [Risques et mitigation](#7-risques-et-mitigation)
8. [Ressources nécessaires](#8-ressources-nécessaires)
9. [Checkpoints de validation](#9-checkpoints-de-validation)
10. [Annexes](#10-annexes)

---

## 1. Executive Summary

### 🎯 Objectif
Fusionner **FinancePerso** (fonctionnalités avancées, stack Python/Streamlit) avec **FinCouple** (UI/UX moderne, stack React/TypeScript) pour créer une application unique combinant:
- **L'expérience utilisateur moderne** de FinCouple (React, design system, responsive)
- **La puissance fonctionnelle** de FinancePerso (IA, projections, gamification, couple)

### 📊 Chiffres clés

| Métrique | FinancePerso | FinCouple | Fusion cible |
|----------|--------------|-----------|--------------|
| **Lignes de code** | ~65,000 Python | ~7,158 TypeScript | ~40,000 (optimisé) |
| **Pages/Écrans** | 22 pages | 6 pages | 12 écrans principaux |
| **Fonctionnalités** | 50+ | 8 | 35+ (essentielles) |
| **Stack** | Streamlit + SQLite | React + Supabase | React + Python API + SQLite |
| **Temps de dév.** | 2+ ans | 2 mois | 6-12 mois (estimé) |

### 🏗️ Approche choisie

**Architecture Hybride:**
- **Frontend (React)**: Dashboard quotidien, transactions, import, visualisations
- **Backend (Python API)**: Logique métier, IA, calculs complexes, batchs
- **Admin (Streamlit)**: Configuration avancée, audit, debug, features expérimentales
- **Database**: SQLite locale (privacy-first) avec sync optionnelle

---

## 2. Analyse comparative des projets

### 2.1 FinancePerso (Projet actuel)

#### ✅ Forces
- **Fonctionnalités très complètes**: 50+ features couvrant tous les aspects de la gestion financière
- **Moteur IA sophistiqué**: Catégorisation multi-niveaux (règles + ML local + Cloud)
- **Gestion de couple avancée**: Prêts entre conjoints, détection transferts, privacy filters
- **Projections patrimoniales**: Monte Carlo, scénarios what-if
- **Gamification**: Badges, streaks, challenges
- **Privacy/GDPR**: Chiffrement AES-256, anonymisation
- **Offline-first**: ML local 100% offline
- **Architecture modulaire**: 49 modules bien organisés

#### ❌ Faiblesses
- **UI limitée par Streamlit**: Reruns à chaque interaction, layout rigide
- **Expérience mobile**: Difficile à optimiser (PWA limitée)
- **Temps de réponse**: Latence sur gros volumes
- **Courbe d'apprentissage**: Interface complexe pour nouveaux utilisateurs
- **Tests E2E difficiles**: Playwright sur Streamlit est limité

#### 📁 Architecture technique
```
FinancePerso/
├── app.py                    # Point d'entrée Streamlit
├── pages/                    # 22 pages Streamlit
│   ├── 01_Import.py         # Import CSV
│   ├── 02_Dashboard.py      # Dashboard
│   ├── 04_Budgets.py        # Budgets
│   ├── 10_Projections.py    # Projections patrimoine
│   ├── 12_Patrimoine.py     # Wealth management
│   └── ...
├── modules/                  # 49 modules métier
│   ├── ai/                  # Suite IA (anomaly, assistant, tags)
│   ├── db/                  # Couche données SQLite
│   ├── ui/                  # Composants UI Streamlit
│   ├── wealth/              # Gestion patrimoine
│   ├── couple/              # Logique couple
│   └── gamification/        # Badges, streaks
└── Data/finance.db          # SQLite local
```

### 2.2 FinCouple (Projet parallèle)

#### ✅ Forces
- **UI/UX exceptionnelle**: Design system shadcn/ui, animations fluides
- **Stack moderne**: React 18, TypeScript, Vite, Tailwind
- **Performance**: Instantanée, pas de reruns
- **Responsive**: Mobile-first design
- **Développement rapide**: Hot reload, DX excellente
- **Type safety**: TypeScript end-to-end
- **State management**: React Query pour cache/serveur state

#### ❌ Faiblesses
- **Fonctionnalités limitées**: Import, dashboard basique, transactions, règles
- **Pas d'IA**: Catégorisation basique par regex uniquement
- **Pas de gestion couple**: Single-user seulement
- **Pas de projections**: Dashboard purement historique
- **Dépendance Supabase**: Couplage fort au SaaS
- **Pas de offline**: Nécessite connexion constante

#### 📁 Architecture technique
```
couple-cashflow-clever/
├── src/
│   ├── components/ui/       # 50+ composants shadcn/ui
│   ├── hooks/               # Custom hooks (React Query)
│   ├── lib/                 # Utils, parsers
│   ├── pages/               # 6 pages React
│   │   ├── Index.tsx       # Dashboard
│   │   ├── Transactions.tsx
│   │   ├── Import.tsx
│   │   └── ...
│   └── integrations/
│       └── supabase/        # Client Supabase
├── supabase/                # Migrations SQL
└── vite.config.ts          # Config build
```

### 2.3 Tableau comparatif détaillé

| Domaine | FinancePerso | FinCouple | Gagnant |
|---------|-------------|-----------|---------|
| **Import CSV** | ⭐⭐⭐⭐⭐ (mapping avancé, présets) | ⭐⭐⭐⭐ (clean, moderne) | Égal |
| **Dashboard** | ⭐⭐⭐ (fonctionnel mais austère) | ⭐⭐⭐⭐⭐ (moderne, fluide) | FinCouple |
| **Catégorisation** | ⭐⭐⭐⭐⭐ (IA + ML + règles) | ⭐⭐⭐ (règles regex uniquement) | FinancePerso |
| **Budgets** | ⭐⭐⭐⭐⭐ (dynamiques, prédictions) | ❌ Non | FinancePerso |
| **Projections** | ⭐⭐⭐⭐⭐ (Monte Carlo, scénarios) | ❌ Non | FinancePerso |
| **Gestion couple** | ⭐⭐⭐⭐⭐ (prêts, transferts, privacy) | ⭐⭐⭐ (comptes séparés/joint) | FinancePerso |
| **Gamification** | ⭐⭐⭐⭐ (badges, streaks) | ❌ Non | FinancePerso |
| **UX/UI** | ⭐⭐⭐ (fonctionnel) | ⭐⭐⭐⭐⭐ (exceptionnelle) | FinCouple |
| **Mobile** | ⭐⭐ (PWA limitée) | ⭐⭐⭐⭐⭐ (responsive native) | FinCouple |
| **Performance** | ⭐⭐⭐ (Streamlit limite) | ⭐⭐⭐⭐⭐ (instantanée) | FinCouple |
| **Privacy** | ⭐⭐⭐⭐⭐ (SQLite local, chiffrement) | ⭐⭐ (dépendance Supabase) | FinancePerso |

---

## 3. Vision de la fusion

### 3.1 Concept: "FinCouple Pro"

**Positionnement**: Application de gestion financière pour couples, alliant simplicité d'utilisation et puissance analytique.

**Tagline**: *"La simplicité de FinCouple, la puissance de FinancePerso"*

### 3.2 Principes directeurs

1. **Privacy by Design**: Données locales par défaut, chiffrement optionnel
2. **Progressive Enhancement**: Core fonctionnel offline, features avancées avec sync
3. **Mobile-First**: Expérience optimale sur smartphone
4. **Couple-Centric**: Conçu pour la gestion financière à deux
5. **IA Assistive**: Pas d'IA intrusive, suggestions contextuelles

### 3.3 Parcours utilisateur cible

```
┌─────────────────────────────────────────────────────────────────┐
│  PARCOURS UTILISATEUR TYPE (Couple: Alice & Bob)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📱 MATIN (Alice - App React)                                   │
│  ├── Dashboard: Vue "Reste à vivre" du mois                     │
│  ├── Notification: "Dépense inhabituelle détectée"              │
│  ├── 1 clic pour catégoriser                                    │
│  └── Badge débloqué: "Streak 7 jours"                           │
│                                                                 │
│  💼 MIDI (Bob - App React)                                      │
│  ├── Import CSV depuis sa banque                                │
│  ├── Auto-catégorisation par IA                                 │
│  └── Validation rapide (5 transactions groupées)                │
│                                                                 │
│  🏠 SOIR (Ensemble - App React)                                 │
│  ├── Vue couple: Répartition dépenses perso/joint               │
│  ├── Discussion prêt en cours                                   │
│  └── Objectif épargne: "Voyage Japon"                           │
│                                                                 │
│  🔧 WEEK-END (Alice - Streamlit Admin)                          │
│  ├── Configuration règles de catégorisation avancées            │
│  ├── Audit des règles IA                                        │
│  ├── Projections patrimoniales (scénarios)                      │
│  └── Export données pour comptable                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Architecture cible

### 4.1 Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ARCHITECTURE HYBRIDE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────┐    ┌─────────────────────┐                    │
│  │   FRONTEND REACT    │    │   FRONTEND STREAMLIT │                   │
│  │   (Utilisateur)     │    │   (Admin/Power User) │                   │
│  ├─────────────────────┤    ├─────────────────────┤                    │
│  │ • Dashboard         │    │ • Audit IA          │                    │
│  │ • Transactions      │    │ • Règles avancées   │                    │
│  │ • Import CSV        │    │ • Projections       │                    │
│  │ • Budgets (vue)     │    │ • Configuration     │                    │
│  │ • Objectifs         │    │ • Debug             │                    │
│  │ • Couple (vue)      │    │ • Rapports          │                    │
│  └──────────┬──────────┘    └──────────┬──────────┘                    │
│             │                          │                                │
│             │    HTTP/WebSocket        │                                │
│             └──────────┬───────────────┘                                │
│                        │                                                │
│  ┌─────────────────────┴─────────────────────┐                         │
│  │           PYTHON API (FastAPI)            │                         │
│  ├───────────────────────────────────────────┤                         │
│  │ • REST API (CRUD)                         │                         │
│  │ • WebSocket (temps réel)                  │                         │
│  │ • Auth (JWT)                              │                         │
│  │ • Batch jobs (IA, imports)                │                         │
│  │ • Webhooks (optionnel)                    │                         │
│  └──────────┬────────────────────────────────┘                         │
│             │                                                          │
│  ┌──────────┴────────────────────────────────┐                         │
│  │           LOGIQUE MÉTIER (Python)         │                         │
│  ├───────────────────────────────────────────┤                         │
│  │ modules/                                  │                         │
│  │ ├── ai/              # Catégorisation IA │                         │
│  │ ├── wealth/          # Projections       │                         │
│  │ ├── couple/          # Logique couple    │                         │
│  │ ├── gamification/    # Badges, streaks   │                         │
│  │ └── ...                                   │                         │
│  └──────────┬────────────────────────────────┘                         │
│             │                                                          │
│  ┌──────────┴────────────────────────────────┐                         │
│  │           BASE DE DONNÉES                 │                         │
│  ├───────────────────────────────────────────┤                         │
│  │ SQLite (principal)                        │                         │
│  │ ├── Chiffrement optionnel (AES-256)      │                         │
│  │ ├── Backup automatique                   │                         │
│  │ └── Sync optionnelle (cloud)             │                         │
│  └───────────────────────────────────────────┘                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Stack technique détaillé

| Couche | Technologie | Justification |
|--------|-------------|---------------|
| **Frontend User** | React 18 + TypeScript + Vite | Performance, DX, écosystème |
| **UI Components** | shadcn/ui + Tailwind | Design system cohérent, accessible |
| **State Management** | React Query (TanStack) | Cache serveur, synchronisation |
| **Frontend Admin** | Streamlit | Rapide pour outils internes, Python natif |
| **API** | FastAPI | Performance, validation Pydantic, auto-docs |
| **Auth** | JWT + bcrypt | Stateless, compatible offline |
| **DB** | SQLite + SQLAlchemy | Local, privacy, migrations gérées |
| **IA/ML** | scikit-learn + transformers | Local possible, fallback cloud |
| **Real-time** | WebSocket (Socket.io) | Notifications, sync |
| **Mobile** | PWA (Vite PWA plugin) | Offline, installable |
| **Tests** | Vitest (FE) + pytest (BE) | Couverture complète |
| **Build** | Docker Compose | Déploiement simple |

### 4.3 Structure du projet fusionné

```
FinCouple-Pro/                              # Monorepo
├── apps/
│   ├── web/                               # Frontend React (ex-FinCouple)
│   │   ├── src/
│   │   │   ├── components/               # UI components
│   │   │   ├── features/                 # Feature-based modules
│   │   │   │   ├── dashboard/
│   │   │   │   ├── transactions/
│   │   │   │   ├── import/
│   │   │   │   ├── budgets/
│   │   │   │   ├── couple/
│   │   │   │   └── auth/
│   │   │   ├── hooks/                    # Custom hooks
│   │   │   ├── lib/                      # Utils
│   │   │   ├── types/                    # TypeScript types
│   │   │   └── App.tsx
│   │   ├── package.json
│   │   └── vite.config.ts
│   │
│   └── admin/                             # Streamlit Admin (ex-FinancePerso pages)
│       ├── pages/                         # Pages admin
│       │   ├── audit_ia.py
│       │   ├── projections.py
│       │   ├── config_advanced.py
│       │   └── ...
│       ├── requirements.txt
│       └── Dockerfile
│
├── api/                                    # Backend FastAPI
│   ├── src/
│   │   ├── main.py                        # Entry point
│   │   ├── routers/                       # API endpoints
│   │   │   ├── transactions.py
│   │   │   ├── categories.py
│   │   │   ├── budgets.py
│   │   │   ├── couple.py
│   │   │   └── ai.py
│   │   ├── services/                      # Business logic (ex-modules/)
│   │   │   ├── ai/
│   │   │   ├── wealth/
│   │   │   ├── couple/
│   │   │   └── gamification/
│   │   ├── models/                        # Pydantic models
│   │   ├── db/                            # Database layer
│   │   └── core/                          # Config, auth, logging
│   ├── tests/
│   └── requirements.txt
│
├── shared/                                 # Code partagé
│   ├── types/                             # Types TypeScript + Python
│   ├── constants/                         # Constants
│   └── schemas/                           # Pydantic/TS schemas
│
├── database/                               # Migrations, seeds
│   ├── migrations/
│   └── seeds/
│
├── docs/                                   # Documentation
├── docker-compose.yml                      # Orchestration
└── README.md
```

### 4.4 Flux de données

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FLUX DE DONNÉES                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. IMPORT CSV                                                          │
│  ─────────────────                                                      │
│  React → API POST /import → Parse CSV → IA Categorization → SQLite     │
│       ↓                                                                 │
│  WebSocket: "Nouvelles transactions disponibles"                       │
│       ↓                                                                 │
│  React: Mise à jour dashboard en temps réel                            │
│                                                                         │
│  2. VALIDATION TRANSACTIONS                                             │
│  ──────────────────────────                                             │
│  React → API PUT /transactions/batch → Validation → Learning Rules     │
│       ↓                                                                 │
│  Background: Réentraînement ML (si assez de nouvelles données)         │
│                                                                         │
│  3. ANALYSES & PROJECTIONS                                              │
│  ─────────────────────────                                              │
│  Streamlit (Admin) → Direct DB access → Analyses complexes             │
│       ↓                                                                 │
│  Ou: React → API GET /projections → Calculs → Résultats                │
│                                                                         │
│  4. SYNCHRONISATION (optionnel)                                         │
│  ──────────────────────────────                                         │
│  SQLite → Sync Service → Cloud (Supabase/PostgreSQL)                   │
│       ↓                                                                 │
│  Multi-device sync                                                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Plan de migration (6-12 mois)

### 5.1 Roadmap visuelle

```
2026
├── Q1 (Mois 1-3): Fondations
│   ├── M1: Setup monorepo, API FastAPI, DB layer
│   ├── M2: Auth, core features (transactions, categories)
│   └── M3: Import CSV React, migration données
│
├── Q2 (Mois 4-6): Core Features
│   ├── M4: Dashboard React avec KPIs
│   ├── M5: Budgets & Objectifs épargne
│   └── M6: Gestion couple (basique)
│
├── Q3 (Mois 7-9): IA & Puissance
│   ├── M7: Intégration IA catégorisation
│   ├── M8: Projections patrimoniales
│   └── M9: Admin Streamlit (features avancées)
│
└── Q4 (Mois 10-12): Polish & Release
    ├── M10: Gamification, badges, streaks
    ├── M11: Tests E2E, optimisation, PWA
    └── M12: Documentation, migration, release
```

### 5.2 Phase 1: Fondations (Mois 1-3)

#### Mois 1: Infrastructure
**Objectif**: Avoir un squelette fonctionnel avec DB + API + React

**Tâches:**
- [ ] Setup monorepo (pnpm workspaces ou Nx)
- [ ] Créer API FastAPI avec structure modulaire
- [ ] Migrer schema DB SQLite (ex-FinancePerso)
- [ ] Setup SQLAlchemy + Alembic migrations
- [ ] Créer app React Vite + shadcn/ui
- [ ] Setup React Query + routing
- [ ] Auth JWT basique (login/register)
- [ ] Docker Compose (API + DB + React)

**Livrables:**
- `docker-compose up` lance l'ensemble
- Auth fonctionnelle (login/register)
- CRUD transactions basique

**Validation:**
- Tests API passent
- React démarre et communique avec API
- DB migrations fonctionnent

---

#### Mois 2: Core Data Layer
**Objectif**: Toute la couche données fonctionnelle

**Tâches:**
- [ ] Migrer tous les modèles DB (ex-FinancePerso)
- [ ] API endpoints CRUD complets
- [ ] Relations (transactions ↔ categories ↔ accounts)
- [ ] Validation Pydantic
- [ ] Tests unitaires API
- [ ] Seeders pour données de test
- [ ] React: Pages Transactions, Catégories
- [ ] React: Formulaires avec validation

**Livrables:**
- API REST complète
- UI CRUD fonctionnelle
- Tests coverage > 60%

**Migration données:**
```bash
# Script de migration FinancePerso → Nouvelle DB
python scripts/migrate_financeperso.py \
  --source Data/finance.db \
  --target postgresql://... # ou nouvelle SQLite
```

---

#### Mois 3: Import CSV & Migration
**Objectif**: Feature parity sur l'import avec FinCouple

**Tâches:**
- [ ] Migrer parser CSV (ex-FinCouple)
- [ ] Intégrer presets banques (ex-FinancePerso)
- [ ] UI mapping colonnes (React)
- [ ] Preview avant import
- [ ] Import batch avec transaction DB
- [ ] Déduplication (hash transactions)
- [ ] Migration données utilisateurs (volontaires)
- [ ] Parallel run (ancien/nouveau côte à côte)

**Livrables:**
- Import CSV fonctionnel (parité FinCouple)
- Migration données testée
- Documentation migration utilisateur

---

### 5.3 Phase 2: Core Features (Mois 4-6)

#### Mois 4: Dashboard Moderne
**Objectif**: Dashboard React avec toutes les visualisations

**Tâches:**
- [ ] KPI Cards (revenus, dépenses, reste à vivre, épargne)
- [ ] Graphique donut (répartition catégories)
- [ ] Graphique line (évolution mensuelle)
- [ ] Tableau transactions récentes
- [ ] Filtres période (mois/année/custom)
- [ ] Responsive mobile
- [ ] Dark mode
- [ ] Tests visuels (Chromatic ou similar)

**Inspirations design:**
- Dashboard FinCouple (à reproduire)
- V5.5 FinancePerso (design system déjà créé)

---

#### Mois 5: Budgets & Objectifs
**Objectif**: Gestion budgétaire complète

**Tâches:**
- [ ] Migration logique budgets (ex-FinancePerso)
- [ ] UI création budget par catégorie
- [ ] Visualisation progression (barres)
- [ ] Alertes dépassement
- [ ] Objectifs épargne
- [ ] Association objectifs ↔ comptes
- [ ] Projections simples (lineaire)

**Fonctionnalités avancées (optionnel):**
- [ ] Budgets dynamiques (ajustement auto)
- [ ] Prédictions ML

---

#### Mois 6: Gestion Couple (Phase 1)
**Objectif**: Support multi-comptes et vue couple

**Tâches:**
- [ ] Multi-comptes (perso A, perso B, joint)
- [ ] Attribution transactions par compte
- [ ] Vue "Comparatif couple"
- [ ] Répartition dépenses communes
- [ ] Détection virements internes
- [ ] Privacy filters (base)

**Non inclus (Phase 3):**
- Gestion des prêts entre conjoints
- Split automatique des dépenses

---

### 5.4 Phase 3: IA & Puissance (Mois 7-9)

#### Mois 7: Intelligence Artificielle
**Objectif**: Catégorisation IA intégrée

**Tâches:**
- [ ] Migration moteur IA (ex-FinancePerso)
- [ ] API endpoint /ai/categorize
- [ ] Règles de catégorisation (regex)
- [ ] ML local (scikit-learn)
- [ ] Fallback IA Cloud (Gemini/OpenAI)
- [ ] Apprentissage incrémental
- [ ] UI: Suggestions catégories dans React
- [ ] Validation rapide (batch)

**Architecture IA:**
```python
# Cascade de catégorisation (ex-FinancePerso)
def categorize_transaction(label: str) -> Category:
    1. Règles exactes (learning_rules)
    2. Règles partielles (pattern matching)
    3. ML Local (si activé et disponible)
    4. IA Cloud (Gemini/OpenAI/DeepSeek)
    5. Catégorie par défaut ("Inconnu")
```

---

#### Mois 8: Projections & Wealth
**Objectif**: Projections patrimoniales avancées

**Tâches:**
- [ ] Migration moteur projections (Monte Carlo)
- [ ] API endpoints /projections/*
- [ ] Scénarios what-if (inflation, rendement)
- [ ] UI: Simulateur React
- [ ] Graphiques probabilités
- [ ] Objectifs patrimoniaux
- [ ] Détection abonnements

**Pages concernées:**
- Projections (Streamlit admin)
- Vue Wealth (optionnel dans React)

---

#### Mois 9: Admin Streamlit
**Objectif**: Portail admin avec features avancées

**Tâches:**
- [ ] Setup Streamlit dédié (admin)
- [ ] Audit IA (qualité catégorisation)
- [ ] Gestion règles avancées
- [ ] Configuration système
- [ ] Debug tools
- [ ] Rapports détaillés
- [ ] Export données (CSV, PDF)

**Différence avec React:**
- Streamlit = outils puissants, complexes
- React = usage quotidien, simple

---

### 5.5 Phase 4: Polish & Release (Mois 10-12)

#### Mois 10: Gamification
**Objectif**: Engagement via gamification

**Tâches:**
- [ ] Migration système badges
- [ ] Streaks (connexion quotidienne)
- [ ] Challenges (objectifs mensuels)
- [ ] UI: Widget gamification React
- [ ] Notifications (toasts)
- [ ] Partage progrès (optionnel)

---

#### Mois 11: Qualité & Performance
**Objectif**: Application production-ready

**Tâches:**
- [ ] Tests E2E (Playwright)
- [ ] Tests API (pytest) - coverage > 80%
- [ ] Optimisation bundle (lazy loading)
- [ ] PWA (offline mode)
- [ ] Cache stratégies (React Query)
- [ ] Performance monitoring (Sentry)
- [ ] Analytics (privacy-friendly)
- [ ] Accessibility (a11y)

---

#### Mois 12: Migration & Documentation
**Objectif**: Lancement en production

**Tâches:**
- [ ] Documentation utilisateur
- [ ] Guide migration FinancePerso → FinCouple Pro
- [ ] Migration finale des données
- [ ] Déploiement production
- [ ] Communication utilisateurs
- [ ] Support post-migration
- [ ] Archivage ancien projet (branche `legacy`)

---

## 6. Matrice des fonctionnalités

### 6.1 Priorisation (RICE)

| Feature | Reach | Impact | Confidence | Effort | RICE | Phase |
|---------|-------|--------|------------|--------|------|-------|
| Import CSV | 100% | 5 | 100% | 3 | 167 | M3 |
| Dashboard React | 100% | 5 | 100% | 4 | 125 | M4 |
| Catégorisation IA | 80% | 5 | 90% | 5 | 72 | M7 |
| Budgets | 70% | 4 | 100% | 4 | 70 | M5 |
| Multi-comptes | 60% | 4 | 100% | 3 | 80 | M6 |
| Projections | 40% | 4 | 80% | 5 | 26 | M8 |
| Gamification | 50% | 3 | 90% | 3 | 45 | M10 |
| Assistant IA | 30% | 4 | 70% | 6 | 14 | M9+ |
| Gestion prêts | 20% | 3 | 100% | 4 | 15 | M9+ |
| Sync cloud | 40% | 3 | 60% | 5 | 14 | Post-M12 |

### 6.2 Mapping features projet → fusion

| Feature FinancePerso | Implémentation cible | Priorité |
|---------------------|---------------------|----------|
| Import CSV avancé | React + API | P0 |
| Validation batch | React + API | P0 |
| Catégorisation IA | API Python | P0 |
| Dashboard multi-vues | React | P0 |
| Budgets dynamiques | React + API | P1 |
| Projections Monte Carlo | Streamlit Admin + API | P1 |
| Gestion couple (prêts) | Streamlit Admin | P2 |
| Gamification | React | P2 |
| Assistant IA | Streamlit Admin | P2 |
| Audit IA | Streamlit Admin | P2 |
| Privacy/GDPR | API + Config | P1 |
| Notifications proactives | React + API | P1 |
| Wealth management | Streamlit Admin | P2 |
| Détection abonnements | API + React | P2 |
| Multi-device sync | Post-M12 | P3 |

### 6.3 Ce qui disparaît

Fonctionnalités non migrées (complexité vs valeur):
- **Modules legacy**: ui_v2, notifications_legacy (remplacés)
- **Features expérimentales**: Certaines features de l'archive
- **Duplications**: Feedback modules multiples (consolidés)
- **Vues redondantes**: Dashboard v5, v5.5 (unifiés dans React)

---

## 7. Risques et mitigation

### 7.1 Matrice des risques

| Risque | Probabilité | Impact | Mitigation |
|--------|------------|--------|------------|
| **Migration données** | Moyen | Critique | Tests exhaustifs, rollback possible, parallel run |
| **Performance API** | Moyen | Élevé | Cache agressif, pagination, lazy loading |
| **Complexité IA** | Élevé | Élevé | MVP sans ML local d'abord, fallback cloud |
| **Adoption utilisateurs** | Moyen | Élevé | Onboarding progressif, feature flags |
| **Sécurité données** | Faible | Critique | Chiffrement, audit sécurité, pentest |
| **Dette technique** | Moyen | Moyen | Refactoring continu, tests, documentation |
| **Ressources humaines** | Élevé | Élevé | Priorisation stricte, scope ajustable |

### 7.2 Stratégies de mitigation

#### Migration données
```
Stratégie: Parallel Run
───────────────────────
Mois 1-6: Ancien et nouveau coexistent
         - Écritures dans les deux systèmes
         - Lecture depuis l'ancien (source de vérité)
         - Comparaison quotidienne des données

Mois 7-9: Switch progressif
         - Utilisateurs volontaires d'abord
         - Feature flag par utilisateur
         - Rollback immédiat si problème

Mois 10-12: Migration complète
         - Migration finale des retardataires
         - Archivage ancien système
```

#### Performance
```
Stratégie: Optimisation progressive
───────────────────────────────────
1. Pagination systématique (limit/offset)
2. Cache React Query (stale-while-revalidate)
3. Cache API (Redis optionnel)
4. Lazy loading des composants
5. Virtualization pour grandes listes
6. Web Workers pour calculs lourds
```

---

## 8. Ressources nécessaires

### 8.1 Équipe recommandée

| Rôle | FTE | Durée | Responsabilités |
|------|-----|-------|-----------------|
| **Lead Full-Stack** | 1 | 12 mois | Architecture, code review, coordination |
| **Développeur React** | 1 | 9 mois (M1-M9) | Frontend, UI/UX, PWA |
| **Développeur Python** | 1 | 9 mois (M1-M9) | API, IA, migrations |
| **DevOps/QA** | 0.5 | 6 mois (M6-M12) | CI/CD, tests, déploiement |
| **Product Owner** | 0.5 | 12 mois | Priorisation, validation, support |

**Total:** 3.5 FTE moyen sur 12 mois

### 8.2 Infrastructure

| Composant | Coût mensuel (estimé) | Notes |
|-----------|----------------------|-------|
| Développement local | €0 | Docker local |
| CI/CD (GitHub Actions) | €0 | Gratuit pour open source |
| Hébergement (optionnel) | €10-50 | VPS si sync cloud |
| Sentry (error tracking) | €0 | Gratuit tier |
| Analytics (Plausible) | €0 | Self-hosted ou gratuit |
| **Total** | **€0-50/mois** | Self-hosted = gratuit |

---

## 9. Checkpoints de validation

### 9.1 Milestones go/no-go

| Milestone | Date | Critères de succès | Décision |
|-----------|------|-------------------|----------|
| **M3** | Fin mois 3 | Import CSV fonctionnel, migration données testée | Go/No-go Phase 2 |
| **M6** | Fin mois 6 | Dashboard + Budgets + Couple basique | Go/No-go Phase 3 |
| **M9** | Fin mois 9 | IA intégrée, Admin Streamlit | Go/No-go Phase 4 |
| **M12** | Fin mois 12 | Tests passent, documentation OK | Release |

### 9.2 KPIs de suivi

| KPI | Cible M3 | Cible M6 | Cible M12 |
|-----|----------|----------|-----------|
| **Couverture tests** | 60% | 75% | 85% |
| **Temps réponse API** | <200ms | <100ms | <50ms |
| **Lighthouse score** | - | 70 | 90 |
| **Utilisateurs migrés** | 0% | 20% | 100% |
| **Bugs critiques** | <5 | <3 | 0 |
| **NPS utilisateurs** | - | >30 | >50 |

---

## 10. Annexes

### 10.1 Glossaire

| Terme | Définition |
|-------|-----------|
| **FTE** | Full-Time Equivalent (équivalent temps plein) |
| **RICE** | Reach × Impact × Confidence / Effort (score de priorisation) |
| **PWA** | Progressive Web App (application web installable) |
| **MVP** | Minimum Viable Product (produit minimum viable) |
| **DB** | Database (base de données) |

### 10.2 Liens utiles

- **FinancePerso**: `/Users/aurelien/Documents/Projets/FinancePerso`
- **FinCouple**: `/Users/aurelien/Documents/Projets/FinancePerso/Ideas/couple-cashflow-clever-main`
- **AGENTS.md**: Guide développement FinancePerso
- **Design System V5.5**: `modules/ui/v5_5/`

### 10.3 Checklist de démarrage

```markdown
## Avant de commencer (Mois 0)

- [ ] Valider ce document avec stakeholders
- [ ] Créer repository monorepo
- [ ] Setup CI/CD basique
- [ ] Créer issues GitHub pour M1
- [ ] Préparer environnement dev (Docker)
- [ ] Rédiger ADRs (Architecture Decision Records)
- [ ] Identifier beta testeurs
```

---

## Conclusion

Ce plan de fusion vise à créer **FinCouple Pro**: une application qui combine:
- ✅ **La simplicité** et l'UX moderne de FinCouple (React)
- ✅ **La puissance** et les fonctionnalités avancées de FinancePerso (Python)
- ✅ **Le respect de la privacy** avec SQLite local
- ✅ **Une architecture évolutive** pour les années à venir

**Prochaine étape:** Validation de ce plan et début Phase 1 (Mois 1)

---

*Document généré le 2026-03-02*  
*Version 1.0*  
*Pour questions: Voir section 10.2*
