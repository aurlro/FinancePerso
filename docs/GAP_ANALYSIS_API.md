# 📋 Gap Analysis - Migration vers FastAPI

> Document généré le $(date) - Phase 1 de l'audit complet

---

## 🎯 Executive Summary

L'application FinancePerso est actuellement dans un état **"Frankenstein"** avec :
- **Backend FastAPI** : Partiellement implémenté (dashboard + transactions read-only)
- **Frontend React** : Mélange de MOCKS, appels Supabase directs, et appels API
- **Base de données** : SQLite (backend) + Supabase (frontend)

**Objectif** : Unifier tout vers FastAPI avec une base SQLite unique.

---

## 📊 Inventaire Backend (web/api/)

### ✅ Endpoints Implémentés

| Méthode | Endpoint | Status | Router |
|---------|----------|--------|--------|
| GET | `/api/health` | ✅ | main.py |
| GET | `/api` | ✅ | main.py |
| GET | `/api/dashboard/stats` | ✅ | dashboard.py |
| GET | `/api/dashboard/breakdown` | ✅ | dashboard.py |
| GET | `/api/dashboard/evolution` | ✅ | dashboard.py |
| GET | `/api/transactions` | ✅ | transactions.py |
| GET | `/api/transactions/{id}` | ✅ | transactions.py |

### ❌ Endpoints MANQUANTS ( critiques en rouge )

#### 🔴 Authentification (P0)
| Méthode | Endpoint | Description | Priorité |
|---------|----------|-------------|----------|
| POST | `/api/auth/register` | Créer compte utilisateur | P0 |
| POST | `/api/auth/login` | Connexion (JWT) | P0 |
| POST | `/api/auth/logout` | Déconnexion | P0 |
| GET | `/api/auth/me` | Profil utilisateur connecté | P0 |
| POST | `/api/auth/refresh` | Rafraîchir token JWT | P1 |

#### 🔴 Comptes Bancaires (P0)
| Méthode | Endpoint | Description | Priorité |
|---------|----------|-------------|----------|
| GET | `/api/accounts` | Lister les comptes | P0 |
| POST | `/api/accounts` | Créer un compte | P0 |
| GET | `/api/accounts/{id}` | Détail compte | P0 |
| PUT | `/api/accounts/{id}` | Modifier compte | P0 |
| DELETE | `/api/accounts/{id}` | Supprimer compte | P1 |
| GET | `/api/accounts/{id}/balance` | Solde du compte | P1 |

#### 🔴 Catégories (P0)
| Méthode | Endpoint | Description | Priorité |
|---------|----------|-------------|----------|
| GET | `/api/categories` | Lister catégories | P0 |
| POST | `/api/categories` | Créer catégorie | P0 |
| GET | `/api/categories/{id}` | Détail catégorie | P1 |
| PUT | `/api/categories/{id}` | Modifier catégorie | P1 |
| DELETE | `/api/categories/{id}` | Supprimer catégorie | P1 |

#### 🔴 Transactions (P0 - Complétion)
| Méthode | Endpoint | Description | Priorité |
|---------|----------|-------------|----------|
| POST | `/api/transactions` | Créer transaction | P0 |
| PUT | `/api/transactions/{id}` | Modifier transaction | P0 |
| DELETE | `/api/transactions/{id}` | Supprimer transaction | P1 |
| POST | `/api/transactions/import` | Import CSV | P0 |
| POST | `/api/transactions/categorize` | Catégorisation IA | P0 |
| POST | `/api/transactions/bulk-update` | Mise à jour massif | P1 |
| POST | `/api/transactions/{id}/validate` | Valider transaction | P1 |

#### 🟠 Règles (P1)
| Méthode | Endpoint | Description | Priorité |
|---------|----------|-------------|----------|
| GET | `/api/rules` | Lister règles catégorisation | P1 |
| POST | `/api/rules` | Créer règle | P1 |
| PUT | `/api/rules/{id}` | Modifier règle | P1 |
| DELETE | `/api/rules/{id}` | Supprimer règle | P1 |
| POST | `/api/rules/test` | Tester pattern regex | P1 |
| GET | `/api/attribution-rules` | Lister règles attribution | P1 |
| POST | `/api/attribution-rules` | Créer règle attribution | P1 |
| PUT | `/api/attribution-rules/{id}` | Modifier règle | P1 |
| DELETE | `/api/attribution-rules/{id}` | Supprimer règle | P1 |

#### 🟠 Foyer / Membres (P1)
| Méthode | Endpoint | Description | Priorité |
|---------|----------|-------------|----------|
| GET | `/api/household` | Infos foyer | P1 |
| PUT | `/api/household` | Modifier foyer | P1 |
| GET | `/api/household/members` | Lister membres | P1 |
| POST | `/api/household/members` | Ajouter membre | P1 |
| PUT | `/api/household/members/{id}` | Modifier membre | P1 |
| DELETE | `/api/household/members/{id}` | Supprimer membre | P1 |
| POST | `/api/household/invite` | Inviter membre | P2 |

#### 🟠 Budgets (P1)
| Méthode | Endpoint | Description | Priorité |
|---------|----------|-------------|----------|
| GET | `/api/budgets` | Lister budgets | P1 |
| POST | `/api/budgets` | Définir budget catégorie | P1 |
| GET | `/api/budgets/alerts` | Alertes dépassement | P2 |

#### 🟡 Analytics & IA (P2)
| Méthode | Endpoint | Description | Priorité |
|---------|----------|-------------|----------|
| GET | `/api/analytics/couple-balance` | Équilibre couple | P2 |
| GET | `/api/analytics/monthly-recap` | Bilan mensuel | P2 |
| GET | `/api/analytics/subscriptions` | Détection abonnements | P2 |
| POST | `/api/ai/categorize` | Catégorisation IA | P2 |
| POST | `/api/ai/attribute` | Attribution membre IA | P2 |

---

## 📦 Schémas Pydantic

### ✅ Schémas Existants (suffisants pour l'instant)

```python
# Dashboard
DashboardStatsResponse
DashboardBreakdownResponse  
DashboardEvolutionResponse
CategoryBreakdownItem

# Transactions
TransactionResponse
TransactionsListResponse
TransactionFilters

# Errors
ErrorResponse
HealthResponse
```

### ❌ Schémas à Créer

```python
# Auth
class UserRegisterRequest(BaseModel):
    email: str
    password: str
    name: str

class UserLoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    household_id: Optional[int]

# Accounts
class AccountCreateRequest(BaseModel):
    name: str
    bank_name: Optional[str]
    account_type: Literal["perso_a", "perso_b", "joint"]
    balance: float = 0.0

class AccountResponse(BaseModel):
    id: int
    name: str
    bank_name: Optional[str]
    account_type: str
    balance: float
    household_id: int
    created_at: str

# Categories
class CategoryCreateRequest(BaseModel):
    name: str
    emoji: str
    color: str
    type: Literal["income", "expense", "both"]
    budget_amount: Optional[float]

class CategoryResponse(BaseModel):
    id: int
    name: str
    emoji: str
    color: str
    type: str
    is_fixed: bool
    budget_amount: Optional[float]

# Rules
class RuleCreateRequest(BaseModel):
    name: str
    pattern: str
    pattern_type: Literal["contains", "regex", "exact", "starts_with", "ends_with"]
    category_id: int
    priority: int = 10

class RuleResponse(BaseModel):
    id: int
    name: str
    pattern: str
    pattern_type: str
    category_id: int
    category_name: str
    priority: int
    is_active: bool
    match_count: int

# Import
class ImportRequest(BaseModel):
    account_id: int
    transactions: List[TransactionImportItem]

class TransactionImportItem(BaseModel):
    date: str
    label: str
    amount: float
    category_id: Optional[int]

class ImportResponse(BaseModel):
    imported: int
    duplicates: int
    errors: List[str]
```

---

## 🎨 Inventaire Frontend - Hooks

### 🔴 Hooks MOCK (À migrer en priorité)

| Hook | Type | Endpoints actuels | Pages utilisatrices |
|------|------|-------------------|---------------------|
| useAuth | MOCK | Aucun | Auth, toutes les pages |
| useAccounts | MOCK | Aucun | Accounts, Import, Transactions, Onboarding |
| useCreateAccount | MOCK | Aucun | Accounts, Onboarding |
| useCategories | MOCK | Aucun | Analytics, Rules, Settings, Import |
| useRules | MOCK | Aucun | Rules, Import |
| useHousehold + membres | MOCK | Aucun | Settings, Onboarding |
| useBudgets | MOCK | Aucun | Analytics, MonthlyRecap |

### 🟢 Hooks SUPABASE (Fonctionnels - à migrer plus tard)

| Hook | Type | Endpoints Supabase | Pages utilisatrices |
|------|------|-------------------|---------------------|
| useCoupleBalance | SUPABASE | profiles, household_members, transactions | CoupleBalance |
| useAttributionRules | SUPABASE | attribution_rules | Rules, Import |
| useNotifications | SUPABASE | notifications (realtime) | Layout |
| useTransactionComments | SUPABASE | transaction_comments | Transactions |
| useSavingsGoals | SUPABASE | savings_goals | Dashboard |
| useForecast | SUPABASE | transactions, category_budgets | Dashboard |

### ✅ Hooks API (Déjà migrés)

| Hook | Type | Endpoints API | Pages utilisatrices |
|------|------|---------------|---------------------|
| useDashboardStats | API | GET /api/dashboard/stats | Index |
| useCategoryBreakdown | API | GET /api/dashboard/breakdown | Index |
| useMonthlyEvolution | API | GET /api/dashboard/evolution | Index |
| useTransactions (Api) | API | GET /api/transactions | Transactions |
| useUpdateTransaction (Api) | API | PUT /api/transactions/:id | Transactions |

---

## 🗺️ Cartographie Pages → API

| Page | Hooks utilisés | Statut | Action requise |
|------|----------------|--------|----------------|
| **Auth** | useAuth (MOCK) | 🔴 | Créer endpoints auth + migrer hook |
| **Accounts** | useAccounts (MOCK) + supabase direct | 🔴 | Créer endpoints accounts + migrer hook + supprimer supabase direct |
| **Transactions** | useTransactionsApi (API) ✅ + useAccounts (MOCK) + supabase direct (CRUD) | 🔴 | Migrer CRUD transactions vers API + supprimer supabase direct |
| **Import** | useAccounts (MOCK) + useCategories (MOCK) + useAttributionRules (SUPABASE) + supabase direct | 🔴 | Créer endpoint import CSV + migrer tous les hooks |
| **Rules** | useRules (MOCK) + useAttributionRules (SUPABASE) + supabase direct | 🟠 | Créer endpoints rules + migrer tous les hooks |
| **Analytics** | useBudgets (MOCK) + useCategories (MOCK) + supabase direct | 🟠 | Créer endpoints analytics + migrer hooks |
| **CoupleBalance** | useCoupleBalance (SUPABASE) | 🟡 | Créer endpoint couple-balance + migrer hook |
| **Settings** | useHousehold (MOCK) + useCategories (SUPABASE) + supabase direct | 🟠 | Créer endpoints household + migrer tous les hooks |
| **Index (Dashboard)** | useDashboardApi (API) ✅ + useOnboardingStatus (MOCK) | 🟡 | Garder API ✅ + migrer onboarding |

---

## 🚨 Problèmes Critiques Identifiés

### 1. **Duplication des hooks**
- `useTransactions` existe en MOCK et API (useTransactionsApi.ts)
- `useCreateCategory` existe en MOCK et SUPABASE (useCategoryManagement.tsx)
- Risque d'import accidentel de la mauvaise version

### 2. **Appels Supabase directs dans les pages**
Pages avec logique métier directement couplée à Supabase :
- **Transactions.tsx** : CRUD complet, pagination, filtres, Edge Functions IA
- **Import.tsx** : Import CSV avec détection de doublons et virements internes
- **Rules.tsx** : CRUD règles + application en masse
- **SettingsPage.tsx** : Suppression de données, mise à jour profil

### 3. **Données incohérentes**
- Les hooks MOCK retournent des données statiques
- Les hooks SUPABASE retournent des données réelles (mais pas la même source que le backend FastAPI)
- Les hooks API retournent des données de SQLite via FastAPI

### 4. **Edge Functions Supabase**
- `categorize-ai` : Appelé dans Transactions.tsx
- `attribute-ai` : Appelé dans Transactions.tsx
- **À migrer** : Vers endpoints FastAPI `/api/ai/categorize` et `/api/ai/attribute`

---

## 📋 Plan d'Action Détaillé (PRs)

### PR #1 : Foundation Auth (P0)
- [ ] Créer router `auth.py`
- [ ] Schémas : UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
- [ ] Endpoints : POST /auth/register, POST /auth/login, GET /auth/me
- [ ] JWT middleware
- [ ] Migrer useAuth.tsx vers API

### PR #2 : CRUD Accounts (P0)
- [ ] Créer router `accounts.py`
- [ ] Schémas : AccountCreateRequest, AccountResponse
- [ ] Endpoints : GET/POST/PUT/DELETE /accounts
- [ ] Migrer useAccounts.tsx vers API
- [ ] Corriger Accounts.tsx (supprimer supabase direct)

### PR #3 : CRUD Categories (P0)
- [ ] Créer router `categories.py`
- [ ] Schémas : CategoryCreateRequest, CategoryResponse
- [ ] Endpoints : GET/POST/PUT/DELETE /categories
- [ ] Migrer useCategories.tsx vers API
- [ ] Unifier avec useCategoryManagement.tsx

### PR #4 : Import CSV (P0)
- [ ] Créer endpoint POST /transactions/import
- [ ] Gestion des doublons (tx_hash)
- [ ] Détection des virements internes
- [ ] Application des règles de catégorisation
- [ ] Migrer logique Import.tsx vers backend

### PR #5 : CRUD Transactions (P0)
- [ ] Complérouter `transactions.py`
- [ ] Endpoints : POST /transactions, PUT /transactions/:id, DELETE /transactions/:id
- [ ] Endpoint POST /transactions/bulk-update
- [ ] Migrer Transactions.tsx vers API (supprimer supabase direct)

### PR #6 : Règles de catégorisation (P1)
- [ ] Créer router `rules.py`
- [ ] Schémas : RuleCreateRequest, RuleResponse
- [ ] Endpoints : GET/POST/PUT/DELETE /rules
- [ ] Endpoint POST /rules/test
- [ ] Migrer useRules.tsx vers API

### PR #7 : Règles d'attribution (P1)
- [ ] Ajouter à `rules.py`
- [ ] Endpoints : GET/POST/PUT/DELETE /attribution-rules
- [ ] Migrer useAttributionRules.tsx vers API

### PR #8 : Foyer et membres (P1)
- [ ] Créer router `household.py`
- [ ] Endpoints : GET/PUT /household, GET/POST/PUT/DELETE /household/members
- [ ] Migrer useHousehold.tsx vers API

### PR #9 : Budgets (P1)
- [ ] Créer router `budgets.py`
- [ ] Endpoints : GET/POST /budgets
- [ ] Migrer useBudgets.tsx vers API

### PR #10 : Analytics & IA (P2)
- [ ] Endpoint GET /analytics/couple-balance
- [ ] Endpoint GET /analytics/monthly-recap
- [ ] Endpoints POST /ai/categorize et /ai/attribute
- [ ] Migrer useCoupleBalance, useForecast vers API

---

## 📝 Conclusion

### Métriques
- **Endpoints existants** : 7
- **Endpoints manquants** : 40+
- **Hooks MOCK à migrer** : 9
- **Hooks SUPABASE à migrer** : 7
- **Pages à corriger** : 10

### Estimation
- **PR #1-5 (P0)** : 2-3 semaines (fonctionnalités critiques)
- **PR #6-9 (P1)** : 1-2 semaines (fonctionnalités importantes)
- **PR #10 (P2)** : 1 semaine (features avancées)

**Total estimé** : 4-6 semaines pour une migration complète et stable.

### Prochaine étape recommandée
Commencer par **PR #1 (Auth)** car c'est la fondation de tout le reste, puis **PR #2 (Accounts)** car c'est une dépendance de l'onboarding.
