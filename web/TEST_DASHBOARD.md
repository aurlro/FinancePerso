# Test du Dashboard - FinancePerso Web

## ✅ Statut

- **Frontend React** : ✅ Build réussi
- **Hooks API** : ✅ Adaptés pour FastAPI
- **API FastAPI** : ✅ Créée avec endpoints dashboard

## 🚀 Lancement pour Test

### Terminal 1 : Lancer l'API Backend

```bash
cd /Users/aurelien/Documents/Projets/FinancePerso
source .venv/bin/activate
cd web/api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Vérification : http://localhost:8000/docs (Swagger UI)

### Terminal 2 : Lancer le Frontend

```bash
cd /Users/aurelien/Documents/Projets/FinancePerso/web/frontend
npm run dev
```

Ouvrir : http://localhost:5173

## 🔧 Endpoints API Disponibles

| Endpoint | Description |
|----------|-------------|
| `GET /api/dashboard/stats?month=2024-03` | KPIs mensuels |
| `GET /api/dashboard/breakdown?month=2024-03` | Répartition catégories |
| `GET /api/dashboard/evolution?months=12` | Évolution sur 12 mois |
| `GET /api/transactions` | Liste transactions paginée |
| `GET /api/health` | Health check |

## 📝 Hooks Utilisés dans Index.tsx

```typescript
const { data: stats, isLoading: loadingStats } = useDashboardStats(monthStr);
const { data: catBreakdownData, isLoading: loadingCat } = useCategoryBreakdown(monthStr);
const { data: monthlyEvolutionData, isLoading: loadingMonthly } = useMonthlyEvolution();
```

## 🎯 Points d'Attention

1. **Format des dates** : Le mois est formaté en `YYYY-MM` (ex: `"2024-03"`)
2. **Adaptation des données** : Les données API (snake_case) sont adaptées vers le format attendu par le composant
3. **Mock data** : Certains composants utilisent encore des mocks (useHousehold, etc.)

## 🔍 Débogage

Si le dashboard ne charge pas :

1. Vérifier que l'API répond : `curl http://localhost:8000/api/health`
2. Vérifier les logs du navigateur (F12 → Console)
3. Vérifier les logs de l'API (Terminal 1)
4. Vérifier que la base SQLite existe : `ls Data/finance.db`

## ✅ Prochaines Étapes après Test

1. **Si ça marche** : Migrer les autres pages (Transactions, Import)
2. **Si problème** : Corriger les endpoints API ou les hooks
3. **Amélioration** : Ajouter l'authentification JWT
