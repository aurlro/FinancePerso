# Architecture FinancePerso

## Modules principaux

### modules/ai/
Suite IA complète:
- `anomaly_detector.py` - Détection anomalies de montant
- `budget_predictor.py` - Prédictions budgétaires
- `conversational_assistant.py` - Chat IA
- `smart_tagger.py` - Suggestion tags
- `trend_analyzer.py` - Analyse tendances
- `rules_auditor.py` - Audit règles

### modules/db/
Couche d'accès données:
- `connection.py` - Gestion connexions SQLite
- `transactions.py` - CRUD transactions
- `categories.py` - Gestion catégories
- `members.py` - Gestion membres
- `rules.py` - Règles d'apprentissage
- `budgets.py` - Objectifs budgétaires
- `tags.py` - Gestion tags
- `migrations.py` - Schéma et migrations

### modules/ui/
Composants UI:
- `feedback.py` - Messages utilisateur (toast, flash)
- `layout.py` - Layouts réutilisables
- `components/` - Composants spécifiques
- `dashboard/` - Widgets dashboard
- `validation/` - UI de validation
- `config/` - UI de configuration

### Autres modules
- `ai_manager.py` - Abstraction multi-provider IA
- `categorization.py` - Logique catégorisation
- `ingestion.py` - Import parsing CSV
- `backup_manager.py` - Sauvegardes
- `analytics.py` / `analytics_v2.py` - Statistiques
- `utils.py` - Fonctions utilitaires
- `logger.py` - Logging
- `exceptions.py` - Classes exceptions

## Schéma DB simplifié

### Tables principales
```sql
transactions:
  - id, date, label, amount
  - category_validated, status
  - member, tags (JSON), tx_hash

categories:
  - id, name, emoji, is_fixed, suggested_tags

members:
  - id, name, member_type

learning_rules:
  - id, pattern, category, priority
```

## Conventions spécifiques

### Import IA
```python
from modules.ai import detect_amount_anomalies
from modules.ai_manager import get_ai_provider, get_active_model_name
```

### Import DB
```python
from modules.db.connection import get_db_connection
from modules.db.transactions import get_all_transactions, add_transaction
```

### Import UI
```python
from modules.ui import load_css, card_kpi, display_flash_messages
from modules.ui.components.transaction_drill_down import render_transaction_drill_down
```

### Gestion erreurs
```python
from modules.exceptions import ValidationError, DatabaseError
from modules.logger import logger
```

### Sécurité
```python
from modules.utils import escape_html, safe_html_template
```

## Anti-patterns spécifiques

| Problème | Solution |
|----------|----------|
| `from modules.ui import card_kpi` dans boucle | Importer une seule fois en haut |
| Modification DB sans invalider cache | `st.cache_data.clear()` |
| Requête DB sans context manager | `with get_db_connection() as conn:` |
| Clés widgets en dur | `key=f"btn_{unique_id}"` |
