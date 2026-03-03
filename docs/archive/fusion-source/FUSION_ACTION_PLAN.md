# 🚀 Plan d'Action - Fusion FinCouple Pro

> Plan d'amélioration adapté depuis CODE_QUALITY_ROADMAP.md vers la fusion

---

## 📋 Contexte

Fusion de **FinancePerso** (Streamlit/Python, fonctionnalités avancées) et **FinCouple** (React/TypeScript, UX moderne) pour créer **FinCouple Pro**.

**Architecture cible**: React + FastAPI + SQLite (privacy-first)

---

## 🎯 Phases de la Fusion

### Phase 1: Fondations (Mois 1) 🔄 NEXT

#### 1.1 Setup Infrastructure
- [ ] Créer monorepo `fincouple-pro`
- [ ] Setup Docker Compose (API + Web + Admin)
- [ ] CI/CD GitHub Actions
- [ ] Structure des dossiers :
  ```
  fincouple-pro/
  ├── apps/
  │   ├── web/          # React + Vite
  │   └── admin/        # Streamlit
  ├── api/              # FastAPI
  ├── database/         # Migrations
  └── docs/             # Documentation
  ```

#### 1.2 Backend FastAPI - Core
- [ ] Setup FastAPI + SQLAlchemy + Alembic
- [ ] Modèles de données (depuis FinancePerso)
  - [ ] User / Household
  - [ ] Account
  - [ ] Category
  - [ ] Transaction
- [ ] Endpoints CRUD de base
- [ ] Authentication JWT

#### 1.3 Frontend React - Setup
- [ ] React 18 + TypeScript + Vite
- [ ] shadcn/ui + Tailwind CSS
- [ ] React Query + React Router
- [ ] Structure features :
  ```
  src/features/
  ├── auth/
  ├── transactions/
  ├── dashboard/
  └── import/
  ```

#### 1.4 Database Migration
- [ ] Schéma SQLite (adapté depuis FinancePerso)
- [ ] Migrations Alembic
- [ ] Scripts migration données existantes

---

### Phase 2: Core Features (Mois 2-3) 📋

#### 2.1 Import & Catégorisation
- [ ] Import CSV (adapté depuis FinancePerso)
- [ ] Mapping intelligent des colonnes
- [ ] Catégorisation IA (intégration API)
- [ ] Validation batch

#### 2.2 Dashboard React
- [ ] Vue "Reste à vivre"
- [ ] KPIs mensuels
- [ ] Graphiques dépenses
- [ ] Notifications temps réel

#### 2.3 Gestion Transactions
- [ ] Liste transactions (paginée)
- [ ] Filtres avancés
- [ ] Édition rapide
- [ ] Historique modifications

#### 2.4 Gestion Couple - Basique
- [ ] Setup ménage
- [ ] Comptes perso/joint
- [ ] Vue répartition dépenses

---

### Phase 3: Intelligence (Mois 4-6) 📋

#### 3.1 IA & Catégorisation
- [ ] Intégration moteur IA FinancePerso
- [ ] Suggestions temps réel
- [ ] Apprentissage règles utilisateur
- [ ] ML local (option offline)

#### 3.2 Budgets Dynamiques
- [ ] Création budgets par catégorie
- [ ] Suivi temps réel
- [ ] Alertes dépassement
- [ ] Prédictions ML

#### 3.3 Projections Patrimoine
- [ ] Monte Carlo simulations
- [ ] Scénarios what-if
- [ ] Objectifs épargne
- [ ] Vue long terme

#### 3.4 Admin Streamlit
- [ ] Audit données
- [ ] Configuration règles IA
- [ ] Export comptable
- [ ] Debug/Monitoring

---

### Phase 4: Release (Mois 7-9) 📋

#### 4.1 Gamification
- [ ] Badges
- [ ] Streaks
- [ ] Challenges couple
- [ ] Leaderboard privé

#### 4.2 Optimisations
- [ ] Performance React
- [ ] Cache API
- [ ] Bundle size
- [ ] Lighthouse score > 90

#### 4.3 Tests & Qualité
- [ ] Tests unitaires (>80%)
- [ ] Tests E2E (Playwright)
- [ ] Tests charge API
- [ ] Documentation API

#### 4.4 Migration Utilisateurs
- [ ] Import données FinancePerso
- [ ] Migration progressive
- [ ] Parallel run option
- [ ] Communication utilisateurs

---

## 📁 Livrables par Phase

### Phase 1
- [ ] Repository GitHub initialisé
- [ ] Docker Compose fonctionnel
- [ ] API FastAPI avec auth
- [ ] React app avec routing
- [ ] Base SQLite connectée

### Phase 2
- [ ] Import CSV fonctionnel
- [ ] Dashboard avec données réelles
- [ ] CRUD transactions complet
- [ ] Vue couple basique

### Phase 3
- [ ] IA catégorisation intégrée
- [ ] Budgets dynamiques
- [ ] Projections patrimoine
- [ ] Admin Streamlit opérationnel

### Phase 4
- [ ] Gamification complète
- [ ] Tests > 80% couverture
- [ ] Documentation complète
- [ ] Migration utilisateurs

---

## 🔧 Ressources Techniques

### Stack Frontend
- React 18 + TypeScript
- Vite (build tool)
- shadcn/ui + Tailwind CSS
- React Query (state server)
- Zustand (state client)
- React Router (navigation)

### Stack Backend
- FastAPI (Python 3.12)
- SQLAlchemy 2.0 (ORM)
- Alembic (migrations)
- Pydantic (validation)
- JWT (auth)
- pytest (tests)

### Database
- SQLite (local)
- Chiffrement optionnel (SQLCipher)
- Backup automatique

---

## 📊 Suivi & Métriques

### KPIs Phase 1
| Métrique | Cible | Outil |
|----------|-------|-------|
| Build time | < 30s | GitHub Actions |
| Test coverage | > 50% | pytest-cov |
| Bundle size | < 500KB | Vite analyzer |
| API latency | < 100ms | FastAPI logs |

### KPIs Phase 4
| Métrique | Cible | Outil |
|----------|-------|-------|
| Test coverage | > 80% | Coverage CI |
| Lighthouse | > 90 | Lighthouse CI |
| Migration | 100% users | Analytics |
| Uptime | 99.9% | Monitoring |

---

## 🗓️ Timeline

```
2026
├── Q1 (M1-M3): FONDATIONS
│   ├── Jan: Setup + Auth
│   ├── Fév: Import + Dashboard
│   └── Mar: Transactions + Couple
│
├── Q2 (M4-M6): INTELLIGENCE
│   ├── Avr: IA + Catégorisation
│   ├── Mai: Budgets + Projections
│   └── Juin: Admin + Polish
│
└── Q3 (M7-M9): RELEASE
    ├── Juil: Gamification
    ├── Août: Tests + Optimisations
    └── Sep: Migration + Launch
```

---

## 📚 Documentation à Créer

### Technique
- [ ] `README.md` - Setup rapide
- [ ] `API.md` - Documentation endpoints
- [ ] `ARCHITECTURE.md` - Décisions techniques
- [ ] `CONTRIBUTING.md` - Guide contributeur

### Utilisateur
- [ ] Guide onboarding
- [ ] FAQ migration
- [ ] Tutoriels vidéo

---

## ✅ Checklist de Démarrage

### Avant de commencer:
- [ ] Lire tous les documents FUSION_*.md
- [ ] Valider approche hybride avec stakeholders
- [ ] Confirmer budget/timeline
- [ ] Identifier équipe (roles)

### Semaine 1:
- [ ] Créer repository
- [ ] Setup Docker
- [ ] Hello World API + Web
- [ ] Première PR merged

---

*Plan basé sur CODE_QUALITY_ROADMAP.md et documentation fusion*
*Dernière mise à jour: 2026-03-02*
