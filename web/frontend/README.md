# FinancePerso Web - Frontend

Frontend React de l'application FinancePerso, migrée depuis Streamlit vers React + FastAPI.

## 🚀 Démarrage rapide

```bash
# Installation des dépendances
npm install

# Lancer le serveur de développement
npm run dev
```

L'application sera accessible sur http://localhost:5173

## 📁 Structure

```
frontend/
├── src/
│   ├── components/      # Composants UI (shadcn/ui)
│   │   ├── ui/         # Composants shadcn de base
│   │   └── ...         # Composants métier
│   ├── hooks/          # Hooks React Query et métier
│   ├── lib/            # Utilitaires et client API
│   ├── pages/          # Pages de l'application
│   └── types/          # Types TypeScript (à créer)
├── public/             # Assets statiques
└── package.json
```

## 🔌 Intégration API

Le frontend communique avec l'API FastAPI via le client dans `src/lib/api.ts`.

Les hooks utilisent **React Query** pour la gestion du cache et des états de chargement.

### Hooks disponibles

- `useAuth()` - Authentification
- `useTransactions()` - Gestion des transactions
- `useCategories()` - Gestion des catégories
- `useBudgets()` - Gestion des budgets
- `useHouseholdMembers()` - Gestion des membres
- `useRules()` - Règles de catégorisation
- `useDashboard()` - Métriques et KPIs

## ⚠️ Migration en cours

Les hooks contiennent actuellement des données mockées (`MOCK_*`).
Pour connecter à l'API FastAPI, remplacez les appels mockés par des appels à `apiClient` :

```typescript
// Avant (mock)
await new Promise(resolve => setTimeout(resolve, 300));
return MOCK_DATA;

// Après (API réelle)
return apiClient.get("/transactions");
```

## 🛠️ Technologies

- **React 18** + **TypeScript**
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - Composants UI
- **React Query** - Gestion d'état serveur
- **React Router** - Navigation
- **Recharts** - Graphiques
- **React Hook Form** + **Zod** - Formulaires
