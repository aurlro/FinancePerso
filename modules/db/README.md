# Couche de persistance données

Accès SQLite, migrations, repositories

## Fichiers principaux

- `connection.py` - Gestionnaire de connexions SQLite
- `migrations.py` - Schéma et migrations de la base de données
- `repositories/` - Pattern Repository pour l'accès aux données
- `models/` - Modèles de données

## Exemple d'utilisation

```python
from modules.db.connection import get_db_connection

with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE status = ?", ("pending",))
    results = cursor.fetchall()
```
