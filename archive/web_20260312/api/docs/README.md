# Documentation API FinancePerso

## Vue d'ensemble

L'API FinancePerso est une API REST complète pour la gestion financière personnelle, construite avec FastAPI.

## Documentation interactive

Lorsque l'API est en cours d'exécution, accédez à :

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc
- **OpenAPI JSON** : http://localhost:8000/openapi.json

## Architecture

```
web/api/
├── main.py              # Point d'entrée FastAPI
├── routers/             # Endpoints organisés par domaine
│   ├── auth.py          # Authentification JWT
│   ├── accounts.py      # Comptes bancaires
│   ├── transactions.py  # Transactions
│   ├── categories.py    # Catégories
│   ├── budgets.py       # Budgets
│   ├── members.py       # Membres
│   ├── rules.py         # Règles de catégorisation
│   ├── dashboard.py     # Statistiques
│   ├── analytics.py     # Analytics avancés
│   ├── notifications.py # Notifications temps réel
│   ├── households.py    # Gestion des foyers
│   └── export.py        # Export de données
├── models/
│   └── schemas.py       # Modèles Pydantic
└── docs/
    └── openapi.yml      # Spécification OpenAPI
```

## Authentification

### JWT Token Flow

1. **Login** → Récupérer access_token + refresh_token
2. **Utiliser** → `Authorization: Bearer <access_token>`
3. **Refresh** → Renouveler avant expiration
4. **Logout** → Révoquer le refresh_token

### Exemple

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=secret"

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}

# Utilisation
curl http://localhost:8000/api/accounts \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

## Endpoints principaux

### Authentification

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/auth/register` | Créer un compte |
| POST | `/auth/login` | Connexion |
| POST | `/auth/refresh` | Rafraîchir le token |
| GET | `/auth/me` | Profil utilisateur |

### Transactions

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/transactions` | Liste paginée |
| PUT | `/transactions/{id}` | Modifier |
| POST | `/transactions/import` | Import CSV |
| POST | `/transactions/categorize` | Catégorisation IA |

### Dashboard & Analytics

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/dashboard/stats` | KPIs mensuels |
| GET | `/analytics/anomalies` | Détection anomalies |
| GET | `/analytics/predictions/cashflow` | Prédictions |

## Codes d'erreur

| Code | Description |
|------|-------------|
| 400 | Requête invalide |
| 401 | Non authentifié |
| 403 | Non autorisé |
| 404 | Ressource non trouvée |
| 422 | Validation échouée |
| 500 | Erreur serveur |

## Tests

### Manuellement

```bash
# Lancer le serveur
cd web/api
python start_api.py

# Tester avec curl
curl http://localhost:8000/api/health
```

### Collection Postman

Importez la collection depuis `/docs/postman-collection.json`

## Développement

### Ajouter un nouvel endpoint

1. Créer/modifier le fichier dans `routers/`
2. Définir les modèles dans `models/schemas.py`
3. Enregistrer le router dans `main.py`
4. Documenter avec docstrings

### Exemple

```python
@router.get("/exemple", response_model=ExempleResponse)
async def exemple_endpoint(
    param: str = Query(..., description="Description"),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Description de l'endpoint.
    
    Args:
        param: Description du paramètre
        
    Returns:
        ExempleResponse
    """
    return ExempleResponse(data=param)
```
