# 03 - Specs Techniques

## 🏗️ Stack

| Couche | Technologie |
|--------|-------------|
| **Frontend** | React 18 + TypeScript + Vite |
| **UI** | shadcn/ui + Tailwind CSS |
| **State** | React Query + Zustand |
| **Backend** | FastAPI (Python 3.12) |
| **ORM** | SQLAlchemy 2.0 |
| **Migrations** | Alembic |
| **DB** | SQLite (local) |
| **Auth** | JWT |

---

## 🔌 API Endpoints

### Auth
```
POST   /api/v1/auth/login
POST   /api/v1/auth/register
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout
```

### Transactions
```
GET    /api/v1/transactions              # Liste (paginée)
GET    /api/v1/transactions/{id}         # Détail
POST   /api/v1/transactions              # Créer
PUT    /api/v1/transactions/{id}         # Modifier
DELETE /api/v1/transactions/{id}         # Supprimer
POST   /api/v1/transactions/batch        # Validation batch
POST   /api/v1/transactions/import       # Import CSV
GET    /api/v1/transactions/stats        # Statistiques
```

### AI
```
POST   /api/v1/ai/categorize             # Catégoriser
POST   /api/v1/ai/categorize-batch       # Batch
GET    /api/v1/ai/suggestions            # Suggestions
POST   /api/v1/ai/chat                   # Assistant
```

### Budgets
```
GET    /api/v1/budgets
POST   /api/v1/budgets
GET    /api/v1/budgets/status            # État actuel
GET    /api/v1/budgets/predictions       # Prédictions ML
```

### Wealth
```
POST   /api/v1/wealth/projections        # Monte Carlo
GET    /api/v1/wealth/subscriptions      # Abonnements
```

---

## 📦 Payloads

### Import CSV
```json
POST /api/v1/transactions/import
{
  "account_id": "uuid",
  "format": "csv",
  "mapping": {
    "date": "Date",
    "label": "Libelle",
    "amount": "Montant"
  },
  "data": "base64_encoded_csv",
  "options": {
    "skip_duplicates": true,
    "auto_categorize": true
  }
}

Response:
{
  "imported": 150,
  "duplicates_skipped": 3,
  "errors": 0,
  "categorized": 142,
  "uncategorized": 8
}
```

### Categorize
```json
POST /api/v1/ai/categorize
{
  "label": "CARREFOUR PARIS 12",
  "amount": -45.67,
  "account_id": "uuid"
}

Response:
{
  "category": "Alimentation",
  "confidence": 0.95,
  "suggested_tags": ["Courses", "Supermarché"]
}
```

---

## 🗄️ Database Schema

### Core Tables
```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    household_id UUID REFERENCES households(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Households
CREATE TABLE households (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Accounts
CREATE TABLE accounts (
    id UUID PRIMARY KEY,
    household_id UUID REFERENCES households(id),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50), -- 'personal', 'joint', 'external'
    owner_id UUID REFERENCES users(id),
    balance DECIMAL(12,2) DEFAULT 0
);

-- Categories
CREATE TABLE categories (
    id UUID PRIMARY KEY,
    household_id UUID REFERENCES households(id),
    name VARCHAR(255) NOT NULL,
    emoji VARCHAR(10),
    is_fixed BOOLEAN DEFAULT false,
    color VARCHAR(7) -- hex color
);

-- Transactions
CREATE TABLE transactions (
    id UUID PRIMARY KEY,
    account_id UUID REFERENCES accounts(id),
    category_id UUID REFERENCES categories(id),
    date DATE NOT NULL,
    label VARCHAR(500) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'validated'
    tags JSONB DEFAULT '[]',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Budgets
CREATE TABLE budgets (
    id UUID PRIMARY KEY,
    household_id UUID REFERENCES households(id),
    category_id UUID REFERENCES categories(id),
    amount DECIMAL(12,2) NOT NULL,
    period VARCHAR(20) DEFAULT 'monthly', -- 'monthly', 'yearly'
    start_date DATE,
    end_date DATE
);
```

---

## 🔒 WebSocket Events

```javascript
// Connection
ws://localhost:8000/ws/notifications

// Server events
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

[→ Design System : 04_UI_UX.md](./04_UI_UX.md)
