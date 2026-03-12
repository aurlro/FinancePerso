# FinancePerso API

API REST FastAPI pour l'application FinancePerso.

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.12+
- Dépendances du projet installées (voir `/requirements.txt`)
- Base de données SQLite initialisée (`Data/finance.db`)

### Installation

```bash
# Depuis la racine du projet
cd /Users/aurelien/Documents/Projets/FinancePerso

# Activer l'environnement virtuel
source .venv/bin/activate

# Installer les dépendances API
pip install -r web/api/requirements-api.txt
```

### Lancement

```bash
# Mode développement (auto-reload)
uvicorn web.api.main:app --reload --host 0.0.0.0 --port 8000

# Ou via Python directement
python -m uvicorn web.api.main:app --reload
```

### Documentation

Une fois lancée, la documentation est accessible à :

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 📡 Endpoints

### General

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Info API |
| GET | `/health` | Health check |

### Dashboard

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/dashboard/stats` | Statistiques mensuelles |
| GET | `/api/v1/dashboard/breakdown` | Répartition par catégorie |
| GET | `/api/v1/dashboard/evolution` | Évolution sur 12 mois |

### Transactions

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/transactions` | Liste paginée |
| GET | `/api/v1/transactions/{id}` | Détail transaction |

## 📊 Exemples

### Statistiques Dashboard

```bash
curl "http://localhost:8000/api/v1/dashboard/stats?month=2024-03"
```

Réponse :
```json
{
  "reste_a_vivre": 2500.50,
  "total_expenses": 1800.00,
  "total_income": 4300.50,
  "epargne_nette": 700.50,
  "period": "2024-03"
}
```

### Répartition par Catégorie

```bash
curl "http://localhost:8000/api/v1/dashboard/breakdown?month=2024-03"
```

Réponse :
```json
{
  "categories": [
    {"name": "Alimentation", "amount": 450.00, "percentage": 25.0, "emoji": "🛒"},
    {"name": "Transport", "amount": 200.00, "percentage": 11.1, "emoji": "🚗"}
  ],
  "total": 1800.0
}
```

### Évolution 12 Mois

```bash
curl "http://localhost:8000/api/v1/dashboard/evolution?months=12"
```

Réponse :
```json
{
  "months": ["2024-01", "2024-02", "2024-03"],
  "expenses": [2000, 1800, 1900],
  "income": [4000, 4200, 4300],
  "savings": [2000, 2400, 2400]
}
```

### Liste des Transactions

```bash
# Toutes les transactions (paginée)
curl "http://localhost:8000/api/v1/transactions?limit=10&offset=0"

# Filtrées par mois et statut
curl "http://localhost:8000/api/v1/transactions?month=2024-03&status=pending"

# Recherche
curl "http://localhost:8000/api/v1/transactions?search=supermarket"
```

## 🔧 Configuration

### CORS

Les origines CORS sont configurables via la variable d'environnement `CORS_ORIGINS` :

```bash
export CORS_ORIGINS="http://localhost:3000,http://localhost:5173"
uvicorn web.api.main:app --reload
```

Par défaut, les origines suivantes sont autorisées :
- `http://localhost:3000` (Next.js)
- `http://localhost:5173` (Vite)
- `http://localhost:8501` (Streamlit)

### Base de données

Le chemin de la base de données est déterminé automatiquement depuis `modules/db/connection.py`.
Pour les tests, vous pouvez surcharger via la variable d'environnement `DB_PATH` :

```bash
export DB_PATH="/path/to/test.db"
```

## 🏗️ Architecture

```
web/api/
├── main.py              # Application FastAPI principale
├── models/
│   ├── __init__.py
│   └── schemas.py       # Modèles Pydantic (request/response)
├── routers/
│   ├── __init__.py
│   ├── dashboard.py     # Routes dashboard (stats, breakdown, evolution)
│   └── transactions.py  # Routes transactions (CRUD)
├── requirements-api.txt # Dépendances
└── README.md            # Ce fichier
```

## 🔒 Sécurité

- **Phase 1**: Pas d'authentification (local/dev uniquement)
- **CORS**: Configuré pour localhost uniquement
- **SQL Injection**: Protection via paramètres bind (SQLite)
- **Validation**: Pydantic pour toutes les entrées

## 📝 TODO (Phases Futures)

- [ ] Authentification JWT
- [ ] Endpoints CRUD complet transactions
- [ ] Endpoints budgets
- [ ] Endpoints membres
- [ ] Endpoints catégories
- [ ] Endpoints import CSV
- [ ] WebSocket pour temps réel
- [ ] Rate limiting
- [ ] Tests automatisés

## 🐛 Debug

### Logs

Les logs sont écrits dans `logs/app.log` (via `modules.logger`).

### Mode debug

```bash
uvicorn web.api.main:app --reload --log-level debug
```

## 📄 License

Même licence que le projet FinancePerso.
