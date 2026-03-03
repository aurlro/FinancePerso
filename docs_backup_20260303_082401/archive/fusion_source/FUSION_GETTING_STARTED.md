# 🚀 Guide de Démarrage - Fusion FinCouple Pro

> Checklist et actions concrètes pour lancer la fusion

---

## ✅ Phase 0: Préparation (Avant le Mois 1)

### Semaine -2: Validation

- [ ] **Revue du plan** avec parties prenantes
  - [ ] Lire `FUSION_MASTERPLAN.md`
  - [ ] Valider approche hybride React + Streamlit
  - [ ] Confirmer SQLite locale
  - [ ] Valider timeline 6-12 mois

- [ ] **Setup environnement**
  - [ ] Créer repository GitHub `fincouple-pro`
  - [ ] Configurer monorepo (pnpm workspaces)
  - [ ] Setup CI/CD GitHub Actions (template)
  - [ ] Créer projet Notion/Jira pour suivi

### Semaine -1: Fondations techniques

- [ ] **Docker environment**
  ```bash
  # Créer structure
  mkdir fincouple-pro && cd fincouple-pro
  mkdir -p apps/{web,admin} api database docs
  
  # Docker Compose de base
  cat > docker-compose.yml << 'EOF'
  version: '3.8'
  services:
    api:
      build: ./api
      ports: ["8000:8000"]
      volumes: ["./data:/app/data"]
    web:
      build: ./apps/web
      ports: ["3000:80"]
    admin:
      build: ./apps/admin
      ports: ["8501:8501"]
  EOF
  ```

- [ ] **Stack choisie**
  - [ ] Frontend: React 18 + TypeScript + Vite
  - [ ] UI: shadcn/ui + Tailwind CSS
  - [ ] State: React Query + Zustand
  - [ ] Backend: FastAPI + SQLAlchemy
  - [ ] DB: SQLite + Alembic
  - [ ] Tests: Vitest (FE) + pytest (BE)

---

## 🏃 Sprint 1: Mois 1 - Setup & Auth

### Semaine 1: Infrastructure

**Jours 1-2: Setup API**
```bash
# Créer API FastAPI
cd api
python -m venv .venv
source .venv/bin/activate
pip install fastapi sqlalchemy alembic pydantic uvicorn

# Structure
mkdir -p src/{models,routers,services,core}
touch src/main.py src/core/config.py
```

**Jours 3-4: Setup React**
```bash
cd apps/web
npm create vite@latest . -- --template react-ts
npm install @tanstack/react-query axios react-router-dom
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# shadcn/ui
npx shadcn-ui@latest init
```

**Jour 5: Docker & CI**
- [ ] Dockerfile pour chaque service
- [ ] GitHub Actions: lint + test + build
- [ ] Pre-commit hooks

### Semaine 2: Database & Models

- [ ] **Migrations Alembic**
  ```bash
  cd api
  alembic init migrations
  # Créer migration initiale avec toutes les tables
  ```

- [ ] **Modèles SQLAlchemy** (depuis FinancePerso)
  - [ ] User / Household
  - [ ] Account
  - [ ] Category
  - [ ] Transaction

- [ ] **Pydantic schemas**
  - [ ] Request/Response models
  - [ ] Validation

### Semaine 3: Authentication

- [ ] **Backend**
  - [ ] JWT generation/validation
  - [ ] Login endpoint
  - [ ] Register endpoint
  - [ ] Password hashing (bcrypt)

- [ ] **Frontend**
  - [ ] Login page
  - [ ] Register page
  - [ ] Auth context
  - [ ] Protected routes
  - [ ] Token storage (httpOnly cookie)

### Semaine 4: CRUD de base

- [ ] **API Endpoints**
  - [ ] GET /transactions
  - [ ] POST /transactions
  - [ ] PUT /transactions/:id
  - [ ] DELETE /transactions/:id

- [ ] **React Pages**
  - [ ] Transactions list
  - [ ] Transaction form
  - [ ] Basic layout

---

## 📊 Suivi de progression

### Tableau de bord du projet

Créer un fichier `PROGRESS.md` à la racine:

```markdown
# Progression Fusion FinCouple Pro

## Phase 1: Fondations (Mois 1)
- [x] Setup repository
- [x] Docker Compose
- [x] API skeleton
- [ ] Auth complète (75%)
- [ ] CRUD transactions (50%)

## Phase 2: Core (Mois 2-3)
- [ ] Import CSV (0%)
- [ ] Catégories (0%)
- [ ] Dashboard (0%)

## Métriques
- Couverture tests: 45%
- Bugs ouverts: 12
- Features complétées: 8/35
```

### KPIs à tracker

| Métrique | Outil | Fréquence |
|----------|-------|-----------|
| Couverture tests | pytest-cov / Vitest | À chaque PR |
| Bugs | GitHub Issues | Continu |
| Performance | Lighthouse CI | Weekly |
| Temps build | GitHub Actions | À chaque push |

---

## 🐛 Debug & Support

### Commandes utiles

```bash
# Démarrer tout
docker-compose up

# Logs
docker-compose logs -f api
docker-compose logs -f web

# Reset DB
docker-compose down -v
rm -rf data/*.db
docker-compose up

# Tests
# Backend
cd api && pytest -v

# Frontend
cd apps/web && npm test

# E2E
cd apps/web && npx playwright test
```

### Points de contrôle

**Checklist quotidienne:**
- [ ] Tests passent
- [ ] Pas de régression sur features existantes
- [ ] Build réussit
- [ ] Pas de secrets dans le code

**Checklist hebdomadaire:**
- [ ] Review code
- [ ] Mise à jour dépendances
- [ ] Backup données
- [ ] Documentation à jour

---

## 📚 Ressources

### Documentation à créer

1. `README.md` - Setup rapide
2. `CONTRIBUTING.md` - Guide contributeur
3. `API.md` - Documentation API (auto-générée)
4. `DEPLOYMENT.md` - Guide déploiement

### Liens externes

- [FastAPI Docs](https://fastapi.tiangolo.com)
- [React Query](https://tanstack.com/query/latest)
- [shadcn/ui](https://ui.shadcn.com)
- [Tailwind CSS](https://tailwindcss.com)

---

## 🎯 Prochaines étapes immédiates

### Si vous commencez maintenant:

1. **Lire** les 3 documents de planification
2. **Cloner** le repository existant:
   ```bash
   git clone /Users/aurelien/Documents/Projets/FinancePerso reference-financeperso
   git clone /Users/aurelien/Documents/Projets/FinancePerso/Ideas/couple-cashflow-clever-main reference-fincouple
   ```
3. **Créer** le nouveau repository
4. **Copier** les assets utiles:
   - FinancePerso: modules/ (logique métier)
   - FinCouple: src/components/ui/ (design system)
5. **Commencer** par l'API FastAPI + Auth

### Questions à résoudre avant M1:

1. **Monorepo tool**: pnpm workspaces vs Nx vs Turborepo ?
2. **Styling**: Tailwind pure ou avec CSS variables ?
3. **Forms**: React Hook Form + Zod ?
4. **Testing**: Vitest ou Jest ? Playwright ou Cypress ?
5. **Documentation**: Storybook pour composants ?

---

*Ready? Set. Go! 🚀*

*Dernière mise à jour: 2026-03-02*
