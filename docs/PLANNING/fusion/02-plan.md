# 02 - Plan : Roadmap 9 mois

## 🗓️ Timeline globale

```
2026
├── Q1 (M1-M3): FONDATIONS 🔄
├── Q2 (M4-M6): INTELLIGENCE
└── Q3 (M7-M9): RELEASE
```

---

## Phase 1 : Fondations (Mois 1)

### Semaine 1 : Infrastructure
- [ ] Repository `fincouple-pro` créé
- [ ] Docker Compose (API + Web + Admin)
- [ ] CI/CD GitHub Actions
- [ ] Structure monorepo

```bash
fincouple-pro/
├── apps/
│   ├── web/          # React + Vite
│   └── admin/        # Streamlit
├── api/              # FastAPI
├── database/         # Alembic migrations
└── docker-compose.yml
```

### Semaine 2 : Backend Core
- [ ] FastAPI + SQLAlchemy 2.0 setup
- [ ] Modèles : User, Household, Account, Category, Transaction
- [ ] Auth JWT (login/register)
- [ ] CRUD endpoints de base

### Semaine 3 : Frontend Core
- [ ] React 18 + TypeScript + Vite
- [ ] shadcn/ui + Tailwind CSS
- [ ] React Query + Router
- [ ] Auth context + Protected routes

### Semaine 4 : Database
- [ ] Schéma SQLite (adapté FinancePerso)
- [ ] Alembic migrations
- [ ] Scripts migration données existantes

**Livrables M1**:
- [ ] Repository fonctionnel
- [ ] API avec auth
- [ ] React app connectée
- [ ] Base SQLite opérationnelle

---

## Phase 2 : Core Features (Mois 2-3)

### Mois 2 : Import & Dashboard

#### Import CSV
- [ ] Upload fichier
- [ ] Mapping intelligent colonnes
- [ ] Preview avant import
- [ ] Détection doublons

#### Dashboard React
- [ ] Vue "Reste à vivre"
- [ ] KPIs mensuels
- [ ] Graphique dépenses
- [ ] Notifications temps réel

### Mois 3 : Transactions & Couple

#### Gestion Transactions
- [ ] Liste paginée
- [ ] Filtres avancés
- [ ] Édition inline
- [ ] Validation batch

#### Gestion Couple (basique)
- [ ] Setup ménage
- [ ] Comptes perso/joint
- [ ] Répartition dépenses

**Livrables M3**:
- [ ] Import CSV fonctionnel
- [ ] Dashboard avec données
- [ ] CRUD transactions complet
- [ ] Vue couple basique

---

## Phase 3 : Intelligence (Mois 4-6)

### Mois 4 : IA & Catégorisation
- [ ] Intégration moteur IA FinancePerso
- [ ] Endpoint `/ai/categorize`
- [ ] Suggestions temps réel
- [ ] Apprentissage règles utilisateur
- [ ] ML local (option offline)

### Mois 5 : Budgets
- [ ] Création budgets catégorie
- [ ] Suivi temps réel
- [ ] Alertes dépassement
- [ ] Prédictions ML

### Mois 6 : Projections & Admin
- [ ] Monte Carlo simulations
- [ ] Scénarios what-if
- [ ] Objectifs épargne
- [ ] Admin Streamlit (audit, config)

**Livrables M6**:
- [ ] IA catégorisation intégrée
- [ ] Budgets dynamiques
- [ ] Projections patrimoine
- [ ] Admin opérationnel

---

## Phase 4 : Release (Mois 7-9)

### Mois 7 : Gamification
- [ ] Système badges
- [ ] Streaks
- [ ] Challenges couple
- [ ] Leaderboard privé

### Mois 8 : Optimisations
- [ ] Performance React
- [ ] Cache API
- [ ] Bundle optimization
- [ ] Lighthouse > 90

### Mois 9 : Tests & Migration
- [ ] Tests > 80% coverage
- [ ] Tests E2E (Playwright)
- [ ] Migration utilisateurs FinancePerso
- [ ] Documentation

**Livrables M9**:
- [ ] Gamification complète
- [ ] Tests > 80%
- [ ] Migration réussie
- [ ] Release publique

---

## 📊 Suivi

### KPIs par phase

| Phase | Métrique | Cible |
|-------|----------|-------|
| M1 | Build time | < 30s |
| M3 | Coverage | > 50% |
| M6 | Lighthouse | > 80 |
| M9 | Coverage | > 80% |

### Points de contrôle

**Checkpoints mensuels**:
- [ ] Review features
- [ ] Mise à jour KPIs
- [ ] Documentation à jour
- [ ] Tests passent

---

[→ Specs techniques : 03_SPECS.md](./03_SPECS.md)
