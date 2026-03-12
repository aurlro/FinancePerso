# FinancePerso Web - Migration React + FastAPI

## 🎯 Architecture

Migration de FinancePerso vers une architecture moderne :
- **Frontend** : React + TypeScript + Vite + shadcn/ui (code Lovable adapté)
- **Backend** : FastAPI (Python) exposant la logique métier existante
- **Database** : SQLite (base existante conservée)

## 📁 Structure

```
web/
├── frontend/          # Application React
│   ├── src/
│   │   ├── components/ui/    # shadcn/ui (40+ composants)
│   │   ├── pages/            # 12 pages (Index, Transactions, etc.)
│   │   ├── hooks/            # Hooks React Query
│   │   │   ├── useDashboardApi.ts    # ✅ Nouveau (API FastAPI)
│   │   │   └── useTransactionsApi.ts # ✅ Nouveau (API FastAPI)
│   │   └── lib/api.ts        # ✅ Client API
│   └── package.json
│
└── api/               # API FastAPI
    ├── main.py               # Point d'entrée
    ├── routers/
    │   ├── dashboard.py      # ✅ Stats, breakdown, evolution
    │   ├── transactions.py   # ✅ CRUD transactions
    │   └── ...               # Autres routers
    └── requirements.txt
```

## 🚀 Lancement

### 1. Démarrer l'API Backend

```bash
cd /Users/aurelien/Documents/Projets/FinancePerso
source .venv/bin/activate
cd web/api
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

L'API est accessible sur http://localhost:8000
Documentation Swagger : http://localhost:8000/docs

### 2. Démarrer le Frontend

```bash
cd /Users/aurelien/Documents/Projets/FinancePerso/web/frontend
npm install
npm run dev
```

Le frontend est accessible sur http://localhost:5173

## ✅ Phase 1 Complétée (Dashboard)

### API Endpoints
- [x] `GET /api/dashboard/stats?month=YYYY-MM` - KPIs mensuels
- [x] `GET /api/dashboard/breakdown?month=YYYY-MM` - Répartition catégories
- [x] `GET /api/dashboard/evolution?months=N` - Évolution sur N mois
- [x] `GET /api/transactions` - Liste paginée avec filtres
- [x] `POST /api/transactions/categorize` - Catégorisation IA

### Hooks React
- [x] `useDashboardStats(month)` - Stats dashboard
- [x] `useCategoryBreakdown(month)` - Répartition
- [x] `useMonthlyEvolution(months)` - Évolution
- [x] `useTransactions(params)` - Liste transactions
- [x] `useCategorizeTransactions()` - Mutation catégorisation

## 📋 Prochaines Étapes

1. **Adapter la page Index.tsx** pour utiliser les nouveaux hooks
2. **Tester** le flux dashboard avec données réelles
3. **Migrer** les autres pages (Transactions, Import, etc.)
4. **Ajouter** l'authentification JWT

## 🔧 Technologies

| Couche | Technologie |
|--------|-------------|
| Frontend | React 18, TypeScript, Vite, Tailwind, shadcn/ui |
| State | TanStack Query (React Query) |
| Backend | FastAPI, Pydantic, Uvicorn |
| Database | SQLite (existante) |
| Auth | JWT (à implémenter) |

## 📝 Notes

- Les hooks Supabase ont été remplacés par des hooks API
- Les composants UI shadcn/ui sont conservés tels quels
- La logique métier Python est réutilisée via l'API
