# Module `modules/db`

> Couche d'accès aux données (Data Access Layer) pour FinancePerso.

## Vue d'ensemble

Ce module gère toute l'interaction avec la base de données SQLite : connexions, migrations, CRUD et requêtes analytiques.

## Architecture

```
modules/db/
├── __init__.py              # Exports publics
├── connection.py            # Gestionnaire de connexions SQLite
├── migrations.py            # Schéma et migrations DB
├── transactions.py          # CRUD transactions
├── categories.py            # Gestion catégories
├── members.py               # Gestion membres foyer
├── rules.py                 # Règles d'apprentissage
├── budgets.py               # Budgets par catégorie
├── stats.py                 # Statistiques globales
├── analytics.py             # Requêtes analytiques
├── dashboard_layouts.py     # Layouts dashboard
├── recycle_bin.py           # Corbeille (soft delete)
├── audit.py                 # Audit et cohérence
├── tags.py                  # Gestion tags
└── validators.py            # Validation données
```

## Utilisation

### Connexion à la base

```python
from modules.db.connection import get_db_connection

with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions LIMIT 10")
    results = cursor.fetchall()
```

### CRUD Transactions

```python
from modules.db.transactions import get_transactions, save_transactions

# Récupérer les transactions
pending = get_transactions(status="pending")

# Sauvegarder des transactions
save_transactions(df, account_label="Compte Courant")
```

### Gestion des membres

```python
from modules.db.members import get_members, add_member

members = get_members()
add_member("John", member_type="HOUSEHOLD")
```

## Schéma de base

### Tables principales

| Table | Description |
|-------|-------------|
| `transactions` | Opérations bancaires importées |
| `categories` | Catégories de dépenses/revenus |
| `members` | Membres du foyer |
| `learning_rules` | Règles d'apprentissage IA |
| `budgets` | Budgets par catégorie |
| `recycle_bin` | Corbeille (soft delete) |
| `dashboard_layouts` | Configurations dashboard |

## Bonnes pratiques

1. **Toujours utiliser le context manager** `get_db_connection()`
2. **Jamais de concatenation SQL** - Utiliser des paramètres bind `?`
3. **Transactions** - Commiter explicitement les modifications

## Tests

```bash
pytest tests/db/ -v
```
