---
name: financeperso-specific
description: Conventions spécifiques au projet FinancePerso (app Streamlit de gestion financière). À utiliser TOUJOURS COMBINÉ avec python-app-auditor (audit code) et/ou streamlit-app-auditor (audit fonctionnel). Ce skill fournit les patterns, architecture et bonnes pratiques propres à FinancePerso. Ne pas utiliser seul - toujours combiner avec un skill d'audit technique.
---

# FinancePerso - Conventions Projet

## Architecture du projet

### Structure
```
FinancePerso/
├── app.py                    # Onboarding + Dashboard
├── pages/                    # Pages Streamlit (numérotées)
│   ├── 1_Import.py
│   ├── 2_Validation.py
│   ├── 3_Synthese.py
│   └── ...
├── modules/                  # Modules métier
│   ├── ai/                  # Suite IA (anomaly_detector, budget_predictor...)
│   ├── db/                  # Couche accès données (connection, transactions...)
│   ├── ui/                  # Composants UI (feedback, layout, components)
│   └── *.py                 # Modules métier (categorization, ingestion...)
├── Data/
│   └── finance.db          # Base SQLite
└── tests/                   # Tests
```

## Patterns spécifiques

### Connexion base de données
```python
from modules.db.connection import get_db_connection

with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE id = ?", (id,))
```

### Session State
```python
# Initialisation toujours avec check
if 'key' not in st.session_state:
    st.session_state.key = default_value

# Modification + rerun
st.session_state.key = new_value
st.rerun()
```

### Widget keys
Format obligatoire: `f"{type}_{unique_id}"`
```python
st.button("Save", key=f"btn_save_{tx_id}")
st.text_input("Label", key=f"input_label_{i}")
```

### Messages utilisateur
Toujours en français:
```python
st.success("✅ Transaction enregistrée")
st.error("❌ Une erreur est survenue")
```

## Modules IA

Pattern d'utilisation:
```python
from modules.ai import detect_amount_anomalies
from modules.ai_manager import get_ai_provider

provider = get_ai_provider()
anomalies = detect_amount_anomalies(df)
```

## UI Components

Import convention:
```python
from modules.ui import load_css, card_kpi, display_flash_messages
from modules.ui.components import render_transaction_drill_down
```

## Gestion des transactions

- `tx_hash` pour déduplication
- Tags stockés comme JSON array
- Table `transaction_history` pour undo

## Tests

Lancer tests:
```bash
pytest
pytest tests/db/ -v
pytest tests/ai/ -v
```

## Combinaison avec les skills globaux

Ce skill contient les conventions spécifiques à FinancePerso. Pour un audit complet, **toujours le combiner** avec:

### Audit technique code
→ **python-app-auditor** + **financeperso-specific**

```
1. Lire AGENTS.md + ce skill pour conventions
2. Lancer python-app-auditor pour audit qualité/sécurité
3. Appliquer les patterns spécifiques FinancePerso
```

### Audit fonctionnel Streamlit  
→ **streamlit-app-auditor** + **financeperso-specific**

```
1. Lancer l'app avec streamlit-app-auditor
2. Tester les fonctionnalités métier
3. Vérifier les patterns FinancePerso (session_state, cache, etc.)
```

### Audit UX
→ **ux-product-designer** seul (pas besoin de ce skill)

### Audit produit/stratégie
→ **product-indispensability-audit** seul (pas besoin de ce skill)

## Références

- [references/architecture.md](references/architecture.md) - Détails architecture
- AGENTS.md à la racine - Guide complet
