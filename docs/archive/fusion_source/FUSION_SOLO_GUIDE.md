# 🚀 Guide Global - FinCouple Pro (Solo Project)

> Version simplifiée pour développeur solo - 6-9 mois

---

## 📋 Vue d'ensemble

### Philosophie "Solo Dev"

```
┌─────────────────────────────────────────────────────────────────┐
│  PRINCIPES POUR 1 DÉVELOPPEUR                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ FAIRE                                                       │
│  • Stack simple et mature (pas de cutting edge)                │
│  • Réutiliser maximum de code existant                         │
│  • Features essentielles d'abord (P0)                          │
│  • Tests automatisés critiques seulement                       │
│  • Documentation au fur et à mesure                            │
│                                                                 │
│  ❌ ÉVITER                                                      │
│  • Microservices / architecture complexe                       │
│  • Réécriture totale                                           │
│  • Feature parity 100% dès le début                            │
│  • Tests E2E complexes                                         │
│  • Multi-cloud / multi-region                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture simplifiée

```
┌─────────────────────────────────────────────────────────────────┐
│  ARCHITECTURE "KEEP IT SIMPLE"                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────┐                                    │
│  │   REACT + VITE          │  ← Front unique                    │
│  │   • Dashboard           │                                    │
│  │   • Transactions        │                                    │
│  │   • Import CSV          │                                    │
│  │   • Budgets             │                                    │
│  │   • Assistant IA        │  ← Intégré ici                     │
│  │   • Admin simplifié     │  ← Pas de Streamlit séparé         │
│  └───────────┬─────────────┘                                    │
│              │ HTTP (REST)                                       │
│              ▼                                                   │
│  ┌─────────────────────────┐                                    │
│  │   FASTAPI               │  ← Backend simple                  │
│  │   • API REST            │                                    │
│  │   • Logique métier      │  ← Importé depuis FinancePerso     │
│  │   • IA (cascade)        │                                    │
│  │   • Auth JWT            │                                    │
│  └───────────┬─────────────┘                                    │
│              │                                                   │
│              ▼                                                   │
│  ┌─────────────────────────┐                                    │
│  │   SQLITE (local)        │  ← Même fichier que FinancePerso   │
│  │   • Schema compatible   │    (migration facile)              │
│  │   • Backup auto         │                                    │
│  └─────────────────────────┘                                    │
│                                                                 │
│  📱 PWA : Service worker pour offline basique                   │
│  ☁️ Sync cloud : Post-MVP (optionnel)                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Scope réduit (réaliste solo)

### Phases simplifiées (6-9 mois)

```
PHASE 1: M1-M2 (2 mois) - "Ça marche"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Setup React + FastAPI + DB
✅ Auth (JWT simple)
✅ CRUD Transactions
✅ Import CSV (depuis FinancePerso)
✅ Catégories basiques
✅ Dashboard simple (4 KPIs + graph)

PHASE 2: M3-M4 (2 mois) - "Utile au quotidien"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Catégorisation IA (copier depuis FinancePerso)
✅ Validation batch
✅ Budgets simples
✅ Multi-comptes (perso/joint)
✅ Vue couple basique

PHASE 3: M5-M6 (2 mois) - "Intelligent"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Assistant IA (chat intégré React)
✅ Projections simples (pas Monte Carlo)
✅ Détection abonnements
✅ Streaks + badges essentiels

PHASE 4: M7-M9 (3 mois) - "Polish"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ PWA / Mobile
✅ Dark mode
✅ Optimisations
✅ Migration données
✅ Documentation
```

### Features P0 (indispensables)

| Feature | Complexité | Source principale |
|---------|------------|-------------------|
| Import CSV | ⭐⭐ | FinCouple (UI) + FinancePerso (logique) |
| Dashboard | ⭐⭐⭐ | FinCouple (design) |
| Transactions CRUD | ⭐⭐ | FinCouple |
| Catégories | ⭐ | FinCouple |
| Auth JWT | ⭐⭐ | Nouveau |
| Catégorisation IA | ⭐⭐⭐ | FinancePerso (à porter) |
| Budgets | ⭐⭐⭐ | FinancePerso (simplifié) |

### Features P1 (importantes mais pas bloquantes)

| Feature | Complexité | Quand ? |
|---------|------------|---------|
| Assistant IA | ⭐⭐⭐ | Phase 3 |
| Projections | ⭐⭐⭐ | Phase 3 (simples) |
| Gamification | ⭐⭐ | Phase 3 (streaks + 5 badges) |
| Gestion couple avancée | ⭐⭐⭐ | Phase 2 (basique) |

### Features P2 (post-MVP)

- Sync cloud
- Monte Carlo complet
- Gestion prêts entre conjoints
- Admin complexe
- Analytics avancées

---

## 🏗️ Stack technique finale

### Frontend

```typescript
// Stack choisi (mature, bien documenté)
{
  "framework": "React 18",
  "build": "Vite",
  "language": "TypeScript",
  "styling": "Tailwind CSS",
  "components": "shadcn/ui",
  "state": "React Query + Zustand (simple)",
  "forms": "React Hook Form + Zod",
  "charts": "Recharts",
  "icons": "Lucide React",
  "http": "Axios",
  "notifications": "Sonner (toasts)"
}
```

### Backend

```python
# Stack choisi
{
    "framework": "FastAPI",
    "orm": "SQLAlchemy 2.0",
    "migrations": "Alembic",
    "auth": "python-jose + passlib",
    "db": "SQLite (aiosqlite async)",
    "ml": "scikit-learn (optionnel)",
    "validation": "Pydantic v2"
}
```

### Pourquoi pas Streamlit séparé ?

```
Avantages d'intégrer l'admin dans React (solo dev):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 1 codebase à maintenir (pas 2)
✅ Pas de context switching
✅ Partage des composants
✅ Déploiement plus simple
✅ Moins de bugs d'intégration

Où mettre les features "admin" ?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Page "Configuration" dans React
• Section "Audit" accessible si isAdmin
• Projections : onglet dans Dashboard
```

---

## 📁 Structure projet (simplifiée)

```
fincouple-pro/
├── 📁 frontend/                    # React app
│   ├── src/
│   │   ├── 📁 components/
│   │   │   └── ui/                # shadcn components
│   │   │
│   │   ├── 📁 features/           # Par domaine
│   │   │   ├── auth/
│   │   │   │   ├── LoginPage.tsx
│   │   │   │   ├── RegisterPage.tsx
│   │   │   │   └── useAuth.ts
│   │   │   │
│   │   │   ├── dashboard/
│   │   │   │   ├── DashboardPage.tsx
│   │   │   │   ├── KpiCards.tsx
│   │   │   │   ├── Charts.tsx
│   │   │   │   └── useDashboard.ts
│   │   │   │
│   │   │   ├── transactions/
│   │   │   │   ├── TransactionList.tsx
│   │   │   │   ├── TransactionForm.tsx
│   │   │   │   ├── ImportWizard.tsx
│   │   │   │   └── useTransactions.ts
│   │   │   │
│   │   │   ├── budgets/
│   │   │   │   └── BudgetsPage.tsx
│   │   │   │
│   │   │   ├── couple/
│   │   │   │   └── CoupleView.tsx
│   │   │   │
│   │   │   └── ai/
│   │   │       ├── ChatAssistant.tsx
│   │   │       └── useAI.ts
│   │   │
│   │   ├── 📁 lib/
│   │   │   ├── api.ts            # Axios config
│   │   │   └── utils.ts
│   │   │
│   │   ├── App.tsx
│   │   └── main.tsx
│   │
│   ├── package.json
│   └── vite.config.ts
│
├── 📁 backend/                     # FastAPI app
│   ├── 📁 app/
│   │   ├── 📁 api/
│   │   │   ├── 📁 routes/
│   │   │   │   ├── auth.py
│   │   │   │   ├── transactions.py
│   │   │   │   ├── categories.py
│   │   │   │   ├── budgets.py
│   │   │   │   └── ai.py
│   │   │   └── deps.py           # Dépendances (DB, auth)
│   │   │
│   │   ├── 📁 core/
│   │   │   ├── config.py         # Settings
│   │   │   └── security.py       # JWT, passwords
│   │   │
│   │   ├── 📁 models/
│   │   │   ├── user.py
│   │   │   ├── transaction.py
│   │   │   └── category.py
│   │   │
│   │   ├── 📁 services/
│   │   │   ├── 📁 ai/            # COPIÉ depuis FinancePerso
│   │   │   │   ├── categorizer.py
│   │   │   │   └── rules_engine.py
│   │   │   ├── categorization.py
│   │   │   └── budgets.py
│   │   │
│   │   ├── 📁 db/
│   │   │   ├── session.py
│   │   │   └── base.py
│   │   │
│   │   └── main.py
│   │
│   ├── 📁 migrations/            # Alembic
│   ├── requirements.txt
│   └── Dockerfile
│
├── 📁 data/                      # SQLite + backups
│   └── .gitkeep
│
├── docker-compose.yml            # Dev uniquement
├── Makefile                      # Commandes rapides
└── README.md
```

---

## 🚀 Plan d'action détaillé (par semaine)

### PHASE 1: Fondations (Semaines 1-8)

#### Semaine 1: Setup minimal
**Objectif**: Avoir un "Hello World" qui fonctionne

```bash
# Jour 1-2: Setup projet
git init fincouple-pro
cd fincouple-pro

# Structure
mkdir -p frontend backend/app/{api/{routes,deps},core,models,services/ai,db}

# Backend minimal
cd backend
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn sqlalchemy alembic pydantic python-jose[cryptography] passlib[bcrypt] python-multipart aiosqlite

# Créer main.py minimal
# Créer requirements.txt
```

```python
# backend/app/main.py (minimal)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FinCouple Pro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

```bash
# Jour 3-4: Frontend minimal
cd ../frontend
npm create vite@latest . -- --template react-ts
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# shadcn
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card input
```

```bash
# Jour 5: Docker Compose
cd ..
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite:///app/data/fincouple.db
  
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
EOF
```

**Validation S1**: `docker-compose up` → API répond + React s'affiche

---

#### Semaine 2: Database & Models
**Objectif**: Schema DB compatible FinancePerso

```bash
# Init Alembic
cd backend
alembic init migrations
```

**Copier depuis FinancePerso**:
- `modules/db/migrations.py` → `backend/migrations/versions/001_initial.py`
- Simplifier (enlever tables non-essentielles)

Tables essentielles:
- `users` (auth JWT)
- `categories`
- `accounts`
- `transactions`
- `categorization_rules`
- `budgets`
- `user_streaks` (gamification simplifiée)

**Validation S2**: Migrations passent, DB créée

---

#### Semaine 3: Authentication
**Objectif**: Login/Register fonctionnels

Backend:
```python
# routes/auth.py
@router.post("/register")
async def register(user: UserCreate):
    # Hash password, create user
    pass

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Verify, create JWT
    pass
```

Frontend:
```tsx
// features/auth/LoginPage.tsx
// Formulaire avec React Hook Form
// Stockage token dans localStorage (simple) ou httpOnly cookie
```

**Validation S3**: Peux créer compte et me connecter

---

#### Semaine 4: CRUD Transactions
**Objectif**: Voir/ajouter/modifier/supprimer transactions

Backend:
- GET /transactions (avec pagination)
- POST /transactions
- PUT /transactions/{id}
- DELETE /transactions/{id}

Frontend:
- Page Transactions avec tableau
- Modal formulaire
- Delete avec confirmation

**Validation S4**: CRUD complet fonctionnel

---

#### Semaine 5: Import CSV (Partie 1)
**Objectif**: Parser CSV côté frontend

Copier depuis FinCouple:
- `src/lib/csv-parser.ts` → `frontend/src/lib/csvParser.ts`

Features:
- Upload fichier
- Détection headers
- Mapping colonnes (date, libellé, montant)
- Preview 10 lignes

**Validation S5**: Peux uploader CSV et voir preview

---

#### Semaine 6: Import CSV (Partie 2)
**Objectif**: Envoyer au backend et insérer en DB

Backend:
- POST /transactions/import
- Batch insert avec déduplication (hash)
- Retourner stats (imported, duplicates, errors)

Frontend:
- Wizard complet (Upload → Mapping → Preview → Import)
- Progress indicator
- Toast de succès

**Validation S6**: Import 100 transactions réussi

---

#### Semaine 7: Dashboard (Partie 1)
**Objectif**: 4 KPIs + données réelles

Backend:
- GET /dashboard/stats?month=2026-03
- Calculs: revenus, dépenses, reste à vivre, épargne

Frontend:
- 4 cards avec KPIs
- Sélecteur de mois
- Loading states

**Validation S7**: Dashboard affiche données réelles

---

#### Semaine 8: Dashboard (Partie 2)
**Objectif**: Graphiques

Frontend:
- Donut: Répartition par catégorie
- Line: Évolution sur 6 mois
- Table: Transactions récentes

Bibliothèque: Recharts (simple, React-friendly)

**Validation S8**: Dashboard complet et joli

---

### PHASE 2: Intelligence (Semaines 9-16)

#### Semaine 9: Catégories & Règles
**Objectif**: Gérer catégories et règles de catégorisation

Backend:
- CRUD categories
- CRUD rules (regex)

Frontend:
- Page Settings > Catégories
- Page Settings > Règles

**Validation S9**: Peux créer règles regex

---

#### Semaine 10: Catégorisation automatique (Partie 1)
**Objectif**: Portage depuis FinancePerso

**Copier et adapter**:
- `modules/categorization_cascade.py` → `backend/app/services/categorization.py`
- Simplifier si nécessaire

Logique cascade:
1. Règles exactes
2. Règles regex
3. Catégorie par défaut

**Validation S10**: Endpoint POST /ai/categorize fonctionne

---

#### Semaine 11: Catégorisation automatique (Partie 2)
**Objectif**: Intégration Import + Validation batch

Import:
- Auto-catégoriser pendant l'import
- Stats dans le retour

Validation batch:
- Sélection multiple
- "Valider et appliquer catégorie"

**Validation S11**: Import 100 tx → 80% catégorisées auto

---

#### Semaine 12: Multi-comptes
**Objectif**: Gérer perso/joint

Backend:
- Champ `account_type` (personal_a, personal_b, joint)
- Filtres sur transactions

Frontend:
- Sélecteur de compte
- Vue "Couple" (comparatif)

**Validation S12**: Peux filtrer par compte

---

#### Semaine 13: Budgets (Partie 1)
**Objectif**: CRUD budgets

Backend:
- CRUD budgets
- Calcul "dépensé vs budget"

Frontend:
- Page Budgets
- Barres de progression

**Validation S13**: Budgets créés et visibles

---

#### Semaine 14: Budgets (Partie 2)
**Objectif**: Alertes et prédictions simples

Backend:
- Alertes si > 80% du budget
- Prédiction fin de mois (simple)

Frontend:
- Alertes dans dashboard
- Indicateurs visuels

**Validation S14**: Alerte quand approche limite

---

#### Semaine 15: Assistant IA (Partie 1)
**Objectif**: Chat basique

Backend:
- POST /ai/chat
- Prompt engineering simple
- Contexte: transactions récentes

Frontend:
- Widget chat flottant
- Messages utilisateur/bot

**Validation S15**: Peux poser questions sur mes finances

---

#### Semaine 16: Assistant IA (Partie 2)
**Objectif**: Suggestions contextuelles

Backend:
- GET /ai/suggestions
- "Vous avez dépensé X en restauration ce mois"
- Suggestions catégorisation

Frontend:
- Cards suggestions dans dashboard

**Validation S16**: Suggestions pertinentes affichées

---

### PHASE 3: Polish (Semaines 17-26)

#### Semaine 17: Gamification (simplifiée)
**Objectif**: Streaks + 5 badges essentiels

Badges:
- "Premier pas" (première transaction)
- "Semaine parfaite" (7 jours connexion)
- "Importeur" (100 transactions)
- "Organisé" (100% transactions catégorisées)
- "Économe" (épargne > objectif)

Backend:
- Table `user_streaks`
- Logique détection badges

Frontend:
- Widget streak dans header
- Page badges

**Validation S17**: Badge débloqué et affiché

---

#### Semaine 18: Projections simples
**Objectif**: Calcul basé règle de 3

Pas de Monte Carlo complexe!

Backend:
- GET /projections/simple
- Si épargne X/mois → objectif atteint en Y mois
- Scénarios simples ("et si +100€/mois ?")

Frontend:
- Simulateur simple
- Graphique projection lineaire

**Validation S18**: Projection affichée

---

#### Semaine 19-20: PWA & Mobile
**Objectif**: Fonctionne bien sur mobile

- Responsive (déjà avec Tailwind)
- PWA: service worker, manifest
- Touch-friendly (boutons + grands)
- Offline basique (cache données)

**Validation S20**: Ajouté sur écran d'accueil iOS/Android

---

#### Semaine 21-22: Dark mode & Polish UI
**Objectif**: Joli dans tous les cas

- Dark mode toggle
- Animations (Framer Motion)
- Loading states
- Empty states
- Error boundaries

**Validation S22**: Lighthouse score > 80

---

#### Semaine 23-24: Migration données
**Objectif**: Migrer depuis FinancePerso

Script:
```bash
python scripts/migrate.py --from Data/finance.db --to data/fincouple.db
```

Process:
1. Export FinancePerso
2. Transform schéma si besoin
3. Import nouveau
4. Vérification

**Validation S24**: Mes données migrées et complètes

---

#### Semaine 25: Tests & Documentation
**Objectif**: Solide et documenté

Tests:
- Tests unitaires backend (pytest)
- Tests composants critiques (Vitest)
- 1-2 tests E2E (Playwright) : login + import

Documentation:
- README (setup, usage)
- Guide utilisateur (basique)
- Changelog

**Validation S25**: Tests passent, README clair

---

#### Semaine 26: Release
**Objectif**: Prêt pour usage quotidien

- Tag v1.0
- Backup FinancePerso
- Switch quotidien sur nouveau
- Monitoring (Sentry gratuit)

**Validation S26**: Je l'utilise quotidiennement

---

## 🛠️ Outils & Scripts

### Makefile (à la racine)

```makefile
.PHONY: dev build test migrate

# Development
dev:
	docker-compose up

dev-backend:
	cd backend && source .venv/bin/activate && uvicorn app.main:app --reload

dev-frontend:
	cd frontend && npm run dev

# Database
migrate:
	cd backend && alembic revision --autogenerate -m "$(msg)"
	cd backend && alembic upgrade head

migrate-rollback:
	cd backend && alembic downgrade -1

# Testing
test-backend:
	cd backend && pytest

test-frontend:
	cd frontend && npm test

# Production
build:
	docker-compose -f docker-compose.prod.yml build

backup:
	cp data/fincouple.db data/backups/fincouple_$(shell date +%Y%m%d).db
```

### Commandes quotidiennes

```bash
# Démarrer
cd fincouple-pro
make dev

# Backup avant gros changement
make backup

# Tests rapides avant commit
make test-backend
make test-frontend

# Nouvelle migration après modif models
make migrate msg="add_user_preferences"
```

---

## ⚡ Tips Solo Dev

### Productivité

1. **Timeboxing**: 2h par feature max, puis ship it
2. **No perfection**: "Good enough" > "Perfect but late"
3. **Reutilisation**: Copier-coller depuis FinancePerso est OK
4. **Tests ciblés**: Tester uniquement ce qui casse souvent
5. **Docs minimales**: Commentaires dans code suffisent souvent

### Éviter la fatigue

1. **1 feature à la fois**: Pas de multitâche
2. **Commits fréquents**: Même incomplets
3. **Backup auto**: Git + Time Machine
4. **Pauses**: 5min toutes les heures
5. **Célébrer**: Tag chaque milestone

### Quand bloquer

**Pas bloquer plus de 2h sur:**
- Bug étrange → Simplifier l'approche
- Feature complexe → Réduire le scope
- Choix technique → Prendre le plus simple

---

## 📊 Checkpoints (Go/No-Go)

| Date | Checkpoint | Critère | Action si échec |
|------|------------|---------|-----------------|
| Fin S4 | Auth + CRUD | Peux créer compte et ajouter transaction | Simplifier auth |
| Fin S8 | Dashboard | Voir mes finances en un coup d'œil | Réduire KPIs |
| Fin S11 | Import IA | Import 100 tx, 70% catégorisées | Améliorer rules |
| Fin S16 | Intelligence | Assistant répond questions | Simplifier prompts |
| Fin S22 | Mobile | Utilisable sur téléphone | Focus desktop |
| Fin S26 | Release | Je l'utilise quotidiennement | Reporter features |

---

## 🎉 Définition de succès

### MVP Réussi si:
- [ ] Je peux importer mes relevés bancaires
- [ ] Les transactions sont auto-catégorisées
- [ ] Je vois mon reste à vivre en 1 seconde
- [ ] Ça marche sur mon téléphone
- [ ] C'est plus agréable que FinancePerso actuel

### v1.0 Réussi si:
- [ ] Je l'utilise quotidiennement depuis 1 mois
- [ ] Aucune régression vs FinancePerso
- [ ] Au moins 1 feature nouvelle utilisée (assistant/budgets)

---

**Ready to start?** → Commencer Semaine 1

*Ce guide est un contrat avec toi-même: scope réduit, livrable régulier, pas de perfectionnisme.*

---

*Dernière mise à jour: 2026-03-02*  
*Version: Solo Dev 1.0*
