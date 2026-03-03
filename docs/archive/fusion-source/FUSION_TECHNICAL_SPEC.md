# 🔧 Spécification Technique - Fusion FinCouple Pro

> Document technique détaillé pour l'implémentation

---

## 1. API Specification (FastAPI)

### 1.1 Structure des endpoints

```
/api/v1/
├── /auth
│   ├── POST /login
│   ├── POST /register
│   ├── POST /refresh
│   └── POST /logout
│
├── /transactions
│   ├── GET    /              # Liste (paginée)
│   ├── GET    /{id}          # Détail
│   ├── POST   /              # Créer
│   ├── PUT    /{id}          # Modifier
│   ├── DELETE /{id}          # Supprimer
│   ├── POST   /batch         # Validation batch
│   ├── POST   /import        # Import CSV
│   └── GET    /stats         # Statistiques
│
├── /categories
│   ├── GET    /
│   ├── POST   /
│   ├── PUT    /{id}
│   └── DELETE /{id}
│
├── /accounts
│   ├── GET    /
│   ├── POST   /
│   └── PUT    /{id}
│
├── /budgets
│   ├── GET    /
│   ├── POST   /
│   ├── GET    /status        # État actuel vs budget
│   └── GET    /predictions   # Prédictions ML
│
├── /couple
│   ├── GET    /summary       # Résumé couple
│   ├── GET    /loans         # Prêts en cours
│   └── POST   /loans         # Nouveau prêt
│
├── /ai
│   ├── POST   /categorize    # Catégoriser une transaction
│   ├── POST   /categorize-batch
│   ├── GET    /suggestions   # Suggestions pour l'utilisateur
│   └── POST   /chat          # Assistant conversationnel
│
├── /wealth
│   ├── POST   /projections   # Projections Monte Carlo
│   └── GET    /subscriptions # Détection abonnements
│
└── /admin
    ├── GET    /audit         # Audit données
    ├── GET    /rules         # Règles catégorisation
    └── POST   /export        # Export données
```

### 1.2 Exemples de payloads

#### POST /transactions/import
```json
{
  "account_id": "uuid",
  "format": "csv",
  "mapping": {
    "date": "Date",
    "label": "Libelle",
    "amount": "Montant"
  },
  "data": "base64_encoded_csv_content",
  "options": {
    "skip_duplicates": true,
    "auto_categorize": true
  }
}
```

#### Response
```json
{
  "imported": 150,
  "duplicates_skipped": 3,
  "errors": 0,
  "categorized": 142,
  "uncategorized": 8
}
```

### 1.3 WebSocket Events

```javascript
// Connection
ws://localhost:8000/ws/notifications

// Events from server
{
  "type": "transaction_imported",
  "data": { "count": 10, "account_id": "uuid" }
}

{
  "type": "budget_alert",
  "data": { "category": "Alimentation", "percentage": 95 }
}

{
  "type": "badge_earned",
  "data": { "badge_id": "streak_7", "name": "Semaine parfaite" }
}
```

---

## 2. Database Schema

### 2.1 Tables principales

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    household_id UUID REFERENCES households(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Households (foyers)
CREATE TABLE households (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Bank Accounts
CREATE TABLE accounts (
    id UUID PRIMARY KEY,
    household_id UUID REFERENCES households(id),
    name VARCHAR(255) NOT NULL,
    account_type VARCHAR(50), -- 'personal_a', 'personal_b', 'joint'
    bank_name VARCHAR(255),
    balance DECIMAL(12,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Categories
CREATE TABLE categories (
    id UUID PRIMARY KEY,
    household_id UUID REFERENCES households(id),
    name VARCHAR(255) NOT NULL,
    color VARCHAR(7) DEFAULT '#94a3b8',
    emoji VARCHAR(10),
    is_fixed BOOLEAN DEFAULT FALSE,
    parent_id UUID REFERENCES categories(id)
);

-- Transactions
CREATE TABLE transactions (
    id UUID PRIMARY KEY,
    account_id UUID REFERENCES accounts(id),
    category_id UUID REFERENCES categories(id),
    date DATE NOT NULL,
    label VARCHAR(500) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    tx_hash VARCHAR(64) UNIQUE, -- Pour déduplication
    is_internal_transfer BOOLEAN DEFAULT FALSE,
    tags JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    validated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Budgets
CREATE TABLE budgets (
    id UUID PRIMARY KEY,
    household_id UUID REFERENCES households(id),
    category_id UUID REFERENCES categories(id),
    amount DECIMAL(12,2) NOT NULL,
    period VARCHAR(20) DEFAULT 'monthly', -- monthly, yearly
    start_date DATE,
    end_date DATE
);

-- Categorization Rules
CREATE TABLE categorization_rules (
    id UUID PRIMARY KEY,
    household_id UUID REFERENCES households(id),
    name VARCHAR(255) NOT NULL,
    pattern VARCHAR(500) NOT NULL, -- Regex
    category_id UUID REFERENCES categories(id),
    priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    match_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Loans (between couple members)
CREATE TABLE loans (
    id UUID PRIMARY KEY,
    household_id UUID REFERENCES households(id),
    lender_id UUID REFERENCES users(id),
    borrower_id UUID REFERENCES users(id),
    amount DECIMAL(12,2) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active', -- active, repaid, cancelled
    created_at TIMESTAMP DEFAULT NOW(),
    repaid_at TIMESTAMP
);

-- Savings Goals
CREATE TABLE savings_goals (
    id UUID PRIMARY KEY,
    household_id UUID REFERENCES households(id),
    name VARCHAR(255) NOT NULL,
    target_amount DECIMAL(12,2) NOT NULL,
    current_amount DECIMAL(12,2) DEFAULT 0,
    deadline DATE,
    icon VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Badges / Achievements
CREATE TABLE user_badges (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    badge_id VARCHAR(100) NOT NULL,
    earned_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Streaks
CREATE TABLE user_streaks (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 2.2 Indexes

```sql
-- Performance indexes
CREATE INDEX idx_transactions_account_date ON transactions(account_id, date DESC);
CREATE INDEX idx_transactions_category ON transactions(category_id);
CREATE INDEX idx_transactions_hash ON transactions(tx_hash);
CREATE INDEX idx_transactions_label ON transactions USING gin(to_tsvector('french', label));

CREATE INDEX idx_rules_household ON categorization_rules(household_id);
CREATE INDEX idx_rules_active ON categorization_rules(household_id, is_active);
```

---

## 3. React Architecture

### 3.1 Folder Structure

```
src/
├── components/
│   └── ui/                    # shadcn/ui components
│
├── features/                  # Feature-based organization
│   ├── auth/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── types.ts
│   │   └── api.ts
│   │
│   ├── transactions/
│   │   ├── components/
│   │   │   ├── TransactionList.tsx
│   │   │   ├── TransactionForm.tsx
│   │   │   └── ImportWizard/
│   │   ├── hooks/
│   │   │   ├── useTransactions.ts
│   │   │   └── useImport.ts
│   │   ├── types.ts
│   │   └── api.ts
│   │
│   ├── dashboard/
│   │   ├── components/
│   │   │   ├── KpiCards.tsx
│   │   │   ├── ExpenseChart.tsx
│   │   │   └── RecentTransactions.tsx
│   │   └── hooks/
│   │       └── useDashboardStats.ts
│   │
│   ├── budgets/
│   ├── categories/
│   ├── couple/
│   └── gamification/
│
├── hooks/                     # Global hooks
│   ├── useAuth.ts
│   ├── useWebSocket.ts
│   └── useToast.ts
│
├── lib/                       # Utilities
│   ├── api.ts                # Axios instance
│   ├── utils.ts              # Helper functions
│   └── constants.ts
│
├── types/                     # Global types
│   └── index.ts
│
└── App.tsx
```

### 3.2 State Management

```typescript
// React Query pattern
const { data: transactions, isLoading } = useQuery({
  queryKey: ['transactions', { page, filters }],
  queryFn: () => api.transactions.list({ page, filters }),
  staleTime: 30 * 1000, // 30s
});

// Mutation
const mutation = useMutation({
  mutationFn: api.transactions.create,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['transactions'] });
    toast.success('Transaction créée');
  },
});
```

### 3.3 Key Components

#### Dashboard Layout
```tsx
// features/dashboard/components/DashboardLayout.tsx
export function DashboardLayout() {
  return (
    <div className="space-y-6">
      <MonthSelector />
      <KpiCards />
      <div className="grid gap-6 lg:grid-cols-2">
        <ExpenseChart />
        <IncomeChart />
      </div>
      <RecentTransactions />
    </div>
  );
}
```

---

## 4. Migration Strategy

### 4.1 Data Migration Script

```python
# scripts/migrate_financeperso.py

import sqlite3
import click
from sqlalchemy import create_engine
from api.models import Transaction, Category, Account

def migrate_database(source_path: str, target_url: str):
    """Migrate from FinancePerso SQLite to new schema."""
    
    source = sqlite3.connect(source_path)
    target = create_engine(target_url)
    
    # Migration steps
    migrate_categories(source, target)
    migrate_accounts(source, target)
    migrate_transactions(source, target)
    migrate_rules(source, target)
    
    source.close()

@click.command()
@click.option('--source', required=True, help='Path to finance.db')
@click.option('--target', required=True, help='Database URL')
@click.option('--dry-run', is_flag=True)
def main(source, target, dry_run):
    if dry_run:
        print("Dry run - no changes will be made")
    migrate_database(source, target)

if __name__ == '__main__':
    main()
```

### 4.2 Mapping ancien → nouveau schema

| Ancienne table | Nouvelle table | Transformations |
|----------------|----------------|-----------------|
| transactions | transactions | tx_hash → garder, status → validated_at |
| categories | categories | emoji ajouté, parent_id nouveau |
| members | users + households | Séparation user/household |
| learning_rules | categorization_rules | Même structure |
| budgets | budgets | Période ajoutée |
| savings_goals | savings_goals | Même structure |

---

## 5. Deployment

### 5.1 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: ./api
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite:///data/fincouple.db
      - JWT_SECRET=${JWT_SECRET}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}

  web:
    build: ./apps/web
    ports:
      - "3000:80"
    depends_on:
      - api

  admin:
    build: ./apps/admin
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
    environment:
      - API_URL=http://api:8000
```

### 5.2 Environment Variables

```bash
# .env
# Database
DATABASE_URL=sqlite:///data/fincouple.db

# Security
JWT_SECRET=your-secret-key
ENCRYPTION_KEY=your-fernet-key

# AI Providers (optional)
GEMINI_API_KEY=
OPENAI_API_KEY=
OLLAMA_URL=http://localhost:11434

# Features
ENABLE_ML_LOCAL=true
ENABLE_CLOUD_AI=true

# Monitoring
SENTRY_DSN=
```

---

## 6. Testing Strategy

### 6.1 Pyramid de tests

```
        ┌─────────┐
        │   E2E   │  ← Playwright (10%)
        │  (slow) │
        ├─────────┤
        │Integration│ ← API tests (20%)
        │  (medium) │
        ├─────────┤
        │  Unit   │  ← pytest/vitest (70%)
        │  (fast) │
        └─────────┘
```

### 6.2 Test Structure

```
tests/
├── api/
│   ├── test_transactions.py
│   ├── test_categories.py
│   └── conftest.py
├── web/
│   ├── e2e/
│   │   ├── import.spec.ts
│   │   └── dashboard.spec.ts
│   └── unit/
└── integration/
    └── test_migration.py
```

---

*Dernière mise à jour: 2026-03-02*
