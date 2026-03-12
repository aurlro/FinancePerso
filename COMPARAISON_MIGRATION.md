# 📊 Comparaison v5.6 Streamlit vs FinCouple React

## Vue d'ensemble

| Aspect | v5.6 Streamlit | FinCouple React |
|--------|---------------|-----------------|
| **Lignes de code** | ~28 000 (Python) | ~4 000 (TS/TSX) |
| **Fichiers** | 287 fichiers .py | 81 fichiers .ts/.tsx |
| **Architecture** | Monolithique | Modulaire SPA |
| **Base de données** | SQLite locale | Supabase (cloud) |
| **Authentification** | Session locale | Supabase Auth |
| **UI** | Widgets Streamlit | React + shadcn/ui |
| **State Management** | st.session_state | TanStack Query + Zustand |
| **Tests** | 33 tests pytest | Vitest (setup minimal) |
| **Mobile** | Responsive basique | Mobile-first |

---

## 📁 Structure comparée

### v5.6 Streamlit (BASE)
```
FinancePerso/
├── app.py                      # Point d'entrée
├── app_v5_5.py                 # Version light
├── pages/                      # 14 pages Streamlit
│   ├── 01_Import.py
│   ├── 02_Dashboard.py
│   ├── 03_Intelligence.py
│   ├── 04_Budgets.py
│   ├── 05_Audit.py
│   ├── 06_Assistant.py
│   ├── 07_Recherche.py
│   ├── 08_Configuration.py
│   ├── 09_Badges.py
│   ├── 10_Projections.py
│   ├── 11_Abonnements.py
│   ├── 12_Patrimoine.py
│   ├── 13_Nouveautes.py
│   └── 14_Notifications.py
├── modules/                    # 287 fichiers Python
│   ├── db/                     # Couche données SQLite
│   │   ├── connection.py
│   │   ├── transactions.py
│   │   ├── categories.py
│   │   ├── rules.py
│   │   └── migrations.py
│   ├── ai/                     # Suite IA
│   │   ├── anomaly_detector.py
│   │   ├── budget_predictor.py
│   │   └── categorization_ai.py
│   ├── couple/                 # Gestion couple
│   │   └── cross_validation.py
│   ├── export/                 # Export PDF
│   │   └── pdf_exporter.py
│   ├── open_banking/           # Import bancaire
│   │   ├── client.py
│   │   ├── providers.py
│   │   └── sync.py
│   ├── ui/                     # Composants UI
│   │   ├── components/
│   │   └── v5_5/
│   ├── categorization.py       # Logique catégorisation
│   ├── ingestion.py            # Import CSV
│   └── ...
└── Data/finance.db             # SQLite (940KB, 471 tx)
```

### FinCouple React (CIBLE)
```
Ideas/couple-cashflow-clever-main/
├── src/
│   ├── pages/                  # 8 pages React
│   │   ├── Index.tsx           # Dashboard
│   │   ├── Transactions.tsx
│   │   ├── Import.tsx
│   │   ├── Accounts.tsx
│   │   ├── Rules.tsx
│   │   ├── SettingsPage.tsx
│   │   ├── Auth.tsx
│   │   └── NotFound.tsx
│   ├── components/
│   │   ├── AppLayout.tsx
│   │   ├── AppSidebar.tsx
│   │   ├── ThemeProvider.tsx
│   │   └── ui/                 # 35 composants shadcn
│   ├── hooks/                  # 9 hooks métier
│   │   ├── useAuth.tsx
│   │   ├── useDashboard.tsx
│   │   ├── useAccounts.tsx
│   │   ├── useCategories.tsx
│   │   ├── useRules.tsx
│   │   └── useHousehold.tsx
│   ├── integrations/
│   │   └── supabase/           # À remplacer
│   │       ├── client.ts
│   │       └── types.ts
│   └── lib/
│       ├── csv-parser.ts       # Parsing CSV
│       └── categorization-engine.ts
```

---

## 🔧 Features comparées

### ✅ Dans les deux projets

| Feature | v5.6 | FinCouple | Commentaire |
|---------|------|-----------|-------------|
| Import CSV | ✅ | ✅ | Les deux ont parsing + mapping |
| Catégorisation auto | ✅ | ✅ | Moteur regex dans les deux |
| Dashboard avec charts | ✅ | ✅ | Recharts (React) vs Plotly (Python) |
| Gestion comptes | ✅ | ✅ | Types perso/joint |
| Gestion catégories | ✅ | ✅ | Couleurs + icônes |
| Règles regex | ✅ | ✅ | CRUD + testeur |
| Détection virements | ✅ | ✅ | Algorithme similaire |
| Dark/Light mode | ✅ | ✅ | Native dans les deux |

### ✅ Uniquement dans v5.6 (à porter)

| Feature | Fichier source | Priorité |
|---------|---------------|----------|
| **Budgets dynamiques** | `modules/budgets_dynamic.py` | 🔴 Haute |
| **Audit transactions** | `pages/05_Audit.py` | 🟡 Moyenne |
| **Assistant IA** | `pages/06_Assistant.py` + `modules/ai/` | 🟡 Moyenne |
| **Recherche globale** | `pages/07_Recherche.py` | 🟢 Basse |
| **Gamification** | `pages/09_Badges.py` + `modules/gamification/` | 🟢 Basse |
| **Projections** | `pages/10_Projections.py` + `modules/cashflow/` | 🟡 Moyenne |
| **Abonnements** | `pages/11_Abonnements.py` | 🟡 Moyenne |
| **Suivi patrimoine** | `pages/12_Patrimoine.py` + `modules/wealth/` | 🟡 Moyenne |
| **Validation croisée** | `modules/couple/cross_validation.py` | 🔴 Haute |
| **Export PDF** | `modules/export/pdf_exporter.py` | 🟡 Moyenne |
| **Open Banking** | `modules/open_banking/` | 🟢 Basse |
| **Notifications V3** | `modules/notifications/` | 🟡 Moyenne |
| **Détection anomalies** | `modules/ai/anomaly_detector.py` | 🟢 Basse |
| **Prédiction budgets** | `modules/ai/budget_predictor.py` | 🟢 Basse |

### ✅ Uniquement dans FinCouple (à garder)

| Feature | Fichier | Intérêt |
|---------|---------|---------|
| Système foyer/invitations | `useHousehold.tsx` | 🔴 Haute - gestion couple |
| Auth complète | `useAuth.tsx` + `Auth.tsx` | 🔴 Haute - à adapter |
| UI moderne shadcn | `components/ui/` | 🔴 Haute - 35 composants |
| Mobile-first | Responsive natif | 🔴 Haute |
| Formulaires Zod | Validation type-safe | 🟡 Moyenne |
| TanStack Query | Cache + sync | 🟡 Moyenne |

---

## 🗄️ Schéma de données

### Tables v5.6 (SQLite)
```sql
-- Tables principales
transactions (id, date, label, amount, category, account, 
            status, member, beneficiary, notes, tx_hash)
categories (id, name, emoji, is_fixed)
members (id, name, member_type)
accounts (id, name, account_type)
budgets (category, amount, period)
rules (pattern, category, priority)
-- + tables annexes (notifications, gamification...)
```

### Tables FinCouple (Supabase → à migrer)
```sql
-- Tables actuelles (Supabase)
profiles (id, display_name, household_id, role)
households (id, name, created_at)
household_invitations (id, household_id, invited_email, status)
bank_accounts (id, name, bank_name, account_type, household_id)
categories (id, name, color, is_default, household_id)
categorization_rules (id, name, regex_pattern, category_id, priority, household_id)
transactions (id, date, label, amount, bank_account_id, category_id, import_hash)

-- Tables manquantes (dans v5.6)
budgets
notifications
gamification
analytics
```

---

## 🎯 Gaps identifiés

### 1. Backend (CRITIQUE)
- **v5.6** : Python + SQLite, tout en local
- **FinCouple** : Supabase (cloud), dépendance externe
- **Action** : Remplacer Supabase par API Python locale

### 2. Auth (CRITIQUE)
- **v5.6** : Session simple, mono-utilisateur
- **FinCouple** : Supabase Auth, multi-utilisateurs avec foyer
- **Action** : Implémenter auth locale (JWT ou session)

### 3. Données (CRITIQUE)
- **v5.6** : 471 transactions, catégories custom
- **FinCouple** : Schéma différent, pas de migration
- **Action** : Script de migration SQLite → nouveau schéma

### 4. Features métier (MOYEN)
- **v5.6** : Budgets, audit, assistant IA, projections...
- **FinCouple** : Base import/dashboard uniquement
- **Action** : Porter les features une par une

### 5. IA (MOYEN)
- **v5.6** : Détection anomalies, prédiction budgets, catégorisation IA
- **FinCouple** : Catégorisation regex uniquement
- **Action** : Intégrer API KIM pour remplacer

---

## 📊 Matrice de migration

| Feature | Complexité | Priorité | Effort estimé |
|---------|-----------|----------|---------------|
| Setup API Python locale | 🟢 Facile | 🔴 Critique | 1 jour |
| Schéma DB SQLite | 🟢 Facile | 🔴 Critique | 1 jour |
| Auth locale | 🟡 Moyen | 🔴 Critique | 2 jours |
| Migration données | 🟡 Moyen | 🔴 Critique | 1 jour |
| CRUD transactions | 🟢 Facile | 🔴 Critique | 1 jour |
| Import CSV | 🟡 Moyen | 🔴 Critique | 2 jours |
| Dashboard | 🟢 Facile | 🔴 Critique | 1 jour |
| Catégorisation | 🟡 Moyen | 🟡 Haute | 2 jours |
| Budgets | 🟡 Moyen | 🟡 Haute | 2 jours |
| Validation croisée | 🟡 Moyen | 🟡 Haute | 2 jours |
| Export PDF | 🟢 Facile | 🟢 Basse | 1 jour |
| Assistant IA (KIM) | 🟡 Moyen | 🟡 Haute | 3 jours |
| Audit | 🔴 Complexe | 🟢 Basse | 3 jours |
| Projections | 🔴 Complexe | 🟢 Basse | 3 jours |
| Gamification | 🔴 Complexe | 🟢 Basse | 4 jours |

**Total estimé** : 3-4 semaines pour core fonctionnel, 6-8 semaines pour tout porter.

---

## 💡 Recommandations

### Option A : Migration complète (6-8 semaines)
Porter toutes les features de v5.6 vers FinCouple React + API locale.

### Option B : Core d'abord (3-4 semaines) ⭐ RECOMMANDÉ
1. Dashboard + Import CSV + Transactions
2. Catégories + Règles
3. Budgets basiques
4. Puis itérer sur le reste

### Option C : Hybrid (2-3 semaines)
Garder v5.6 pour features avancées, React pour usage quotidien.

---

*Document généré le : Mars 2026*
*Source : Analyse comparative v5.6 Streamlit vs FinCouple React*
