# FinancePerso v6.0 - Architecture React + API Locale

## 🎯 Vue d'ensemble

Nouvelle architecture moderne avec **React frontend** et **Python backend**, remplaçant la version Streamlit legacy.

```
┌─────────────┐      HTTP/REST      ┌─────────────┐
│   React     │ ◄──────────────────► │   FastAPI   │
│  Frontend   │   localhost:5173     │   Backend   │
│  (client/)  │                      │  (server/)  │
└─────────────┘                      └──────┬──────┘
                                            │
                                            ▼ SQLite
                                       finance_v6.db
```

## 📁 Structure

```
FinancePerso/
├── client/              # Frontend React + TypeScript + Vite
│   ├── src/
│   │   ├── pages/      # Dashboard, Transactions, Settings...
│   │   ├── components/ # UI components (shadcn/ui)
│   │   ├── services/   # API calls
│   │   └── hooks/      # React hooks
│   └── package.json
│
├── server/              # Backend FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── models/     # SQLAlchemy models
│   │   ├── routers/    # API endpoints
│   │   └── schemas/    # Pydantic schemas
│   └── requirements.txt
│
├── shared/              # Types partagés
├── scripts/             # Scripts utilitaires
└── Data/                # SQLite databases (legacy + v6)
```

## 🚀 Démarrage rapide

### Prérequis
- Node.js 18+ + pnpm (ou npm)
- Python 3.11+

### Installation

```bash
# 1. Cloner et entrer dans le projet
cd FinancePerso

# 2. Setup automatique
./scripts/setup_v6.sh

# Ou manuellement :
# --- Backend ---
cd server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# --- Frontend ---
cd ../client
pnpm install  # ou npm install
```

### Lancement

```bash
# Terminal 1 - Backend
cd server
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend  
cd client
pnpm dev

# Ouvrir http://localhost:5173
```

## 🔄 Migration depuis v5 (Streamlit)

```bash
# 1. Migrer les données
python scripts/migrate_to_v6.py

# 2. Vérifier
ls -la Data/
# finance.db (legacy)
# finance_v6.db (nouvelle)
```

## 📚 Documentation

- `client/README.md` - Guide frontend
- `server/README.md` - Guide backend
- `ARCHITECTURE_v6.md` - Détails techniques

## 🛠️ Développement

### Frontend
```bash
cd client
pnpm dev          # Dev server
pnpm build        # Production build
pnpm test         # Tests
```

### Backend
```bash
cd server
source venv/bin/activate
uvicorn app.main:app --reload

# API docs: http://localhost:8000/docs
```

## 🏛️ Architecture

### Stack Technique

| Couche | Technologie |
|--------|-------------|
| Frontend | React 18, TypeScript, Vite, TailwindCSS |
| State | Zustand (client), TanStack Query (server) |
| UI | Radix UI + shadcn/ui components |
| Backend | FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| Database | SQLite (async via aiosqlite) |
| Charts | Recharts |

### Avantages vs Streamlit

- ✅ **Performance** - React SPA rapide
- ✅ **UX** - Interface moderne, responsive
- ✅ **Offline** - SQLite locale, pas de cloud requis
- ✅ **Scalabilité** - Architecture API REST propre
- ✅ **Tests** - Tests unitaires frontend + backend

## 📄 License

MIT - FinancePerso Team
