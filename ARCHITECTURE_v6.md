# FinancePerso v6.0 - Architecture Documentation

## Vue d'ensemble

FinancePerso v6.0 est une refonte complète de l'application avec une architecture moderne **React + TypeScript frontend** et **FastAPI + SQLite backend**.

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT (React)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  React 18   │  │ TypeScript  │  │       Vite 5            │ │
│  │  Router 6   │  │   Zustand   │  │    TanStack Query       │ │
│  │  Recharts   │  │ TailwindCSS │  │      Lucide UI          │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│                              │                                  │
│                              ▼ HTTP/REST                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ CORS (localhost:5173 ↔ localhost:8000)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        SERVER (FastAPI)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   FastAPI   │  │  Pydantic   │  │      SQLAlchemy 2.0     │ │
│  │   Uvicorn   │  │   OAuth2    │  │      aiosqlite          │ │
│  │   CORS      │  │   JWT       │  │      Alembic            │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│                    ┌─────────────────┐                          │
│                    │   SQLite (async)│  Data/finance_v6.db      │
│                    └─────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Structure du projet

```
FinancePerso/
├── client/                    # Frontend React + TypeScript
│   ├── public/               # Static assets
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   │   ├── ui/          # shadcn/ui components
│   │   │   ├── layout/      # Layout components
│   │   │   └── charts/      # Chart components
│   │   ├── pages/           # Route pages
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Transactions.tsx
│   │   │   ├── Categories.tsx
│   │   │   ├── Accounts.tsx
│   │   │   ├── Budgets.tsx
│   │   │   ├── Import.tsx
│   │   │   └── Settings.tsx
│   │   ├── hooks/           # React Query hooks
│   │   │   ├── useTransactions.ts
│   │   │   ├── useCategories.ts
│   │   │   ├── useDashboard.ts
│   │   │   └── ...
│   │   ├── services/        # API clients
│   │   │   ├── api.ts       # Axios instance
│   │   │   ├── transactions.ts
│   │   │   ├── categories.ts
│   │   │   └── ...
│   │   ├── types/           # TypeScript types
│   │   │   └── index.ts     # Re-export from shared/
│   │   ├── utils/           # Utility functions
│   │   ├── contexts/        # React contexts
│   │   ├── stores/          # Zustand stores
│   │   ├── App.tsx          # Main App component
│   │   ├── main.tsx         # Entry point
│   │   └── index.css        # Global styles
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── server/                    # Backend FastAPI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI app factory
│   │   ├── database.py       # SQLAlchemy config
│   │   ├── models/           # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── base.py       # Base model + mixins
│   │   │   ├── category.py
│   │   │   ├── account.py
│   │   │   ├── transaction.py
│   │   │   ├── member.py
│   │   │   ├── budget.py
│   │   │   └── learning_rule.py
│   │   ├── schemas/          # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── category.py
│   │   │   ├── account.py
│   │   │   ├── transaction.py
│   │   │   ├── member.py
│   │   │   ├── budget.py
│   │   │   └── dashboard.py
│   │   ├── routers/          # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── transactions.py
│   │   │   ├── categories.py
│   │   │   ├── accounts.py
│   │   │   ├── budgets.py
│   │   │   ├── members.py
│   │   │   └── dashboard.py
│   │   ├── services/         # Business logic
│   │   ├── middleware/       # Custom middleware
│   │   └── utils/            # Utilities
│   ├── tests/                # Pytest tests
│   ├── alembic/              # Database migrations
│   ├── requirements.txt
│   └── pyproject.toml
│
├── shared/                    # Shared type definitions
│   └── schemas.ts            # TypeScript types (source of truth)
│
├── scripts/                   # Utility scripts
│   ├── migrate_from_v5.py    # Migration from v5
│   └── setup_dev.sh          # Dev environment setup
│
└── docker-compose.yml         # Optional Docker setup
```

---

## Stack Technique

### Frontend

| Technologie | Version | Usage |
|-------------|---------|-------|
| React | 18.2+ | UI library |
| TypeScript | 5.3+ | Type safety |
| Vite | 5.1+ | Build tool |
| React Router | 6.22+ | Routing |
| TanStack Query | 5.18+ | Server state management |
| Zustand | 4.5+ | Client state management |
| TailwindCSS | 3.4+ | Styling |
| Radix UI | 1.0+ | Headless UI components |
| Recharts | 2.12+ | Charts |
| Axios | 1.6+ | HTTP client |
| date-fns | 3.3+ | Date manipulation |
| Lucide React | 0.33+ | Icons |

### Backend

| Technologie | Version | Usage |
|-------------|---------|-------|
| Python | 3.11+ | Language |
| FastAPI | 0.109+ | Web framework |
| SQLAlchemy | 2.0+ | ORM |
| Pydantic | 2.6+ | Data validation |
| Uvicorn | 0.27+ | ASGI server |
| aiosqlite | 0.19+ | Async SQLite |
| Alembic | 1.13+ | Migrations |
| python-jose | 3.3+ | JWT handling |
| passlib | 1.7+ | Password hashing |
| pytest-asyncio | 0.23+ | Testing |

---

## Architecture Backend

### Database Layer

```python
# SQLAlchemy 2.0 with async support
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# Models with type hints
class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"
    
    id: Mapped[str] = mapped_column(primary_key=True, default=generate_uuid)
    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    # ...
```

### API Layer

```python
# FastAPI router with dependency injection
@router.get("", response_model=PaginatedResponse[Transaction])
async def list_transactions(
    filters: TransactionFilters = Depends(),
    db: AsyncSession = Depends(get_db),
):
    # Implementation
```

### Schema Layer (Pydantic v2)

```python
class TransactionCreate(BaseSchema):
    date: date = Field(..., description="Transaction date")
    amount: float = Field(..., gt=0)
    description: str = Field(..., min_length=1, max_length=500)
    # Auto-validation + serialization
```

---

## Architecture Frontend

### State Management

```typescript
// Server state with TanStack Query
const { data, isLoading } = useTransactions(filters);

// Client state with Zustand
const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
}));
```

### API Layer

```typescript
// Axios instance with interceptors
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

// Typed API functions
export const transactionApi = {
  getAll: (filters?: TransactionFilters) => 
    api.get<PaginatedResponse<Transaction>>('/transactions', { params: filters }),
  // ...
};
```

### Component Structure

```typescript
// Container components (pages) handle data fetching
export const Transactions: React.FC = () => {
  const { data } = useTransactions();
  return <TransactionTable data={data} />;
};

// Presentational components receive data via props
interface TransactionTableProps {
  data: Transaction[];
}
```

---

## API Endpoints

### Transactions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/transactions` | List with filters |
| GET | `/api/transactions/{id}` | Get single |
| POST | `/api/transactions` | Create |
| PATCH | `/api/transactions/{id}` | Update |
| DELETE | `/api/transactions/{id}` | Soft delete |
| POST | `/api/transactions/bulk` | Bulk update |
| POST | `/api/transactions/{id}/validate` | Validate |
| POST | `/api/transactions/import/preview` | Preview CSV |
| POST | `/api/transactions/import` | Confirm import |

### Categories

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/categories` | List all |
| GET | `/api/categories/tree` | Hierarchical |
| POST | `/api/categories` | Create |
| PATCH | `/api/categories/{id}` | Update |
| DELETE | `/api/categories/{id}` | Delete |

### Accounts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/accounts` | List all |
| POST | `/api/accounts` | Create |
| PATCH | `/api/accounts/{id}` | Update |
| DELETE | `/api/accounts/{id}` | Delete |

### Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard` | Full dashboard |
| GET | `/api/dashboard/stats` | Main stats |
| GET | `/api/dashboard/trend` | Monthly trend |
| GET | `/api/dashboard/spending` | By category |
| GET | `/api/dashboard/forecast` | Cashflow prediction |

---

## Database Schema

### Tables

```sql
-- Categories
CREATE TABLE categories (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    emoji TEXT DEFAULT '📁',
    color TEXT DEFAULT '#3B82F6',
    type TEXT DEFAULT 'variable',
    is_fixed BOOLEAN DEFAULT FALSE,
    budget_limit NUMERIC(12,2),
    parent_id TEXT REFERENCES categories(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Accounts
CREATE TABLE accounts (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT DEFAULT 'checking',
    balance NUMERIC(12,2) DEFAULT 0,
    currency TEXT DEFAULT 'EUR',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions (core table)
CREATE TABLE transactions (
    id TEXT PRIMARY KEY,
    date DATE NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    description TEXT NOT NULL,
    type TEXT DEFAULT 'expense',
    status TEXT DEFAULT 'pending',
    is_validated BOOLEAN DEFAULT FALSE,
    category_id TEXT REFERENCES categories(id),
    account_id TEXT NOT NULL REFERENCES accounts(id),
    beneficiary TEXT,
    notes TEXT,
    tags TEXT, -- JSON array
    is_recurring BOOLEAN DEFAULT FALSE,
    hash TEXT UNIQUE NOT NULL, -- deduplication
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- pnpm or npm

### Backend Setup

```bash
cd server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd client
pnpm install  # or npm install

# Run development server
pnpm dev      # or npm run dev
```

### Full Stack (simultaneous)

```bash
# Terminal 1 - Backend
cd server && uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd client && pnpm dev

# Access:
# - Frontend: http://localhost:5173
# - API Docs: http://localhost:8000/docs
```

---

## Migration from v5 (Streamlit)

### Data Migration

```bash
# Run migration script
python scripts/migrate_from_v5.py \
    --source Data/finance.db \
    --target Data/finance_v6.db
```

### Feature Parity Checklist

- [x] Database models
- [ ] CSV import
- [ ] AI categorization
- [ ] Dashboard charts
- [ ] Transaction validation
- [ ] Budget tracking
- [ ] Member management
- [ ] Settings page

---

## Security Considerations

### Backend

- CORS restricted to localhost in development
- Input validation via Pydantic
- SQL injection prevention via SQLAlchemy
- Password hashing with bcrypt (for future auth)
- JWT token authentication (for future auth)

### Frontend

- XSS prevention via React's escaping
- CSRF protection via SameSite cookies
- Input sanitization before API calls

---

## Performance Optimizations

### Backend

- Async database operations
- Connection pooling
- Query optimization with proper indexes
- Response caching with ETags

### Frontend

- React Query caching and stale-while-revalidate
- Virtualized lists for large datasets
- Lazy loading of routes
- Image optimization

---

## Testing Strategy

### Backend

```python
# pytest with async support
@pytest.mark.asyncio
async def test_create_transaction(client, db):
    response = await client.post("/api/transactions", json={...})
    assert response.status_code == 201
```

### Frontend

```typescript
// Vitest + React Testing Library
describe('TransactionTable', () => {
  it('renders transactions', () => {
    render(<TransactionTable data={mockTransactions} />);
    expect(screen.getByText('Test Transaction')).toBeInTheDocument();
  });
});
```

---

## Deployment

### Production Build

```bash
# Frontend
cd client && pnpm build

# Backend (with frontend static files)
cd server && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker (optional)

```bash
docker-compose up -d
```

---

## Future Enhancements

1. **Authentication**: JWT-based auth with refresh tokens
2. **Mobile App**: React Native or PWA
3. **Real-time**: WebSocket for live updates
4. **Offline**: Service Worker + localStorage sync
5. **AI Features**: TensorFlow.js for local categorization
6. **Reports**: PDF/Excel export
7. **Multi-currency**: Real-time exchange rates
8. **Bank Sync**: Open Banking integration

---

## License

Same as FinancePerso v5 (see main LICENSE file)
